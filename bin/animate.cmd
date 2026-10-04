@echo off
call "%~dp0_env.cmd"
if "%~1"=="" (
  echo Usage: animate HERO [--dry-run]    e.g. animate Drakness
  echo Video prompts from data\animation cards, then MiniMax workflows tracked in git, then deploy to DEV.
  call "%~dp0_end.cmd" 1
  exit /b 1
)
set "EXTRA=%~2"
if "%~2"=="" set "EXTRA=%~3"
if "%~2"=="--dry-run" set "EXTRA=--dry-run"
echo == video prompts
%PY% tools\generators\gen_animation.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
echo == video workflows
%PY% tools\workflows\comfy_workflows.py make --engine minimax --create --hero %~1 %EXTRA%
echo == deploy to DEV
%PY% tools\workflows\comfy_workflows.py deploy --engine minimax --hero %~1 %EXTRA%
call "%~dp0_end.cmd" %errorlevel%
