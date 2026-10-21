@echo off
rem people-gallery   build overview and full review pages together; overview links each person to their filtered review
rem                  includes category likeness cross-references, full rankings and Angel-to-Sister/Prospect candidates
call "%~dp0_env.cmd"
%PY% tools\art\likeness_library\review_gallery.py --artists %*
if errorlevel 1 goto end
%PY% tools\art\people_gallery.py --artists %*
:end
call "%~dp0_end.cmd" %errorlevel%
