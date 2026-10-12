@echo off
rem people-gallery   one page with every person's headshot and full photo (angels, sisters, prospects, artists' people) to look at in a browser: <work>\_reports\people_gallery.html
rem                  people-gallery --out DIR writes somewhere else; the library routine (library.cmd) writes it at the end
call "%~dp0_env.cmd"
%PY% tools\art\people_gallery.py --artists %*
call "%~dp0_end.cmd" %errorlevel%
