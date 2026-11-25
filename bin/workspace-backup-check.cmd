@echo off
call "%~dp0_env.cmd"
if "%~2"=="" (
  echo Usage: workspace-backup-check "Workspace" RUN
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\workflows\comfy_workflows.py backup-check "%~1" "%~2"
call "%~dp0_end.cmd" %errorlevel%
