@echo off
rem Test subprocesses inherit one absolute, git-ignored scratch root.
if not exist "%~dp0..\tmp" mkdir "%~dp0..\tmp"
if not exist "%~dp0..\tmp" exit /b 1
for %%I in ("%~dp0..\tmp") do set "TEMP=%%~fI"
set "TMP=%TEMP%"
set "TMPDIR=%TEMP%"
exit /b 0
