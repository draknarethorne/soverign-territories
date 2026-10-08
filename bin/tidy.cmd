@echo off
call "%~dp0_env.cmd"
if "%~1"=="" (
  echo Usage: tidy "Workspace" [--apply]    sorts loose workflows into their folders and removes empty folders; preview unless --apply.  tidy all = every workspace
  call "%~dp0_end.cmd" 1
  exit /b 1
)
if /i "%~1"=="all" (
  %PY% tools\workflows\comfy_workflows.py tidy %~2
) else (
  %PY% tools\workflows\comfy_workflows.py tidy -w "%~1" %~2
)
call "%~dp0_end.cmd" %errorlevel%
