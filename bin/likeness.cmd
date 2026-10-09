@echo off
rem likeness    compare faces in the photo library; sort, merge and retire photos by likeness   (likeness alike | compare A B | folder NAME | like FILE | sort | merge A B | retire NAME | undo)
rem             moving commands preview until you add --apply; --sheet FILE.png saves a picture of the faces involved
call "%~dp0_env.cmd"
%PY% tools\art\likeness.py %*
call "%~dp0_end.cmd" %errorlevel%
