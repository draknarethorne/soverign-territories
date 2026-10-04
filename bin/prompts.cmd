@echo off
call "%~dp0_env.cmd"
%PY% tools\generators\gen_prompt.py %*
call "%~dp0_end.cmd" %errorlevel%
