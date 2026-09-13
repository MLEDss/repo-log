from __future__ import annotations

from pathlib import Path

from repo_log.logseq_names import page_to_filename
from repo_log.paths import assert_write_path
from repo_log.templates import load_template
from repo_log.usage import usage_page_body

CONFIG_EDN = """\
{:meta/version 1
 :preferred-format :markdown
 :file/name-format :triple-lowbar
 :feature/enable-journals? true
 :pages-directory "pages"
 :journals-directory "journals"}
"""

CONTENTS = """\
- [[使用]]
- [[对接/Cursor]]
- [[对接/ChatGPT]]
- 学习页（由引擎写入 `pages/`）
	- 概念、对话、案例、文献
- 工程计划只在镜像里看；改计划回原仓库。
"""

HUBS = {
    "对接/Cursor": "- 运行 `python -m repo_log catalog` 后写入 Cursor 工程镜像。\n",
    "对接/ChatGPT": "- 运行 `python -m repo_log catalog` 后写入 ChatGPT 工程镜像。\n",
}


def _write_if_missing(path: Path, text: str) -> None:
    if not path.is_file():
        path.write_text(text, encoding="utf-8")


def init_graph(root: Path | str, *, allow_external: bool = False) -> Path:
    dest = assert_write_path(root, allow_external=allow_external)
    (dest / "pages").mkdir(parents=True, exist_ok=True)
    (dest / "journals").mkdir(parents=True, exist_ok=True)
    logseq = dest / "logseq"
    logseq.mkdir(parents=True, exist_ok=True)
    (logseq / "config.edn").write_text(CONFIG_EDN, encoding="utf-8")
    (dest / "pages" / "contents.md").write_text(CONTENTS, encoding="utf-8")
    (dest / "pages" / page_to_filename("使用")).write_text(
        usage_page_body(graph=dest), encoding="utf-8"
    )
    for title, body in HUBS.items():
        _write_if_missing(dest / "pages" / page_to_filename(title), body)
    for stem in ("对话", "概念", "案例", "文献"):
        title = f"模板/{stem}"
        body = load_template(stem)
        header = f"template:: {stem}\ntemplate-including-parent:: false\n"
        if not body.startswith("template::"):
            body = header + body
        path = dest / "pages" / page_to_filename(title)
        _write_if_missing(path, body.rstrip() + "\n")
    return dest
