@echo off
rem library-backup  snapshot the photo library, ComfyUI inputs and workspace config (preview unless --apply)
call "%~dp0_env.cmd"
%PY% tools\art\library_backup.py %*
call "%~dp0_end.cmd" %errorlevel%
