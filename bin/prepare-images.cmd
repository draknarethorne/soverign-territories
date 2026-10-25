@echo off
rem prepare-images   sandbox sidecar pilot; preview by default, --apply retains inputs and comparisons only
call "%~dp0_env.cmd"
%PY% tools\art\image_preparation.py %*
call "%~dp0_end.cmd" %errorlevel%
