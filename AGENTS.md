# Repo Log — Agent Guidance

## Project goal

Sidecar **engine** for Logseq OG file graphs (the product). The desktop
console, Cursor/ChatGPT skills, and a Logseq plugin are *adapters* that
call this engine. Do **not** fork Logseq. Do **not** treat a skill, a
plugin, or the console as a second write path. User-facing text is
Chinese; identifiers and code comments are English.

This repo **builds the sidecar tool**. It does not analyze, OCR, or ingest
sibling-project PDFs. Agent conventions (handover + plan + isolation rules)
are adapted from `D:\Optics Simulation`, `D:\LED Tools`,
`D:\LED Tools-chatgpt`, and `D:\DisplayCaliber`; conflict → ask the user.
Those trees are **read-only references**. Never use their `.venv`, source,
or runtime paths.

## Read first

1. `docs/交接文档.md` — what exists and current contracts.
2. `docs/计划.md` — active plan and phase gates.
3. `docs/方案.md` — product intent (layers, RAG, license).
4. `docs/contracts/project-bridge.md` — Cursor/ChatGPT docs in notes.
5. `.cursor/rules/runtime-isolation.mdc`, `.cursor/rules/secrecy.mdc`,
   `.cursor/rules/architecture.mdc`.

## Authority and conflict resolution

`AGENTS.md`, `docs/交接文档.md`, `docs/计划.md`, tests, and
`.cursor/rules/*.mdc` must stay consistent; no source silently overrides
another. If any two conflict, stop and ask which is authoritative.
Ambiguous paths or licenses → ask; the user is final.

## Hard runtime isolation (non-negotiable)

Repository root `D:\Repo Log` is the **complete** create / edit / install /
run boundary.

- Create, edit, install, and run **only** inside this repository.
- Do not write to `D:\Optics Simulation`, `D:\DisplayCaliber`, `D:\LED Tools`,
  `D:\LED Tools-chatgpt`, `D:\Knowledge`, Zotero, Logseq app data, Docker
  volumes, or any other disk path.
- Sibling projects may be **read** only when aligning conventions the user
  asked for. Do not copy their secrets, PDFs, or notes into this repo.
- Python: when third-party deps exist, only `.venv` at the repo root
  (`.\.venv\Scripts\python.exe -m pip install …`). Never `pip install --user`,
  never global site-packages, never another project’s `.venv`.
- Until a root `.venv` is required, stdlib + `python -m unittest` from
  `src/` on `PYTHONPATH` is the default.
- Tests write only under `tests/` (typically `tmp_path` / `tests/.tmp`).
  Never pass `--allow-external`. Never set `REPO_LOG_ALLOW_EXTERNAL`.
- Default engine graph is **`out/notes` inside this repo** (`python -m
  repo_log init`). User-owned graphs (`D:\Knowledge`) and RAG inboxes stay
  outside; the agent does not create them. The user may run the CLI with
  `--allow-external` on their machine; the agent must not.

```powershell
$env:PYTHONPATH = Join-Path (Get-Location) 'src'
python -m unittest discover -s tests -q
python -m repo_log init
python -m repo_log page-name "概念/文件光源"
```

## Hard secrecy rules (non-negotiable)

**Forbidden** — proprietary manuals, customer sizes, BOE 内训 originals,
full Cursor/ChatGPT transcripts, and RAG/Docker volumes must never be:

- committed to git
- copied into `templates/`, `tests/fixtures/`, or `docs/`
- `@`-attached in bulk into chat
- included in CI artifacts

Operational rules:

- This workspace implements capture/templates/CLI. Do not run PDF
  chapter-mining or LightTools-manual workflows here.
- Fixtures are **synthetic** (short fake jsonl / markdown).
- Distilled dialogue pages: 5–15 bullets, not full logs.
- Do not copy sibling `docs/video-notes/` or `参考文件/` into this tree;
  the tool may *link* IDs (`案例/<id>`, `文献/<citekey>`) later.

## Scope and decisions

- Small isolated fixes and their tests may proceed directly.
- Before changing page-ID contracts, default graph paths, or RAG dataset
  names, update `docs/计划.md` and wait if the user must choose.
- Do not add npm/Clojure/Logseq-core as a dependency of the Python engine.
  The Logseq plugin lives in `plugin/` and may use `@logseq/libs` there only.
- Do not add PDF-ingest / OCR / embedding pipelines unless the user
  explicitly asks for that product feature.

## Change and verification workflow

1. Read the plan and existing tests.
2. Smallest in-repo change.
3. Add focused tests (normal, boundary, refuse-outside-repo).
4. Run unittest from the repo root.
5. Record the change in `docs/交接文档.md` 「分支改动记录」.
6. Preserve unrelated dirty worktree files.

### Definition of done

- Focused tests added and passing.
- Isolation and secrecy rules not violated.
- Change logged in `docs/交接文档.md`.
- **No files created outside this repository.**

## Git

- Do not commit unless the user asks.
- Commit messages: concise imperative English.
- Before every commit, confirm staged paths contain no transcripts, PDFs,
  `.env`, or copies of sibling-project secrets.
