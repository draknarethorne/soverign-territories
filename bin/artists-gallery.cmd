@echo off
rem artists-gallery   preview/check/publish separate read-only Artist pages; no matching or intake
call "%~dp0_env.cmd"
%PY% tools\art\artists_gallery.py %*
call "%~dp0_end.cmd" %errorlevel%
