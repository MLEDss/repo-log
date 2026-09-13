from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from repo_log.capture import distill_chatgpt_export, distill_transcript, write_dialogue_page
from repo_log.catalog import write_catalog, write_catalog_from_settings
from repo_log.export import export_markdown
from repo_log.logseq_names import page_to_filename
from repo_log.graph import init_graph
from repo_log.pages import write_case_page, write_concept_page, write_literature_page
from repo_log.settings import (
    load_settings,
    remove_project,
    resolve_notes_out,
    save_settings,
    upsert_project,
)
from repo_log.usage import format_status


def _add_out(p: argparse.ArgumentParser, required: bool = True) -> None:
    p.add_argument("--out-dir", type=Path, required=required)
    p.add_argument(
        "--allow-external",
        action="store_true",
        help="User-only: write outside this repo. Agent must never pass this.",
    )


def _add_settings(p: argparse.ArgumentParser) -> None:
    p.add_argument("--settings", type=Path)


def _pages_dir(args: argparse.Namespace) -> Path:
    if args.out_dir is not None:
        return args.out_dir
    settings = getattr(args, "settings", None)
    return resolve_notes_out(load_settings(settings)) / "pages"


def main(argv: list[str] | None = None) -> int:
    args_list = sys.argv[1:] if argv is None else argv
    if not args_list:
        from repo_log.server import serve as serve_engine

        serve_engine()
        return 0
    parser = argparse.ArgumentParser(
        prog="repo_log",
        description="以 Logseq OG 为底座的笔记引擎。无参数时启动本机引擎（供插件调用）。",
    )
    sub = parser.add_subparsers(dest="cmd", required=False)

    p_name = sub.add_parser("page-name", help="Logseq OG filename for a page title")
    p_name.add_argument("title")

    p_init = sub.add_parser("init", help="Create a Logseq OG graph folder")
    p_init.add_argument("--out-dir", type=Path)
    p_init.add_argument("--settings", type=Path)
    p_init.add_argument("--allow-external", action="store_true")

    p_status = sub.add_parser("status", help="Print graph path and how to use it")
    p_status.add_argument("--settings", type=Path)

    p_app = sub.add_parser("app", help="Open the desktop console")
    p_app.add_argument("--settings", type=Path)

    p_serve = sub.add_parser("serve", help="Localhost HTTP for the Logseq plugin")
    p_serve.add_argument("--host", default="127.0.0.1")
    p_serve.add_argument("--port", type=int, default=8765)
    p_serve.add_argument("--settings", type=Path)

    p_cap = sub.add_parser("capture", help="Distill Cursor jsonl or ChatGPT export")
    p_cap.add_argument("--transcript", type=Path)
    p_cap.add_argument("--chatgpt", type=Path)
    p_cap.add_argument("--title", default="")
    p_cap.add_argument("--source", default="Cursor")
    p_cap.add_argument("--concept", default="")
    _add_out(p_cap, required=False)
    _add_settings(p_cap)

    p_cat = sub.add_parser("catalog", help="Mirror registered projects into Logseq pages/")
    p_cat.add_argument("--config", type=Path, help="Legacy registry JSON")
    p_cat.add_argument("--settings", type=Path, help="Settings JSON (default out/settings.json)")
    _add_out(p_cat, required=False)

    p_proj = sub.add_parser("project", help="Add/remove/list projects in tool settings")
    p_sub = p_proj.add_subparsers(dest="project_cmd", required=True)
    p_add = p_sub.add_parser("add", help="Register or update a project (anytime)")
    p_add.add_argument("--root", required=True)
    p_add.add_argument("--ide", default="cursor", choices=["cursor", "chatgpt"])
    p_add.add_argument("--id", dest="project_id", default="")
    p_add.add_argument("--settings", type=Path)
    p_add.add_argument("--allow-external", action="store_true")
    p_rm = p_sub.add_parser("remove", help="Unregister a project by id")
    p_rm.add_argument("--id", dest="project_id", required=True)
    p_rm.add_argument("--settings", type=Path)
    p_rm.add_argument("--allow-external", action="store_true")
    p_ls = p_sub.add_parser("list", help="Show registered projects")
    p_ls.add_argument("--settings", type=Path)

    p_concept = sub.add_parser("concept", help="Write a 概念 page")
    p_concept.add_argument("--name", required=True)
    p_concept.add_argument("--summary", default="")
    p_concept.add_argument("--mixup", default="")
    p_concept.add_argument("--lumerical", default="")
    p_concept.add_argument("--lighttools", default="")
    p_concept.add_argument("--zemax", default="")
    p_concept.add_argument("--formula", default="")
    p_concept.add_argument("--case", action="append", default=[])
    _add_out(p_concept, required=False)
    _add_settings(p_concept)

    p_lit = sub.add_parser("literature", help="Write a 文献 page")
    p_lit.add_argument("--citekey", required=True)
    p_lit.add_argument("--concept", default="")
    p_lit.add_argument("--summary", default="")
    p_lit.add_argument("--highlight", action="append", default=[])
    p_lit.add_argument("--zotero", default="")
    _add_out(p_lit, required=False)
    _add_settings(p_lit)

    p_case = sub.add_parser("case", help="Write a short 案例 pointer page")
    p_case.add_argument("--id", required=True)
    p_case.add_argument("--source", default="")
    p_case.add_argument("--software", default="")
    p_case.add_argument("--concept", default="")
    p_case.add_argument("--summary", default="")
    p_case.add_argument("--mixup", default="")
    p_case.add_argument("--insight", default="")
    _add_out(p_case, required=False)
    _add_settings(p_case)

    p_ex = sub.add_parser("export-inbox", help="Copy md pages to a RAG inbox folder")
    p_ex.add_argument("--from-dir", type=Path, required=True)
    _add_out(p_ex)

    args = parser.parse_args(args_list)
    if args.cmd == "serve":
        from repo_log.server import serve as serve_engine

        serve_engine(host=args.host, port=args.port, settings_path=args.settings)
        return 0
    if args.cmd == "app":
        from repo_log.gui import run_app

        run_app(getattr(args, "settings", None))
        return 0
    if args.cmd in (None, "status"):
        sys.stdout.write(format_status(settings_path=getattr(args, "settings", None)))
        return 0
    if args.cmd == "page-name":
        sys.stdout.write(page_to_filename(args.title) + "\n")
        return 0
    if args.cmd == "init":
        data = load_settings(args.settings)
        dest = args.out_dir or resolve_notes_out(data)
        if args.out_dir is not None:
            data["notes_out"] = str(Path(args.out_dir))
        save_settings(data, args.settings, allow_external=args.allow_external)
        path = init_graph(dest, allow_external=args.allow_external)
        sys.stdout.write(
            f"已建图，下一步用 Logseq OG 打开这个文件夹：\n{path}\n"
            "打开后点侧栏 Contents → 使用。看命令：.\\repo-log.ps1\n"
        )
        return 0
    if args.cmd == "project":
        settings = args.settings
        if args.project_cmd == "list":
            data = load_settings(settings)
            sys.stdout.write(json.dumps(data.get("projects") or [], ensure_ascii=False, indent=2) + "\n")
            return 0
        if args.project_cmd == "remove":
            ok = remove_project(
                args.project_id, settings_path=settings, allow_external=args.allow_external
            )
            sys.stdout.write(("removed\n" if ok else "missing\n"))
            return 0
        entry = upsert_project(
            root=args.root,
            ide=args.ide,
            project_id=args.project_id or None,
            settings_path=settings,
            allow_external=args.allow_external,
        )
        sys.stdout.write(json.dumps(entry, ensure_ascii=False) + "\n")
        return 0
    if args.cmd == "catalog":
        if args.config:
            if args.out_dir is None:
                parser.error("catalog --config requires --out-dir")
            paths = write_catalog(
                args.config, args.out_dir, allow_external=args.allow_external
            )
        else:
            paths = write_catalog_from_settings(
                args.settings,
                args.out_dir,
                allow_external=args.allow_external,
            )
        sys.stdout.write(f"{len(paths)} pages\n去 Logseq 打开 [[对接/Cursor]] 或 [[对接/ChatGPT]]。\n")
        return 0
    if args.cmd == "concept":
        path = write_concept_page(
            args.name,
            summary=args.summary,
            mixup=args.mixup,
            lumerical=args.lumerical,
            lighttools=args.lighttools,
            zemax=args.zemax,
            formula=args.formula,
            cases=args.case,
            out_dir=_pages_dir(args),
            allow_external=args.allow_external,
        )
        sys.stdout.write(str(path) + "\n")
        return 0
    if args.cmd == "literature":
        path = write_literature_page(
            args.citekey,
            concept=args.concept,
            summary=args.summary,
            highlights=args.highlight,
            zotero=args.zotero,
            out_dir=_pages_dir(args),
            allow_external=args.allow_external,
        )
        sys.stdout.write(str(path) + "\n")
        return 0
    if args.cmd == "case":
        path = write_case_page(
            args.id,
            source=args.source,
            software=args.software,
            concept=args.concept,
            summary=args.summary,
            mixup=args.mixup,
            insight=args.insight,
            out_dir=_pages_dir(args),
            allow_external=args.allow_external,
        )
        sys.stdout.write(str(path) + "\n")
        return 0
    if args.cmd == "export-inbox":
        written = export_markdown(
            args.from_dir, args.out_dir, allow_external=args.allow_external
        )
        sys.stdout.write(f"{len(written)} files\n")
        return 0
    if args.chatgpt:
        title, bullets = distill_chatgpt_export(args.chatgpt)
        if args.title:
            title = args.title
        source = "ChatGPT"
    elif args.transcript:
        bullets = distill_transcript(args.transcript)
        title = args.title or "untitled"
        source = args.source
    else:
        parser.error("capture requires --transcript or --chatgpt")
    path = write_dialogue_page(
        _pages_dir(args),
        title=title,
        source=source,
        concept=args.concept,
        bullets=bullets,
        allow_external=args.allow_external,
    )
    sys.stdout.write(str(path) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
