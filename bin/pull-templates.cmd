@echo off
call "%~dp0_env.cmd"
rem pull-templates         keep the ST stage templates you tuned in the templates workspace (Sovereign Territories) as the repo masters
%PY% tools\workflows\comfy_workflows.py pull --templates %*
call "%~dp0_end.cmd" %errorlevel%
