# Repo Log

**Logseq plugin** = buttons and settings. **Python engine** = writes pages. **Logseq OG** = browse the graph. Do not open Optics/LED repos as a Logseq graph.

## Daily use

1. Double-click `repo-log.cmd` (engine at `http://127.0.0.1:8765`; leave it running).
2. Open Logseq OG on `D:\Repo Log\out\notes`.
3. First time: Developer mode → Plugins → **Load unpacked plugin** → `D:\Repo Log\plugin` (run `npm run build` in `plugin/` once).
4. Toolbar **RL**.

Marketplace listing needs a public GitHub repo and a PR to [logseq/marketplace](https://github.com/logseq/marketplace). After `gh auth login`, run `.\scripts\publish-marketplace.ps1`. See `docs/marketplace/README.md` and `plugin/README.md`.

Fallback window: `.\repo-log.ps1 app`.
