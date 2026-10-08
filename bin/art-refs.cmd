@echo off
call "%~dp0_env.cmd"
if "%~1"=="" (
  echo Usage: art-refs where-used PIECE            e.g. art-refs where-used wardrobe/weapons/swords/greatsword
  echo        art-refs move OLD NEW [--dry-run]    moves a piece and every path and id that points at it
  echo        art-refs regroup MAP.json [--dry-run]
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\art\art_refs.py %*
call "%~dp0_end.cmd" %errorlevel%
