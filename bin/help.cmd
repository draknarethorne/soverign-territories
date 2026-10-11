@echo off
echo.
echo  Sovereign Territories command scripts. Run them from a terminal, or double-click menu.cmd.
echo  HERO is a hero name such as Draknara. STAGE is optional: poses, head, scene, hair, motion, armor, clothing, video, or "studio" for every studio stage.
echo  A set is deployed to its HOME workspace (see workspaces.cmd). The scripts that change files do it for real; the underlying tool previews unless you give it --apply, so add --dry-run as the last argument to preview a script.
echo.
echo  THE USUAL LOOP
echo    refresh.cmd HERO [STAGE]        prompts, workflows and deploy for one hero (to her home workspace^(s^))
echo    refresh-group.cmd GROUP         the same for a whole set: angel-primes, sovereign-dawn, sovereign-territories, drakn-sisters
echo    refresh-firered.cmd HERO [STAGE]  the loop for FireRed (local test workflows, not in git)
echo    animate.cmd HERO                video prompts, MiniMax workflows, deploy
echo    pull.cmd HERO [STAGE]           keep what you made or edited in ComfyUI (new = curated; edits to curated, zz_Shots, candidates and finals are captured; a final's image goes to assets\art)
echo.
echo  WORKSPACES
echo    setup-workspace.cmd "WS" [--apply]   the whole job for one workspace: deploy its sets, tidy, cleanup, status (preview unless --apply)
echo    status.cmd [filters]            repo against every workspace
echo    workspaces.cmd                  workspaces, homes, what each accepts and what the repo holds
echo    publish.cmd HERO "WS" [STAGE]   a TEMPORARY copy in a workspace that accepts the set (Sovereign Territories takes any set: reels, feeds)
echo    cleanup.cmd "WS" [--apply]      remove what that workspace is not home for (clone leftovers, finished temporary copies)
echo    tidy.cmd "WS"^|all [--apply]     sort loose workflows into folders, remove empty folders
echo.
echo  DEPLOY AND PULL, FINER CONTROL
echo    deploy.cmd HERO [STAGE]         repo to the hero's home workspace(s)
echo    deploy-group.cmd GROUP          repo to a whole set's home workspace
echo    make.cmd HERO [STAGE]           create or refresh that hero's workflows from the prompts (repo only)
echo    update.cmd [filters]            refresh prompt text in every existing repo workflow
echo    fork.cmd WORKFLOW TAG           copy a generated workflow to hand-edit it (curated), and put it in the home workspace
echo    deploy-curated.cmd HERO         copy hand-curated workflows to a workspace that lacks them  ^(= deploy --include curated^)
echo    pull-shots.cmd HERO / deploy-shots.cmd HERO   keep / copy what you saved under zz_Shots  ^(= pull --only shots / deploy --include shots^)
echo    finals.cmd ACTION "WS"          candidates and finals: status, sort ^(files them where their name says; never deletes^), promote, pull, deploy, reclassify ^(repo cleanup^)
echo    deploy-templates.cmd / pull-templates.cmd     the ST stage templates, to and from Sovereign Territories
echo    inputs.cmd [status ^| pull -w WS ^| reset --hero H ^| photos ^| set HERO --photo F ...]  which images each hero's workflows read; pull keeps the default images you chose in ComfyUI in workspaces.json (do it before reset); photos re-points a chosen photo that was renamed
echo    originals.cmd [--dry-run] [--only NAME] [--no-headshots]   the photo library: name originals after their folder, scale to 944x1104, make face headshots, move copies of removed originals to the _org archive, re-point chosen photos  ^(docs\art\original-photos.md^)
echo    likeness.cmd folder ^| clean ^| group ^| sisters ^| pairs ^| alike ^| compare ^| like ^| sort --singles ^| review --out ^| loosen ^| lookalikes ^| names ^| merge ^| retire ^| undo   faces: one-person checks, artists into people, sisters as a family, angel-to-sister pairing, empty Various, look-alike guard, names ^(previews; --apply moves; --sheet F.png^)  ^(docs\art\likeness.md^)
echo    denoise.cmd [--reset]; sync-inputs.cmd; organize-outputs.cmd
echo.
echo  ART DATA
echo    prompts.cmd [filters]           regenerate prompts from data\art (all, or gen_prompt.py filters such as --group G --slug S)
echo    videoprompts.cmd [card.json]    regenerate video prompts from data\animation cards
echo    scaffold-angels.cmd [SLUG^|--alpha]  write the standard card set for the angels (--alpha: the two alpha test heroes); --coverage reports library use
echo    scaffold-sister.cmd SLUG        write a sister's studio kit cards
echo    scaffold-characters.cmd         write the character scenes (angels: Lineup, duty, quiet, domain, celebration; sisters: domain, craft, celebration) from scene-recipes.json
echo    art-refs.cmd where-used^|move^|regroup   find or safely move an art piece and every reference to it
echo    extract-literals.cmd [--apply]  find text pasted into several cards and turn it into pieces (preview unless --apply)
echo    audit.cmd NAME                  one front door for the audits below: identity, negation, library, style, codex, all (the cheap checks validate runs); changes nothing
echo    style-audit.cmd [--prompts]     rank art wording by how illustrated (vs photographic) it reads; changes nothing
echo    library-audit.cmd [--scope S]   find thin library folders that many cards lean on, and pieces no card uses; changes nothing
echo    negation-audit.cmd [--review]   find negations (do not, never, no X) in the positive prompts, which a model reads as the thing named; changes nothing
echo    identity-audit.cmd [--check]    check each angel, sister and bound hero: colours defined and in the Prime prompt, build in the Bare prompt, no bulky wording on female angels
echo    todo.cmd [--print]              write docs\todo.md: where every top-tier card stands (finals and candidates in the repo) and the open work of the active plans; run pull first
echo    codex-drift.cmd [--check]       compare the roster pages in docs\codex\heroes with the cards and identity JSON (the JSON wins); changes nothing
echo.
echo  CHECKS
echo    validate.cmd [--quick^|--full]   schema and link checks + tool tests; --quick adds a short validator self-test (under 2 min), --full all of it (about 6 min)
echo    test.cmd                        the workflow tool tests only (routing, accepts, zz_ guards)
echo    check.cmd                       every commit hook (or the same checks directly when pre-commit is not installed)
echo.
echo  See workflows\README.md for the model: one home workspace per set, temporary copies where a workspace accepts them, zz_ items mastered in the workspace.
echo.
