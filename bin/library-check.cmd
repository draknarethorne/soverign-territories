@echo off
rem library-check    read-only selected-pool intake check; use --run-id to check an applied receipt.
call "%~dp0_env.cmd"
%PY% tools\art\likeness_library\normal_import.py --check %*
call "%~dp0_end.cmd" %errorlevel%
