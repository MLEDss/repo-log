# Submit Repo Log to the Logseq marketplace

Official process: https://github.com/logseq/marketplace

Live catalog checked 2026-09-13 (`plugins.json` on `logseq/marketplace`): **no** package titled Repo Log, id `logseq-plugin-repo-log`, or repo `*/repo-log`. Nearby but different products:

- `logseq-chatgpt-plugin` — ChatGPT inside Logseq, not a sidecar capture/catalog engine
- `logseq-quick-capture` — journal / page quick capture, not Cursor jsonl or project catalog

## Marketplace checklist (reviewer file)

Reviewers compare against [journals-calendar `publish.yml`](https://github.com/xyhp915/logseq-journals-calendar/blob/main/.github/workflows/publish.yml). This repo now has `.github/workflows/publish.yml` (not a custom name). Tag builds attach:

- `logseq-plugin-repo-log-<tag>.zip`
- `package.json`

`@logseq/libs` on npm is **0.0.17** (latest as of 2026-09-13).

## Before the PR

1. Log in on this machine: `.\scripts\gh-login.ps1` (or `gh auth login`).
2. Run `.\scripts\publish-marketplace.ps1` (creates public `MLEDss/repo-log`, fills `manifest.json` `repo`, pushes, tags `v0.1.0`).
3. Wait until the GitHub release has the zip (Actions on that tag).
4. Re-run `.\scripts\publish-marketplace.ps1 -MarketplacePr` (forks `logseq/marketplace`, copies `packages/logseq-plugin-repo-log/`, opens PR). PR body draft: `docs/marketplace/PR.md`.

Until that merge, install unpacked: Plugins → Load unpacked plugin → `plugin/` (`npm run build` first).
