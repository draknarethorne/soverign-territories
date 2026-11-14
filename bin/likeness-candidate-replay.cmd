@echo off
setlocal
call "%~dp0_env.cmd"
if errorlevel 1 exit /b %errorlevel%
"%PY%" "%~dp0..\tools\art\likeness_candidate_replay.py" %*
exit /b %errorlevel%
