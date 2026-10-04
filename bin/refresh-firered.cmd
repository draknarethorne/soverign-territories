@echo off
call "%~dp0_env.cmd"
if "%~1"=="" (
  echo Usage: refresh-firered HERO [STAGE] [--dry-run]    e.g. refresh-firered Draknora scene
  echo Prompts, then FireRed workflows kept in workflows\.test\firered and not in git, then deploy to DEV.
  call "%~dp0_end.cmd" 1
  exit /b 1
)
set "STAGE="
set "EXTRA=%~3"
if not "%~2"=="" (
  if "%~2"=="--dry-run" (set "EXTRA=--dry-run") else (if "%~2"=="studio" (set "STAGE=--class studio") else (set "STAGE=--stage %~2"))
)
echo == prompts
%PY% tools\generators\gen_prompt.py >nul
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
echo == FireRed workflows
%PY% tools\workflows\comfy_workflows.py make --engine firered --create --hero %~1 %STAGE% %EXTRA%
echo == deploy to DEV
%PY% tools\workflows\comfy_workflows.py deploy --engine firered --hero %~1 %STAGE% %EXTRA%
call "%~dp0_end.cmd" %errorlevel%
