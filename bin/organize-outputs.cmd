@echo off
call "%~dp0_env.cmd"
rem organize-outputs       preview: move rendered images into <project>\<set>\<Hero>\... ;  organize-outputs --apply does it
%PY% tools\workflows\organize_outputs.py %*
call "%~dp0_end.cmd" %errorlevel%
