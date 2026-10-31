@echo off
setlocal
rem Bounded isolated 20-30 photo FULL/LEAN publication and recovery experiment.
call "%~dp0_env.cmd"
call "%~dp0_test-env.cmd"
if errorlevel 1 exit /b 1
%PY% tools\art\library_storage_experiment.py %*
call "%~dp0_end.cmd" %errorlevel%
