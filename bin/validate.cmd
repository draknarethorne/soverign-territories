@echo off
call "%~dp0_env.cmd"
%PY% tools\validators\validate_data.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\validators\test_validate_data.py
call "%~dp0_end.cmd" %errorlevel%
