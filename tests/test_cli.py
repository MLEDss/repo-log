import shutil
import unittest
from pathlib import Path

from repo_log.__main__ import main
from repo_log.capture import distill_chatgpt_export
from repo_log.paths import repo_root


class CliTests(unittest.TestCase):
    def setUp(self):
        self.root = repo_root()
        self.out = self.root / "tests" / ".tmp" / "cli"
        shutil.rmtree(self.out, ignore_errors=True)

    def tearDown(self):
        shutil.rmtree(self.out, ignore_errors=True)

    def test_capture_jsonl_cli(self):
        sample = self.root / "tests" / "fixtures" / "transcripts" / "sample.jsonl"
        main(
            [
                "capture",
                "--transcript",
                str(sample),
                "--out-dir",
                str(self.out),
                "--title",
                "封装后光型",
                "--concept",
                "封装后光型",
            ]
        )
        files = list(self.out.glob("对话___*.md"))
        self.assertEqual(len(files), 1)
        text = files[0].read_text(encoding="utf-8")
        self.assertIn("source:: Cursor", text)
        self.assertIn("[[概念/封装后光型]]", text)
        self.assertLessEqual(text.count("\t- 问：") + text.count("\t- 答："), 15)

    def test_capture_chatgpt_cli(self):
        sample = self.root / "tests" / "fixtures" / "chatgpt" / "sample.json"
        title, bullets = distill_chatgpt_export(sample)
        self.assertEqual(title, "径向表 vs 文件光源")
        self.assertTrue(any("远场" in b for b in bullets))
        main(
            [
                "capture",
                "--chatgpt",
                str(sample),
                "--out-dir",
                str(self.out),
                "--concept",
                "文件光源",
            ]
        )
        text = next(self.out.glob("对话___*.md")).read_text(encoding="utf-8")
        self.assertIn("source:: ChatGPT", text)
        self.assertIn("[[概念/文件光源]]", text)

    def test_concept_and_literature(self):
        main(
            [
                "concept",
                "--name",
                "文件光源",
                "--summary",
                "带位置的射线，不是纯角表",
                "--mixup",
                "IES 远场表不是 rayfile",
                "--zemax",
                "Source File",
                "--formula",
                "os-led-source-model-v0",
                "--case",
                "[[案例/bili-zemax-led-source]]",
                "--out-dir",
                str(self.out),
            ]
        )
        concept = self.out / "概念___文件光源.md"
        self.assertTrue(concept.is_file())
        ctext = concept.read_text(encoding="utf-8")
        self.assertIn("id:: 文件光源", ctext)
        self.assertIn("带位置的射线", ctext)
        self.assertIn("[[公式/os-led-source-model-v0]]", ctext)
        main(
            [
                "literature",
                "--citekey",
                "smith2020",
                "--concept",
                "文件光源",
                "--summary",
                "只记自己的理解",
                "--highlight",
                "回射要留几何",
                "--out-dir",
                str(self.out),
            ]
        )
        lit = (self.out / "文献___smith2020.md").read_text(encoding="utf-8")
        self.assertIn("citekey:: smith2020", lit)
        self.assertIn("回射要留几何", lit)
        self.assertNotIn(".pdf", lit)

    def test_case_is_short_pointer(self):
        main(
            [
                "case",
                "--id",
                "bili-zemax-led-source",
                "--source",
                "Bilibili",
                "--software",
                "Zemax",
                "--concept",
                "文件光源",
                "--summary",
                "径向表 / RSMX；回射需几何",
                "--mixup",
                "不能当纯 rayfile 模板",
                "--insight",
                "O2 要自建杯+胶水",
                "--out-dir",
                str(self.out),
            ]
        )
        text = (self.out / "案例___bili-zemax-led-source.md").read_text(encoding="utf-8")
        self.assertIn("id:: bili-zemax-led-source", text)
        self.assertIn("docs/video-notes/bili-zemax-led-source.md", text)
        self.assertIn("逐帧表仍以仓库", text)
        self.assertNotIn("scene_0001", text)

    def test_export_inbox_and_refuse_external(self):
        main(
            [
                "concept",
                "--name",
                "BSDF",
                "--summary",
                "散射双向分布",
                "--out-dir",
                str(self.out),
            ]
        )
        inbox = self.root / "tests" / ".tmp" / "inbox"
        shutil.rmtree(inbox, ignore_errors=True)
        main(
            [
                "export-inbox",
                "--from-dir",
                str(self.out),
                "--out-dir",
                str(inbox),
            ]
        )
        self.assertTrue((inbox / "概念___BSDF.md").is_file())
        with self.assertRaises(ValueError):
            main(
                [
                    "case",
                    "--id",
                    "x",
                    "--out-dir",
                    r"D:\Knowledge\logseq-optics\pages",
                ]
            )
