@echo off
call "%~dp0_env.cmd"
%PY% tools\workflows\reference_rendering.py %*
call "%~dp0_end.cmd" %errorlevel%
