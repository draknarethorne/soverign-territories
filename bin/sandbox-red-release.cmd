@echo off
rem Sandbox-only red release experiment; never updates shared workflow consumers.
call "%~dp0_env.cmd"
%PY% tools\art\likeness_library\sandbox_red_release.py %*
set "RC=%errorlevel%"
call "%~dp0_end.cmd" %RC%
exit /b %RC%
