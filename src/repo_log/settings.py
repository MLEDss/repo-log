from __future__ import annotations

import json
import re
from pathlib import Path

from repo_log.paths import assert_write_path, repo_root
from repo_log.registry import (
    DEFAULT_EXCLUDE,
    DEFAULT_INCLUDE,
    DEFAULT_MAX_BYTES,
    ProjectSpec,
    load_registry_data,
)

def default_settings_path() -> Path:
    return repo_root() / "out" / "settings.json"


def example_settings_path() -> Path:
    return repo_root() / "config" / "settings.example.json"


def slug_id(name: str) -> str:
    text = re.sub(r"[^a-z0-9]+", "-", name.strip().lower())
    return text.strip("-") or "project"


def empty_settings() -> dict:
    return {
        "notes_out": "out/notes",
        "include": list(DEFAULT_INCLUDE),
        "exclude": list(DEFAULT_EXCLUDE),
        "max_bytes": DEFAULT_MAX_BYTES,
        "mirror": "full",
        "projects": [],
    }


def load_settings(path: Path | None = None) -> dict:
    target = Path(path) if path else default_settings_path()
    if not target.is_file():
        data = empty_settings()
        if example_settings_path().is_file() and target == default_settings_path():
            example = json.loads(example_settings_path().read_text(encoding="utf-8"))
            for key in ("include", "exclude", "max_bytes", "mirror", "notes_out"):
                if key in example:
                    data[key] = example[key]
        return data
    data = json.loads(target.read_text(encoding="utf-8"))
    base = empty_settings()
    base.update({k: v for k, v in data.items() if v is not None})
    base["projects"] = list(data.get("projects") or [])
    return base


def save_settings(data: dict, path: Path | None = None, *, allow_external: bool = False) -> Path:
    target = assert_write_path(path or default_settings_path(), allow_external=allow_external)
    target.parent.mkdir(parents=True, exist_ok=True)
    payload = empty_settings()
    payload.update(data)
    payload["projects"] = list(data.get("projects") or [])
    target.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return target


def resolve_notes_out(data: dict) -> Path:
    raw = Path(str(data.get("notes_out") or "out/notes"))
    if raw.is_absolute():
        return raw
    return repo_root() / raw


def specs_from_settings(data: dict) -> list[ProjectSpec]:
    return load_registry_data(data)


def upsert_project(
    *,
    root: Path | str,
    ide: str = "cursor",
    project_id: str | None = None,
    settings_path: Path | None = None,
    allow_external: bool = False,
) -> dict:
    ide = ide.strip().lower()
    if ide not in {"cursor", "chatgpt"}:
        raise ValueError("ide must be cursor or chatgpt")
    folder = Path(root)
    pid = (project_id or slug_id(folder.name)).strip()
    if not pid:
        raise ValueError("project id is empty")
    data = load_settings(settings_path)
    entry = {"id": pid, "ide": ide, "root": str(folder)}
    projects = []
    replaced = False
    for item in data.get("projects") or []:
        same_id = str(item.get("id")) == pid
        same_root = Path(str(item.get("root"))) == folder
        if same_id or same_root:
            if not replaced:
                projects.append(entry)
                replaced = True
            continue
        projects.append(item)
    if not replaced:
        projects.append(entry)
    data["projects"] = projects
    save_settings(data, settings_path, allow_external=allow_external)
    return entry


def remove_project(
    project_id: str,
    *,
    settings_path: Path | None = None,
    allow_external: bool = False,
) -> bool:
    data = load_settings(settings_path)
    before = list(data.get("projects") or [])
    data["projects"] = [p for p in before if str(p.get("id")) != project_id]
    save_settings(data, settings_path, allow_external=allow_external)
    return len(data["projects"]) < len(before)
