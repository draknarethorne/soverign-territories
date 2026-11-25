@echo off
call "%~dp0_env.cmd"
if "%~1"=="" (
  echo Usage: deploy-group GROUP [--stage STAGE] [--match TEXT] [--mode patch] [--workspace-backups] [--dry-run]
  echo Copies a whole set's workflows from the repo to its home workspace; with no hero filter this is how the Sovereign Dawn cards and the angels are deployed.
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\workflows\comfy_workflows.py deploy --apply --group %~1 %~2 %~3 %~4 %~5 %~6 %~7 %~8 %~9
call "%~dp0_end.cmd" %errorlevel%
