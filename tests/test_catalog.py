import json
import shutil
import unittest
from pathlib import Path

from repo_log.catalog import write_catalog
from repo_log.logseq_names import page_to_filename
from repo_log.paths import repo_root


def _tree_files(root: Path) -> set[str]:
    return {p.relative_to(root).as_posix() for p in root.rglob("*") if p.is_file()}


class CatalogTests(unittest.TestCase):
    def setUp(self):
        self.root = repo_root()
        self.fixtures = self.root / "tests" / "fixtures" / "projects"
        self.out = self.root / "tests" / ".tmp" / "notes-out"
        shutil.rmtree(self.out, ignore_errors=True)
        self.config = self.root / "tests" / ".tmp" / "registry.json"
        self.config.parent.mkdir(parents=True, exist_ok=True)
        payload = {
            "projects": [
                {
                    "id": "cursor-demo",
                    "ide": "cursor",
                    "root": str(self.fixtures / "cursor-demo"),
                },
                {
                    "id": "chatgpt-demo",
                    "ide": "chatgpt",
                    "root": str(self.fixtures / "chatgpt-demo"),
                },
            ]
        }
        self.config.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")

    def tearDown(self):
        shutil.rmtree(self.out, ignore_errors=True)
        if self.config.exists():
            self.config.unlink()

    def test_mirrors_cursor_and_chatgpt_docs(self):
        before_c = _tree_files(self.fixtures / "cursor-demo")
        before_g = _tree_files(self.fixtures / "chatgpt-demo")
        written = write_catalog(self.config, self.out)
        self.assertGreaterEqual(len(written), 6)
        pages = self.out / "pages"
        plan = pages / page_to_filename("工程/cursor-demo/docs/计划")
        self.assertTrue(plan.is_file())
        text = plan.read_text(encoding="utf-8")
        self.assertIn("type:: 工程镜像", text)
        self.assertIn("Cursor 侧现行计划", text)
        hub_c = (pages / page_to_filename("对接/Cursor")).read_text(encoding="utf-8")
        hub_g = (pages / page_to_filename("对接/ChatGPT")).read_text(encoding="utf-8")
        self.assertIn("[[工程/cursor-demo]]", hub_c)
        self.assertIn("[[工程/chatgpt-demo]]", hub_g)
        self.assertEqual(before_c, _tree_files(self.fixtures / "cursor-demo"))
        self.assertEqual(before_g, _tree_files(self.fixtures / "chatgpt-demo"))
        self.assertFalse((self.fixtures / "cursor-demo" / "logseq").exists())
        self.assertFalse((self.fixtures / "chatgpt-demo" / "pages").exists())

    def test_refuses_writing_into_source_tree(self):
        with self.assertRaises(ValueError):
            write_catalog(self.config, self.fixtures / "cursor-demo")

    def test_refuses_writing_above_source_tree(self):
        with self.assertRaises(ValueError):
            write_catalog(self.config, self.fixtures)
