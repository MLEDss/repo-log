# Submit a new Plugin to Marketplace

**Plugin GitHub repo URL:** https://github.com/MLEDss/repo-log

## GitHub releases checklist

- [x] a legal [package.json](https://gist.github.com/xyhp915/bb9f67f5b430ac0da2629d586a3e4d69#explain-packagejson) file.
- [x] a [valid CI workflow](https://github.com/xyhp915/logseq-journals-calendar/blob/main/.github/workflows/publish.yml#L10) build action for Github releases. (theme plugin for [this](https://github.com/Sansui233/logseq-bonofix-theme/blob/master/.github/workflows/publish.yml)).
- [x] a release which includes a release zip pkg from a successful build.
- [x] a clear README file, ideally with an image or gif showcase. (For more friendly to users, it is recommended to have English version description).
- [x] a license in the LICENSE file.

> ⚠️ The new incoming plugin recommended fields in [manifest.json](https://github.com/logseq/marketplace?tab=readme-ov-file#how-to-submit-your-plugin):
> `supportsDB` - [optional] Whether the plugin supports database graph.
> `supportsDBOnly` - [optional] Whether the plugin only supports database graph.

This plugin is a control panel for a local Python engine in the same repository. It does not fork Logseq. Capture and catalog writes stay in `python -m repo_log serve` (`127.0.0.1` only). `effect` is false. `unsupportedGraphType` is `db` (OG file graphs only).
