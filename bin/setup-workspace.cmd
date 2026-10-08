@echo off
call "%~dp0_env.cmd"
if "%~1"=="" (
  echo Usage: setup-workspace "Workspace" [--apply]    the whole job for one workspace: deploy every set it is home for ^(with curated workflows and shots^), tidy, cleanup what it is not home for, status
  echo   Preview unless --apply.  e.g. setup-workspace "Angel Primes"   then   setup-workspace "Angel Primes" --apply
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\workflows\comfy_workflows.py setup -w "%~1" %~2
call "%~dp0_end.cmd" %errorlevel%
