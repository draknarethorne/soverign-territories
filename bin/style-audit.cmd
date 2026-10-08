@echo off
call "%~dp0_env.cmd"
rem style-audit            rank the backgrounds, effects and realms by how illustrated their wording is (nothing is changed)
rem style-audit --prompts  also count the style words in the generated scene and showcase prompts per set
%PY% tools\art\style_audit.py %*
call "%~dp0_end.cmd" %errorlevel%
