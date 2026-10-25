@echo off
rem people-gallery-review   large, read-only Gallery and Review photo report; thumbnails cached beside the HTML
call "%~dp0_env.cmd"
%PY% tools\art\likeness_library\review_gallery.py %*
call "%~dp0_end.cmd" %errorlevel%
