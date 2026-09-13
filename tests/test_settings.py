import json
import unittest
from pathlib import Path

from repo_log.__main__ import main
from repo_log.catalog import write_catalog_from_settings
from repo_log.logseq_names import page_to_filename
from repo_log.paths import repo_root
from repo_log.settings import load_settings, slug_id, upsert_project


class SettingsTests(unittest.TestCase):
    def setUp(self):
        self.root = repo_root()
        self.tmp = self.root / "tests" / ".tmp" / "settings-run"
        self.settings = self.tmp / "settings.json"
        self.notes = self.tmp / "notes"
        self.fixtures = self.root / "tests" / "fixtures" / "projects"
        self.settings.parent.mkdir(parents=True, exist_ok=True)

    def test_slug_and_upsert_anytime(self):
        self.assertEqual(slug_id("LED Tools-chatgpt"), "led-tools-chatgpt")
        first = upsert_project(
            root=self.fixtures / "cursor-demo",
            ide="cursor",
            settings_path=self.settings,
        )
        self.assertEqual(first["id"], "cursor-demo")
        upsert_project(
            root=self.fixtures / "chatgpt-demo",
            ide="chatgpt",
            settings_path=self.settings,
        )
        again = upsert_project(
            root=self.fixtures / "cursor-demo",
            ide="cursor",
            project_id="cursor-demo",
            settings_path=self.settings,
        )
        data = load_settings(self.settings)
        self.assertEqual(len(data["projects"]), 2)
        self.assertEqual(again["root"], str(self.fixtures / "cursor-demo"))

    def test_add_then_catalog_from_settings(self):
        main(
            [
                "project",
                "add",
                "--root",
                str(self.fixtures / "cursor-demo"),
                "--ide",
                "cursor",
                "--settings",
                str(self.settings),
            ]
        )
        main(
            [
                "project",
                "add",
                "--root",
                str(self.fixtures / "chatgpt-demo"),
                "--ide",
                "chatgpt",
                "--settings",
                str(self.settings),
            ]
        )
        listed = json.loads(
            Path(self.settings).read_text(encoding="utf-8")
        )["projects"]
        self.assertEqual({p["ide"] for p in listed}, {"cursor", "chatgpt"})
        write_catalog_from_settings(self.settings, self.notes)
        hub = self.notes / "pages" / page_to_filename("对接/ChatGPT")
        self.assertTrue(hub.is_file())
        self.assertIn("chatgpt-demo", hub.read_text(encoding="utf-8"))
