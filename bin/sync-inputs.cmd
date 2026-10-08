@echo off
call "%~dp0_env.cmd"
rem sync-inputs            preview: which input images each workspace's workflows load and which are missing from its input folder;  sync-inputs --apply copies them
%PY% tools\workflows\sync_inputs.py %*
call "%~dp0_end.cmd" %errorlevel%
