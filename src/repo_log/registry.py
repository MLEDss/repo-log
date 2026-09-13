from __future__ import annotations

import json
from dataclasses import dataclass, field
from fnmatch import fnmatch
from pathlib import Path

DEFAULT_INCLUDE = ["AGENTS.md", "docs/*.md"]
DEFAULT_EXCLUDE = ["**/参考文件/**", "**/*.pdf", "**/*.mp4", "**/.venv/**"]
DEFAULT_MAX_BYTES = 262144


@dataclass(frozen=True)
class ProjectSpec:
    id: str
    ide: str
    root: Path
    include: tuple[str, ...] = field(default_factory=lambda: tuple(DEFAULT_INCLUDE))
    exclude: tuple[str, ...] = field(default_factory=lambda: tuple(DEFAULT_EXCLUDE))
    max_bytes: int = DEFAULT_MAX_BYTES


def load_registry_data(data: dict) -> list[ProjectSpec]:
    include = tuple(data.get("include") or DEFAULT_INCLUDE)
    exclude = tuple(data.get("exclude") or DEFAULT_EXCLUDE)
    max_bytes = int(data.get("max_bytes") or DEFAULT_MAX_BYTES)
    projects = []
    for item in data.get("projects") or []:
        ide = str(item["ide"]).strip().lower()
        if ide not in {"cursor", "chatgpt"}:
            raise ValueError(f"ide must be cursor or chatgpt, got {ide!r}")
        projects.append(
            ProjectSpec(
                id=str(item["id"]).strip(),
                ide=ide,
                root=Path(item["root"]),
                include=tuple(item.get("include") or include),
                exclude=tuple(item.get("exclude") or exclude),
                max_bytes=int(item.get("max_bytes") or max_bytes),
            )
        )
    return projects


def load_registry(path: Path) -> list[ProjectSpec]:
    return load_registry_data(json.loads(Path(path).read_text(encoding="utf-8")))


def _rel_posix(root: Path, path: Path) -> str:
    return path.resolve().relative_to(root.resolve()).as_posix()


def iter_project_docs(spec: ProjectSpec) -> list[Path]:
    root = spec.root.resolve()
    if not root.is_dir():
        return []
    found: dict[Path, Path] = {}
    for pattern in spec.include:
        for match in root.glob(pattern):
            if match.is_file():
                found[match.resolve()] = match
    docs: list[Path] = []
    for path in sorted(found.values(), key=lambda p: _rel_posix(root, p).lower()):
        rel = _rel_posix(root, path)
        if any(fnmatch(rel, pat) or fnmatch(path.name, pat) for pat in spec.exclude):
            continue
        if path.stat().st_size > spec.max_bytes:
            continue
        docs.append(path)
    return docs
