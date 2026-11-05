@echo off
setlocal
call "%~dp0_env.cmd"
%PY% tools\art\lean_continue.py %*
call "%~dp0_end.cmd" %errorlevel%
