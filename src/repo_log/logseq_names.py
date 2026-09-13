from __future__ import annotations

import re

_INVALID = re.compile(r'[<>:"|?*]')


def page_to_filename(page_name: str) -> str:
    """Logseq OG default: slash in titles becomes a triple underscore on disk."""
    name = page_name.strip().strip("/")
    if not name:
        raise ValueError("page name is empty")
    name = name.replace("/", "___")
    name = _INVALID.sub("_", name)
    if not name.endswith(".md"):
        name = f"{name}.md"
    return name
