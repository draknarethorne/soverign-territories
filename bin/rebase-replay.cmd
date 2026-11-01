@echo off
setlocal
rem Preserved FULL baseline -> isolated tmp\r3 LEAN replay. Default/--dry-run writes nothing.
rem --apply resumes stages; completed --apply verifies instead of reprocessing. --check is independent.
call "%~dp0_env.cmd"
call "%~dp0_test-env.cmd"
if errorlevel 1 exit /b 1
%PY% tools\art\library_rebase_replay.py %*
call "%~dp0_end.cmd" %errorlevel%
