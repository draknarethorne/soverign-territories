@echo off
call "%~dp0_env.cmd"
if "%~1"=="" (
  echo Usage: pull-shots HERO [--dry-run]    keeps the workflows you saved under zz_Shots in the hero's workspaces ^(her own and Drakn Sisters^); subfolders are kept, edits are captured again
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\workflows\comfy_workflows.py pull --shots --to uat --hero %~1 %2
call "%~dp0_end.cmd" %errorlevel%
