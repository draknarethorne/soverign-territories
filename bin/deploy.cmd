@echo off
call "%~dp0_env.cmd"
if "%~1"=="" (
  echo Usage: deploy HERO [STAGE] [--dry-run]    e.g. deploy Draknara scene
  echo Copies the hero's workflows from the repo to her home workspace^(s^); an existing workflow only gets its prompt values updated. Use deploy-group for a whole set.
  call "%~dp0_end.cmd" 1
  exit /b 1
)
set "STAGE="
set "EXTRA=%~3"
if not "%~2"=="" (
  if "%~2"=="--dry-run" (set "EXTRA=--dry-run") else (if "%~2"=="studio" (set "STAGE=--class studio") else (set "STAGE=--stage %~2"))
)
%PY% tools\workflows\comfy_workflows.py deploy --hero %~1 %STAGE% %EXTRA%
call "%~dp0_end.cmd" %errorlevel%
