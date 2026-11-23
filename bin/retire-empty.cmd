@echo off
rem Recoverable Sandbox retirement of folders emptied by one applied SIMPLE rebase. Preview by default; mutation needs --apply.
call "%~dp0_env.cmd"
%PY% tools\art\likeness_library\retire_empty_cli.py %*
set "RC=%errorlevel%"
call "%~dp0_end.cmd" %RC%
exit /b %RC%
