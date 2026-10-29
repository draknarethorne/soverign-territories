@echo off
rem library-preview    every step of library.cmd as a preview: nothing is moved or written (except the log). Then run library.cmd
call "%~dp0_env.cmd"
%PY% tools\art\library_sync.py --dry-run %*
call "%~dp0_end.cmd" %errorlevel%
