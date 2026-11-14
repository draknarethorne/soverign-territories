@echo off
rem Double-click menu for the common operations. Each choice runs one of the scripts in this folder.
:menu
echo.
echo  Sovereign Territories
echo   1  Refresh a hero (prompts, workflows, deploy to her home workspace)
echo   2  Refresh a whole set (angel-primes, sovereign-dawn ...)
echo   3  Set up a workspace (deploy its sets, tidy, cleanup, status)
echo   4  Publish a temporary copy to another workspace
echo   5  Clean up a workspace
echo   6  Status
echo   7  Workspaces
echo   8  Preview tests for changed work (HEAD; bin\validate.cmd --changed HEAD --check executes)
echo   Y  Isolated quick mutation validation (safe beside intake)
echo   Z  Routine commit checks (use bin\check.cmd --deep for explicit test hooks)
echo   0  Deep quality checks (explicit unit and mutation hooks; slower)
echo   9  Refresh FireRed for a hero
echo   A  Animate a hero (video prompts, workflows, deploy)
echo   L  Photo library: sort new photos in Various, remove duplicates, rebuild all scaled images
echo   R  Photo review gallery (read-only audit; history-only repair flags in Help)
echo   G  Preview gallery upkeep (rename, padded/head/chest; no matching or writes)
echo   GR Preview reports-only gallery refresh (no photo upkeep)
echo   P  Preview sandbox image preparation comparisons (no source or identity changes)
echo      P also offers COMPACT/COLLAGE history, mixed storage experiments or a complete rebase replay
echo   U  Preview same-mask eraser A/B (LaMa vs OpenCV; comparison only)
echo   V  Preview unconfirmed overlay reference candidates
echo   J  Preview early Junk quarantine from a completed preparation report (no moves)
echo   T  Preview artist-only likeness grouping in the sandbox (shared engine, no moves)
echo   V  Preview separate Artist gallery pages (no matching or source changes)
echo   C  Photo library check (read only: anything waiting?)
echo   B  Back up the photo library and ComfyUI inputs
echo      B also offers lossless snapshot archives or a bounded format benchmark (Help lists apply/check)
echo   X  Intake-aware sandbox clean start (inventory or verify; completed-stage recovery flags in Help)
echo   LC Preview saved-input LEAN continuation (no reset, intake, matching or install)
echo   LS Preview saved-evidence likeness shadow scope (no image reads or library changes)
echo   LP Preview visual likeness review packet (report only, no membership changes)
echo   LR Preview character-reference confirmation packet (validated pair feedback, no library changes)
echo   LT Preview whole-library realignment candidate or frozen-reference control (no installation)
echo   LF Preview coherent identity fragments and a bounded non-face context review (no installation)
echo   LX Preview returned-fragment reference repair and association comparison (no installation)
echo   LD Preview appearance/family disposition handoff from reconciliation (no rescoring)
echo   LQ Preview candidate replay, split investigation or actual shadow reformation (no installation)
echo   LO Preview local visual-cue observations or optional model setup (no identity changes)
echo   LG Preview own-core/category diagnostics and bounded existing-CLIP region ablation
echo   LE Preview ordered entrance/core/retention experiments (no installed changes)
echo   LH Preview original-anchor multi-view reconciliation (saved controls, no installed changes)
echo   LA Preview smaller-view non-core association state (no core influence or installed changes)
echo   N  Preview sandbox run-retention decisions (read only)
echo   F  Preview reference-render batch (offline, no workflow deployment or queue)
echo   D  Refresh rendering selection/results gallery (reports only)
echo   O  Refresh the ComfyUI outputs browser (reports only; pull is separate)
echo   E  Compare frozen reference sources and renders (reports only)
echo   S  Style audit (which art wording leans illustrated)
echo   K  Backdrop wording check (read only: old cream studio wording left in the repo or a workspace?)
echo   H  Help (all scripts)
echo   Q  Quit
set "CH="
set /p "CH=Choice: "
if /i "%CH%"=="Q" exit /b 0
if /i "%CH%"=="H" call "%~dp0help.cmd" & pause & goto menu
if /i "%CH%"=="S" call "%~dp0style-audit.cmd" & pause & goto menu
if /i "%CH%"=="K" call "%~dp0backdrop.cmd" --repo --workspaces --check & pause & goto menu
if /i "%CH%"=="L" call "%~dp0library.cmd" & pause & goto menu
if /i "%CH%"=="R" call "%~dp0people-gallery-review.cmd" & pause & goto menu
if /i "%CH%"=="G" call "%~dp0people-gallery.cmd" --dry-run & pause & goto menu
if /i "%CH%"=="GR" call "%~dp0people-gallery.cmd" --reports-only --dry-run & pause & goto menu
if /i "%CH%"=="C" call "%~dp0library-check.cmd" & pause & goto menu
if /i "%CH%"=="B" goto backup
if /i "%CH%"=="X" goto sandboxrebase
if /i "%CH%"=="LC" goto leancontinue
if /i "%CH%"=="LS" goto likenessshadow
if /i "%CH%"=="LP" goto likenesspacket
if /i "%CH%"=="LR" goto characterpacket
if /i "%CH%"=="LT" goto referencetrial
if /i "%CH%"=="LF" goto fragmenttrial
if /i "%CH%"=="LX" goto reconciliation
if /i "%CH%"=="LD" goto disposition
if /i "%CH%"=="LQ" goto candidatereplay
if /i "%CH%"=="LO" goto localobserver
if /i "%CH%"=="LG" goto categorydiagnostics
if /i "%CH%"=="LE" goto entrancetrial
if /i "%CH%"=="LH" goto hypothesistrial
if /i "%CH%"=="LA" goto viewassociations
if /i "%CH%"=="N" goto retention
if /i "%CH%"=="F" goto referencerender
if /i "%CH%"=="D" goto rendergallery
if /i "%CH%"=="O" goto outputsgallery
if /i "%CH%"=="E" goto referencecomparison
if /i "%CH%"=="P" goto preparation
if /i "%CH%"=="U" goto erasercompare
if /i "%CH%"=="V" goto overlayreview
if /i "%CH%"=="J" goto preparationjunk
if /i "%CH%"=="T" goto artistlikeness
if /i "%CH%"=="V" goto artistgallery
if "%CH%"=="2" goto group
if "%CH%"=="3" goto setup
if "%CH%"=="4" goto publish
if "%CH%"=="5" goto cleanup
if "%CH%"=="6" call "%~dp0status.cmd" & pause & goto menu
if "%CH%"=="7" call "%~dp0workspaces.cmd" & pause & goto menu
if "%CH%"=="8" call "%~dp0validate.cmd" --changed HEAD --dry-run & pause & goto menu
if /i "%CH%"=="Y" call "%~dp0validate.cmd" --isolated --quick & pause & goto menu
if /i "%CH%"=="Z" call "%~dp0check.cmd" & pause & goto menu
if "%CH%"=="0" call "%~dp0check.cmd" --deep & pause & goto menu
set "SCRIPT="
if "%CH%"=="1" set "SCRIPT=refresh.cmd"
if "%CH%"=="9" set "SCRIPT=refresh-firered.cmd"
if /i "%CH%"=="A" set "SCRIPT=animate.cmd"
if not defined SCRIPT goto menu
set "HERO="
set "STG="
set /p "HERO=Hero (for example Draknara): "
set /p "STG=Stage (poses, head, scene, hair, motion, armor, clothing, studio; blank for all): "
set "DRY="
set /p "DRY=Dry run first? (y/n): "
set "FLAG="
if /i "%DRY%"=="y" set "FLAG=--dry-run"
if "%STG%"=="" (
  call "%~dp0%SCRIPT%" "%HERO%" "" %FLAG%
) else (
  call "%~dp0%SCRIPT%" "%HERO%" "%STG%" %FLAG%
)
pause
goto menu
:referencerender
set "ROOT="
set "BATCH="
set /p "ROOT=Library absolute path: "
set /p "BATCH=Render request JSON absolute path: "
call "%~dp0render-reference.cmd" preview "%BATCH%" --root "%ROOT%" --dry-run
pause
goto menu
:rendergallery
set "ROOT="
set /p "ROOT=Library absolute path: "
call "%~dp0render-gallery.cmd" --root "%ROOT%" --apply
pause
goto menu
:outputsgallery
set "ROOT="
set /p "ROOT=Library absolute path: "
call "%~dp0render-reference.cmd" outputs --root "%ROOT%" --apply
pause
goto menu
:referencecomparison
set "ROOT="
set "BATCH="
set /p "ROOT=Library absolute path: "
set /p "BATCH=Frozen reference batch ID: "
call "%~dp0render-reference.cmd" compare "%BATCH%" --root "%ROOT%" --dry-run
if errorlevel 1 (
  pause
  goto menu
)
set "APPLY="
set /p "APPLY=Publish comparison page? (y/n): "
if /i "%APPLY%"=="y" call "%~dp0render-reference.cmd" compare "%BATCH%" --root "%ROOT%" --apply
pause
goto menu
:preparation
set "PREPARATION=prepare"
set /p "PREPARATION=Preview prepare/history/experiment/replay (Enter keeps prepare): "
if /i "%PREPARATION%"=="history" goto preparationhistory
if /i "%PREPARATION%"=="experiment" goto storageexperiment
if /i "%PREPARATION%"=="replay" goto rebasepreview
set "ROOT="
set "RUN="
set /p "ROOT=Sandbox Working absolute path: "
set /p "RUN=Comparison run absolute path inside Working\_reports\preparation: "
set "STORAGE="
set /p "STORAGE=Evidence storage (full/lean; Enter resumes saved mode or starts lean): "
if "%STORAGE%"=="" (
  call "%~dp0prepare-images.cmd" --root "%ROOT%" --out "%RUN%" --dry-run
) else (
  call "%~dp0prepare-images.cmd" --root "%ROOT%" --out "%RUN%" --storage-mode "%STORAGE%" --dry-run
)
pause
goto menu
:preparationhistory
set "ROOT="
set "REPORT="
set "RUN="
set "STORAGE=compact"
set /p "ROOT=Sandbox Working absolute path: "
set /p "REPORT=Existing FULL or LEAN preparation report absolute path: "
set /p "RUN=New output directly inside Working\_reports\preparation-history: "
set /p "STORAGE=History mode compact/collage (Enter keeps compact): "
call "%~dp0preparation-history.cmd" --root "%ROOT%" --report "%REPORT%" --out "%RUN%" --mode "%STORAGE%" --dry-run
pause
goto menu
:rebasepreview
call "%~dp0rebase-replay.cmd" --dry-run
pause
goto menu
:storageexperiment
set "ROOT="
set "RUN="
set /p "ROOT=Read-only source library Working absolute path: "
set /p "RUN=NEW experiment output absolute path strictly under repository tmp: "
call "%~dp0storage-experiment.cmd" --root "%ROOT%" --out "%RUN%" --dry-run
pause
goto menu
:erasercompare
set "REPORT="
set "SOURCES="
set "RUN="
set /p "REPORT=Existing preparation run absolute path: "
set /p "SOURCES=Sources JSON list absolute path: "
set /p "RUN=New run absolute path inside Working\_reports\eraser-compare: "
call "%~dp0eraser-compare.cmd" --report "%REPORT%" --sources "%SOURCES%" --out "%RUN%" --dry-run
pause
goto menu
:overlayreview
set "REPORT="
set "SOURCES="
set "RUN="
set /p "REPORT=Existing preparation report absolute path: "
set /p "SOURCES=Source-list JSON absolute path: "
set /p "RUN=New run absolute path inside Working\_reports\eraser-compare: "
call "%~dp0overlay-review.cmd" --report "%REPORT%" --sources "%SOURCES%" --out "%RUN%" --dry-run
goto menu

:preparationjunk
set "ROOT="
set "RUN="
set /p "ROOT=Sandbox Working absolute path: "
set /p "RUN=Existing preparation run absolute path: "
call "%~dp0prepare-images.cmd" --root "%ROOT%" --out "%RUN%" --quarantine-junk --dry-run
pause
goto menu
:artistlikeness
set "ROOT="
set /p "ROOT=Sandbox Working absolute path: "
call "%~dp0likeness-artists.cmd" --root "%ROOT%" --dry-run group --singles
pause
goto menu
:artistgallery
set "ROOT="
set /p "ROOT=Sandbox Working absolute path: "
call "%~dp0artists-gallery.cmd" --root "%ROOT%" --dry-run
pause
goto menu
:sandboxrebase
set "ROOT="
set "RUN="
set /p "ROOT=Sandbox Working absolute path: "
set /p "RUN=New run directory inside Working (or existing run to verify): "
set "VERIFY="
set /p "VERIFY=Verify existing run only? (y/n): "
if /i "%VERIFY%"=="y" (
  call "%~dp0sandbox-rebase.cmd" "%ROOT%" "%RUN%" --check
  call "%~dp0rebase-recap.cmd" "%RUN%" --dry-run
) else (
  call "%~dp0sandbox-rebase.cmd" "%ROOT%" "%RUN%" --dry-run
)
echo Whole fresh rebase with live progress: bin\rebase-flow.cmd --root "%ROOT%" --run NAME --apply (preview without --apply)
echo Select --profile fast^|lean^|full; FAST is original-byte grouping/naming testing, not an implicit disposable mode.
echo Add --baseline working to preserve the installed baseline; --regroup --review-source "ASSESSMENT-DIR" enables tracked appearance stages and bound review evidence.
echo Explicit disposable sandbox/LEAN: add --recovery-mode disposable on every command; skips pre-intake derivatives/backup, reset-only recovery.
pause
goto menu
:retention
set "ROOT="
set /p "ROOT=Sandbox Working absolute path: "
call "%~dp0storage-retention.cmd" --root "%ROOT%" preview
pause
goto menu
:group
set "GRP="
set "DRY="
set /p "GRP=Set (angel-primes, sovereign-dawn, sovereign-territories, drakn-sisters): "
set /p "DRY=Dry run first? (y/n): "
set "FLAG="
if /i "%DRY%"=="y" set "FLAG=--dry-run"
call "%~dp0refresh-group.cmd" "%GRP%" %FLAG%
pause
goto menu
:setup
set "WS="
set "APPLY="
set /p "WS=Workspace (for example Angel Primes): "
set /p "APPLY=Apply (n = preview only)? (y/n): "
set "FLAG="
if /i "%APPLY%"=="y" set "FLAG=--apply"
call "%~dp0setup-workspace.cmd" "%WS%" %FLAG%
pause
goto menu
:publish
set "HERO="
set "WS="
set "DRY="
set /p "HERO=Hero (for example Drakness): "
set /p "WS=Workspace that accepts the set (for example Sovereign Territories): "
set /p "DRY=Dry run first? (y/n): "
set "FLAG="
if /i "%DRY%"=="y" set "FLAG=--dry-run"
call "%~dp0publish.cmd" "%HERO%" "%WS%" "" %FLAG%
pause
goto menu
:cleanup
set "WS="
set "APPLY="
set /p "WS=Workspace to clean up (for example Angel Primes): "
set /p "APPLY=Apply (n = preview only)? (y/n): "
set "FLAG="
if /i "%APPLY%"=="y" set "FLAG=--apply"
call "%~dp0cleanup.cmd" "%WS%" %FLAG%
pause
goto menu
:leancontinue
set "LCROOT="
set "LCSOURCE="
set "LCRUN="
set /p "LCROOT=Absolute sandbox Working path: "
set /p "LCSOURCE=Original completed LEAN run name: "
set /p "LCRUN=New continuation run name: "
call "%~dp0lean-continue.cmd" --root "%LCROOT%" --source-run "%LCSOURCE%" --run "%LCRUN%" --dry-run
pause
goto menu
:likenessshadow
set "LSRUN="
set "LSOUT="
set "LSMAX=1500"
set /p "LSRUN=Absolute saved baseline run directory: "
set /p "LSOUT=New absolute experiment directory under repository tmp: "
set /p "LSMAX=Maximum scoped photos (default 1500; preview11 neighbourhood needs 2400): "
call "%~dp0likeness-shadow.cmd" --run "%LSRUN%" --out "%LSOUT%" --max-photos "%LSMAX%" --dry-run
pause
goto menu
:likenesspacket
set "LPEXPERIMENT="
set "LPOUT="
set /p "LPEXPERIMENT=Absolute verified shadow experiment directory: "
set /p "LPOUT=New absolute reports\likeness-reassessment\NAME directory: "
call "%~dp0likeness-review-packet.cmd" --experiment "%LPEXPERIMENT%" --out "%LPOUT%" --dry-run
pause
goto menu
:characterpacket
set "LREXPERIMENT="
set "LRREVIEW="
set "LRFEEDBACK="
set "LRCLARIFICATIONS="
set "LROUT="
set /p "LREXPERIMENT=Absolute verified shadow experiment directory: "
set /p "LRREVIEW=Absolute completed pair review packet directory: "
set /p "LRFEEDBACK=Absolute raw pair feedback JSON: "
set /p "LRCLARIFICATIONS=Absolute separate clarification JSON: "
set /p "LROUT=New absolute reports\likeness-reassessment\NAME directory: "
call "%~dp0likeness-character-packet.cmd" --experiment "%LREXPERIMENT%" --review-packet "%LRREVIEW%" --feedback "%LRFEEDBACK%" --clarifications "%LRCLARIFICATIONS%" --out "%LROUT%" --dry-run
pause
goto menu
:referencetrial
set "LTEXPERIMENT="
set "LTPACKET="
set "LTANSWERS="
set "LTOUT="
set "LTMODE="
set /p "LTEXPERIMENT=Absolute verified shadow experiment directory: "
set /p "LTPACKET=Absolute character confirmation report directory: "
set /p "LTANSWERS=Absolute completed character answer JSON: "
set /p "LTOUT=New absolute reports\likeness-reassessment\NAME directory: "
set /p "LTMODE=Build general realignment candidate? Y/N (default Y): "
if /i "%LTMODE%"=="N" (
  call "%~dp0likeness-reference-trial.cmd" --experiment "%LTEXPERIMENT%" --character-packet "%LTPACKET%" --answers "%LTANSWERS%" --out "%LTOUT%" --compare-order --dry-run
) else (
  call "%~dp0likeness-reference-trial.cmd" --experiment "%LTEXPERIMENT%" --character-packet "%LTPACKET%" --answers "%LTANSWERS%" --out "%LTOUT%" --compare-order --realign --dry-run
)
pause
goto menu
:disposition
set "LDSOURCE="
set "LDOUT="
set /p "LDSOURCE=Absolute verified reconciliation report directory: "
set /p "LDOUT=New absolute reports\likeness-reassessment\NAME directory: "
call "%~dp0likeness-disposition-trial.cmd" --source "%LDSOURCE%" --out "%LDOUT%" --dry-run
pause
goto menu
:categorydiagnostics
set "LCSOURCE="
set "LCOUT="
set /p "LCSOURCE=Absolute assessed reformation report directory: "
set /p "LCOUT=New absolute reports\likeness-reassessment\NAME directory: "
call "%~dp0likeness-diagnostics.cmd" --source "%LCSOURCE%" --out "%LCOUT%" --dry-run
pause
goto menu
:entrancetrial
set "LESOURCE="
set "LEOUT="
set "LECOALESCE="
set "LEDIRECTED="
set /p "LESOURCE=Absolute assessed reformation report directory: "
set /p "LEOUT=New absolute reports\likeness-reassessment\NAME directory: "
set /p "LEDIRECTED=Run bounded directed reformation shadow? Y/N (default N): "
if /i "%LEDIRECTED%"=="Y" (
  call "%~dp0likeness-entrance-trial.cmd" --source "%LESOURCE%" --out "%LEOUT%" --directed --dry-run
  pause
  goto menu
)
set /p "LECOALESCE=Add paired reference-view coalescence experiment? Y/N (default N): "
if /i "%LECOALESCE%"=="Y" (
  call "%~dp0likeness-entrance-trial.cmd" --source "%LESOURCE%" --out "%LEOUT%" --coalesce --dry-run
  pause
  goto menu
)
call "%~dp0likeness-entrance-trial.cmd" --source "%LESOURCE%" --out "%LEOUT%" --dry-run
pause
goto menu
:hypothesistrial
set "LHSOURCE="
set "LHBASELINE="
set "LHOUT="
set /p "LHSOURCE=Absolute assessed reformation report directory: "
set /p "LHBASELINE=Absolute verified coalesced entrance report directory: "
set /p "LHOUT=New absolute reports\likeness-reassessment\NAME directory: "
call "%~dp0likeness-hypothesis-trial.cmd" --source "%LHSOURCE%" --baseline "%LHBASELINE%" --out "%LHOUT%" --dry-run
pause
goto menu
:viewassociations
set "LASOURCE="
set "LABASELINE="
set "LAOUT="
set /p "LASOURCE=Absolute assessed reformation report directory: "
set /p "LABASELINE=Absolute verified hypothesis reconciliation report directory: "
set /p "LAOUT=New absolute reports\likeness-reassessment\NAME directory: "
call "%~dp0likeness-view-associations.cmd" --source "%LASOURCE%" --baseline "%LABASELINE%" --out "%LAOUT%" --dry-run
pause
goto menu
:localobserver
set "LOMODE="
set /p "LOMODE=Preview S=model/runtime setup, O=local observations (default O): "
if /i "%LOMODE%"=="S" (
  call "%~dp0likeness-observe.cmd" --setup --dry-run
  pause
  goto menu
)
set "LOSOURCE="
set "LOOUT="
set /p "LOSOURCE=Absolute assessed reformation report directory: "
set /p "LOOUT=New absolute reports\likeness-reassessment\NAME directory: "
call "%~dp0likeness-observe.cmd" --source "%LOSOURCE%" --out "%LOOUT%" --dry-run
pause
goto menu
:candidatereplay
set "LQSOURCE="
set "LQOUT="
set "LQSPLIT="
set /p "LQSOURCE=Absolute verified reconciliation report directory: "
set /p "LQOUT=New absolute reports\likeness-reassessment\NAME directory: "
set /p "LQSPLIT=Mode: Y=split investigation, R=shadow reformation, A=own-membership and pool assessment, N=replay: "
if /i "%LQSPLIT%"=="Y" goto splitinvestigation
if /i "%LQSPLIT%"=="R" goto reformation
if /i "%LQSPLIT%"=="A" goto reformation
call "%~dp0likeness-candidate-replay.cmd" --source "%LQSOURCE%" --out "%LQOUT%" --dry-run
pause
goto menu
:splitinvestigation
set "LQREUSE="
set "LQEVALUATION="
set /p "LQREUSE=Absolute original frozen connected-candidate report directory: "
set /p "LQEVALUATION=Absolute returned candidate evaluation JSON: "
call "%~dp0likeness-candidate-replay.cmd" --source "%LQSOURCE%" --out "%LQOUT%" --reuse-result "%LQREUSE%" --split-evaluation "%LQEVALUATION%" --dry-run
pause
goto menu
:reformation
set "LQREUSE="
set "LQEVALUATION="
set /p "LQREUSE=Absolute original frozen connected-candidate report directory: "
set /p "LQEVALUATION=Absolute returned candidate evaluation JSON: "
if /i "%LQSPLIT%"=="A" goto membershipassessment
call "%~dp0likeness-candidate-replay.cmd" --source "%LQSOURCE%" --out "%LQOUT%" --reuse-result "%LQREUSE%" --split-evaluation "%LQEVALUATION%" --reform --dry-run
pause
goto menu
:membershipassessment
call "%~dp0likeness-candidate-replay.cmd" --source "%LQSOURCE%" --out "%LQOUT%" --reuse-result "%LQREUSE%" --split-evaluation "%LQEVALUATION%" --reform --assess-membership --dry-run
pause
goto menu
:reconciliation
set "LXSOURCE="
set "LXANSWERS="
set "LXOUT="
set /p "LXSOURCE=Absolute verified fragment-trial report directory: "
set /p "LXANSWERS=Absolute returned fragment answers JSON: "
set /p "LXOUT=New absolute reports\likeness-reassessment\NAME directory: "
call "%~dp0likeness-reconcile-trial.cmd" --source "%LXSOURCE%" --answers "%LXANSWERS%" --out "%LXOUT%" --dry-run
pause
goto menu
:fragmenttrial
set "LFEXPERIMENT="
set "LFCANDIDATE="
set "LFFEEDBACK="
set "LFMODEL="
set "LFOUT="
set /p "LFEXPERIMENT=Absolute verified shadow experiment directory: "
set /p "LFCANDIDATE=Absolute verified realignment candidate report directory: "
set /p "LFFEEDBACK=Absolute returned identity-only answer JSON: "
set /p "LFMODEL=Absolute EXISTING local ViT-B-32 safetensors checkpoint (no download): "
set /p "LFOUT=New absolute reports\likeness-reassessment\NAME directory: "
call "%~dp0likeness-fragment-trial.cmd" --experiment "%LFEXPERIMENT%" --candidate "%LFCANDIDATE%" --feedback "%LFFEEDBACK%" --context-checkpoint "%LFMODEL%" --out "%LFOUT%" --dry-run
pause
goto menu
:backup
set "RETIRECHECK="
set /p "RETIRECHECK=Check a synthetic Recycle Bin receipt? Full path (blank = backup/archive): "
if not "%RETIRECHECK%"=="" (
  call "%~dp0backup-retire.cmd" --check "%RETIRECHECK%"
  pause
  goto menu
)
set "ARCHIVE="
set /p "ARCHIVE=Preview lossless archive of an existing snapshot? Full path (blank = backup/benchmark): "
if not "%ARCHIVE%"=="" (
  set "ARCHIVEROOT="
  set /p "ARCHIVEROOT=Library root for durable large archives (blank = bounded tmp experiment): "
  set "ARCHIVEOUT="
  set /p "ARCHIVEOUT=New absolute output under repo tmp or selected library _backup\_packed: "
  call :archivepreview
  pause
  goto menu
)
set "SNAPSHOT="
set /p "SNAPSHOT=Benchmark an existing snapshot instead? Full snapshot path (blank = normal backup): "
if not "%SNAPSHOT%"=="" (
  call "%~dp0library-backup.cmd" --benchmark "%SNAPSHOT%" --dry-run
  pause
  goto menu
)
set "APPLY="
set "FLAG="
set /p "APPLY=Create the snapshot now? (n = preview only): "
if /i "%APPLY%"=="y" set "FLAG=--apply"
call "%~dp0library-backup.cmd" %FLAG%
pause
goto menu
:archivepreview
if not "%ARCHIVEROOT%"=="" (
  call "%~dp0backup-archive.cmd" "%ARCHIVE%" --library-root "%ARCHIVEROOT%" --out "%ARCHIVEOUT%" --dry-run
  exit /b
)
call "%~dp0backup-archive.cmd" "%ARCHIVE%" --out "%ARCHIVEOUT%" --dry-run
exit /b
