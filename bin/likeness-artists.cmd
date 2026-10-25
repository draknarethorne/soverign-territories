@echo off
rem Artist-only entry point; same engine, separate discovery, cache and history.
call "%~dp0_env.cmd"
%PY% tools\art\likeness_artists.py %*
call "%~dp0_end.cmd" %errorlevel%
