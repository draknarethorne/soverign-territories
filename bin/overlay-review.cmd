@echo off
rem overlay-review   unconfirmed overlay reference candidates; preview by default
call "%~dp0_env.cmd"
%PY% tools\art\overlay_reference_review.py %*
call "%~dp0_end.cmd" %errorlevel%
