@echo off
rem Sandbox movement history; preview by default, writes only a new report with --apply.
call "%~dp0_env.cmd"
%PY% tools\art\likeness_library\movement_history.py %*
set "RC=%errorlevel%"
call "%~dp0_end.cmd" %RC%
exit /b %RC%
