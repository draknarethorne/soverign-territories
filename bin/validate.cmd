@echo off
call "%~dp0_env.cmd"
rem validate            schema and link checks + the workflow tool tests (fast)
rem validate --quick    also a short validator self-test, one case per kind of check (under 2 minutes)
rem validate --full     also the whole validator self-test (about 6 minutes; it changes real files in place and undoes each change)
%PY% tools\validators\validate_data.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\workflows\test_comfy_workflows.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\generators\test_gen_prompt_extends.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
if /i "%~1"=="--quick" %PY% tools\validators\test_validate_data.py --quick
if /i "%~1"=="--full" %PY% tools\validators\test_validate_data.py
call "%~dp0_end.cmd" %errorlevel%
