@echo off
echo.
echo  Sovereign Territories command scripts. Run them from a terminal, or double-click menu.cmd.
echo  HERO is a hero name such as Draknara. STAGE is optional: poses, head, scene, hair, motion, armor, clothing, video, or "studio" for every studio stage.
echo  Add --dry-run as the last argument to any deploy, promote or make script to preview.
echo.
echo  BUILD
echo    prompts.cmd [filters]          regenerate prompts from data/art (all, or gen_prompt.py filters)
echo    videoprompts.cmd [card.json]   regenerate video prompts from data/animation cards
echo    validate.cmd                   schema and link checks plus the validator self-tests
echo    check.cmd                      every pre-commit hook
echo.
echo  WORKFLOWS (repo masters)
echo    make.cmd HERO [STAGE]          create or refresh that hero's workflows from the prompts
echo    update.cmd                     refresh prompt text in every existing repo workflow
echo    inputs.cmd                     show which A-pose image each hero's workflows read
echo.
echo  DEPLOY AND PROMOTE
echo    refresh-dev.cmd HERO [STAGE]   prompts, then make, then deploy to DEV (the usual loop)
echo    refresh-firered.cmd HERO [STAGE] the same loop for FireRed (local test workflows, not in git)
echo    animate.cmd HERO               video prompts, MiniMax workflows, then deploy to DEV
echo    deploy-dev.cmd HERO [STAGE]    repo to DEV (Soverign Territories)
echo    deploy-uat.cmd HERO [STAGE]    repo to the hero or group UAT workspace
echo    deploy-prod.cmd HERO [STAGE]   repo to the series PROD workspace
echo    promote-uat.cmd HERO [STAGE]   MOVE approved workflows from DEV to UAT
echo    promote-prod.cmd HERO [STAGE]  MOVE approved workflows from UAT to PROD
echo    pull-dev.cmd HERO [STAGE]      keep what you made or edited in DEV (new = curated; edits to curated are captured)
echo    fork.cmd WORKFLOW TAG          copy a generated workflow to hand-edit it (curated), and put it in DEV
echo    deploy-curated.cmd HERO        copy hand-curated workflows to a workspace that lacks them
echo    deploy-templates.cmd           put the ST stage templates in DEV
echo.
echo  LOOK
echo    status.cmd [filters]           repo against every workspace
echo    workspaces.cmd                 workspaces, routes and what the repo holds
echo.
echo  See workflows\README.md for the model: DEV, UAT, PROD.
echo.
