# Submit Repo Log to the Logseq marketplace

Official process: https://github.com/logseq/marketplace

Live catalog checked 2026-09-13 (`plugins.json` on `logseq/marketplace`): **no** package titled Repo Log, id `logseq-plugin-repo-log`, or repo `*/repo-log`. Nearby but different products:

- `logseq-chatgpt-plugin` — ChatGPT inside Logseq, not a sidecar capture/catalog engine
- `logseq-quick-capture` — journal / page quick capture, not Cursor jsonl or project catalog

## Status

- Plugin GitHub repo (public): https://github.com/MLEDss/repo-log
- Release zip: https://github.com/MLEDss/repo-log/releases/tag/v0.1.0
- Marketplace PR (open, mergeable): https://github.com/logseq/marketplace/pull/900

Search → Install in Logseq Marketplace works only after that PR is merged.

## Marketplace checklist (reviewer file)

Reviewers compare against [journals-calendar `publish.yml`](https://github.com/xyhp915/logseq-journals-calendar/blob/main/.github/workflows/publish.yml). This repo has `.github/workflows/publish.yml`. Tag builds attach:

- `logseq-plugin-repo-log-<tag>.zip`
- `package.json`

`@logseq/libs` on npm is **0.0.17** (latest as of 2026-09-13).
