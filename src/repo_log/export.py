from __future__ import annotations

import json
import shutil
from pathlib import Path

from repo_log.paths import assert_write_path
from repo_log.templates import default_inbox_dir, default_pages_dir


def export_markdown(
    source_dir: Path | str | None = None,
    dest_dir: Path | str | None = None,
    *,
    allow_external: bool = False,
) -> list[Path]:
    """Copy .md pages to a RAG inbox. Destination must stay in-repo unless allowed."""
    src = Path(source_dir or default_pages_dir())
    dest = assert_write_path(dest_dir or default_inbox_dir(), allow_external=allow_external)
    dest.mkdir(parents=True, exist_ok=True)
    written: list[Path] = []
    if not src.is_dir():
        return written
    for path in sorted(src.glob("*.md")):
        target = dest / path.name
        shutil.copy2(path, target)
        written.append(target)
    return written


def load_json(path: Path) -> object:
    return json.loads(Path(path).read_text(encoding="utf-8"))
