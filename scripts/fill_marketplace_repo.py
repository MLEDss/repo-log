"""Fill GitHub slug into marketplace listing files. In-repo only."""

from __future__ import annotations

import json
import sys
from pathlib import Path


def repo_root() -> Path:
    return Path(__file__).resolve().parents[1]


def fill(repo_slug: str) -> Path:
    if "/" not in repo_slug or repo_slug.startswith("REPLACE_"):
        raise ValueError("repo slug must be user/repo")
    root = repo_root()
    man = root / "docs" / "marketplace" / "packages" / "logseq-plugin-repo-log" / "manifest.json"
    data = json.loads(man.read_text(encoding="utf-8"))
    data["repo"] = repo_slug
    man.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    pkg = root / "plugin" / "package.json"
    pdata = json.loads(pkg.read_text(encoding="utf-8"))
    pdata["repository"] = {"type": "git", "url": f"https://github.com/{repo_slug}.git"}
    pkg.write_text(json.dumps(pdata, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    pr = root / "docs" / "marketplace" / "PR.md"
    pr.write_text(
        pr.read_text(encoding="utf-8").replace("REPLACE_WITH_GITHUB_USER/repo-log", repo_slug),
        encoding="utf-8",
    )
    return man


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("usage: python scripts/fill_marketplace_repo.py USER/REPO", file=sys.stderr)
        return 2
    print(fill(argv[1]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
