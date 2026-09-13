$ErrorActionPreference = "Stop"
$root = $PSScriptRoot
$env:PYTHONPATH = Join-Path $root "src"
Set-Location $root
python -m repo_log @args
