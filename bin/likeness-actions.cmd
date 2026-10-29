@echo off
rem likeness-actions   validate, preview, apply or undo staged likeness actions
call "%~dp0_env.cmd"
%PY% tools\art\likeness_library\actions.py %*
call "%~dp0_end.cmd" %errorlevel%
