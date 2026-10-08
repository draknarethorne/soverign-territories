@echo off
call "%~dp0_env.cmd"
rem extract-literals            preview: sentences, poses and expressions pasted into several art cards that should become pieces
rem extract-literals --apply    write the pieces and point the cards at them (then run prompts.cmd and check git status prompts\ shows nothing changed)
%PY% tools\art\extract_literals.py %*
call "%~dp0_end.cmd" %errorlevel%
