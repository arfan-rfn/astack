"""Small, dependency-free wrapper around project snapshots, Git and upstream setup."""

from __future__ import annotations

import argparse
import base64
import contextlib
import difflib
import fcntl
import hashlib
import json
import os
import platform
import re
import stat
import subprocess
import sys
import tempfile
from datetime import UTC, datetime
from pathlib import Path, PurePosixPath
from uuid import uuid4

VERSION = "0.1.0"
MANIFEST = ".workflow-managed.json"
SHA = re.compile(r"[0-9a-f]{40}\Z")
NAME = re.compile(r"[a-z0-9][a-z0-9-]*\Z")


class WorkflowError(Exception):
    pass


def now():
    return datetime.now(UTC).isoformat()


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, indent=2, sort_keys=True) + "\n").encode()


def read_json(path):
    try:
        return json.loads(path.read_bytes())
    except (OSError, ValueError) as exc:
        raise WorkflowError(f"Cannot read JSON {path}: {exc}") from exc


def atomic(path, data, mode=0o600):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temp = tempfile.mkstemp(prefix=".workflow-", dir=path.parent)
    try:
        with os.fdopen(fd, "wb") as stream:
            stream.write(data)
            stream.flush()
            os.fsync(stream.fileno())
        os.chmod(temp, mode)
        os.replace(temp, path)
        directory = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(temp):
            os.unlink(temp)


def run(argv, cwd=None, env=None):
    result = subprocess.run(argv, cwd=cwd, env=env, capture_output=True, check=False)
    if result.returncode:
        raise WorkflowError(
            f"Command failed ({result.returncode}): {argv[0]}\n"
            + (result.stdout + result.stderr).decode(errors="replace")[-3000:]
        )
    return result.stdout


def relative(value):
    if not isinstance(value, str) or not value or "\\" in value:
        raise WorkflowError(f"Invalid relative path: {value!r}")
    p = PurePosixPath(value)
    if (
        not p.parts
        or p.is_absolute()
        or any(x in ("..", ".git") for x in p.parts)
        or str(p) != value
    ):
        raise WorkflowError(f"Unsafe relative path: {value}")
    return p


def safe_path(root, name):
    p = relative(name)
    result = root / p
    for parent in result.parents:
        if parent == root:
            break
        if parent.is_symlink():
            raise WorkflowError(f"Symlink parent refused: {parent}")
    return result


def entry(path):
    if path.is_symlink():
        return {"link": os.readlink(path)}
    if not path.exists():
        return None
    if not path.is_file():
        raise WorkflowError(f"Expected file, found directory or special file: {path}")
    return {
        "data": base64.b64encode(path.read_bytes()).decode(),
        "mode": stat.S_IMODE(path.stat().st_mode),
    }


def file_entry(data, mode=0o644):
    return {"data": base64.b64encode(data).decode(), "mode": mode}


def identity(item):
    return digest(encoded(item)) if item is not None else None


def put(root, name, item):
    p = safe_path(root, name)
    if item is None:
        p.unlink(missing_ok=True)
    elif "link" in item:
        p.parent.mkdir(parents=True, exist_ok=True)
        temp = p.with_name(f".workflow-link-{uuid4().hex}")
        temp.symlink_to(item["link"])
        os.replace(temp, p)
    else:
        atomic(p, base64.b64decode(item["data"]), item["mode"])


def descriptor(root):
    d = read_json(root / "workflow.json")
    if not isinstance(d, dict):
        raise WorkflowError("workflow.json must contain an object")
    if d.get("schema") != 1 or not NAME.fullmatch(d.get("project", "")):
        raise WorkflowError("workflow.json needs schema 1 and a lowercase project identifier")
    bundle = d.get("bundle", {})
    if not isinstance(bundle, dict):
        raise WorkflowError("bundle must be an object")
    if not SHA.fullmatch(bundle.get("revision", "")):
        raise WorkflowError("bundle.revision must be an immutable 40-character Git commit")
    if not NAME.fullmatch(d.get("profile", "")):
        raise WorkflowError("An explicit profile is required")
    skills = d.get("skills", [])
    if not isinstance(skills, list) or not skills or any(not isinstance(s, str) for s in skills):
        raise WorkflowError("skills must be a nonempty array of names")
    if len(skills) != len(set(skills)) or any(not NAME.fullmatch(s) for s in skills):
        raise WorkflowError("Select a nonempty list of unique skill names")
    adapters = d.get("adapters", {})
    if (
        not isinstance(adapters, dict)
        or not adapters
        or any(
            k not in ("codex", "claude") or v not in ("symlink", "copy")
            for k, v in adapters.items()
        )
    ):
        raise WorkflowError("Adapters must select codex/claude and symlink/copy")
    if not isinstance(d.get("documents", []), list):
        raise WorkflowError("documents must be an array")
    for doc in d.get("documents", []):
        relative(doc)
    locks = d.get("locks", {})
    if not isinstance(locks, dict) or set(locks) - {"skills", "tools"}:
        raise WorkflowError("locks selects skills and tools lock paths, or null")
    for lock in locks.values():
        if lock is not None:
            relative(lock)
    if not isinstance(d.get("checks"), dict) or set(d["checks"]) != {"fast", "task", "full"}:
        raise WorkflowError("Declare fast, task, full checks; use null for unavailable lanes")
    for command in d["checks"].values():
        if command is not None and (not isinstance(command, str) or not command.strip()):
            raise WorkflowError("Checks are nonempty project commands or null")
    if not isinstance(d.get("capabilities", {}), dict):
        raise WorkflowError("capabilities must be an object")
    for cap, requirement in d.get("capabilities", {}).items():
        if not NAME.fullmatch(cap) or requirement not in ("required", "optional"):
            raise WorkflowError("Capability values must be required or optional")
    return d


class Project:
    def __init__(self, root, state, host=None, project_id=None):
        self.root = Path(root).resolve()
        self.state = Path(state).expanduser().resolve()
        if self.state == self.root or self.state.is_relative_to(self.root):
            raise WorkflowError("Host state must be outside the project checkout")
        self.d = descriptor(self.root)
        if project_id and self.d["project"] != project_id:
            raise WorkflowError("Project identifier does not match workflow.json")
        self.host = host or {}
        self.local = self.state / "projects" / digest(str(self.root).encode())[:24]

    @contextlib.contextmanager
    def lock(self):
        self.local.mkdir(parents=True, exist_ok=True, mode=0o700)
        with (self.local / "lock").open("a") as stream:
            try:
                fcntl.flock(stream, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except BlockingIOError as exc:
                raise WorkflowError(
                    "Another operation holds this project's activation lock"
                ) from exc
            yield

    def leases(self):
        path = self.local / "sessions"
        return list(path.glob("*.json")) if path.exists() else []

    def drained(self):
        if self.leases():
            raise WorkflowError("Active session leases block activation; close them explicitly")
        mapping = self.host.get("projects", {}).get(self.d["project"], {})
        if (
            mapping.get("drained") is not True
            or Path(mapping.get("path", "")).resolve() != self.root
        ):
            raise WorkflowError(
                "Host descriptor must declare this exact checkout drained before activation"
            )

    def managed(self):
        p = self.root / MANIFEST
        return read_json(p) if p.is_file() and not p.is_symlink() else None

    def conflicts(self, files=None):
        managed = self.managed()
        findings = []
        if managed:
            for name, expected in managed["files"].items():
                actual = entry(safe_path(self.root, name))
                if identity(actual) != expected:
                    message = f"Managed content drift: {name}"
                    # Show the exact patch when a local transaction backup is available.
                    backup = self.local / "installed.json"
                    if backup.exists():
                        old = read_json(backup).get(name)
                        if old and actual and "data" in old and "data" in actual:
                            before = (
                                base64.b64decode(old["data"])
                                .decode(errors="replace")
                                .splitlines(True)
                            )
                            after = (
                                base64.b64decode(actual["data"])
                                .decode(errors="replace")
                                .splitlines(True)
                            )
                            message += "\n" + "".join(
                                difflib.unified_diff(before, after, f"locked/{name}", name)
                            )
                    findings.append(message)
            owned_roots = {
                "/".join(n.split("/")[:3])
                for n in managed["files"]
                if n.startswith((".agents/skills/", ".claude/skills/"))
            }
            for name in sorted(owned_roots):
                folder = safe_path(self.root, name)
                if folder.is_symlink() or not folder.is_dir():
                    continue
                for path in folder.rglob("*"):
                    rel = path.relative_to(self.root).as_posix()
                    if not path.is_dir() and rel not in managed["files"]:
                        findings.append(f"Unmanaged file in owned skill: {rel}")
        if files:
            owned = managed["files"] if managed else {}
            for name in files:
                if (
                    name not in owned
                    and name != MANIFEST
                    and entry(safe_path(self.root, name)) is not None
                ):
                    if name == "workflow.json":
                        continue  # descriptor authoring is the explicit initial opt-in
                    findings.append(f"Unmanaged collision: {name}")
        if (self.root / ".git").exists():
            unmerged = run(["git", "ls-files", "-u"], cwd=self.root)
            if unmerged:
                findings.append("Unmerged Git entries exist; resolve them before activation")
        return findings

    def doctor(self):
        findings = [{"required": True, "message": x} for x in self.conflicts()]

        def add(message, required=True):
            findings.append({"required": required, "message": message})

        m = self.managed()
        if not m:
            add("No managed snapshot; run bootstrap")
        elif m.get("revision") != self.d["bundle"]["revision"]:
            add("Descriptor revision differs from installed snapshot")
        if (self.local / "journal.json").exists():
            add("Interrupted activation; bootstrap must recover the journal")
        references = self.d.get("documents", []) + [
            name for name in self.d.get("locks", {}).values() if name is not None
        ]
        for name in references:
            p = safe_path(self.root, name)
            if not p.is_file() or not p.resolve().is_relative_to(self.root):
                add(f"Missing or external project reference: {name}")
        names = {}
        roots = [self.root / ".agents/skills"]
        if "claude" in self.d["adapters"]:
            roots.append(self.root / ".claude/skills")
        roots.extend(Path(p).expanduser() for p in self.host.get("discovery_roots", []))
        # Canonical Claude aliases and equal generated copies are one implementation.
        for directory in roots:
            if not directory.exists():
                continue
            for skill in sorted(directory.iterdir()):
                md = skill / "SKILL.md"
                if skill.is_symlink() and not skill.exists():
                    add(f"Broken discovery link: {skill}")
                    continue
                if not md.is_file():
                    continue
                content = md.read_text()
                match = re.search(r"^name:\s*([\w-]+)\s*$", content, re.M)
                if not match:
                    add(f"Missing skill name: {md}")
                    continue
                name = match[1]
                prior = names.get(name)
                alias = (
                    skill.parent == self.root / ".claude/skills"
                    and skill.name == name
                    and self.d["adapters"].get("claude") == "copy"
                    and name in self.d["skills"]
                    and m
                    and f".claude/skills/{name}/SKILL.md" in m["files"]
                )
                if prior and md.resolve() != prior.resolve() and not alias:
                    add(f"Duplicate discovered name {name}: {prior} and {md}")
                names.setdefault(name, md)
                for link in (
                    re.findall(r"\]\(([^)#]+)(?:#[^)]*)?\)", content)
                    if name in self.d["skills"]
                    else []
                ):
                    if "://" in link or link.startswith("#"):
                        continue
                    target = md.parent / link
                    if not target.exists() or not target.resolve().is_relative_to(self.root):
                        add(f"Missing or external skill reference: {md}: {link}")
        for name in self.d["skills"]:
            canonical = self.root / ".agents/skills" / name / "SKILL.md"
            if not canonical.is_file():
                add(f"Selected skill not discoverable: {name}")
            elif not re.search(rf"^name:\s*{re.escape(name)}\s*$", canonical.read_text(), re.M):
                add(f"Selected skill declares a different discovered name: {name}")
            if "claude" in self.d["adapters"]:
                alias = self.root / ".claude/skills" / name / "SKILL.md"
                if not alias.is_file() or (
                    canonical.is_file() and alias.read_bytes() != canonical.read_bytes()
                ):
                    add(f"Adapter content mismatch: {name}")
        capabilities = self.host.get("capabilities", {})
        capability_results = {}
        for name, requirement in self.d.get("capabilities", {}).items():
            probe = capabilities.get(name)
            available = False
            if isinstance(probe, list) and probe and all(isinstance(s, str) for s in probe):
                with contextlib.suppress(OSError, subprocess.TimeoutExpired):
                    available = (
                        subprocess.run(
                            probe,
                            cwd=self.root,
                            stdout=subprocess.DEVNULL,
                            stderr=subprocess.DEVNULL,
                            timeout=10,
                        ).returncode
                        == 0
                    )
            if not available:
                add(f"Capability unavailable: {name}", requirement == "required")
            capability_results[name] = {"available": available, "requirement": requirement}
        return {
            "schema": 1,
            "project": self.d["project"],
            "revision": self.d["bundle"]["revision"],
            "ok": not any(f["required"] for f in findings),
            "findings": findings,
            "capabilities": capability_results,
        }

    def recover(self):
        journal = self.local / "journal.json"
        if not journal.exists():
            return
        self.drained()
        txn = read_json(journal)
        # A third party's edits after interruption must never be discarded.
        for name in txn["before"]:
            actual = entry(safe_path(self.root, name))
            if actual not in (txn["before"][name], txn["after"].get(name)):
                raise WorkflowError(
                    f"Recovery conflicts with a concurrent edit: {name}; journal retained"
                )
        for name, item in txn["before"].items():
            put(self.root, name, item)
        journal.unlink()
        self.d = descriptor(self.root)

    def activate(self, files):
        self.drained()
        if (self.local / "journal.json").exists():
            raise WorkflowError("Recover interrupted activation with bootstrap first")
        incoming = json.loads(base64.b64decode(files[MANIFEST]["data"]))
        desc = json.loads(base64.b64decode(files["workflow.json"]["data"]))
        identities = {k: identity(v) for k, v in files.items() if k != MANIFEST}
        if (
            incoming.get("files") != identities
            or incoming.get("revision") != desc["bundle"]["revision"]
        ):
            raise WorkflowError("Candidate content differs from its resolved manifest")
        conflicts = self.conflicts(files)
        if conflicts:
            raise WorkflowError("\n".join(conflicts))
        old = self.managed()
        names = set(files) | (set(old["files"]) if old else set()) | {MANIFEST}
        before = {n: entry(safe_path(self.root, n)) for n in sorted(names)}
        after = {n: files.get(n) for n in sorted(names)}
        if before == after:
            return False
        txn = {"created_at": now(), "before": before, "after": after}
        if old:
            atomic(self.local / "history" / f"{old['revision']}.json", encoded(before))
        atomic(self.local / "journal.json", encoded(txn))
        try:
            for name, item in after.items():
                put(self.root, name, item)
            # Validate activated content and references before releasing the gate.
            self.d = descriptor(self.root)
            report = self.doctor()
            errors = [
                f["message"]
                for f in report["findings"]
                if f["required"] and not f["message"].startswith("Interrupted activation")
            ]
            if errors:
                raise WorkflowError("\n".join(errors))
            atomic(self.local / "installed.json", encoded(files))
        except BaseException:
            for name, item in before.items():
                put(self.root, name, item)
            self.d = descriptor(self.root)
            (self.local / "journal.json").unlink()
            raise
        (self.local / "journal.json").unlink()
        return True


def snapshot(project, source, revision):
    if not SHA.fullmatch(revision):
        raise WorkflowError("Candidate must be an immutable 40-character commit")
    source = Path(source).resolve()
    if run(["git", "rev-parse", f"{revision}^{{commit}}"], cwd=source).decode().strip() != revision:
        raise WorkflowError("Source did not resolve the requested commit")
    d = json.loads(json.dumps(project.d))
    d["bundle"]["revision"] = revision

    def blob(name):
        return run(["git", "show", f"{revision}:{name}"], cwd=source)

    profile = json.loads(blob(f"profiles/{d['profile']}.json"))
    if not set(d["skills"]).issubset(profile["skills"]):
        raise WorkflowError("Selected skills are not part of the selected profile")
    files = {
        "workflow.json": file_entry(encoded(d)),
        "tools/workflow.py": file_entry(blob("astack/workflow.py"), 0o755),
    }
    tool_lock = d.get("locks", {}).get("tools")
    if tool_lock is not None:
        files[tool_lock] = file_entry(blob("tools.lock.json"))
        files["tools/upstream.py"] = file_entry(blob("astack/upstream.py"), 0o755)
    for name in d["skills"]:
        prefix = f"skills/{name}/"
        listing = run(["git", "ls-tree", "-r", "-z", revision, "--", prefix], cwd=source)
        found = False
        for record in listing.split(b"\0"):
            if not record:
                continue
            meta, rawpath = record.split(b"\t", 1)
            mode, kind, oid = meta.decode().split()
            path = rawpath.decode()
            if kind != "blob" or mode not in ("100644", "100755"):
                raise WorkflowError(f"Only regular portable skill assets are supported: {path}")
            rel = path[len(prefix) :]
            relative(rel)
            content = run(["git", "cat-file", "blob", oid], cwd=source)
            files[f".agents/skills/{name}/{rel}"] = file_entry(content, int(mode, 8) & 0o777)
            if d["adapters"].get("claude") == "copy":
                files[f".claude/skills/{name}/{rel}"] = files[f".agents/skills/{name}/{rel}"]
            found |= rel == "SKILL.md"
        if not found:
            raise WorkflowError(f"Source does not contain skill {name}")
        if d["adapters"].get("claude") == "symlink":
            files[f".claude/skills/{name}"] = {"link": f"../../.agents/skills/{name}"}
    manifest = {
        "schema": 1,
        "revision": revision,
        "source": d["bundle"].get("repository"),
        "adapter_version": VERSION,
        "files": {k: identity(v) for k, v in files.items()},
    }
    files[MANIFEST] = file_entry(encoded(manifest))
    return files


def inventory(roots):
    """Read only skill metadata and Git provenance; never read settings or credentials."""
    results = []
    for location in roots:
        root = Path(location).expanduser()
        if not root.exists():
            results.append({"path": str(root), "exists": False})
            continue
        for md in sorted(root.glob("*/SKILL.md")):
            content = md.read_bytes()
            match = re.search(rb"^name:\s*(.+)$", content, re.M)
            row = {
                "path": str(md.parent),
                "resolved_path": str(md.parent.resolve()),
                "name": match[1].decode() if match else None,
                "sha256": digest(content),
                "symlink": md.parent.is_symlink(),
                "owner": "unclassified",
            }
            try:
                row["revision"] = run(["git", "rev-parse", "HEAD"], cwd=md.parent).decode().strip()
                row["status"] = run(["git", "status", "--porcelain"], cwd=md.parent).decode()
            except WorkflowError:
                row["revision"] = None
            results.append(row)
    return {
        "schema": 1,
        "created_at": now(),
        "os": platform.system(),
        "architecture": platform.machine(),
        "skills": results,
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--version", action="version", version=VERSION)
    parser.add_argument("--host", type=Path, help="Private host descriptor (never committed)")
    parser.add_argument("--state", type=Path, default=Path.home() / ".local/state/astack")
    sub = parser.add_subparsers(dest="command", required=True)
    inv = sub.add_parser("inventory", help="Read-only inventory of explicit skill roots")
    inv.add_argument("roots", nargs="+", type=Path)
    for command in ("bootstrap", "doctor", "update", "rollback", "run", "session-close"):
        p = sub.add_parser(command)
        p.add_argument(
            "--project", required=True, help="Identifier mapped in host, or checkout path"
        )
        p.add_argument("--json", action="store_true")
        if command in ("bootstrap", "update"):
            p.add_argument(
                "--source", type=Path, help="Local Git source checkout, exact commits only"
            )
            p.add_argument("--candidate", help="Full immutable Git commit")
        if command == "bootstrap":
            p.add_argument("--dry-run", action="store_true")
        if command == "rollback":
            p.add_argument("--to", required=True)
        if command == "run":
            p.add_argument("argv", nargs=argparse.REMAINDER)
        if command == "session-close":
            p.add_argument("--token", required=True)
    args = parser.parse_args(argv)
    try:
        if args.command == "inventory":
            print(encoded(inventory(args.roots)).decode(), end="")
            return 0
        host = read_json(args.host) if args.host else {}
        mapping = host.get("projects", {}).get(args.project, {})
        root = mapping.get("path", args.project)
        p = Project(root, args.state, host, args.project if mapping else None)
        if args.command == "doctor":
            result = p.doctor()
            print(encoded(result).decode(), end="")
            return 0 if result["ok"] else 1
        if args.command == "bootstrap" and args.dry_run:
            conflicts = p.conflicts()
            result = {
                "dry_run": True,
                "revision": args.candidate or p.d["bundle"]["revision"],
                "project": p.d["project"],
                "conflicts": conflicts,
                "actions": [
                    "prepare locked snapshot",
                    "verify owned content and references",
                    "require drained target",
                    "preserve owned entries",
                    "activate snapshot",
                ],
                "active_sessions": len(p.leases()),
            }
            if args.source:
                files = snapshot(p, args.source, result["revision"])
                result["files"] = sorted(files)
                result["conflicts"] = p.conflicts(files)
            elif args.candidate:
                if not SHA.fullmatch(args.candidate):
                    raise WorkflowError("Candidate must be an immutable commit")
                files = read_json(p.local / "candidates" / f"{args.candidate}.json")
                result["files"] = sorted(files)
                result["conflicts"] = p.conflicts(files)
            print(encoded(result).decode(), end="")
            return 1 if result["conflicts"] else 0
        with p.lock():
            if args.command == "session-close":
                if not re.fullmatch(r"[0-9a-f]{32}", args.token):
                    raise WorkflowError("Invalid session token")
                (p.local / "sessions" / f"{args.token}.json").unlink()
                print("Session lease closed")
                return 0
            if args.command == "run":
                report = p.doctor()
                if not report["ok"]:
                    raise WorkflowError(encoded(report).decode())
                command = args.argv[1:] if args.argv[:1] == ["--"] else args.argv
                if not command:
                    raise WorkflowError("Supply an agent command after --")
                token = uuid4().hex
                declared = host.get("runtime_identity", {})
                runtime_version = None
                probe = declared.get("version_argv")
                if isinstance(probe, list) and probe and all(isinstance(s, str) for s in probe):
                    observed = subprocess.run(probe, capture_output=True, timeout=10)
                    if observed.returncode == 0:
                        runtime_version = observed.stdout.decode(errors="replace").strip()[:500]
                session = {
                    "schema": 1,
                    "created_at": now(),
                    "token": token,
                    "project_revision": run(["git", "rev-parse", "HEAD"], cwd=p.root)
                    .decode()
                    .strip(),
                    "bundle_revision": p.d["bundle"]["revision"],
                    "manifest": p.managed(),
                    "adapter_version": VERSION,
                    "python": platform.python_version(),
                    "runtime_identity": {
                        "provider": declared.get("provider"),
                        "model": declared.get("model"),
                        "effort": declared.get("effort"),
                        "version": runtime_version,
                        "selection_evidence": "host-declared; null means unobserved",
                    },
                    "runtime": command[0],
                    "capabilities": report,
                    "pid": os.getpid(),
                }
                lease = p.local / "sessions" / f"{token}.json"
                atomic(lease, encoded(session))
            elif args.command == "rollback":
                if not SHA.fullmatch(args.to):
                    raise WorkflowError("Rollback target must be an immutable commit")
                files = read_json(p.local / "history" / f"{args.to}.json")
                p.activate({k: v for k, v in files.items() if v is not None})
                print("Rollback verified")
                return 0
            else:
                if args.command == "bootstrap":
                    p.recover()
                revision = args.candidate or p.d["bundle"]["revision"]
                if not SHA.fullmatch(revision):
                    raise WorkflowError("Candidate must be an immutable commit")
                candidate = p.local / "candidates" / f"{revision}.json"
                if args.source:
                    files = snapshot(p, args.source, revision)
                elif candidate.exists():
                    files = read_json(candidate)
                elif args.command == "bootstrap" and p.managed() and not args.candidate:
                    report = p.doctor()
                    if not report["ok"]:
                        raise WorkflowError(encoded(report).decode())
                    print("Snapshot already verified; no changes")
                    return 0
                else:
                    raise WorkflowError(
                        "Provide --source with the locked Git checkout; no implicit latest fetch"
                    )
                if args.command == "update":
                    if not args.candidate:
                        raise WorkflowError("update requires --candidate <full commit>")
                    atomic(candidate, encoded(files))
                    print(f"Candidate staged at {candidate}; stable project unchanged")
                else:
                    changed = p.activate(files)
                    print(
                        "Snapshot activated and verified"
                        if changed
                        else "Snapshot already verified; no changes"
                    )
                return 0
        # The lock is released, but the durable lease blocks activation throughout the child run.
        try:
            result = subprocess.run(command, cwd=p.root)
            session["finished_at"] = now()
            session["exit_code"] = result.returncode
            atomic(p.local / "records" / f"{token}.json", encoded(session))
            return result.returncode
        finally:
            with p.lock():
                lease.unlink(missing_ok=True)
    except (
        WorkflowError,
        OSError,
        KeyError,
        TypeError,
        ValueError,
        AttributeError,
        subprocess.TimeoutExpired,
    ) as exc:
        print(f"workflow: {exc}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
