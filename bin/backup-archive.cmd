@echo off
rem Lossless snapshot packing; preview unless --apply. --library-root enables durable packing/explicit verified old-backup retirement.
call "%~dp0_env.cmd"
%PY% tools\art\library_backup_archive.py %*
call "%~dp0_end.cmd" %errorlevel%
