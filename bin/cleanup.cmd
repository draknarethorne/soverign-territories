@echo off
call "%~dp0_env.cmd"
if "%~1"=="" (
  echo Usage: cleanup "Workspace" [filters] [--workspace-backups] [--prefix-map OLD=NEW] [--retire-planned-home] [--apply]
  echo   Preview unless --apply; keeps zz_ items and normally requires matching home workflows.
  echo   Explicit --retire-planned-home requires --group, --hero and --workspace-backups.
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\workflows\comfy_workflows.py cleanup -w "%~1" %2 %3 %4 %5 %6 %7 %8 %9
call "%~dp0_end.cmd" %errorlevel%
