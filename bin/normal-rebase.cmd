@echo off
rem Stable whole-library rebase composition. Preview by default; mutation needs --apply.
call "%~dp0_env.cmd"
%PY% tools\art\likeness_library\normal_rebase.py %*
set "RC=%errorlevel%"
call "%~dp0_end.cmd" %RC%
exit /b %RC%
