@echo off
rem preparation-history   independent bounded lossy history; preview by default; NEVER source pruning
call "%~dp0_env.cmd"
%PY% tools\art\preparation_history_bundle.py %*
call "%~dp0_end.cmd" %errorlevel%
