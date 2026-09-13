from __future__ import annotations

import json
from datetime import date
from pathlib import Path

from repo_log.logseq_names import page_to_filename
from repo_log.paths import assert_write_path

_MAX_BULLETS = 15
_MAX_CHARS = 240


def _text_of(message: dict) -> str:
    content = message.get("message", {}).get("content") or message.get("content")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(str(item.get("text") or ""))
        return "\n".join(parts)
    return ""


def distill_transcript(path: Path, *, max_bullets: int = _MAX_BULLETS) -> list[str]:
    bullets: list[str] = []
    text = Path(path).read_text(encoding="utf-8")
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            obj = json.loads(line)
        except json.JSONDecodeError:
            continue
        role = obj.get("role") or obj.get("type")
        if role not in {"user", "assistant"}:
            continue
        body = " ".join(_text_of(obj).split())
        if not body:
            continue
        prefix = "问" if role == "user" else "答"
        bullets.append(f"{prefix}：{body[:_MAX_CHARS]}")
        if len(bullets) >= max_bullets:
            break
    return bullets


def distill_chatgpt_export(path: Path, *, max_bullets: int = _MAX_BULLETS) -> tuple[str, list[str]]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    title = str(data.get("title") or "untitled").strip() or "untitled"
    mapping = data.get("mapping") or {}
    ranked: list[tuple[float, str]] = []
    for node in mapping.values():
        if not isinstance(node, dict):
            continue
        msg = node.get("message") or {}
        role = ((msg.get("author") or {}).get("role"))
        if role not in {"user", "assistant"}:
            continue
        content = msg.get("content") or {}
        parts = content.get("parts") if isinstance(content, dict) else None
        if isinstance(parts, list):
            body = " ".join(str(p) for p in parts if isinstance(p, str))
        else:
            body = _text_of({"content": content})
        body = " ".join(body.split())
        if not body:
            continue
        prefix = "问" if role == "user" else "答"
        stamp = msg.get("create_time") or 0
        try:
            order = float(stamp)
        except (TypeError, ValueError):
            order = 0.0
        ranked.append((order, f"{prefix}：{body[:_MAX_CHARS]}"))
    ranked.sort(key=lambda item: item[0])
    bullets = [text for _, text in ranked[:max_bullets]]
    return title, bullets


def render_dialogue_page(
    *,
    title: str,
    source: str,
    concept: str,
    bullets: list[str],
    day: date | None = None,
) -> str:
    day = day or date.today()
    concept_link = concept if concept.startswith("[[") else f"[[概念/{concept}]]"
    lines = [
        f"type:: 对话",
        f"date:: {day.isoformat()}",
        f"source:: {source}",
        f"concept:: {concept_link}",
        "tags:: #对话",
        "",
        "- 要点",
    ]
    if bullets:
        for item in bullets:
            lines.append(f"\t- {item}")
    else:
        lines.append("\t- （空）")
    lines.extend(
        [
            "- 可操作",
            "\t- 下一步只干一件事",
            "- 证据",
            "\t- 仓库：",
            "\t- 案例：",
            "- 待核实",
            "\t-",
            "",
        ]
    )
    return "\n".join(lines)


def write_dialogue_page(
    out_dir: Path | str,
    *,
    title: str,
    source: str,
    concept: str,
    bullets: list[str],
    allow_external: bool = False,
    day: date | None = None,
) -> Path:
    dest_dir = assert_write_path(out_dir, allow_external=allow_external)
    dest_dir.mkdir(parents=True, exist_ok=True)
    page_name = f"对话/{day.isoformat() if day else date.today().isoformat()}-{title}"
    dest = dest_dir / page_to_filename(page_name)
    dest.write_text(
        render_dialogue_page(
            title=title, source=source, concept=concept, bullets=bullets, day=day
        ),
        encoding="utf-8",
    )
    return dest
