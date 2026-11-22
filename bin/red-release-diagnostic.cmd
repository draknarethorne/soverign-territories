@echo off
rem Read-only red-member diagnostic; no preview output or release is published.
call "%~dp0_env.cmd"
%PY% tools\art\likeness_library\red_release_diagnostic.py %*
set "RC=%errorlevel%"
call "%~dp0_end.cmd" %RC%
exit /b %RC%
