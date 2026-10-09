@echo off
call "%~dp0_env.cmd"
rem todo            write docs\todo.md: where every top-tier card stands (finals and candidates kept in the repo) and the open work of the active plans; run pull first
rem todo --print    show it instead of writing
%PY% tools\art\todo_report.py %*
call "%~dp0_end.cmd" %errorlevel%

