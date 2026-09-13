from __future__ import annotations

from pathlib import Path

from repo_log.paths import repo_root


def templates_dir() -> Path:
    return repo_root() / "templates"


def default_graph_dir() -> Path:
    from repo_log.settings import load_settings, resolve_notes_out

    return resolve_notes_out(load_settings())


def default_pages_dir() -> Path:
    return default_graph_dir() / "pages"


def default_inbox_dir() -> Path:
    return repo_root() / "out" / "rag-inbox"


def load_template(stem: str) -> str:
    path = templates_dir() / f"{stem}.md"
    if not path.is_file():
        raise FileNotFoundError(f"missing template: {path}")
    return path.read_text(encoding="utf-8")
