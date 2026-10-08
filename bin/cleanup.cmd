@echo off
call "%~dp0_env.cmd"
if "%~1"=="" (
  echo Usage: cleanup "Workspace" [--apply]    removes what the workspace is not home for ^(a clone's leftovers, finished temporary copies^); preview unless --apply
  echo   Moves workflows to workflows\.sync\backup, only when the set's home workspace holds an identical copy. zz_ items are never touched.
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\workflows\comfy_workflows.py cleanup -w "%~1" %~2
call "%~dp0_end.cmd" %errorlevel%
