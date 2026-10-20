@echo off
rem people-gallery   one page with up to nine photos per person (angels, sisters, prospects, artists' people): <work>\_reports\library\people_gallery.html
rem                  includes Angel-to-Sister/Prospect candidates; --out DIR writes the gallery there
call "%~dp0_env.cmd"
%PY% tools\art\people_gallery.py --artists %*
call "%~dp0_end.cmd" %errorlevel%
