@echo off
rem Explicit experimental entrypoint; directed rebase additionally requires a recipe.
call "%~dp0_env.cmd"
%PY% tools\art\likeness_experiments\__main__.py %*
call "%~dp0_end.cmd" %errorlevel%
