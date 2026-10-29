@echo off
setlocal
call "%~dp0_env.cmd"
call "%~dp0_test-env.cmd"
if errorlevel 1 exit /b 1
rem Routine commit checks; --deep also runs the explicit test/mutation hooks.
set "ST_DEEP_CHECK="
if "%~1"=="" goto argumentsready
if /i "%~1"=="--deep" (
  set "ST_DEEP_CHECK=1"
  goto argumentsready
)
echo ERROR: usage: bin\check.cmd [--deep]
call "%~dp0_end.cmd" 2
exit /b 2
:argumentsready
%PY% -m pre_commit --version >nul 2>nul
if errorlevel 1 (
  echo ERROR: pre-commit is required. Install it with python -m pip install pre-commit.
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% -m pre_commit run --hook-stage pre-commit --all-files
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
if defined ST_DEEP_CHECK %PY% -m pre_commit run --hook-stage manual --all-files
call "%~dp0_end.cmd" %errorlevel%
