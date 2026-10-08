@echo off
call "%~dp0_env.cmd"
if "%~1"=="" (
  echo Usage: refresh HERO [STAGE] [--dry-run]    e.g. refresh Draknara scene
  echo The usual loop for one hero: regenerate her prompts, create or refresh her workflows, deploy them to her home workspace^(s^).
  call "%~dp0_end.cmd" 1
  exit /b 1
)
set "STAGE="
set "EXTRA=%~3"
if not "%~2"=="" (
  if "%~2"=="--dry-run" (set "EXTRA=--dry-run") else (if "%~2"=="studio" (set "STAGE=--class studio") else (set "STAGE=--stage %~2"))
)
call "%~dp0_slug.cmd" "%~1"
echo == prompts
%PY% tools\generators\gen_prompt.py --slug %SLUG% >nul
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
echo == workflows
%PY% tools\workflows\comfy_workflows.py make --create --hero %~1 %STAGE% %EXTRA%
echo == deploy to the home workspace
%PY% tools\workflows\comfy_workflows.py deploy --hero %~1 %STAGE% %EXTRA%
call "%~dp0_end.cmd" %errorlevel%
