@echo off
call "%~dp0_env.cmd"
%PY% tools\generators\scaffold_generic_set.py %*
set "RESULT=%errorlevel%"
call "%~dp0_end.cmd" %RESULT%
exit /b %RESULT%
