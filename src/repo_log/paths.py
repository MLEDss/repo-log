from __future__ import annotations

import os
from pathlib import Path

_ALLOW_ENV = "REPO_LOG_ALLOW_EXTERNAL"


def repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def assert_write_path(path: Path | str, *, allow_external: bool = False) -> Path:
    """Refuse writes outside this repository unless explicitly allowed."""
    resolved = Path(path).expanduser().resolve()
    root = repo_root()
    try:
        resolved.relative_to(root)
        return resolved
    except ValueError:
        env_on = os.environ.get(_ALLOW_ENV, "").strip() in {"1", "true", "TRUE", "yes"}
        if allow_external or env_on:
            return resolved
        raise ValueError(
            f"Refusing to write outside D:\\Repo Log: {resolved}"
        ) from None
