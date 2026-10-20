@echo off
rem likeness-actions   validate or preview a downloaded likeness action manifest
call "%~dp0_env.cmd"
%PY% tools\art\likeness_library\actions.py %*
call "%~dp0_end.cmd" %errorlevel%
