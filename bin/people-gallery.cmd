@echo off
rem people-gallery   preview local housekeeping; --apply backs up, normalizes and builds derivatives + both reports
call "%~dp0_env.cmd"
%PY% tools\art\gallery_maintenance.py %*
call "%~dp0_end.cmd" %errorlevel%
