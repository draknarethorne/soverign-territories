@echo off
rem library     THE photo routine: drop new photos in Various\gallery, run this. originals, duplicates, likeness (junk, review, sort, singles), originals again, check, sync-inputs, index.
rem             library --dry-run previews every step; library --no-likeness does only the file housekeeping; library --min 0.40 loosens the merge of one-photo prospects (docs\art\likeness.md)
call "%~dp0_env.cmd"
%PY% tools\art\library_sync.py %*
call "%~dp0_end.cmd" %errorlevel%
