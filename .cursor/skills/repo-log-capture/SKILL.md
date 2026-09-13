---
name: repo-log-capture
description: Distills a Cursor or ChatGPT conversation into a Logseq OG 对话 page via python -m repo_log. Use when the user asks to 入库, capture a dialogue, write a 对话 page, or dump this chat into Repo Log.
---

# Repo Log capture

Write only inside `D:\Repo Log`. Never pass `--allow-external`. Never set `REPO_LOG_ALLOW_EXTERNAL`. Do not copy full transcripts, PDFs, or sibling-repo docs.

## Steps

1. Working directory: `D:\Repo Log`. Prefer `.\repo-log.ps1` (sets PYTHONPATH). Or `$env:PYTHONPATH = Join-Path (Get-Location) 'src'` then `python -m repo_log`.
2. If the graph is missing: `.\repo-log.ps1 init`
3. Distill 5–15 bullets (not the full log). Write a short jsonl under `out/scratch/` (role + text only).
4. `.\repo-log.ps1 capture --transcript out\scratch\<name>.jsonl --title <主题> --concept <概念名>`
5. ChatGPT official export: `.\repo-log.ps1 capture --chatgpt <conversations.json> --concept <概念名>`
6. After writing, tell the user to refresh Logseq on `out/notes` and open the `对话/` page.

Default pages live in `out/notes/pages` (open `out/notes` in Logseq OG).
