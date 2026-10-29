@echo off
call "%~dp0_env.cmd"
%PY% tools\art\library_audit.py %*
call "%~dp0_end.cmd" %errorlevel%
