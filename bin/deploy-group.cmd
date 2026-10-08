@echo off
call "%~dp0_env.cmd"
if "%~1"=="" (
  echo Usage: deploy-group GROUP [--dry-run]    e.g. deploy-group sovereign-dawn
  echo Copies a whole set's workflows from the repo to its home workspace; with no hero filter this is how the Sovereign Dawn cards and the angels are deployed.
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\workflows\comfy_workflows.py deploy --group %~1 %~2
call "%~dp0_end.cmd" %errorlevel%
