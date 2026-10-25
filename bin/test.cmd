@echo off
call "%~dp0_env.cmd"
rem Fast code tests for workflow tools, prompt generation and photo-library galleries.
%PY% tools\workflows\test_comfy_workflows.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\art\test_people_gallery.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\art\test_artists_gallery.py
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% -m unittest tools.art.likeness_library.tests.test_review_gallery
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\generators\test_gen_prompt_extends.py
call "%~dp0_end.cmd" %errorlevel%
