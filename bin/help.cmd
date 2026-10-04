@echo off
echo.
echo  Sovereign Territories command scripts. Run them from a terminal, or double-click menu.cmd.
echo  HERO is a hero name such as Draknara. STAGE is optional: poses, head, scene, hair, motion, armor, clothing.
echo  Add --dry-run as the last argument to any deploy, promote or make script to preview.
echo.
echo  BUILD
echo    prompts.cmd [filters]          regenerate prompts from data/art (all, or gen_prompt.py filters)
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
echo    deploy-dev.cmd HERO [STAGE]    repo to DEV (Soverign Territories)
echo    deploy-uat.cmd HERO [STAGE]    repo to the hero or group UAT workspace
echo    deploy-prod.cmd HERO [STAGE]   repo to the series PROD workspace
echo    promote-uat.cmd HERO [STAGE]   MOVE approved workflows from DEV to UAT
echo    promote-prod.cmd HERO [STAGE]  MOVE approved workflows from UAT to PROD
echo    pull-dev.cmd HERO [STAGE]      bring workflows that only exist in DEV into the repo
echo    deploy-templates.cmd           put the ST stage templates in DEV
echo.
echo  LOOK
echo    status.cmd [filters]           repo against every workspace
echo    workspaces.cmd                 workspaces, routes and what the repo holds
echo.
echo  See workflows\README.md for the model: DEV, UAT, PROD.
echo.
