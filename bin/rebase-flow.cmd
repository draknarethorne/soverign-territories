@echo off
rem rebase-flow  run the whole fresh sandbox rebase (reset, originals, backup, intake, preview, install, checks) with live progress, timings and space; preview unless --apply, --check shows status
call "%~dp0_env.cmd"
%PY% tools\art\rebase_flow.py %*
call "%~dp0_end.cmd" %errorlevel%
