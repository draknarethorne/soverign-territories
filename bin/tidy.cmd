@echo off
call "%~dp0_env.cmd"
if "%~1"=="" (
  echo Usage: tidy "Workspace" [--stage STAGE] [--group GROUP] [--apply]    preview unless --apply. Filtered runs leave empty folders alone.
  call "%~dp0_end.cmd" 1
  exit /b 1
)
if /i "%~1"=="all" (
  %PY% tools\workflows\comfy_workflows.py tidy %~2 %~3 %~4 %~5 %~6
) else (
  %PY% tools\workflows\comfy_workflows.py tidy -w "%~1" %~2 %~3 %~4 %~5 %~6
)
call "%~dp0_end.cmd" %errorlevel%
