$ErrorActionPreference = "Stop"
$gh = "C:\Program Files\GitHub CLI\gh.exe"
if (-not (Test-Path $gh)) { throw "gh.exe missing" }
& $gh auth login --hostname github.com --git-protocol https --web --skip-ssh-key
