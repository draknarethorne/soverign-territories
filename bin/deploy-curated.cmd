@echo off
call "%~dp0_env.cmd"
if "%~1"=="" (
  echo Usage: deploy-curated HERO [--dry-run]    copies the hand-curated workflows a workspace lacks; never overwrites your edits
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\workflows\comfy_workflows.py deploy --curated --hero %~1 %2
call "%~dp0_end.cmd" %errorlevel%
