from __future__ import annotations

import os
import subprocess
from dataclasses import dataclass
from pathlib import Path

from repo_log.capture import distill_chatgpt_export, distill_transcript, write_dialogue_page
from repo_log.catalog import write_catalog_from_settings
from repo_log.graph import init_graph
from repo_log.settings import (
    load_settings,
    remove_project,
    resolve_notes_out,
    save_settings,
    upsert_project,
)
from repo_log.templates import default_pages_dir


@dataclass(frozen=True)
class ActionResult:
    ok: bool
    message: str


def load_state(settings_path: Path | None = None) -> dict:
    data = load_settings(settings_path)
    graph = resolve_notes_out(data)
    return {
        "data": data,
        "graph": graph,
        "ready": (graph / "logseq" / "config.edn").is_file(),
        "projects": list(data.get("projects") or []),
        "settings_path": Path(settings_path) if settings_path else None,
    }


def pages_dir(settings_path: Path | None = None) -> Path:
    if settings_path is None:
        return default_pages_dir()
    return resolve_notes_out(load_settings(settings_path)) / "pages"


def init_notes(settings_path: Path | None = None) -> ActionResult:
    data = load_settings(settings_path)
    dest = resolve_notes_out(data)
    save_settings(data, settings_path)
    path = init_graph(dest)
    return ActionResult(True, f"已建图：{path}\n用「打开图文件夹」或 Logseq Add a graph 打开它。")


def add_project(
    root: Path | str,
    *,
    ide: str = "cursor",
    project_id: str | None = None,
    settings_path: Path | None = None,
) -> ActionResult:
    folder = Path(root)
    if not folder.is_dir():
        return ActionResult(False, f"文件夹不存在：{folder}")
    entry = upsert_project(
        root=folder, ide=ide, project_id=project_id, settings_path=settings_path
    )
    return ActionResult(True, f"已登记 {entry['id']}（{entry['ide']}）\n{entry['root']}\n再点「更新镜像」。")


def drop_project(project_id: str, *, settings_path: Path | None = None) -> ActionResult:
    ok = remove_project(project_id, settings_path=settings_path)
    if not ok:
        return ActionResult(False, f"没有这个工程：{project_id}")
    return ActionResult(True, f"已移除 {project_id}")


def catalog_notes(settings_path: Path | None = None) -> ActionResult:
    state = load_state(settings_path)
    if not state["projects"]:
        return ActionResult(False, "还没有工程。先「添加工程」，再更新镜像。")
    if not state["ready"]:
        init_notes(settings_path)
    paths = write_catalog_from_settings(settings_path)
    return ActionResult(
        True,
        f"已写入 {len(paths)} 页。到 Logseq 打开 [[对接/Cursor]] 或 [[对接/ChatGPT]]。",
    )


def capture_file(
    path: Path | str,
    *,
    kind: str,
    title: str = "",
    concept: str = "",
    settings_path: Path | None = None,
) -> ActionResult:
    src = Path(path)
    if not src.is_file():
        return ActionResult(False, f"找不到文件：{src}")
    if kind == "chatgpt":
        found_title, bullets = distill_chatgpt_export(src)
        page_title = title.strip() or found_title
        source = "ChatGPT"
    elif kind == "cursor":
        bullets = distill_transcript(src)
        page_title = title.strip() or src.stem
        source = "Cursor"
    else:
        return ActionResult(False, "入库类型只能是 cursor 或 chatgpt")
    dest = write_dialogue_page(
        pages_dir(settings_path),
        title=page_title,
        source=source,
        concept=concept.strip() or page_title,
        bullets=bullets,
    )
    return ActionResult(True, f"已写入对话页：\n{dest}\n到 Logseq 打开该页。")


def open_graph_folder(settings_path: Path | None = None) -> ActionResult:
    graph = load_state(settings_path)["graph"]
    if not graph.is_dir():
        return ActionResult(False, "图还没有。先点「初始化图」。")
    os.startfile(graph)  # noqa: S606 — Windows explorer on the in-repo graph
    return ActionResult(True, f"已打开文件夹：{graph}\nLogseq 用 Add a graph 选这个文件夹。")


def logseq_exe() -> Path | None:
    base = Path(os.environ.get("LOCALAPPDATA") or "")
    home = Path.home()
    candidates = [
        base / "Logseq" / "Logseq.exe",
        base / "Programs" / "Logseq" / "Logseq.exe",
        home / "AppData" / "Local" / "Logseq" / "Logseq.exe",
        Path(os.environ.get("ProgramFiles") or r"C:\Program Files") / "Logseq" / "Logseq.exe",
    ]
    for item in candidates:
        if item.is_file():
            return item
    return None


def launch_logseq(settings_path: Path | None = None) -> ActionResult:
    graph = load_state(settings_path)["graph"]
    exe = logseq_exe()
    if exe is None:
        return ActionResult(
            False,
            f"没找到 Logseq。请先安装 Logseq OG，然后 Add a graph 打开：\n{graph}",
        )
    subprocess.Popen([str(exe)], close_fds=True)
    return ActionResult(True, f"已启动 Logseq。图路径：\n{graph}\n若列表里没有，用 Add a graph 选这个文件夹。")
