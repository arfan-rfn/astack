import contextlib
import io
import json
import os
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch

from astack import workflow as w


SOURCE = Path(__file__).resolve().parents[1]


class WorkflowTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.base = Path(self.temp.name).resolve()
        self.source = self.base / "source"
        self.source.mkdir()
        w.run(["git", "init", "-q", str(self.source)])
        for folder in ("skills", "profiles", "astack"):
            import shutil
            shutil.copytree(SOURCE / folder, self.source / folder,
                            ignore=shutil.ignore_patterns("__pycache__"))
        (self.source / "tools.lock.json").write_bytes((SOURCE / "tools.lock.json").read_bytes())
        self.rev = self.commit("initial")
        self.root = self.base / "project"
        self.root.mkdir()
        w.run(["git", "init", "-q", str(self.root)])
        self.d = json.loads((SOURCE / "examples/workflow.json").read_text())
        self.d["bundle"]["revision"] = self.rev
        self.d["capabilities"] = {}
        (self.root / "workflow.json").write_bytes(w.encoded(self.d))
        (self.root / "README.md").write_text("Project rules\n")
        self.state = self.base / "state"
        self.host = {"projects": {"example": {"path": str(self.root), "drained": True}}}
        self.p = w.Project(self.root, self.state, self.host)

    def commit(self, message):
        w.run(["git", "add", "."], cwd=self.source)
        w.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
               "commit", "-qm", message], cwd=self.source)
        return w.run(["git", "rev-parse", "HEAD"], cwd=self.source).decode().strip()

    def files(self, rev=None):
        return w.snapshot(self.p, self.source, rev or self.rev)

    def install(self):
        with self.p.lock():
            self.p.activate(self.files())

    def new_revision(self):
        path = self.source / "skills/workflow-build/SKILL.md"
        path.write_text(path.read_text() + "\nA reviewed improvement.\n")
        return self.commit("improve build")

    def test_bootstrap_is_exact_and_idempotent(self):
        self.install()
        files = self.files()
        before = {n: (w.entry(self.root / n), (self.root / n).lstat().st_mtime_ns) for n in files}
        with self.p.lock():
            self.assertFalse(self.p.activate(files))
        after = {n: (w.entry(self.root / n), (self.root / n).lstat().st_mtime_ns) for n in files}
        self.assertEqual(before, after)
        self.assertTrue(self.p.doctor()["ok"])
        self.assertFalse((self.root / "skills-lock.json").exists())

    def test_source_worktree_edits_are_not_consumed(self):
        (self.source / "skills/workflow-build/SKILL.md").write_text("uncommitted drift")
        self.install()
        self.assertNotIn("uncommitted", (self.root / ".agents/skills/workflow-build/SKILL.md").read_text())

    def test_managed_edit_stops_with_diff(self):
        self.install()
        path = self.root / ".agents/skills/workflow-build/SKILL.md"
        path.write_text(path.read_text() + "\nlocal customization\n")
        with self.p.lock(), self.assertRaisesRegex(w.WorkflowError, "local customization"):
            self.p.activate(self.files(self.new_revision()))
        self.assertIn("local customization", path.read_text())
        self.assertFalse(self.p.doctor()["ok"])

    def test_initial_collision_is_not_replaced(self):
        path = self.root / ".agents/skills/workflow-build/SKILL.md"
        path.parent.mkdir(parents=True)
        path.write_text("custom")
        with self.p.lock(), self.assertRaisesRegex(w.WorkflowError, "Unmanaged collision"):
            self.p.activate(self.files())
        self.assertEqual(path.read_text(), "custom")

    def test_missing_reference_rolls_back_failed_activation(self):
        self.d["documents"].append("missing.md")
        (self.root / "workflow.json").write_bytes(w.encoded(self.d))
        self.p = w.Project(self.root, self.state, self.host)
        with self.p.lock(), self.assertRaisesRegex(w.WorkflowError, "Missing or external project reference"):
            self.p.activate(self.files())
        self.assertFalse((self.root / w.MANIFEST).exists())
        self.assertFalse((self.root / ".agents/skills/workflow-build/SKILL.md").exists())

    def test_duplicate_discovery_is_rejected(self):
        self.install()
        global_root = self.base / "global"
        path = global_root / "workflow-build/SKILL.md"
        path.parent.mkdir(parents=True)
        path.write_text("---\nname: workflow-build\n---\nGlobal copy\n")
        self.p.host["discovery_roots"] = [str(global_root)]
        self.assertTrue(any("Duplicate discovered" in f["message"] for f in self.p.doctor()["findings"]))

    def test_missing_skill_reference_is_rejected(self):
        path = self.source / "skills/workflow-build/SKILL.md"
        path.write_text(path.read_text() + "\n[required](references/missing.md)\n")
        revision = self.commit("broken reference")
        with self.p.lock(), self.assertRaisesRegex(w.WorkflowError, "Missing or external skill reference"):
            self.p.activate(self.files(revision))

    def test_source_skill_must_declare_selected_discovery_name(self):
        path = self.source / "skills/workflow-build/SKILL.md"
        path.write_text(path.read_text().replace("name: workflow-build", "name: unexpected"))
        rev = self.commit("wrong discovered name")
        with self.p.lock(), self.assertRaisesRegex(w.WorkflowError, "different discovered name"):
            self.p.activate(self.files(rev))

    def test_capability_failure_is_scoped(self):
        self.install()
        self.p.d["capabilities"] = {"ios": "optional"}
        self.assertTrue(self.p.doctor()["ok"])
        self.p.d["capabilities"]["ios"] = "required"
        self.assertFalse(self.p.doctor()["ok"])

    def test_interrupted_write_restores_previous_bytes(self):
        self.install()
        before = {n: w.entry(self.root / n) for n in self.files()}
        original = w.put
        calls = 0
        def failure(root, name, item):
            nonlocal calls
            calls += 1
            if calls == 3:
                raise OSError("disk failure")
            original(root, name, item)
        with self.p.lock(), patch.object(w, "put", failure), self.assertRaisesRegex(OSError, "disk failure"):
            self.p.activate(self.files(self.new_revision()))
        self.assertEqual(before, {n: w.entry(self.root / n) for n in before})
        self.assertFalse((self.p.local / "journal.json").exists())

    def test_crash_journal_recovery_and_concurrent_edit(self):
        self.install()
        path = ".agents/skills/workflow-build/SKILL.md"
        before = {path: w.entry(self.root / path)}
        after = {path: w.file_entry(b"partial write")}
        w.atomic(self.p.local / "journal.json", w.encoded({"before": before, "after": after}))
        w.put(self.root, path, after[path])
        self.assertFalse(self.p.doctor()["ok"])
        w.put(self.root, path, w.file_entry(b"concurrent edit"))
        with self.assertRaisesRegex(w.WorkflowError, "concurrent edit"):
            self.p.recover()
        w.put(self.root, path, after[path])
        self.p.recover()
        self.assertEqual(w.entry(self.root / path), before[path])
        self.assertTrue(self.p.doctor()["ok"])

    def test_concurrent_preparation_lock(self):
        with self.p.lock():
            code = "from astack.workflow import Project; import sys; p=Project(sys.argv[1],sys.argv[2]);\nwith p.lock(): pass"
            result = subprocess.run([sys.executable, "-c", code, str(self.root), str(self.state)],
                                    cwd=SOURCE, capture_output=True)
            self.assertNotEqual(result.returncode, 0)
            self.assertIn(b"activation lock", result.stderr)

    def test_active_session_and_undrained_target_refuse(self):
        with self.p.lock():
            w.atomic(self.p.local / "sessions/live.json", b"{}")
            with self.assertRaisesRegex(w.WorkflowError, "session leases"):
                self.p.activate(self.files())
            (self.p.local / "sessions/live.json").unlink()
            self.p.host["projects"]["example"]["drained"] = False
            with self.assertRaisesRegex(w.WorkflowError, "drained"):
                self.p.activate(self.files())

    def test_unmerged_git_entries_survive_activation_refusal(self):
        self.install()
        def git(*args):
            return w.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
                          *args], cwd=self.root)
        git("add", ".")
        git("commit", "-qm", "baseline")
        git("switch", "-c", "left")
        (self.root / "README.md").write_text("left\n")
        git("commit", "-am", "left")
        git("switch", "-c", "right", "HEAD~1")
        (self.root / "README.md").write_text("right\n")
        git("commit", "-am", "right")
        with self.assertRaises(w.WorkflowError):
            git("merge", "left")
        conflict = (self.root / "README.md").read_bytes()
        index = git("ls-files", "-u")
        self.assertTrue(index)
        with self.p.lock(), self.assertRaisesRegex(w.WorkflowError, "Unmerged Git entries"):
            self.p.activate(self.files(self.new_revision()))
        self.assertEqual(conflict, (self.root / "README.md").read_bytes())
        self.assertEqual(index, git("ls-files", "-u"))

    def test_candidate_staging_and_rollback_preserve_unrelated_files(self):
        self.install()
        next_rev = self.new_revision()
        files = self.files(next_rev)
        w.atomic(self.p.local / "candidates" / f"{next_rev}.json", w.encoded(files))
        self.assertEqual(w.descriptor(self.root)["bundle"]["revision"], self.rev)
        with self.p.lock():
            self.p.activate(files)
        (self.root / "unrelated.txt").write_text("keep")
        (self.root / "settings.json").write_text('{"unrelated":true}')
        history = w.read_json(self.p.local / "history" / f"{self.rev}.json")
        with self.p.lock():
            self.p.activate({k: v for k, v in history.items() if v is not None})
        self.assertEqual(w.descriptor(self.root)["bundle"]["revision"], self.rev)
        self.assertEqual((self.root / "unrelated.txt").read_text(), "keep")
        self.assertEqual((self.root / "settings.json").read_text(), '{"unrelated":true}')

    def test_dry_run_does_not_create_state(self):
        with contextlib.redirect_stdout(io.StringIO()):
            rc = w.main(["--state", str(self.state), "bootstrap", "--project", str(self.root),
                         "--source", str(self.source), "--dry-run"])
        self.assertEqual(rc, 0)
        self.assertFalse(self.state.exists())
        self.assertFalse((self.root / w.MANIFEST).exists())

    def test_unstaged_candidate_never_reports_success(self):
        self.install()
        with contextlib.redirect_stderr(io.StringIO()):
            rc = w.main(["--state", str(self.state), "bootstrap", "--project", str(self.root),
                         "--candidate", "a" * 40])
        self.assertEqual(rc, 2)
        self.assertEqual(w.descriptor(self.root)["bundle"]["revision"], self.rev)

    def test_copy_adapter_does_not_hide_same_name_in_another_folder(self):
        self.d["adapters"]["claude"] = "copy"
        (self.root / "workflow.json").write_bytes(w.encoded(self.d))
        self.p = w.Project(self.root, self.state, self.host)
        self.install()
        extra = self.root / ".claude/skills/alias/SKILL.md"
        extra.parent.mkdir(parents=True)
        extra.write_text("---\nname: workflow-build\n---\n")
        self.assertFalse(self.p.doctor()["ok"])

    def test_extra_file_in_managed_skill_blocks_update(self):
        self.install()
        extra = self.root / ".agents/skills/workflow-build/custom.md"
        extra.write_text("keep customization")
        with self.p.lock(), self.assertRaisesRegex(w.WorkflowError, "Unmanaged file in owned skill"):
            self.p.activate(self.files(self.new_revision()))
        self.assertEqual(extra.read_text(), "keep customization")

    def test_candidate_bytes_must_match_resolved_manifest(self):
        self.install()
        files = self.files(self.new_revision())
        files[".agents/skills/workflow-build/SKILL.md"] = w.file_entry(b"tampered candidate")
        with self.p.lock(), self.assertRaisesRegex(w.WorkflowError, "resolved manifest"):
            self.p.activate(files)
        self.assertTrue(self.p.doctor()["ok"])

    def test_project_configuration_change_is_staged_without_live_edits(self):
        self.install()
        old = (self.root / "workflow.json").read_bytes()
        proposal = self.base / "proposal.json"
        d = w.read_json(self.root / "workflow.json")
        d["checks"]["task"] = "make project-specific-test"
        proposal.write_bytes(w.encoded(d))
        with contextlib.redirect_stdout(io.StringIO()):
            rc = w.main(["--state", str(self.state), "update", "--project", str(self.root),
                         "--candidate", self.rev, "--source", str(self.source),
                         "--descriptor", str(proposal)])
        self.assertEqual(rc, 0)
        self.assertEqual(old, (self.root / "workflow.json").read_bytes())
        candidate = w.read_json(self.p.local / "candidates" / f"{self.rev}.json")
        with self.p.lock():
            self.p.activate(candidate)
        self.assertEqual(w.descriptor(self.root)["checks"]["task"], "make project-specific-test")

    def test_malformed_descriptor_returns_normal_cli_error(self):
        for value in ([], {"schema": 1, "project": "example", "bundle": []}):
            with self.subTest(value=value):
                (self.root / "workflow.json").write_bytes(w.encoded(value))
                output = io.StringIO()
                with contextlib.redirect_stderr(output):
                    rc = w.main(["doctor", "--project", str(self.root)])
                self.assertEqual(rc, 2)
                self.assertNotIn("Traceback", output.getvalue())

    def test_unsafe_paths_and_source_symlinks_are_refused(self):
        for name in ("../outside", "/outside", ".git/config", "a/../../outside"):
            with self.subTest(name=name), self.assertRaises(w.WorkflowError):
                w.safe_path(self.root, name)
        (self.root / "tools").symlink_to(self.base)
        with self.p.lock(), self.assertRaisesRegex(w.WorkflowError, "Symlink parent"):
            self.p.activate(self.files())
        (self.root / "tools").unlink()
        (self.source / "skills/workflow-build/outside").symlink_to("/etc/passwd")
        rev = self.commit("nonportable link")
        with self.assertRaisesRegex(w.WorkflowError, "regular portable"):
            self.files(rev)

    def test_copy_adapter_is_equal_and_drift_is_detected(self):
        self.d["adapters"]["claude"] = "copy"
        (self.root / "workflow.json").write_bytes(w.encoded(self.d))
        self.p = w.Project(self.root, self.state, self.host)
        self.install()
        self.assertTrue(self.p.doctor()["ok"])
        (self.root / ".claude/skills/workflow-build/references/state.md").write_text("bad")
        self.assertFalse(self.p.doctor()["ok"])

    def test_cli_exit_code_and_session_records(self):
        self.install()
        w.run(["git", "add", "."], cwd=self.root)
        w.run(["git", "-c", "user.name=Test", "-c", "user.email=test@example.invalid",
               "commit", "-qm", "project"], cwd=self.root)
        with contextlib.redirect_stdout(io.StringIO()):
            rc = w.main(["--state", str(self.state), "run", "--project", str(self.root),
                         "--", sys.executable, "-c", "raise SystemExit(7)"])
        self.assertEqual(rc, 7)
        self.assertEqual(self.p.leases(), [])
        record = w.read_json(next((self.p.local / "records").glob("*.json")))
        self.assertEqual(record["exit_code"], 7)
        self.assertIsNotNone(__import__("datetime").datetime.fromisoformat(record["created_at"]).tzinfo)


import sys

if __name__ == "__main__":
    unittest.main()
