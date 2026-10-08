@echo off
call "%~dp0_env.cmd"
if "%~1"=="" (
  echo Usage: pull HERO [STAGE] [--dry-run]    keeps what you made or edited in the hero's home workspace: new workflows become curated, edits to curated ones and shots are captured in the repo
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
