from __future__ import annotations

from datetime import date
from pathlib import Path

from repo_log.logseq_names import page_to_filename
from repo_log.paths import assert_write_path
from repo_log.templates import default_pages_dir, load_template


def _bullets(items: list[str], indent: str = "\t") -> str:
    cleaned = [item.strip() for item in items if item and item.strip()]
    if not cleaned:
        return f"{indent}- "
    return "\n".join(f"{indent}- {item}" for item in cleaned)


def write_page(
    page_title: str,
    body: str,
    *,
    out_dir: Path | str | None = None,
    allow_external: bool = False,
) -> Path:
    dest_dir = assert_write_path(out_dir or default_pages_dir(), allow_external=allow_external)
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / page_to_filename(page_title)
    dest.write_text(body.rstrip() + "\n", encoding="utf-8")
    return dest


def render_concept_page(
    *,
    name: str,
    summary: str = "",
    mixup: str = "",
    lumerical: str = "",
    lighttools: str = "",
    zemax: str = "",
    formula: str = "",
    cases: list[str] | None = None,
    dialogues: list[str] | None = None,
) -> str:
    formula_link = formula if not formula or formula.startswith("[[") else f"[[公式/{formula}]]"
    text = load_template("概念")
    text = text.replace("id::", f"id:: {name}", 1)
    if formula_link:
        text = text.replace("formula:: [[公式/]]", f"formula:: {formula_link}", 1)
    tab = "\t"
    replacements = {
        "- 一句话\n\t-\n": f"- 一句话\n{_bullets([summary])}\n",
        "- 易混\n\t-\n": f"- 易混\n{_bullets([mixup])}\n",
        f"{tab}- Lumerical\n{tab}{tab}-\n": f"{tab}- Lumerical\n{_bullets([lumerical], indent=tab * 2)}\n",
        f"{tab}- LightTools\n{tab}{tab}-\n": f"{tab}- LightTools\n{_bullets([lighttools], indent=tab * 2)}\n",
        f"{tab}- Zemax\n{tab}{tab}-\n": f"{tab}- Zemax\n{_bullets([zemax], indent=tab * 2)}\n",
        "- 案例\n\t-\n": f"- 案例\n{_bullets(cases or [])}\n",
        "- 对话\n\t-\n": f"- 对话\n{_bullets(dialogues or [])}\n",
    }
    for old, new in replacements.items():
        text = text.replace(old, new, 1)
    return text


def render_literature_page(
    *,
    citekey: str,
    concept: str = "",
    summary: str = "",
    highlights: list[str] | None = None,
    zotero: str = "",
) -> str:
    concept_link = concept if not concept or concept.startswith("[[") else f"[[概念/{concept}]]"
    text = load_template("文献")
    text = text.replace("citekey::", f"citekey:: {citekey}", 1)
    if zotero:
        text = text.replace("zotero::", f"zotero:: {zotero}", 1)
    if concept_link:
        text = text.replace("concept:: [[概念/]]", f"concept:: {concept_link}", 1)
    text = text.replace("- 一句话\n\t-\n", f"- 一句话\n{_bullets([summary])}\n", 1)
    hi = highlights or []
    text = text.replace(
        "- 高亮（只写自己的话，不贴大段原文）\n\t-\n",
        "- 高亮（只写自己的话，不贴大段原文）\n" + _bullets(hi) + "\n",
        1,
    )
    return text


def render_case_page(
    *,
    video_id: str,
    source: str = "",
    software: str = "",
    concept: str = "",
    summary: str = "",
    mixup: str = "",
    insight: str = "",
) -> str:
    concept_link = concept if not concept or concept.startswith("[[") else f"[[概念/{concept}]]"
    text = load_template("案例")
    text = text.replace("id:: bili-", f"id:: {video_id}", 1)
    if source:
        text = text.replace("source::", f"source:: {source}", 1)
    if software:
        text = text.replace("software::", f"software:: {software}", 1)
    if concept_link:
        text = text.replace("concept:: [[概念/]]", f"concept:: {concept_link}", 1)
    text = text.replace("repo:: docs/video-notes/", f"repo:: docs/video-notes/{video_id}.md", 1)
    text = text.replace("<id>", video_id)
    text = text.replace("- 一句话\n\t-\n", f"- 一句话\n{_bullets([summary])}\n", 1)
    text = text.replace(
        "- 易混 / 不能当什么模板\n\t-\n",
        f"- 易混 / 不能当什么模板\n{_bullets([mixup])}\n",
        1,
    )
    text = text.replace(
        "- 对本仓的启示\n\t-\n",
        f"- 对本仓的启示\n{_bullets([insight])}\n",
        1,
    )
    return text


def write_concept_page(name: str, *, out_dir: Path | str | None = None, allow_external: bool = False, **kwargs) -> Path:
    return write_page(
        f"概念/{name}",
        render_concept_page(name=name, **kwargs),
        out_dir=out_dir,
        allow_external=allow_external,
    )


def write_literature_page(citekey: str, *, out_dir: Path | str | None = None, allow_external: bool = False, **kwargs) -> Path:
    return write_page(
        f"文献/{citekey}",
        render_literature_page(citekey=citekey, **kwargs),
        out_dir=out_dir,
        allow_external=allow_external,
    )


def write_case_page(video_id: str, *, out_dir: Path | str | None = None, allow_external: bool = False, **kwargs) -> Path:
    return write_page(
        f"案例/{video_id}",
        render_case_page(video_id=video_id, **kwargs),
        out_dir=out_dir,
        allow_external=allow_external,
    )


def write_dialogue_from_template(
    *,
    title: str,
    source: str,
    concept: str,
    bullets: list[str],
    day: date | None = None,
    out_dir: Path | str | None = None,
    allow_external: bool = False,
) -> Path:
    day = day or date.today()
    concept_link = concept if not concept or concept.startswith("[[") else f"[[概念/{concept}]]"
    text = load_template("对话")
    text = text.replace("{{date}}", day.isoformat())
    text = text.replace("source:: Cursor", f"source:: {source}", 1)
    if concept_link:
        text = text.replace("concept:: [[概念/]]", f"concept:: {concept_link}", 1)
    point_lines = "\n".join(f"\t- {b}" for b in bullets) if bullets else "\t- 一句话结论"
    text = text.replace("\t- 一句话结论", point_lines, 1)
    return write_page(
        f"对话/{day.isoformat()}-{title}",
        text,
        out_dir=out_dir,
        allow_external=allow_external,
    )
