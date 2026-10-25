@echo off
rem General library only; Artists use likeness-artists.cmd with the same engine.
rem likeness    compare faces in the photo library; sort, merge, retire or archive people   (audit-core | family-preview | likeness rebaseline [--apply-categories] | alike | compare A B | folder NAME | like FILE | sort | merge A B | retire NAME | archive-list FILE | promote PROSPECT HERO | undo)
rem             moving commands preview until you add --apply; --sheet FILE.png saves a picture of the faces involved
call "%~dp0_env.cmd"
%PY% tools\art\likeness.py %*
call "%~dp0_end.cmd" %errorlevel%
