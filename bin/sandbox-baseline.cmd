@echo off
rem sandbox-baseline   verify/refresh Source and reset disposable Working without history
call "%~dp0_env.cmd"
%PY% tools\art\likeness_library\sandbox_baseline.py %*
call "%~dp0_end.cmd" %errorlevel%
