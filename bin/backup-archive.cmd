@echo off
rem Bounded lossless snapshot archive experiment; preview unless --apply; repo tmp outputs only.
call "%~dp0_env.cmd"
%PY% tools\art\library_backup_archive.py %*
call "%~dp0_end.cmd" %errorlevel%
