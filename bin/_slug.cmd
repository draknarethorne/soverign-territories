@echo off
rem Helper: sets SLUG to the lower-case first argument (a hero name such as Draknara -> draknara), the folder name the art cards use.
set "SLUG="
for /f "delims=" %%i in ('%PY% -c "import sys; print(sys.argv[1].lower())" %1') do set "SLUG=%%i"
