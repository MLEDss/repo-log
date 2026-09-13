# Create the public GitHub repo, tag a plugin release, and optionally open the marketplace PR.
# Does not write git config. Requires: gh auth login (see scripts/gh-login.ps1).
param(
  [switch]$MarketplacePr,
  [string]$RepoName = "repo-log",
  [string]$Tag = "v0.1.0"
)

$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
Set-Location $root

$ghCmd = Get-Command gh -ErrorAction SilentlyContinue
if ($ghCmd) {
  $ghExe = $ghCmd.Source
} else {
  $ghExe = "C:\Program Files\GitHub CLI\gh.exe"
}
if (-not (Test-Path $ghExe)) {
  throw "GitHub CLI missing. Install gh, then run .\scripts\gh-login.ps1"
}

function Invoke-Gh {
  param([Parameter(ValueFromRemainingArguments = $true)][string[]]$GhArgs)
  & $ghExe @GhArgs
  if ($LASTEXITCODE -ne 0) {
    throw "gh $($GhArgs -join ' ') failed with exit $LASTEXITCODE"
  }
}

& $ghExe auth status
if ($LASTEXITCODE -ne 0) {
  throw "Not logged in. Run .\scripts\gh-login.ps1 then retry this script."
}

$login = (& $ghExe api user --jq .login).Trim()
if (-not $login) { throw "gh api user returned empty login" }
$repoSlug = "$login/$RepoName"

python (Join-Path $root "scripts\fill_marketplace_repo.py") $repoSlug
if ($LASTEXITCODE -ne 0) { throw "fill_marketplace_repo.py failed" }

function Invoke-GitAsUser {
  param([Parameter(ValueFromRemainingArguments = $true)][string[]]$GitArgs)
  git -c "user.name=$login" -c "user.email=$login@users.noreply.github.com" @GitArgs
  if ($LASTEXITCODE -ne 0) {
    throw "git $($GitArgs -join ' ') failed with exit $LASTEXITCODE"
  }
}

git add -A
git rev-parse HEAD 2>$null | Out-Null
$pending = git status --porcelain
if ($pending) {
  Invoke-GitAsUser commit -m "Prepare Logseq marketplace listing for $repoSlug."
}

git remote get-url origin 2>$null | Out-Null
if ($LASTEXITCODE -ne 0) {
  Invoke-Gh repo create $RepoName --public --source=. --remote=origin --description "Sidecar engine and Logseq OG plugin for Repo Log"
}
git push -u origin HEAD
if ($LASTEXITCODE -ne 0) { throw "git push failed" }

$existingTag = git tag -l $Tag
if (-not $existingTag) {
  git tag $Tag
}
git push origin $Tag
if ($LASTEXITCODE -ne 0) { throw "git push tag failed" }

if (-not $MarketplacePr) {
  Write-Output "Pushed $repoSlug and tag $Tag. Wait for Actions to attach the zip, then run:"
  Write-Output "  .\scripts\publish-marketplace.ps1 -MarketplacePr"
  exit 0
}

$deadline = (Get-Date).AddMinutes(8)
$zipReady = $false
while ((Get-Date) -lt $deadline) {
  $assets = & $ghExe release view $Tag --json assets --jq ".assets[].name" 2>$null
  if ($LASTEXITCODE -eq 0 -and $assets -match "logseq-plugin-repo-log") {
    $zipReady = $true
    break
  }
  Start-Sleep -Seconds 15
}
if (-not $zipReady) {
  throw "Release $Tag has no plugin zip yet. Open the Actions tab, wait, then rerun with -MarketplacePr."
}

$tmp = Join-Path $root "tests\.tmp\marketplace-fork"
if (Test-Path $tmp) { Remove-Item $tmp -Recurse -Force }
New-Item -ItemType Directory -Path (Split-Path $tmp) -Force | Out-Null
Invoke-Gh repo fork logseq/marketplace --clone=false --default-branch-only
Invoke-Gh repo clone "$login/marketplace" $tmp -- --depth 1
$pkgDir = Join-Path $tmp "packages\logseq-plugin-repo-log"
New-Item -ItemType Directory -Path $pkgDir -Force | Out-Null
Copy-Item (Join-Path $root "docs\marketplace\packages\logseq-plugin-repo-log\manifest.json") (Join-Path $pkgDir "manifest.json")
Copy-Item (Join-Path $root "docs\marketplace\packages\logseq-plugin-repo-log\icon.png") (Join-Path $pkgDir "icon.png")
Push-Location $tmp
try {
  git checkout -b "add-logseq-plugin-repo-log"
  git add -- packages/logseq-plugin-repo-log/manifest.json packages/logseq-plugin-repo-log/icon.png
  Invoke-GitAsUser commit -m "add logseq-plugin-repo-log"
  git push -u origin HEAD
  if ($LASTEXITCODE -ne 0) { throw "marketplace fork push failed" }
  $bodyFile = Join-Path $root "docs\marketplace\PR.md"
  Invoke-Gh pr create --repo logseq/marketplace --base master --head "${login}:add-logseq-plugin-repo-log" --title "add logseq-plugin-repo-log" --body-file $bodyFile
} finally {
  Pop-Location
}

Write-Output "Marketplace PR opened against logseq/marketplace."
