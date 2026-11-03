@echo off
rem rebase-recap   RUN-DIR [--dry-run ^| --check] [--out FILE] [--expectations FILE]  per-run HTML of moves, renames, holds, look-alikes; sandbox-rebase runs it automatically
call "%~dp0_env.cmd"
%PY% tools\art\likeness_library\rebase_recap.py %*
call "%~dp0_end.cmd" %errorlevel%
