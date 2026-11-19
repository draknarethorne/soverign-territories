@echo off
rem rebase-manifest   preview/build/check a review-only full-rebase source manifest
call "%~dp0_env.cmd"
%PY% tools\art\likeness_library\rebase_manifest.py %*
call "%~dp0_end.cmd" %errorlevel%
