@echo off
call "%~dp0_env.cmd"
%PY% tools\workflows\reference_gallery.py %*
call "%~dp0_end.cmd" %errorlevel%
