import unittest

from repo_log.logseq_names import page_to_filename


class PageNameTests(unittest.TestCase):
    def test_slash_becomes_triple_underscore(self):
        self.assertEqual(page_to_filename("概念/文件光源"), "概念___文件光源.md")

    def test_dialogue_page(self):
        self.assertEqual(
            page_to_filename("对话/2026-09-12-封装后光型"),
            "对话___2026-09-12-封装后光型.md",
        )

    def test_empty_rejected(self):
        with self.assertRaises(ValueError):
            page_to_filename("  /  ")
