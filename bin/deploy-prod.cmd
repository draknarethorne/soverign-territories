@echo off
call "%~dp0_env.cmd"
if "%~1"=="" (
  echo Usage: deploy-prod HERO [STAGE] [--dry-run]    e.g. deploy-prod Drakness scene
  call "%~dp0_end.cmd" 1
  exit /b 1
)
set "STAGE="
set "EXTRA=%~3"
if not "%~2"=="" (
  if "%~2"=="--dry-run" (set "EXTRA=--dry-run") else (set "STAGE=--stage %~2")
)
%PY% tools\workflows\comfy_workflows.py deploy --to prod --hero %~1 %STAGE% %EXTRA%
call "%~dp0_end.cmd" %errorlevel%
