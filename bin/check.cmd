@echo off
call "%~dp0_env.cmd"
%PY% -m pre_commit run --all-files
call "%~dp0_end.cmd" %errorlevel%
