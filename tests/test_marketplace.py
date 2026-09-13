import importlib.util
import json
import unittest

from repo_log.paths import repo_root


def _load_fill():
    path = repo_root() / "scripts" / "fill_marketplace_repo.py"
    spec = importlib.util.spec_from_file_location("fill_marketplace_repo", path)
    mod = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(mod)
    return mod


class MarketplaceListingTests(unittest.TestCase):
    def test_fill_refuses_placeholder_and_does_not_write(self):
        mod = _load_fill()
        man = repo_root() / "docs" / "marketplace" / "packages" / "logseq-plugin-repo-log" / "manifest.json"
        before = man.read_text(encoding="utf-8")
        with self.assertRaises(ValueError):
            mod.fill("REPLACE_WITH_GITHUB_USER/repo-log")
        with self.assertRaises(ValueError):
            mod.fill("nopath")
        self.assertEqual(before, man.read_text(encoding="utf-8"))
        self.assertIn("MLEDss/repo-log", json.loads(before)["repo"])
        self.assertNotIn("REPLACE_WITH_GITHUB_USER", before)

    def test_publish_workflow_is_official_name(self):
        self.assertTrue((repo_root() / ".github" / "workflows" / "publish.yml").is_file())
        self.assertFalse((repo_root() / ".github" / "workflows" / "plugin-publish.yml").exists())
        self.assertTrue((repo_root() / "scripts" / "publish-marketplace.ps1").is_file())
        self.assertTrue((repo_root() / "docs" / "marketplace" / "PR.md").is_file())
