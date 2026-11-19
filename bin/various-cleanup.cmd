@echo off
rem Portable run-bound raw library cleanup, preview by default.
call "%~dp0_env.cmd"
%PY% tools\art\likeness_library\various_cleanup.py %*
set "RC=%errorlevel%"
call "%~dp0_end.cmd" %RC%
exit /b %RC%
