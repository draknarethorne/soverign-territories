@echo off
rem Explicit compatibility entrypoint for the former whole-library housekeeping routine.
call "%~dp0_env.cmd"
%PY% tools\art\library_sync.py %*
call "%~dp0_end.cmd" %errorlevel%
