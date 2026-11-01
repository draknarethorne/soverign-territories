@echo off
rem Synthetic tmp\retire-proof samples ONLY. Preview by default. No purge or permanent deletion.
call "%~dp0_env.cmd"
%PY% tools\art\backup_retirement.py %*
call "%~dp0_end.cmd" %errorlevel%
