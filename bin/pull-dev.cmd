@echo off
call "%~dp0_env.cmd"
if "%~1"=="" (
  echo Usage: pull-dev HERO [STAGE] [--dry-run]    keeps workflows you made or edited in DEV: new ones become curated workflows, edits to curated ones are captured
  call "%~dp0_end.cmd" 1
  exit /b 1
)
set "STAGE="
set "EXTRA=%~3"
if not "%~2"=="" (
  if "%~2"=="--dry-run" (set "EXTRA=--dry-run") else (if "%~2"=="studio" (set "STAGE=--class studio") else (set "STAGE=--stage %~2"))
)
%PY% tools\workflows\comfy_workflows.py pull --hero %~1 %STAGE% %EXTRA%
call "%~dp0_end.cmd" %errorlevel%
