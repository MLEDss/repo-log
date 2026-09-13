@echo off
cd /d "%~dp0"
set "PYTHONPATH=%~dp0src"
echo Repo Log engine http://127.0.0.1:8765
echo Load unpacked plugin: "%~dp0plugin"
python -m repo_log %*
if errorlevel 1 pause
