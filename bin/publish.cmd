@echo off
call "%~dp0_env.cmd"
if "%~2"=="" (
  echo Usage: publish HERO "Workspace" [STAGE] [--dry-run]    puts a temporary copy of the hero's set in another workspace that accepts it
  echo   e.g. publish Drakness "Sovereign Territories"        ^(videos for reels and feeds^)   remove it later with cleanup "Sovereign Territories"
  call "%~dp0_end.cmd" 1
  exit /b 1
)
set "STAGE="
set "EXTRA=%~4"
if not "%~3"=="" (
  if "%~3"=="--dry-run" (set "EXTRA=--dry-run") else (if "%~3"=="studio" (set "STAGE=--class studio") else (set "STAGE=--stage %~3"))
)
%PY% tools\workflows\comfy_workflows.py deploy --hero %~1 -w "%~2" %STAGE% %EXTRA%
call "%~dp0_end.cmd" %errorlevel%
