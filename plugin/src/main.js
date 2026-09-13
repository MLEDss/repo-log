import "@logseq/libs";
import "./style.css";

const DEFAULT_URL = "http://127.0.0.1:8765";

const DIALOGUE_TPL = `type:: 对话
date::
source:: Cursor
concept:: [[概念/]]
tags:: #对话

- 要点
	- 
- 可操作
	- 
- 证据
	- 仓库：
	- 案例：
- 待核实
	- `;

const CONCEPT_TPL = `type:: 概念
id::
tags:: #概念

- 一句话
	- 
- 易混
	- 
- 待核实
	- `;

function engineUrl() {
  const fromSettings = logseq.settings && logseq.settings.engineUrl;
  return String(fromSettings || DEFAULT_URL).replace(/\/$/, "");
}

async function api(method, path, body) {
  const opts = { method, headers: { "Content-Type": "application/json" } };
  if (body) opts.body = JSON.stringify(body);
  const res = await fetch(engineUrl() + path, opts);
  const data = await res.json();
  if (!res.ok && !data.message) data.message = res.statusText;
  return data;
}

function $(id) {
  return document.getElementById(id);
}

function render(data) {
  const ready = data.ready ? "ready" : "not initialized";
  $("graph").textContent = ready + "  " + (data.graph || "");
  const list = $("projects");
  list.innerHTML = "";
  (data.projects || []).forEach((item) => {
    const li = document.createElement("li");
    li.dataset.id = item.id;
    li.textContent = item.id + " [" + item.ide + "] " + item.root;
    li.onclick = () => {
      list.querySelectorAll("li").forEach((el) => (el.style.fontWeight = "normal"));
      li.style.fontWeight = "bold";
      list.dataset.selected = item.id;
    };
    list.appendChild(li);
  });
  $("log").textContent = data.message || JSON.stringify(data, null, 2);
}

async function refresh() {
  try {
    render(await api("GET", "/api/status"));
  } catch (err) {
    $("log").textContent =
      "Engine offline. In the Repo Log repo run: python -m repo_log serve\n" + err;
  }
}

async function run(fn) {
  try {
    const data = await fn();
    render(data);
    if (window.logseq && data && data.message) {
      logseq.UI.showMsg(data.ok ? data.message : data.message, data.ok ? "success" : "warning");
    }
  } catch (err) {
    $("log").textContent = String(err);
    if (window.logseq) logseq.UI.showMsg(String(err), "error");
  }
}

function bindUi() {
  $("btn-init").onclick = () => run(() => api("POST", "/api/init", {}));
  $("btn-catalog").onclick = () => run(() => api("POST", "/api/catalog", {}));
  $("btn-add").onclick = () =>
    run(() => api("POST", "/api/projects", { root: $("root").value.trim(), ide: $("ide").value }));
  $("btn-remove").onclick = () => {
    const id = $("projects").dataset.selected;
    if (!id) {
      $("log").textContent = "Select a project in the list first.";
      return;
    }
    run(() => api("DELETE", "/api/projects/" + encodeURIComponent(id)));
  };
  $("btn-cursor").onclick = () =>
    run(() =>
      api("POST", "/api/capture", {
        kind: "cursor",
        path: $("cap-path").value.trim(),
        title: $("cap-title").value.trim(),
        concept: $("cap-concept").value.trim(),
      })
    );
  $("btn-gpt").onclick = () =>
    run(() =>
      api("POST", "/api/capture", {
        kind: "chatgpt",
        path: $("cap-path").value.trim(),
        title: $("cap-title").value.trim(),
        concept: $("cap-concept").value.trim(),
      })
    );
  $("btn-use").onclick = () => logseq.App.pushState("page", { name: "使用" });
  $("btn-close").onclick = () => logseq.hideMainUI();
}

async function insertTemplate(text) {
  await logseq.Editor.insertAtEditingCursor(text);
}

function bootPlugin() {
  logseq.useSettingsSchema([
    {
      key: "engineUrl",
      type: "string",
      default: DEFAULT_URL,
      title: "Engine URL",
      description: "Local `python -m repo_log serve` address. Must stay on this machine.",
    },
  ]);
  logseq.provideModel({
    openPanel() {
      logseq.showMainUI({ autoFocus: true });
    },
  });
  logseq.App.registerUIItem("toolbar", {
    key: "repo-log",
    template:
      '<a data-on-click="openPanel" class="button" title="Repo Log" style="font-size:12px;font-weight:700;">RL</a>',
  });
  logseq.Editor.registerSlashCommand("Repo Log: open panel", () =>
    logseq.showMainUI({ autoFocus: true })
  );
  logseq.Editor.registerSlashCommand("Repo Log: initialize graph", () =>
    run(() => api("POST", "/api/init", {}))
  );
  logseq.Editor.registerSlashCommand("Repo Log: update catalog", () =>
    run(() => api("POST", "/api/catalog", {}))
  );
  logseq.Editor.registerSlashCommand("Repo Log: dialogue template", () =>
    insertTemplate(DIALOGUE_TPL)
  );
  logseq.Editor.registerSlashCommand("Repo Log: concept template", () =>
    insertTemplate(CONCEPT_TPL)
  );
  logseq.App.registerCommandPalette(
    { key: "repo-log-open", label: "Repo Log: open panel" },
    () => logseq.showMainUI({ autoFocus: true })
  );
}

bindUi();
refresh();
logseq.ready(bootPlugin).catch(console.error);
