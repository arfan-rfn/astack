"""Prepare upstream packages in separate, immutable provider and state roots."""
import argparse
import hashlib
import os
from pathlib import Path
import subprocess
import sys
import tempfile

try:
    from astack.workflow import WorkflowError, SHA, NAME, atomic, encoded, now, read_json, run
except ModuleNotFoundError:  # Standalone project snapshot, adjacent to workflow.py.
    from workflow import WorkflowError, SHA, NAME, atomic, encoded, now, read_json, run


def rendered_identity(root):
    """Hash discovered instructions and references, following links with cycle detection."""
    hashes = {}
    def walk(path, name, ancestors):
        resolved = path.resolve()
        if resolved in ancestors:
            raise WorkflowError(f"Cyclic upstream installation: {path}")
        if path.is_dir():
            if path.name in ("node_modules", ".git"):
                return
            for child in sorted(path.iterdir()):
                walk(child, f"{name}/{child.name}", ancestors | {resolved})
        elif path.is_file():
            hashes[name] = {"sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                            "mode": path.stat().st_mode & 0o777}
        else:
            raise WorkflowError(f"Broken upstream reference: {path}")
    walk(root, "skills", set())
    return hashlib.sha256(encoded(hashes)).hexdigest()


def verify(target, spec):
    record = read_json(target / "prepared.json")
    revision = run(["git", "rev-parse", "HEAD"], cwd=target / "source").decode().strip()
    if revision != spec["revision"] or revision != record["source_revision"]:
        raise WorkflowError("Gstack source revision drift")
    if run(["git", "status", "--porcelain", "--untracked-files=no"], cwd=target / "source"):
        raise WorkflowError("Gstack tracked source drift")
    if record["rendered_identity"] != rendered_identity(target / record["skills_path"]):
        raise WorkflowError("Gstack rendered instructions drift")
    env = os.environ | record["environment"]
    for key in ("auto_upgrade", "update_check"):
        value = run([str(target / "source/bin/gstack-config"), "get", key], env=env).decode().strip()
        if value != "false":
            raise WorkflowError(f"Gstack {key} must remain false")
    return record


def prepare(target, spec, adapter, source=None):
    if adapter not in ("codex", "claude") or not SHA.fullmatch(spec["revision"]):
        raise WorkflowError("Unsupported adapter or nonimmutable upstream pin")
    target = target.resolve()
    if (target / "prepared.json").exists():
        record = verify(target, spec)
        if record["adapter"] != adapter:
            raise WorkflowError("Prepared generation belongs to a different adapter; use a new target")
        return record
    if target.exists():
        raise WorkflowError("Target exists without verified preparation; use a new empty generation")
    target.mkdir(parents=True, mode=0o700)
    # This path never becomes active automatically. A failed setup is retained for inspection.
    env = os.environ | {"GSTACK_STATE_ROOT": str(target / "state"),
                        "CODEX_HOME": str(target / "codex"),
                        "CLAUDE_CONFIG_DIR": str(target / "claude"),
                        "GSTACK_SKIP_PLAYWRIGHT": "1", "GSTACK_SKIP_FONTS": "1",
                        "GSTACK_HARNESS_AUTO": "0"}
    run(["git", "clone", "--no-hardlinks", "--no-checkout", str(source or spec["repository"]),
         str(target / "source")])
    run(["git", "remote", "set-url", "origin", spec["repository"]], cwd=target / "source")
    # Always prove provenance against upstream even when reusing a local object cache.
    run(["git", "fetch", "origin", spec["revision"]], cwd=target / "source")
    run(["git", "checkout", "--detach", spec["revision"]], cwd=target / "source")
    setup = target / "source/setup"
    result = subprocess.run([str(setup), "--host", adapter, "--global", "--no-team",
                             "--prefix", "--no-browser", "--no-harness-auto"],
                            env=env, cwd=target / "source", capture_output=True)
    atomic(target / "setup.log", result.stdout + result.stderr)
    if result.returncode:
        raise WorkflowError(f"Upstream setup failed ({result.returncode}); inspect {target / 'setup.log'}")
    for key, value in (("auto_upgrade", "false"), ("update_check", "false"), ("telemetry", "off")):
        run([str(target / "source/bin/gstack-config"), "set", key, value], env=env)
    skill_path = f"{adapter}/skills"
    record = {"schema": 1, "prepared_at": now(), "adapter": adapter,
              "source_revision": spec["revision"], "source_repository": spec["repository"],
              "skills_path": skill_path, "rendered_identity": rendered_identity(target / skill_path),
              "environment": {k: env[k] for k in ("GSTACK_STATE_ROOT", "CODEX_HOME", "CLAUDE_CONFIG_DIR")},
              "browser": "pending: Chromium not installed by this preparation"}
    atomic(target / "prepared.json", encoded(record))
    return verify(target, spec)


def restore_skills(directory, lock_path, spec):
    """Invoke the manager in an empty candidate; never accept existing directories."""
    directory = directory.resolve()
    if directory.exists():
        raise WorkflowError("Skills restoration requires a nonexistent candidate directory")
    original = lock_path.read_bytes()
    expected = read_json(lock_path).get("skills", {})
    if not expected:
        raise WorkflowError("A nonempty manager-owned skills lock is required")
    directory.mkdir(parents=True, mode=0o700)
    atomic(directory / "skills-lock.json", original)
    with tempfile.TemporaryDirectory(prefix="astack-skills-cli-") as temp:
        cli = Path(temp)
        atomic(cli / "package.json", encoded({"private": True, "dependencies": {"skills": spec["version"]}}))
        run(["npm", "install", "--package-lock-only", "--ignore-scripts", "--no-audit", "--no-fund"], cwd=cli)
        resolved = read_json(cli / "package-lock.json")["packages"]["node_modules/skills"]
        if resolved["integrity"] != spec["integrity"] or resolved["version"] != spec["version"]:
            raise WorkflowError("Skills CLI integrity differs from the approved tool lock")
        run(["npm", "ci", "--ignore-scripts", "--no-audit", "--no-fund"], cwd=cli)
        package = cli / "node_modules/skills"
        binary = read_json(package / "package.json")["bin"]
        binary = binary["skills"] if isinstance(binary, dict) else binary
        run(["node", str(package / binary), "experimental_install", "--frozen-lockfile", "--force"],
            cwd=directory, env=os.environ | {"DISABLE_TELEMETRY": "1"})
    if (directory / "skills-lock.json").read_bytes() != original:
        raise WorkflowError("Skill manager changed a frozen lock")
    for name in expected:
        if not NAME.fullmatch(name) or not (directory / ".agents/skills" / name / "SKILL.md").is_file():
            raise WorkflowError(f"Skill manager did not restore locked skill: {name}")
    return {"restored_at": now(), "identity": rendered_identity(directory / ".agents/skills")}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--lock", type=Path, required=True)
    sub = parser.add_subparsers(dest="command", required=True)
    for command in ("gstack-prepare", "gstack-verify"):
        p = sub.add_parser(command)
        p.add_argument("--target", type=Path, required=True)
        if command == "gstack-prepare":
            p.add_argument("--adapter", choices=["codex", "claude"], required=True)
            p.add_argument("--source", type=Path)
    p = sub.add_parser("skills-restore")
    p.add_argument("--target", type=Path, required=True)
    p.add_argument("--skills-lock", type=Path, required=True)
    args = parser.parse_args()
    try:
        lock = read_json(args.lock)
        if args.command == "gstack-prepare":
            result = prepare(args.target, lock["gstack"], args.adapter, args.source)
        elif args.command == "gstack-verify":
            result = verify(args.target.resolve(), lock["gstack"])
        else:
            result = restore_skills(args.target, args.skills_lock, lock["skills_cli"])
        print(encoded(result).decode(), end="")
    except (WorkflowError, OSError, KeyError) as exc:
        print(f"upstream: {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
