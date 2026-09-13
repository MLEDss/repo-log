# Repo Log (Logseq plugin)

Control panel for a **Logseq OG file graph**. Buttons and settings live in Logseq. Page files are written by the local Python engine (`python -m repo_log serve`). This plugin does **not** fork Logseq and does **not** implement a second write path for capture/catalog.

![Repo Log panel](./showcase.png)

Marketplace install gives you this panel only. You still need the Python engine from the same GitHub repository running on `127.0.0.1:8765`.

## Install

### Marketplace (after listing)

1. Plugins → Marketplace → search **Repo Log** → Install.
2. Clone this GitHub repository (it contains the engine).
3. From the repo root: `python -m repo_log serve` (binds `127.0.0.1:8765` only).
4. Open the OG graph at `out/notes` (run `python -m repo_log init` once).
5. Toolbar **RL**.

Until [marketplace PR #900](https://github.com/logseq/marketplace/pull/900) is merged, use unpacked install:

1. Enable Developer mode in Logseq settings.
2. `cd plugin && npm install && npm run build`
3. Plugins → Load unpacked plugin → this `plugin/` folder.
4. Open graph `out/notes` from the Repo Log repository.
5. Start the engine: `python -m repo_log serve`.
6. Toolbar **RL**.

### Slash commands

- `Repo Log: open panel`
- `Repo Log: initialize graph` / `update catalog` (engine)
- `Repo Log: dialogue template` / `concept template` (insert skeleton at cursor)

## Settings

- **Engine URL** — default `http://127.0.0.1:8765`. Do not point this at the public internet.

## Develop

```bash
cd plugin
npm install
npm run build
```

Release zip is built by `.github/workflows/publish.yml` on git tags (asset `logseq-plugin-repo-log-<tag>.zip` plus `package.json`).

## License

MIT
