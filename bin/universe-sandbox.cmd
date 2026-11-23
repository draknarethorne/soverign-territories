@echo off
rem Identity-universe Sandbox builder. Preview by default; --apply builds a new Working, --check rehashes it.
call "%~dp0_env.cmd"
%PY% tools\art\likeness_library\universe_sandbox.py %*
set "RC=%errorlevel%"
call "%~dp0_end.cmd" %RC%
exit /b %RC%
