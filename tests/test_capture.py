import shutil
import unittest
from datetime import date
from pathlib import Path

from repo_log.capture import distill_transcript, write_dialogue_page
from repo_log.paths import repo_root


class CaptureTests(unittest.TestCase):
    def setUp(self):
        self.root = repo_root()
        self.out = self.root / "tests" / ".tmp" / "capture"
        shutil.rmtree(self.out, ignore_errors=True)

    def tearDown(self):
        shutil.rmtree(self.out, ignore_errors=True)

    def test_distill_sample_jsonl(self):
        sample = self.root / "tests" / "fixtures" / "transcripts" / "sample.jsonl"
        bullets = distill_transcript(sample)
        self.assertGreaterEqual(len(bullets), 2)
        self.assertTrue(any("径向表" in b for b in bullets))
        self.assertLessEqual(len(bullets), 15)

    def test_write_stays_in_repo(self):
        sample = self.root / "tests" / "fixtures" / "transcripts" / "sample.jsonl"
        dest = write_dialogue_page(
            self.out,
            title="封装后光型",
            source="Cursor",
            concept="封装后光型",
            bullets=distill_transcript(sample),
            day=date(2026, 9, 12),
        )
        self.assertTrue(dest.is_file())
        self.assertTrue(str(dest.resolve()).startswith(str(self.root.resolve())))
        text = dest.read_text(encoding="utf-8")
        self.assertIn("type:: 对话", text)
        self.assertIn("[[概念/封装后光型]]", text)

    def test_write_outside_repo_refused(self):
        with self.assertRaises(ValueError):
            write_dialogue_page(
                Path(r"D:\Knowledge\logseq-optics\pages"),
                title="x",
                source="Cursor",
                concept="y",
                bullets=["要点"],
            )
