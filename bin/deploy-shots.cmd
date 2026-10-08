@echo off
call "%~dp0_env.cmd"
if "%~1"=="" (
  echo Usage: deploy-shots HERO [--dry-run]    copies the kept shots a workspace lacks into zz_Shots; never overwrites your edits
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\workflows\comfy_workflows.py deploy --shots --hero %~1 %2
call "%~dp0_end.cmd" %errorlevel%
