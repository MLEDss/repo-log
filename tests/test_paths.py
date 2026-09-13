import tempfile
import unittest
from pathlib import Path

from repo_log.paths import assert_write_path, repo_root


class WritePathTests(unittest.TestCase):
    def test_inside_repo_ok(self):
        target = repo_root() / "tests" / ".tmp" / "ok.md"
        self.assertEqual(assert_write_path(target), target.resolve())

    def test_optics_simulation_rejected(self):
        with self.assertRaises(ValueError) as ctx:
            assert_write_path(r"D:\Optics Simulation\docs\should-not-write.md")
        self.assertIn("outside", str(ctx.exception))

    def test_knowledge_rejected(self):
        with self.assertRaises(ValueError):
            assert_write_path(r"D:\Knowledge\logseq-optics\pages\x.md")

    def test_temp_outside_rejected(self):
        outside = Path(tempfile.gettempdir()) / "repo-log-should-not-write.md"
        try:
            outside.resolve().relative_to(repo_root())
        except ValueError:
            pass
        else:
            self.skipTest("temp dir unexpectedly inside repo")
        with self.assertRaises(ValueError):
            assert_write_path(outside)
