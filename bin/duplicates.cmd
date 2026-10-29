@echo off
rem duplicates    the same picture kept twice anywhere in the photo library (any folder, any name): report; duplicates --apply sets the extra copies aside in _archive. library.cmd runs it for you
call "%~dp0_env.cmd"
%PY% tools\art\duplicates.py %*
call "%~dp0_end.cmd" %errorlevel%
