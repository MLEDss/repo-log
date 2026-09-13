from __future__ import annotations

from pathlib import Path

from repo_log.logseq_names import page_to_filename
from repo_log.paths import assert_write_path
from repo_log.registry import ProjectSpec, iter_project_docs, load_registry, load_registry_data
from repo_log.settings import load_settings, resolve_notes_out


def _is_relative_to(child: Path, parent: Path) -> bool:
    try:
        child.resolve().relative_to(parent.resolve())
        return True
    except ValueError:
        return False


def assert_notes_isolated(out_dir: Path | str, sources: list[Path], *, allow_external: bool = False) -> Path:
    dest = assert_write_path(out_dir, allow_external=allow_external).resolve()
    for raw in sources:
        root = Path(raw).resolve()
        if _is_relative_to(dest, root) or _is_relative_to(root, dest):
            raise ValueError(f"Refusing to mix notes output with project tree: {root}")
    return dest


def _page_title(project_id: str, rel: str) -> str:
    stem = rel[:-3] if rel.lower().endswith(".md") else rel
    return f"工程/{project_id}/{stem}"


def _write_page(pages_dir: Path, title: str, body: str) -> Path:
    dest = pages_dir / page_to_filename(title)
    dest.write_text(body, encoding="utf-8")
    return dest


def _mirror_body(spec: ProjectSpec, rel: str, source: Path, text: str) -> str:
    return "\n".join(
        [
            "type:: 工程镜像",
            f"ide:: {spec.ide}",
            f"project:: {spec.id}",
            f"source:: {source.resolve().as_posix()}",
            "readonly:: yes",
            "",
            f"- 真源：`{rel}`（在 {spec.ide} 项目里改）。本页只读镜像。",
            f"- 打开原文件：`{source.resolve()}`",
            "",
            text.rstrip(),
            "",
        ]
    )


def _index_body(ide: str, specs: list[ProjectSpec], titles: dict[str, list[str]]) -> str:
    lines = [
        f"type:: 对接索引",
        f"ide:: {ide}",
        "readonly:: yes",
        "",
        f"- {ide} 项目文档镜像。改计划回工程仓，不要在本页当真源。",
        "",
    ]
    for spec in specs:
        lines.append(f"- [[工程/{spec.id}]]  `{spec.root}`")
        for title in titles.get(spec.id, []):
            lines.append(f"\t- [[{title}]]")
        lines.append("")
    return "\n".join(lines)


def write_catalog(
    config_path: Path | str,
    out_dir: Path | str,
    *,
    allow_external: bool = False,
) -> list[Path]:
    return emit_catalog(
        load_registry(Path(config_path)),
        out_dir,
        allow_external=allow_external,
    )


def write_catalog_from_settings(
    settings_path: Path | str | None = None,
    out_dir: Path | str | None = None,
    *,
    allow_external: bool = False,
) -> list[Path]:
    data = load_settings(Path(settings_path) if settings_path else None)
    dest = out_dir if out_dir is not None else resolve_notes_out(data)
    return emit_catalog(
        load_registry_data(data),
        dest,
        allow_external=allow_external,
    )


def emit_catalog(
    specs: list[ProjectSpec],
    out_dir: Path | str,
    *,
    allow_external: bool = False,
) -> list[Path]:
    dest = assert_notes_isolated(
        out_dir, [s.root for s in specs], allow_external=allow_external
    )
    pages_dir = dest / "pages"
    pages_dir.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    titles: dict[str, list[str]] = {}
    for spec in specs:
        if not spec.root.resolve().is_dir():
            continue
        titles[spec.id] = []
        proj_title = f"工程/{spec.id}"
        doc_links: list[str] = []
        for doc in iter_project_docs(spec):
            rel = doc.resolve().relative_to(spec.root.resolve()).as_posix()
            title = _page_title(spec.id, rel)
            text = doc.read_text(encoding="utf-8")
            written.append(
                _write_page(pages_dir, title, _mirror_body(spec, rel, doc, text))
            )
            titles[spec.id].append(title)
            doc_links.append(f"- [[{title}]]")
        proj_body = "\n".join(
            [
                "type:: 工程项目",
                f"ide:: {spec.ide}",
                f"project:: {spec.id}",
                f"root:: {spec.root.resolve().as_posix()}",
                "readonly:: yes",
                "",
                f"- IDE：{spec.ide}",
                f"- 根目录：`{spec.root.resolve()}`",
                "",
                *doc_links,
                "",
            ]
        )
        written.append(_write_page(pages_dir, proj_title, proj_body))
        titles[spec.id].insert(0, proj_title)

    by_ide: dict[str, list[ProjectSpec]] = {"cursor": [], "chatgpt": []}
    for spec in specs:
        if spec.root.resolve().is_dir():
            by_ide.setdefault(spec.ide, []).append(spec)
    for ide, group in by_ide.items():
        if not group:
            continue
        hub = "对接/Cursor" if ide == "cursor" else "对接/ChatGPT"
        written.append(_write_page(pages_dir, hub, _index_body(ide, group, titles)))

    return written
