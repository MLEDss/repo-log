$ErrorActionPreference = "Stop"
$root = Split-Path -Parent $PSScriptRoot
if (-not (Test-Path (Join-Path $root "plugin\package.json"))) {
  $root = Get-Location
}
$plugin = Join-Path $root "plugin"
$dist = Join-Path $plugin "dist\index.html"
if (-not (Test-Path $dist)) {
  Push-Location $plugin
  npm run build
  Pop-Location
}
$name = "logseq-plugin-repo-log"
$release = Join-Path $root "release"
$stage = Join-Path $release $name
if (Test-Path $release) { Remove-Item $release -Recurse -Force }
New-Item -ItemType Directory -Path $stage | Out-Null
Copy-Item (Join-Path $plugin "README.md") $stage
Copy-Item (Join-Path $plugin "package.json") $stage
Copy-Item (Join-Path $plugin "icon.png") $stage
Copy-Item (Join-Path $plugin "showcase.png") $stage
Copy-Item (Join-Path $root "LICENSE") $stage
Copy-Item (Join-Path $plugin "dist") (Join-Path $stage "dist") -Recurse
$zip = Join-Path $release "$name.zip"
if (Test-Path $zip) { Remove-Item $zip -Force }
Compress-Archive -Path $stage -DestinationPath $zip
Write-Output $zip
