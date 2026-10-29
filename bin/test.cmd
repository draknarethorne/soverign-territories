@echo off
call "%~dp0_env.cmd"
rem Fast code tests for workflow tools, prompt generation and photo-library galleries.
%PY% -m unittest tools.workflows.test_reference_rendering tools.workflows.test_reference_execution tools.workflows.test_reference_gallery tools.workflows.test_reference_outputs tools.workflows.test_reference_comparison tools.workflows.test_backdrop
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
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
%PY% -m unittest tools.art.test_clean_preparation tools.art.test_retained_preparation tools.art.test_storage_retention
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% -m unittest tools.art.likeness_library.tests.test_sandbox_reset tools.art.test_temporary_storage
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% -m unittest tools.art.likeness_library.tests.test_review_gallery
if errorlevel 1 (
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% -m unittest tools.generators.test_gen_prompt_extends tools.generators.test_deluxe_reference
call "%~dp0_end.cmd" %errorlevel%
