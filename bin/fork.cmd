@echo off
call "%~dp0_env.cmd"
if "%~2"=="" (
  echo Usage: fork WORKFLOW TAG    e.g. fork Drakness_MiniMax_Video_X_Pose_Laugh Hand
  echo Copies a generated workflow to workflows\_curated as WORKFLOW_TAG and puts it in the hero's home workspace so you can hand-edit it in ComfyUI.
  echo Save it in ComfyUI, then run pull to keep your changes.
  call "%~dp0_end.cmd" 1
  exit /b 1
)
%PY% tools\workflows\comfy_workflows.py fork %~1 --as %~2 %3 %4
call "%~dp0_end.cmd" %errorlevel%
