import json
import shutil
import sys
import tempfile
import unittest
from io import StringIO
from pathlib import Path

from repo_log.__main__ import main
from repo_log.graph import init_graph
from repo_log.logseq_names import page_to_filename
from repo_log.paths import repo_root


class GraphInitTests(unittest.TestCase):
    def setUp(self):
        self.root = repo_root()
        self.tmp = self.root / "tests" / ".tmp" / "graph-run"
        shutil.rmtree(self.tmp, ignore_errors=True)
        self.tmp.mkdir(parents=True)
        self.graph = self.tmp / "notes"
        self.settings = self.tmp / "settings.json"

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_init_creates_og_layout(self):
        main(
            [
                "init",
                "--out-dir",
                str(self.graph),
                "--settings",
                str(self.settings),
            ]
        )
        config = (self.graph / "logseq" / "config.edn").read_text(encoding="utf-8")
        self.assertIn(":file/name-format :triple-lowbar", config)
        self.assertIn(":preferred-format :markdown", config)
        self.assertTrue((self.graph / "pages" / "contents.md").is_file())
        self.assertTrue((self.graph / "journals").is_dir())
        self.assertTrue((self.graph / "pages" / page_to_filename("对接/Cursor")).is_file())
        self.assertTrue((self.graph / "pages" / page_to_filename("模板/对话")).is_file())
        usage = (self.graph / "pages" / page_to_filename("使用")).read_text(encoding="utf-8")
        self.assertIn("Logseq OG", usage)
        self.assertIn("入库", usage)
        self.assertIn("插件", usage)
        contents = (self.graph / "pages" / "contents.md").read_text(encoding="utf-8")
        self.assertIn("[[使用]]", contents)
        data = json.loads(self.settings.read_text(encoding="utf-8"))
        self.assertEqual(Path(data["notes_out"]), self.graph)

    def test_status_explains_how_to_open(self):
        main(
            [
                "init",
                "--out-dir",
                str(self.graph),
                "--settings",
                str(self.settings),
            ]
        )
        buf = StringIO()
        old = sys.stdout
        sys.stdout = buf
        try:
            code = main(["status", "--settings", str(self.settings)])
        finally:
            sys.stdout = old
        self.assertEqual(code, 0)
        text = buf.getvalue()
        self.assertIn(str(self.graph), text)
        self.assertIn("plugin/", text)
        self.assertIn("RL", text)

    def test_wrapper_script_sets_pythonpath(self):
        script = self.root / "repo-log.ps1"
        text = script.read_text(encoding="utf-8")
        self.assertIn("PYTHONPATH", text)
        self.assertIn("python -m repo_log", text)

    def test_capture_defaults_to_graph_pages(self):
        main(
            [
                "init",
                "--out-dir",
                str(self.graph),
                "--settings",
                str(self.settings),
            ]
        )
        sample = self.root / "tests" / "fixtures" / "transcripts" / "sample.jsonl"
        main(
            [
                "capture",
                "--transcript",
                str(sample),
                "--title",
                "封装后光型",
                "--concept",
                "封装后光型",
                "--settings",
                str(self.settings),
            ]
        )
        pages = self.graph / "pages"
        files = list(pages.glob("对话___*.md"))
        self.assertEqual(len(files), 1)
        self.assertIn("source:: Cursor", files[0].read_text(encoding="utf-8"))

    def test_init_refuses_outside_repo(self):
        with self.assertRaises(ValueError):
            init_graph(r"D:\Knowledge\logseq-optics")
        outside = Path(tempfile.gettempdir()) / "repo-log-graph"
        try:
            outside.resolve().relative_to(self.root)
        except ValueError:
            pass
        else:
            self.skipTest("temp dir unexpectedly inside repo")
        with self.assertRaises(ValueError):
            init_graph(outside)


class SkillAdapterTests(unittest.TestCase):
    def test_skill_calls_engine_and_forbids_external(self):
        path = repo_root() / ".cursor" / "skills" / "repo-log-capture" / "SKILL.md"
        text = path.read_text(encoding="utf-8")
        self.assertIn("python -m repo_log", text)
        self.assertIn("Never pass `--allow-external`", text)
        self.assertIn("repo-log.ps1", text)
