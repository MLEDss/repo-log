from __future__ import annotations

from pathlib import Path

from repo_log.settings import load_settings, resolve_notes_out

USAGE_PAGE = """\
type:: 使用
tags:: #使用

- 图路径：`{graph}`
- 这是什么
	- 你现在打开的这个文件夹就是笔记图。用 **Logseq OG** 翻双链。
	- 写页用本仓引擎，不要在本图里改工程计划（镜像只读）。
- 每天怎么用
	- **插件**：Logseq 工具栏 **RL**（或斜杠 Repo Log 打开面板）。先在本仓运行 `python -m repo_log serve`。
	- **翻**：在这张 OG 图里点 [[对接/Cursor]]、概念、对话。
	- **记对话**：插件「入库」，或在 Cursor 说「入库」。
	- **看工程计划**：插件「添加工程」一次，再「更新镜像」。改计划仍回那个仓库。
- 第一次（只做一遍）
	- 1. `D:\\Repo Log` 运行 `.\\repo-log.cmd`（启动引擎）。
	- 2. Logseq OG 打开本图；开发者模式 → Load unpacked plugin → `D:\\Repo Log\\plugin`。
	- 3. 点工具栏 RL → 初始化图 → 添加工程 → 更新镜像。
	- 4. 点 [[对接/Cursor]] 或 [[对接/ChatGPT]]。
- 常用命令（都在 `D:\\Repo Log` 下）
	- `.\\repo-log.cmd` — 启动本机引擎（插件要连它）
	- `.\\repo-log.ps1 app` — 备用桌面窗口
	- `.\\repo-log.ps1 status` — 打印图路径
- 不要
	- 不要用 Logseq 打开光学 / LED / DisplayCaliber 仓库当图根。
	- 不要在镜像页里改计划。
	- 不要对 Agent 使用 `--allow-external`。
"""


def usage_page_body(*, graph: Path) -> str:
    return USAGE_PAGE.format(graph=graph)


def format_status(*, settings_path: Path | None = None) -> str:
    data = load_settings(settings_path)
    graph = resolve_notes_out(data)
    ready = (graph / "logseq" / "config.edn").is_file()
    lines = [
        "Repo Log — 怎么用",
        "",
        f"图路径：{graph}",
        (
            "状态：已就绪。引擎：.\\repo-log.cmd ；Logseq 加载 plugin/ ，工具栏 RL。"
            if ready
            else "状态：图还没建。先 .\\repo-log.cmd，再在插件里点「初始化图」。"
        ),
        "插件里：添加工程、更新镜像、对话入库。",
        "",
        "登记的工程：",
    ]
    projects = list(data.get("projects") or [])
    if not projects:
        lines.append("  （无）在插件里点「添加工程」，或：")
        lines.append('  .\\repo-log.ps1 project add --root "D:\\Optics Simulation" --ide cursor')
        lines.append("  .\\repo-log.ps1 catalog")
    else:
        for item in projects:
            root = item.get("root")
            exists = Path(str(root)).is_dir() if root else False
            mark = "在" if exists else "路径不存在"
            lines.append(f"  - {item.get('id')}  ({item.get('ide')})  {root}  [{mark}]")
        lines.append("  更新镜像：.\\repo-log.ps1 catalog")
    lines.extend(
        [
            "",
            "对话入库：插件按钮，或在 Cursor 说「入库」。",
            "不要把工程仓当成 Logseq 图根打开。",
            "",
        ]
    )
    return "\n".join(lines)
