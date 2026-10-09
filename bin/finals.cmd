@echo off
call "%~dp0_env.cmd"
if "%~1"=="" (
  echo Usage: finals ACTION "Workspace" [--apply]
  echo    status   "WS"                 candidates, finals and which slots still lack a final
  echo    sort     "WS" [--apply]       file candidates and finals where their name says; never deletes ^(preview unless --apply^)
  echo    promote  "WS" NAME [--apply]  make a candidate or shot the final for its slot; the old final is archived
  echo    pull     "WS"                 keep them in the repo ^(_candidates, _final^); `pull` does this too
  echo    deploy   "WS" [--apply]       put repo ones the workspace lacks into their folders
  echo    reclassify [--apply]          clean the repo with the same rules ^(old numbered shots to _candidates, duplicates to backup^)
  echo    images [--apply]             copy the render of each final into assets\art
  echo    record [--apply]             write each final's seed, denoise and inputs into data\art\finals ^(make replays them^)
  call "%~dp0_end.cmd" 1
  exit /b 1
)
if /i "%~1"=="reclassify" (
  %PY% tools\workflows\comfy_workflows.py finals reclassify %~2
) else if /i "%~1"=="images" (
  %PY% tools\workflows\comfy_workflows.py finals images %~2
) else if /i "%~1"=="record" (
  %PY% tools\workflows\comfy_workflows.py finals record %~2
) else if /i "%~1"=="promote" (
  %PY% tools\workflows\comfy_workflows.py finals promote %~3 -w "%~2" %~4
) else (
  %PY% tools\workflows\comfy_workflows.py finals %~1 -w "%~2" %~3
)
call "%~dp0_end.cmd" %errorlevel%
