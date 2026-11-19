@echo off
rem library-preview    preview selected Various arrivals against all cached eligible identities.
call "%~dp0_env.cmd"
%PY% tools\art\likeness_library\normal_import.py --dry-run %*
call "%~dp0_end.cmd" %errorlevel%
