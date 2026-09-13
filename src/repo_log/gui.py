from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import filedialog, messagebox, simpledialog, ttk

from repo_log.actions import (
    ActionResult,
    add_project,
    capture_file,
    catalog_notes,
    drop_project,
    init_notes,
    launch_logseq,
    load_state,
    open_graph_folder,
)


def _ask(parent: tk.Misc, title: str, prompt: str, initial: str = "") -> str | None:
    value = simpledialog.askstring(title, prompt, parent=parent, initialvalue=initial)
    if value is None:
        return None
    return value.strip()


class RepoLogApp(tk.Tk):
    def __init__(self, settings_path: Path | None = None) -> None:
        super().__init__()
        self.settings_path = settings_path
        self.title("Repo Log")
        self.geometry("720x640")
        self.minsize(640, 560)
        self._build()
        self.refresh()

    def _build(self) -> None:
        pad = {"padx": 12, "pady": 6}
        root = ttk.Frame(self)
        root.pack(fill=tk.BOTH, expand=True)

        ttk.Label(root, text="Repo Log", font=("Microsoft YaHei UI", 16, "bold")).pack(
            anchor="w", **pad
        )
        ttk.Label(
            root,
            text="按钮和设置在这里。翻双链用 Logseq OG 打开下面的图。",
        ).pack(anchor="w", padx=12)

        graph = ttk.LabelFrame(root, text="图")
        graph.pack(fill=tk.X, padx=12, pady=8)
        self.graph_var = tk.StringVar()
        ttk.Label(graph, textvariable=self.graph_var, wraplength=660).pack(
            anchor="w", padx=8, pady=4
        )
        row = ttk.Frame(graph)
        row.pack(fill=tk.X, padx=8, pady=4)
        ttk.Button(row, text="初始化图", command=self.on_init).pack(side=tk.LEFT, padx=2)
        ttk.Button(row, text="打开图文件夹", command=self.on_open_folder).pack(side=tk.LEFT, padx=2)
        ttk.Button(row, text="启动 Logseq", command=self.on_logseq).pack(side=tk.LEFT, padx=2)

        projects = ttk.LabelFrame(root, text="工程（设置）")
        projects.pack(fill=tk.BOTH, expand=True, padx=12, pady=4)
        self.listbox = tk.Listbox(projects, height=6)
        self.listbox.pack(fill=tk.BOTH, expand=True, padx=8, pady=4)
        prow = ttk.Frame(projects)
        prow.pack(fill=tk.X, padx=8, pady=4)
        ttk.Label(prow, text="IDE").pack(side=tk.LEFT)
        self.ide_var = tk.StringVar(value="cursor")
        ttk.Combobox(
            prow,
            textvariable=self.ide_var,
            values=("cursor", "chatgpt"),
            width=10,
            state="readonly",
        ).pack(side=tk.LEFT, padx=6)
        ttk.Button(prow, text="添加工程…", command=self.on_add).pack(side=tk.LEFT, padx=2)
        ttk.Button(prow, text="移除所选", command=self.on_remove).pack(side=tk.LEFT, padx=2)
        ttk.Button(prow, text="更新镜像", command=self.on_catalog).pack(side=tk.LEFT, padx=2)

        cap = ttk.LabelFrame(root, text="对话入库")
        cap.pack(fill=tk.X, padx=12, pady=4)
        crow = ttk.Frame(cap)
        crow.pack(fill=tk.X, padx=8, pady=6)
        ttk.Button(crow, text="入库 Cursor jsonl…", command=self.on_capture_cursor).pack(
            side=tk.LEFT, padx=2
        )
        ttk.Button(crow, text="入库 ChatGPT 导出…", command=self.on_capture_gpt).pack(
            side=tk.LEFT, padx=2
        )

        log = ttk.LabelFrame(root, text="状态")
        log.pack(fill=tk.BOTH, expand=True, padx=12, pady=8)
        self.log = tk.Text(log, height=8, wrap=tk.WORD)
        self.log.pack(fill=tk.BOTH, expand=True, padx=8, pady=6)

    def state(self) -> dict:
        return load_state(self.settings_path)

    def refresh(self) -> None:
        st = self.state()
        flag = "已就绪" if st["ready"] else "未初始化"
        self.graph_var.set(f"{flag}  {st['graph']}")
        self.listbox.delete(0, tk.END)
        for item in st["projects"]:
            self.listbox.insert(tk.END, f"{item.get('id')}  [{item.get('ide')}]  {item.get('root')}")

    def show(self, result: ActionResult) -> None:
        self.log.delete("1.0", tk.END)
        self.log.insert(tk.END, result.message)
        if not result.ok:
            messagebox.showerror("Repo Log", result.message)
        self.refresh()

    def on_init(self) -> None:
        self.show(init_notes(self.settings_path))

    def on_open_folder(self) -> None:
        self.show(open_graph_folder(self.settings_path))

    def on_logseq(self) -> None:
        self.show(launch_logseq(self.settings_path))

    def on_add(self) -> None:
        folder = filedialog.askdirectory(title="选择工程仓库根目录")
        if not folder:
            return
        self.show(add_project(folder, ide=self.ide_var.get(), settings_path=self.settings_path))

    def on_remove(self) -> None:
        st = self.state()
        idx = self.listbox.curselection()
        if not idx:
            self.show(ActionResult(False, "先在列表里选一个工程。"))
            return
        pid = str(st["projects"][idx[0]].get("id") or "")
        self.show(drop_project(pid, settings_path=self.settings_path))

    def on_catalog(self) -> None:
        self.show(catalog_notes(self.settings_path))

    def _capture(self, kind: str, filetypes: list[tuple[str, str]]) -> None:
        path = filedialog.askopenfilename(title="选择对话文件", filetypes=filetypes)
        if not path:
            return
        title = _ask(self, "入库", "标题（可空）")
        if title is None:
            return
        concept = _ask(self, "入库", "概念名（可空）")
        if concept is None:
            return
        self.show(
            capture_file(
                path,
                kind=kind,
                title=title,
                concept=concept,
                settings_path=self.settings_path,
            )
        )

    def on_capture_cursor(self) -> None:
        self._capture("cursor", [("JSONL", "*.jsonl"), ("全部", "*.*")])

    def on_capture_gpt(self) -> None:
        self._capture("chatgpt", [("JSON", "*.json"), ("全部", "*.*")])


def run_app(settings_path: Path | None = None) -> None:
    app = RepoLogApp(settings_path=settings_path)
    app.mainloop()
