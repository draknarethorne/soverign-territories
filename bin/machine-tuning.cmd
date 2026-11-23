@echo off
rem Per-machine parallelism: show (read-only), set/clear previews unless --apply; writes only the git-ignored data\config\machine-tuning.local.json.
call "%~dp0_env.cmd"
%PY% tools\art\machine_tuning.py %*
set "RC=%errorlevel%"
call "%~dp0_end.cmd" %RC%
exit /b %RC%
