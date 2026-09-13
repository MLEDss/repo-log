import json
import shutil
import threading
import unittest
import urllib.error
import urllib.request
from pathlib import Path

from repo_log.logseq_names import page_to_filename
from repo_log.paths import repo_root
from repo_log.server import make_server
from repo_log.settings import empty_settings, save_settings


class EngineHttpTests(unittest.TestCase):
    def setUp(self):
        self.root = repo_root()
        self.tmp = self.root / "tests" / ".tmp" / "server-run"
        shutil.rmtree(self.tmp, ignore_errors=True)
        self.tmp.mkdir(parents=True)
        self.settings = self.tmp / "settings.json"
        self.graph = self.tmp / "notes"
        data = empty_settings()
        data["notes_out"] = str(self.graph)
        save_settings(data, self.settings)
        self.httpd = make_server(host="127.0.0.1", port=0, settings_path=self.settings)
        self.thread = threading.Thread(target=self.httpd.serve_forever, daemon=True)
        self.thread.start()
        self.base = f"http://127.0.0.1:{self.httpd.server_address[1]}"

    def tearDown(self):
        self.httpd.shutdown()
        self.httpd.server_close()
        shutil.rmtree(self.tmp, ignore_errors=True)

    def _json(self, method: str, path: str, body: dict | None = None) -> dict:
        data = None if body is None else json.dumps(body).encode("utf-8")
        req = urllib.request.Request(
            self.base + path,
            data=data,
            method=method,
            headers={"Content-Type": "application/json"},
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            return json.loads(resp.read().decode("utf-8"))

    def test_init_add_catalog_via_http(self):
        st = self._json("GET", "/api/status")
        self.assertFalse(st["ready"])
        init = self._json("POST", "/api/init", {})
        self.assertTrue(init["ok"])
        self.assertTrue(init["ready"])
        demo = self.root / "tests" / "fixtures" / "projects" / "cursor-demo"
        added = self._json("POST", "/api/projects", {"root": str(demo), "ide": "cursor"})
        self.assertTrue(added["ok"])
        cat = self._json("POST", "/api/catalog", {})
        self.assertTrue(cat["ok"])
        hub = self.graph / "pages" / page_to_filename("对接/Cursor")
        self.assertTrue(hub.is_file())
        sample = self.root / "tests" / "fixtures" / "transcripts" / "sample.jsonl"
        cap = self._json(
            "POST",
            "/api/capture",
            {"kind": "cursor", "path": str(sample), "title": "封装后光型", "concept": "封装后光型"},
        )
        self.assertTrue(cap["ok"])
        self.assertTrue(any((self.graph / "pages").glob("对话___*.md")))

    def test_refuses_non_localhost_bind(self):
        with self.assertRaises(ValueError):
            make_server(host="0.0.0.0", port=0, settings_path=self.settings)


class PluginAdapterTests(unittest.TestCase):
    def test_plugin_matches_marketplace_spec(self):
        root = repo_root() / "plugin"
        pkg = json.loads((root / "package.json").read_text(encoding="utf-8"))
        self.assertEqual(pkg["logseq"]["id"], "logseq-plugin-repo-log")
        self.assertEqual(pkg["main"], "dist/index.html")
        self.assertIn("@logseq/libs", pkg.get("dependencies") or {})
        self.assertEqual(pkg["logseq"].get("unsupportedGraphType"), "db")
        self.assertTrue((root / "LICENSE").is_file())
        js = (root / "src" / "main.js").read_text(encoding="utf-8")
        self.assertIn('import "@logseq/libs"', js)
        self.assertIn("/api/catalog", js)
        self.assertIn("/api/capture", js)
        self.assertIn("registerSlashCommand", js)
        self.assertNotIn("createPage", js)
        self.assertNotIn("--allow-external", js)
        self.assertTrue((root / "icon.png").is_file())
        self.assertTrue((root / "showcase.png").is_file())
        workflow_path = repo_root() / ".github" / "workflows" / "publish.yml"
        self.assertTrue(workflow_path.is_file())
        self.assertFalse((repo_root() / ".github" / "workflows" / "plugin-publish.yml").exists())
        workflow = workflow_path.read_text(encoding="utf-8")
        self.assertIn("PLUGIN_NAME: logseq-plugin-repo-log", workflow)
        self.assertIn("contents: write", workflow)
        self.assertIn("${{ env.PLUGIN_NAME }}-${{ steps.build.outputs.tag_name }}.zip", workflow)
        self.assertIn("asset_name: package.json", workflow)
        self.assertIn("ncipollo/release-action", workflow)
        self.assertIn("plugin/LICENSE", workflow)
        manifest = json.loads(
            (repo_root() / "docs" / "marketplace" / "packages" / "logseq-plugin-repo-log" / "manifest.json").read_text(
                encoding="utf-8"
            )
        )
        self.assertEqual(manifest["title"], "Repo Log")
        self.assertFalse(manifest["effect"])
        self.assertFalse(manifest["supportsDB"])
        self.assertFalse(manifest["supportsDBOnly"])
        self.assertEqual(manifest["repo"], "MLEDss/repo-log")
        readme = (root / "README.md").read_text(encoding="utf-8")
        self.assertIn("python -m repo_log serve", readme)
        self.assertIn("./showcase.png", readme)
        self.assertNotIn("createPage", readme)
        root_readme = (repo_root() / "README.md").read_text(encoding="utf-8")
        self.assertIn("plugin/showcase.png", root_readme)
        self.assertIn("plugin/package.json", root_readme)
        pr = (repo_root() / "docs" / "marketplace" / "PR.md").read_text(encoding="utf-8")
        self.assertIn("package.json", pr)
        self.assertIn("LICENSE", pr)
