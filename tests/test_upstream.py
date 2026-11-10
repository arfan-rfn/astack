from pathlib import Path
import tempfile
import unittest

from astack.upstream import rendered_identity, restore_skills
from astack.workflow import WorkflowError


class UpstreamTests(unittest.TestCase):
    def test_generated_helper_bytes_and_modes_are_part_of_identity(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            binary = root / "gstack/browse/dist/browse"
            binary.parent.mkdir(parents=True)
            binary.write_bytes(b"helper one")
            before = rendered_identity(root)
            binary.write_bytes(b"helper two")
            self.assertNotEqual(before, rendered_identity(root))
            before = rendered_identity(root)
            binary.chmod(0o755)
            self.assertNotEqual(before, rendered_identity(root))

    def test_broken_and_cyclic_tool_links_are_refused(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            link = root / "link"
            link.symlink_to("missing")
            with self.assertRaisesRegex(WorkflowError, "Broken upstream"):
                rendered_identity(root)
            link.unlink()
            link.symlink_to(root)
            with self.assertRaisesRegex(WorkflowError, "Cyclic upstream"):
                rendered_identity(root)

    def test_restore_refuses_existing_candidate_before_touching_it(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root / "custom").write_text("preserve")
            with self.assertRaisesRegex(WorkflowError, "nonexistent"):
                restore_skills(root, root / "missing.json", {})
            self.assertEqual((root / "custom").read_text(), "preserve")
