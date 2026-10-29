@echo off
rem Sandbox run retention: preview by default; every state change requires --apply.
call "%~dp0_env.cmd"
%PY% tools\art\storage_retention.py %*
call "%~dp0_end.cmd" %errorlevel%
