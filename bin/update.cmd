@echo off
call "%~dp0_env.cmd"
%PY% tools\workflows\comfy_workflows.py make --apply %*
call "%~dp0_end.cmd" %errorlevel%
