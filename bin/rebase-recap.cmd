@echo off
rem rebase-recap RUN-DIR or SIMPLE-RECEIPT.json; SIMPLE previews by default, --apply writes only recap/audit reports.
call "%~dp0_env.cmd"
%PY% tools\art\likeness_library\rebase_recap.py %*
call "%~dp0_end.cmd" %errorlevel%
