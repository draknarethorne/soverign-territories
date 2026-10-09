@echo off
call "%~dp0_env.cmd"
rem codex-drift            compare docs\codex\heroes (roster tables, sister, bound, dragon and angel pages) with the cards and identity JSON; changes nothing
rem codex-drift --check    exit 1 on any drift (validate.cmd runs this); the JSON wins, so update the document
%PY% tools\art\codex_drift.py %*
call "%~dp0_end.cmd" %errorlevel%
