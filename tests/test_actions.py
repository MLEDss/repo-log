import shutil
import unittest

from repo_log.actions import (
    add_project,
    capture_file,
    catalog_notes,
    drop_project,
    init_notes,
    load_state,
)
from repo_log.logseq_names import page_to_filename
from repo_log.paths import repo_root
from repo_log.settings import empty_settings, save_settings


class ActionTests(unittest.TestCase):
    def setUp(self):
        self.root = repo_root()
        self.tmp = self.root / "tests" / ".tmp" / "actions-run"
        shutil.rmtree(self.tmp, ignore_errors=True)
        self.tmp.mkdir(parents=True)
        self.settings = self.tmp / "settings.json"
        self.graph = self.tmp / "notes"
        self.fixtures = self.root / "tests" / "fixtures" / "projects"
        data = empty_settings()
        data["notes_out"] = str(self.graph)
        save_settings(data, self.settings)

    def tearDown(self):
        shutil.rmtree(self.tmp, ignore_errors=True)

    def test_init_add_catalog_capture(self):
        init = init_notes(self.settings)
        self.assertTrue(init.ok)
        self.assertTrue((self.graph / "logseq" / "config.edn").is_file())
        added = add_project(
            self.fixtures / "cursor-demo",
            ide="cursor",
            settings_path=self.settings,
        )
        self.assertTrue(added.ok)
        st = load_state(self.settings)
        self.assertEqual(len(st["projects"]), 1)
        cat = catalog_notes(self.settings)
        self.assertTrue(cat.ok)
        hub = self.graph / "pages" / page_to_filename("对接/Cursor")
        self.assertTrue(hub.is_file())
        sample = self.root / "tests" / "fixtures" / "transcripts" / "sample.jsonl"
        cap = capture_file(
            sample,
            kind="cursor",
            title="封装后光型",
            concept="封装后光型",
            settings_path=self.settings,
        )
        self.assertTrue(cap.ok)
        self.assertTrue(any(self.graph.joinpath("pages").glob("对话___*.md")))

    def test_add_missing_folder_and_empty_catalog(self):
        missing = add_project(self.tmp / "no-such", settings_path=self.settings)
        self.assertFalse(missing.ok)
        empty = catalog_notes(self.settings)
        self.assertFalse(empty.ok)
        add_project(
            self.fixtures / "chatgpt-demo",
            ide="chatgpt",
            settings_path=self.settings,
        )
        dropped = drop_project("chatgpt-demo", settings_path=self.settings)
        self.assertTrue(dropped.ok)
        gone = drop_project("chatgpt-demo", settings_path=self.settings)
        self.assertFalse(gone.ok)


class GuiSmokeTests(unittest.TestCase):
    def test_window_title(self):
        try:
            import tkinter
        except ImportError:
            self.skipTest("tkinter missing")
        try:
            probe = tkinter.Tk()
            probe.destroy()
        except tkinter.TclError:
            self.skipTest("no display")
        from repo_log.gui import RepoLogApp

        tmp = repo_root() / "tests" / ".tmp" / "gui-run"
        shutil.rmtree(tmp, ignore_errors=True)
        tmp.mkdir(parents=True)
        settings = tmp / "settings.json"
        data = empty_settings()
        data["notes_out"] = str(tmp / "notes")
        save_settings(data, settings)
        app = RepoLogApp(settings_path=settings)
        app.withdraw()
        try:
            self.assertEqual(app.title(), "Repo Log")
            self.assertIn("未初始化", app.graph_var.get())
        finally:
            app.destroy()
            shutil.rmtree(tmp, ignore_errors=True)
