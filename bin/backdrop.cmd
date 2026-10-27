@echo off
call "%~dp0_env.cmd"
if "%~1"=="" (
  echo Usage: backdrop --repo ^| -w "WORKSPACE" ^| --workspaces ^| --root DIR  [--dry-run ^| --check]
  echo   swaps the old cream studio-backdrop wording for the light-grey standard in hand-made workflows and prompts ^(zz_Shots, curated, captured^); backups go to workflows\.sync\backup
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\workflows\backdrop.py %*
call "%~dp0_end.cmd" %errorlevel%
