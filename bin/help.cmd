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
echo  PHOTO LIBRARY: THE ROUTINE (drop new photos in Various\gallery, then)
echo    library.cmd                     everything; automatically makes a full pre-run snapshot and prefers one updated incoming same-ID photo
echo                                    draft likeness policy refuses before housekeeping; use library-preview.cmd until approved
echo    library-preview.cmd             the same, every step as a preview ^(nothing moves^)
echo    library-check.cmd               read only: is it in step, any duplicates, any photo waiting? Exit 1 when work is waiting
echo    library-backup.cmd [--apply ^| --full ^| --verify SNAPSHOT]  preview, create, or verify a dated snapshot (^--full keeps generated derivatives)
echo    library-backup.cmd --restore SNAPSHOT --destination NEW_DIR [--apply]  preview/materialize exact recovery with regenerated derivatives; never overwrites a live tree
echo    people-gallery.cmd [--dry-run ^| --check ^| --apply] [--root DIR] [--cache FILE] [--out DIR] [--policy FILE]  preview/check local housekeeping; apply backs up, normalizes originals, maintains padded/head/chest and both viewers; NO matching
echo                                    active action undo blocks apply; undo first or explicitly --settle-actions to close undo with full recovery snapshot
echo                                    --preserve-action-undo leaves active-action identity trees untouched and maintains others; held files remain diagnostic, no settlement
echo    people-gallery-review.cmd [--root DIR] [--cache FILE] [--out DIR] [--policy FILE] [--keep SCORE]  local Gallery + Review audit; filters, rankings and staged actions
echo    artists-gallery.cmd [--root DIR] [--cache FILE] [--dry-run ^| --check ^| --apply]  separate Artist overview/photo review; shared small thumbnails in _reports\artists, NO matching or source changes
echo    prepare-images.cmd --root "SANDBOX\Working" --out "Working\_reports\preparation\RUN" [--limit 28] [--dry-run ^| --apply ^| --check]  sidecar original/control/geometry/denoise/tone, larger pages and padded examples; NO source or identity changes
echo                                    --source-folder "Various\gallery" --limit 0 compares ALL direct incoming images; face gate, crop/crop/LaMa/frame trace and masks BEFORE filter comparisons; NO live moves
echo                                    v16 can recommend LaMa cleanup; --apply may download pinned CPU models once. --dry-run inventories only; --check verifies existing evidence.
echo                                    Artists\ARTIST\gallery uses the SAME preparation and padding, retaining artist-only source scope; copies in Various cannot imply artist ownership
echo                                    existing RUN --quarantine-junk previews eligible loose-intake moves; --apply verifies a scoped backup and moves to nested _junk, never deletes or matches
echo                                    existing RUN --undo-junk previews exact recovery; --apply restores verified bytes; --check verifies completed disposition too. Ordinary library runs do NOT retry Junk
echo    sandbox-rebase.cmd "SANDBOX\Working" "RUN-DIR" [--dry-run ^| --replan ^| --apply ^| --check ^| --undo]  clean cast-only rebuild; fresh cache, flattened candidates, verified backup and rollback copies
echo    likeness-actions.cmd validate FILE.json  check staged actions against current photo IDs, hashes, folders and catalogue
echo    likeness-actions.cmd preview FILE.json   show intended destinations; never moves photos or edits metadata
echo    likeness-actions.cmd apply FILE.json --apply  verified backup, then apply staged moves and metadata decisions
echo    likeness-actions.cmd undo [BATCH_ID] --apply  verified backup, then undo the newest action batch
echo    likeness.cmd crops              one web page with every cropped photo, the uncropped original beside it ^(likeness.cmd crop --undo --apply reverses the last batch^)
echo    likeness.cmd                    general roots ONLY: Angels, Sisters, Models, Prospects, Potentials, Various; Artists are excluded
echo    likeness-artists.cmd --root "SANDBOX\Working" --dry-run group --singles  shared engine, artist-only preview; --check scans without cache/history writes
echo                                    artist scan, junk, crop, group, folder inspection, diagnostics and index reuse the same code; artist state lives in Working\_likeness\artists
echo                                    general state lives in Working\_likeness\general; default post-move originals stays scoped and does not retarget selected workflows
echo    duplicates.cmd [--apply]        the same picture kept twice anywhere in the library ^(any folder, any name^)
echo    originals.cmd --check           are the scaled copies and headshots in step with every gallery?
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
echo    compare-primes.cmd [HERO ...]   Prime renders side by side, Qwen and FireRed, normal and configured alternate flows, with a face score against the photo each started from  ^(docs\art\prime-flows.md^)
echo    originals.cmd [--dry-run] [--only NAME] [--no-headshots] [--archive-old]   the photo library: name originals after their folder, scale to 944x1104 ^(reel screenshots cut to the picture^), make face headshots, move old copies to _archive, re-point chosen photos  ^(docs\art\original-photos.md^)
echo    likeness.cmd diagnostics --out DIR [--policy FILE]  one-pass calibration + active-person folder checks; writes CSVs and a Markdown report ^(read only; explicit --root and --cache for sandbox^)
echo    likeness.cmd family-preview [--policy FILE] [--out DIR]  direct reference scores, surname reuse and naming collisions ^(JSON + HTML; suggestions only, no library changes^)
echo    likeness.cmd sandbox-reset       preview restoring only Models, Prospects, Potentials from the verified sandbox Source snapshot; --apply to restore ^(requires --root ...\Working^)
echo    likeness.cmd audit-core ^| calibrate ^| folder ^| clean ^| sisters ^| pairs ^| alike ^| compare ^| like ^| sort --singles ^| reconcile ^| singles ^| junk ^| review --out ^| loosen ^| lookalikes ^| names ^| index ^| profile ^| who ^| merge ^| retire ^| retire-empty ^| archive-list ^| promote ^| rename ^| undo   general faces: read-only core/outlier audit, combined Review + Various preview, one-person checks, sisters as a family, angel-to-sister pairing, empty Various, unusable photos to _junk, look-alike guard, names, who-could-play-what table ^(previews; --apply moves; --sheet F.png^)  ^(docs\art\likeness.md^)
echo    likeness.cmd policy                 show the validated draft shared likeness thresholds; rebaseline remains gated pending review
echo    likeness.cmd reconcile [--out FILE.json] [--apply]  incoming, Review, outliers, identity merges and category moves; verified backup, journal and read-only final-core check; production requires approved policy
echo                                    also previews evidence-based identity/photo protection, original-name provenance and virtual family naming; manual unprotect persists until explicitly protected again
echo    likeness.cmd rebaseline              read-only category, routing, and cast-similarity preview; sandbox category moves require --apply-categories and a verified Working backup
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
echo    library-audit.cmd [--scope S]   find thin ART piece folders that many cards lean on, and pieces no card uses ^(not the photo library: that is library.cmd^); changes nothing
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
