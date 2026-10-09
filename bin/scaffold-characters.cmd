@echo off
call "%~dp0_env.cmd"
rem Character scenes: the angels' Lineup, duty, quiet, domain and celebration scenes, and the sisters' domain, craft and celebration scenes (data/art/_settings/scene-recipes.json).
rem Existing cards are kept, so it is safe to re-run. Then run prompts.cmd and make.cmd (see help.cmd).
%PY% tools\generators\scaffold_angel_set.py --character %*
if errorlevel 1 goto done
%PY% tools\generators\scaffold_sister_character.py
:done
call "%~dp0_end.cmd" %errorlevel%
