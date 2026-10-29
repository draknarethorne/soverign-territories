@echo off
rem library-check    read only: is the library in step (names, scaled copies, headshots, frames), any duplicates, any photo waiting to be sorted? exit 1 when work is waiting. Then run library.cmd
call "%~dp0_env.cmd"
%PY% tools\art\library_sync.py --check %*
call "%~dp0_end.cmd" %errorlevel%
