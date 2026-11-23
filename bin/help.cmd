@echo off
echo.
echo  Sovereign Territories command scripts. Run them from a terminal, or double-click menu.cmd.
echo    check.cmd             routine hygiene and data validity; no unit/mutation tests or push rerun
echo    check.cmd --deep      explicit routine checks plus all manual unit/mutation hooks
echo    validate.cmd --changed HEAD --dry-run  preview tests for tracked and non-ignored untracked work; --check executes
echo    validate.cmd --scope workflow --check  explicit subsystem: workflow, intake, library, data, quality, full
echo    validate.cmd --full   explicit full offline regressions and isolated mutations; routine CI uses fast guards, full only on dispatch
echo    validate.cmd --quick  isolated mutation smoke suite ONLY; all test launchers use ignored repo tmp
echo    validate.cmd --isolated [--quick]  mutation validation on ONE disposable data/tools copy; private recovery journal, live repository read-only
echo  HERO is a hero name such as Draknara. STAGE is optional: poses, head, scene, hair, motion, armor, clothing, video, or "studio" for every studio stage.
echo  A set is deployed to its HOME workspace (see workspaces.cmd). The scripts that change files do it for real; the underlying tool previews unless you give it --apply, so add --dry-run as the last argument to preview a script.
echo  Exception: refresh, refresh-group, refresh-firered and animate still regenerate prompts with --dry-run; only their workflow/deploy steps preview.
echo.
echo  THE USUAL LOOP
echo    refresh.cmd HERO [STAGE]        prompts, workflows and deploy for one hero (to her home workspace^(s^))
echo    refresh-group.cmd GROUP         the same for a whole set: angel-primes, sovereign-dawn, sovereign-territories, drakn-sisters
echo    refresh-firered.cmd HERO [STAGE]  the loop for FireRed (local test workflows, not in git)
echo    animate.cmd HERO                video prompts, MiniMax workflows, deploy
echo    pull.cmd HERO [STAGE]           keep what you made or edited in ComfyUI (new = curated; edits to curated, zz_Shots, candidates and finals are captured; a final's image goes to assets\art)
echo.
echo  PHOTO LIBRARY: THE ROUTINE (drop new photos in Various\gallery, then)
echo    library.cmd [--photo-id ID ...] [--profile lean^|full^|fast] [--apply]  selected normal pipeline includes frozen audit/family metadata and Gallery/Overview/Review publication; preview is default
echo                                    bounded three-profile proof passed; full-current-library, fresh-baseline and human identity/crop acceptance remain gated
echo                                    FULL/LEAN use the same offline native recipe and matcher; FULL retains richer products; FAST defers editing/944 and never certifies raw pixels clean
echo    library.cmd --update-photo-id ID --run-id RUN [--apply]  explicit recoverable same-photo replacement; retains existing owner and name
echo    various-cleanup.cmd --root RAW_LIBRARY --plan PLAN --sha256 HASH [--dry-run ^| --check ^| --apply --backup-confirmed]
echo                                    replay a reviewed SIMPLE raw-baseline cleanup: remove exact Various copies, move intentional edits into the original path, archive older originals
echo                                    dry-run before applying; does not touch sealed Source or a catalogue-managed library
echo    various-cleanup.cmd --root LIBRARY --scan-exact  print hash-bound discard plan for same-ID, same-byte arrivals before intake or rebase
echo                                    exact-only plans also work on catalogue-managed libraries and never archive the discarded files
echo    library.cmd --recover --run-id RUN [--apply]  preview/apply exact partial-publication recovery from its journal
echo    library-preview.cmd [--photo-id ID ...] [--profile P]  preview pending/selected intake; no library writes
echo    library-check.cmd --photo-id ID [--photo-id ID ...]  read-only selected intake check; --run-id ID verifies an applied receipt
echo    library.cmd --undo --run-id ID [--apply]  preview or execute exact backed-up membership recovery
echo    rebase-manifest.cmd --run-id ID [--dry-run ^| --apply ^| --check]  Production originals + verified unique Sandbox arrivals; review-only proposal, never resets/publishes
echo    sandbox-baseline.cmd --root ABS_SANDBOX_WORKING [--dry-run ^| --run-id ID --apply ^| --run-id ID --check]
echo                                    refresh verified Production Source then reset disposable Working with NO old history/carry-forward; preview first, Production read-only
echo                                    --frozen-source-sha256 HASH --run-id ID replays existing sealed Source, preserves old Working, and never refreshes Source
echo    universe-sandbox.cmd --name ID --seed CATEGORY/Name [--include CATEGORY/Name ...] [--mode blank ^| named] [--dry-run ^| --apply ^| --check]
echo                                    copies a verified identity universe (pre-rebase originals, sealed LEAN preparation, cache) into a NEW
echo                                    B:\Sovereign Territories Universes\ID\Sovereign Territories Sandbox\Working; main Sandbox and Production read-only
echo                                    --expand-band yellow^|green^|orange (default yellow) --hop2-band (default green) --hops 0^|1^|2 (default 1) --max-photos N
echo    universe-sandbox.cmd --name ID --mode empty [--source-folder DIR ^| --source-various DIR] [--dry-run ^| --apply ^| --check]
echo                                    empty ready-to-intake universe; DIR top-level images copied read-only into Various\gallery, SHA-256 verified
echo                                    --source-various: DIR\gallery to Various\gallery, each DIR\Name to Various\Name\gallery; then likeness.py --root W seed --apply
echo                                    then normal-rebase.cmd --root UNIVERSE_WORKING --cache UNIVERSE_WORKING\_likeness\general\cache.json --profile lean
echo    machine-tuning.cmd show ^| set --preparation-workers N [--threads-per-worker N] [--worker-memory-gib G] --evidence TEXT [--apply] ^| clear [--apply]
echo                                    this machine's parallel workers: command line, ST_INTAKE_WORKERS, git-ignored data\config\machine-tuning.local.json,
echo                                    else capacity from the shared baseline data\config\machine-tuning.json; never changes another machine
echo    normal-rebase.cmd --root ABS_SANDBOX_WORKING --profile lean --run-id ID [--dry-run ^| --apply ^| --check]
echo                                    SIMPLE whole-library composition, distinct from incremental library.cmd; preview can prepare/measure all selected inputs, without publishing assignments
echo                                    --preparation-workers 1^|2^|3 opts into that many FULL/LEAN preparation workers; default 1, repeat on apply; validate per machine first
echo                                    --repeat verifies applied receipt; --recover previews exact recovery, --recover-apply restores; draft apply requires --sandbox-apply-draft in Sandbox only
echo                                    --measure-missing is post-apply local-model report-only; general-domain cache only, no fallback/cache/source/alignment writes or downloads
echo                                    recoverable image errors produce an incomplete receipt and nonzero exit; core qualification is skipped
echo                                    stable IDs disclose original + existing standard_name normalization; verified retained versions preserve lineage and are not extra voters
echo                                    --check rehashes source bytes and report bindings; actual reference/candidate IDs require human review
echo                                    --lock-cast-admission locks Sisters/Angels receiving only; repeat on preview/apply/check; cast rivals stay visible
echo                                    Sandbox release replay: supply --release-receipt FILE --release-audit FILE --release-review DIR and chronological --release-run ID for every release on preview AND apply
echo                                    verified released photos enter matching before identity formation; apply remains bound to the exact preview and lineage
echo                                    --reconsider-holds re-evaluates prior Review holds in Sandbox; repeat on preview/apply, accepted matches, history and safeguards remain
echo                                    --fresh-source-release selects red/orange/unscored initial Gallery members before core formation and reconsiders holds; repeat on preview/apply; Sandbox only, not with release replay
echo                                    emptied identity folders retire AUTOMATICALLY inside the apply transaction ^(same in library.cmd intake^): preview lists them, apply moves them intact to _retired
echo                                    after the photos move; --check verifies them, --recover-apply restores them; an emptied Sisters/Angels folder stops preview/apply with a report
echo    retire-empty.cmd --root ABS_SANDBOX_WORKING --receipt APPLIED-SIMPLE-RECEIPT --run-id ID [--dry-run ^| --apply ^| --check ^| --recover ^| --recover-apply] [--folder CATEGORY/Name ...]
echo                                    manual catch-up for folders emptied by an older rebase; recoverable, journalled; preview saves a new plan+digest, apply needs that exact unstale plan
echo                                    an emptied Sisters/Angels folder stops with a report ^(never retired here^); existing plan/journal never overwritten; pruning _retired stays manual
echo    red-release-diagnostic.cmd --root WORKING --receipt RECEIPT --report SNAPSHOT.html --cache CACHE [--check] [--inspect-consumers] [--simulate-routes [--simulate-core-refresh [--simulate-destination-scores]]]
echo                                    read-only diagnostic; consumer scan includes discovered local installs; hypothetical routing never resolves gaps or applies a release
echo                                    --workflow-configuration FILE must match the report-bound selection configuration; saved-run centering retains its original configuration
echo    sandbox-red-release.cmd --root WORKING --run-id ID --receipt RECEIPT --report SNAPSHOT.html --cache CACHE [--dry-run ^| --apply]
echo                                    Sandbox-only experiment; records moves and proposed replacements but never modifies shared workflows or Production
echo    sandbox-red-release.cmd --root WORKING --run-id ID --current-review DIR --cache CACHE --release-band red --release-band orange --dry-run
echo                                    read-only current Review census; verifies saved policy, sources and scores; does not route or release photos
echo    sandbox-red-release.cmd --root WORKING --run-id ID --current-review DIR --cache CACHE --release-band red --release-band orange --receipt RECEIPT --report AUDIT.html --prior-run ID --dry-run
echo                                    current Sandbox routed preview; --apply additionally requires --expected-plan-sha256 from this exact preview
echo                                    --include-unscored also selects unavailable own-core scores and reports independently scored rivals
echo                                    repeat --continuation-run ID in chronological order for later journalled releases
echo                                    does not update workflows; exposes selected photos, empty former cores and unresolved consumer coverage
echo    sandbox-red-release.cmd --root WORKING --run-id ID [--check ^| --recover ^| --recover-apply]  verify or recover its journalled Sandbox experiment
echo    library-legacy.cmd              former whole-library originals/duplicates/crop/reconcile routine; not the normal default
echo    likeness-experiments.cmd legacy-reconcile [--root WORKING --cache FILE --out FILE]
echo                                    explicit legacy merge/category/protection experiment; preview by default; no normal-intake import
echo    likeness-experiments.cmd directed-rebase --root WORKING --run RUN --baseline working --regroup --directed --directed-recipe RECIPE
echo                                    experimental composition only; directed rebase requires its explicit recipe
echo    likeness.cmd reconcile           explicit legacy compatibility alias for likeness-experiments legacy-reconcile
echo    library-backup.cmd [--apply ^| --full ^| --verify SNAPSHOT]  preview, create, or verify a dated snapshot (^--full keeps generated derivatives)
echo    library-backup.cmd --restore SNAPSHOT --destination NEW_DIR [--apply]  preview/materialize exact recovery with regenerated derivatives; never overwrites a live tree
echo    library-backup.cmd --benchmark SNAPSHOT [--limit 24] [--max-mib 32] [--out REPO_TMP_DIR] [--dry-run ^| --apply ^| --check]  bounded directory/ZIP64 stored/deflate1 measurements; never changes library or backup defaults
echo    backup-archive.cmd SNAPSHOT --out "ABS_REPO_TMP_NEW" [--format hybrid ^| stored] [--dry-run ^| --apply]  bounded lossless cold-backup packing with exact-content reuse; no source deletion
echo    backup-archive.cmd --check BUNDLE   verify independently; --restore BUNDLE --destination ABS_REPO_TMP_NEW [--apply] materializes the original snapshot for ordinary library-backup restore
echo                                    --library-root ABS_LIBRARY opts into durable _backup\_packed bundles and 100k-file/64-GiB bounds; original manifests remain exact
echo                                    --prune-source SNAPSHOT --library-root ROOT --bundle BUNDLE --materialized SNAPSHOT_PROOF --recovered ORDINARY_PROOF [--dry-run ^| --apply] explicitly deletes ONLY verified older backup copies; newest stays
echo    backup-retire.cmd --check RECEIPT  synthetic tmp\retire-proof Recycle Bin proof only; recover --receipt RECEIPT [--dry-run ^| --apply]; no production deletion or purge
echo    people-gallery.cmd [--dry-run ^| --check ^| --apply] [--root DIR] [--cache FILE] [--out DIR] [--policy FILE]  preview/check local housekeeping; apply backs up, normalizes originals, maintains padded/head/chest and both viewers; NO matching
echo                                    --reports-only previews/checks/refreshes Overview, Review and history from existing photos/derivatives; no renames, derivative maintenance, pruning or backups
echo                                    active action undo blocks apply; undo first or explicitly --settle-actions to close undo with full recovery snapshot
echo                                    --preserve-action-undo leaves active-action identity trees untouched and maintains others; held files remain diagnostic, no settlement
echo    people-gallery-review.cmd [--root DIR] [--cache FILE] [--out DIR] [--policy FILE] [--keep SCORE]  local Gallery + Review audit; filters, rankings and staged actions
echo                                    --history-only [--dry-run ^| --check ^| --apply] verifies/repairs only intake history; previews by default, no photo-viewer rebuild
echo    artists-gallery.cmd [--root DIR] [--cache FILE] [--dry-run ^| --check ^| --apply]  separate Artist overview/photo review; shared small thumbnails in _reports\artists, NO matching or source changes
echo    prepare-images.cmd --root "SANDBOX\Working" --out "Working\_reports\preparation\RUN" [--limit 28] [--dry-run ^| --apply ^| --check]  sidecar original/control/geometry/denoise/tone, larger pages and padded examples; NO source or identity changes
echo                                    new v23 runs default to LEAN: exact-byte role reuse and recommended padding only; --storage-mode full keeps richer diagnostics; saved/interrupted modes persist. NOT FAST
echo    originals.cmd --root DIR --only Various [--apply ^| --check]  independent framing maintenance; does not assign identities
echo    originals.cmd --root DIR --photo-id ID --no-repoint [--dry-run ^| --apply ^| --check]  selected framing only; no native rename/cleanup, unrelated pruning or reassignment
echo    preparation-history.cmd --root "SANDBOX\Working" --report "REPORT" --out "Working\_reports\preparation-history\NEW" --mode compact [--dry-run ^| --apply ^| --check]
echo                                    compact downsizes diagnostics; collage makes labelled sheets; both retain exact originals/selected native/padded bytes once per photo. Independent new bundle, NO source PRUNE
echo    storage-experiment.cmd --root "SOURCE\Working" --out "REPO\tmp\NEW" [--limit 24] [--dry-run ^| --apply ^| --check]  mixed 20-30 photo copied FULL/LEAN rebase, matching, publication, backup and restore; source stays read-only
echo    rebase-replay.cmd [--dry-run ^| --apply ^| --check]  complete same-input applied-baseline replay into isolated tmp\r4; verified three-worker/four-thread runtime; strict output/route gates before installation, backup and recovery
echo                                    --source-folder "Various\gallery" --limit 0 compares ALL direct incoming images; v22 overlay-first, guarded crop/erase/residual/reconstruct/compose BEFORE filters; NO live moves
echo                                    no detected proposal skips person segmentation and composition-only suggestions, NOT a clean-pixel guarantee; denoise/tone comparisons remain
echo                                    confirmed-pattern reconstruction is synthetic; final recommended pixels feed sandbox matching. --apply may download pinned CPU models once; --check verifies evidence.
echo                                    Artists\ARTIST\gallery uses the SAME preparation and padding, retaining artist-only source scope; copies in Various cannot imply artist ownership
echo                                    existing RUN --quarantine-junk previews eligible loose-intake moves; --apply verifies a scoped backup and moves to nested _junk, never deletes or matches
echo                                    existing RUN --undo-junk previews exact recovery; --apply restores verified bytes; --check verifies completed disposition too. Ordinary library runs do NOT retry Junk
echo    eraser-compare.cmd --report "Working\_reports\preparation\RUN" --sources LIST.json --out "Working\_reports\eraser-compare\NEW" [--dry-run ^| --apply ^| --check]
echo                                    same-mask A/B: saved LaMa vs OpenCV Telea/NS r3 on the identical pre-eraser input; 1..64 listed rows, explicit skips
echo                                    --sequence previews/runs an EXPERIMENTAL erase-first sequence against saved v16; apply uses pinned CPU models, no default recipe change
echo                                    --sequence --head-overlay extends guarded cleanup with synthetic pill/head reconstruction FOR REVIEW; no assignment or automatic core promotion
echo                                    --sequence --enhancements compares native denoise/tone/sharpen on that review recommendation; diagnostics only, no automatic quality ranking
echo    overlay-review.cmd --report DIR --sources LIST.json --out "Working\_reports\eraser-compare\NEW" [--dry-run ^| --apply ^| --check]
echo                                    unconfirmed logo/pill reference proposals anywhere in the image; no source repainting or automatic confirmation
echo                                    comparison only: no selection, assignment, model load or source change; --check verifies every hash read-only
echo    rebase-flow.cmd --root "SANDBOX\Working" --run NAME [--profile fast ^| lean ^| full] [--dry-run ^| --apply ^| --check] [--recovery-mode full ^| disposable] [--workers N] [--from STEP] [--until STEP] [--with-previews]
echo                                    --baseline working skips destructive reset; --regroup enables the maintained appearance lifecycle and stage viewers
echo                                    --directed --directed-recipe NAME explicitly selects the experimental directed Sandbox path; saved preview/resume/check must use the same recipe
echo                                    the whole fresh rebase in order: full reset, originals + check, backup of the fresh baseline, intake, matching plan, install, checks
echo                                    explicit disposable sandbox/LEAN skips originals + baseline backup and creates NO transaction rollback; reset-only recovery, reports retained
echo                                    full recovery is the default, with backup and exact undo; use the SAME recovery mode on resume/check
echo                                    FAST skips pre-intake originals/check, image editing and installed 944x1104 generation; backup remains with full recovery. All profiles share matching/publication/checks
echo                                    reset preview, intake inventory and the separate intake check are skipped unless --with-previews (the apply steps repeat their guards)
echo                                    live progress: per-step start/finish, phase timings, photo count + ETA, space after each step; resumes at the first unfinished step
echo                                    --verbose streams EVERY child line; --heartbeat N sets progress seconds; full per-step logs are always retained
echo                                    timing references: Nov 5 LEAN for measured disposable steps, Nov 3 otherwise; NOT a new-code forecast; --until bounds remaining work
echo                                    process-flow recap and per-step logs: tmp\session-logs\rebase-flow\NAME\flow.md; --check prints it read-only
echo                                    --reuse-run ORIGINAL --recovery-mode disposable starts at matching from verified saved LEAN intake; skips reset/intake and keeps ORIGINAL unchanged
echo    lean-continue.cmd --root "SANDBOX\Working" --source-run ORIGINAL --run NEW [--dry-run ^| --apply ^| --check ^| --install]
echo                                    --dry-run is inventory only; --apply builds a SEPARATE matching preview with original prepared pixels and measured faces; no intake or install
echo                                    --regroup --directed --directed-recipe NAME selects the SAME experimental lifecycle; --review-source ABS_DIR passes direct constraints; choices bind resumes/checks
echo                                    --dominant-provisional explicitly permits existing dominant-face measurements ONLY for non-reference provisional intake; --undone-quality-run ABS_RUN verifies exact completed quality undo before original-input reuse
echo                                    --capture-regroup-call on --apply --regroup --directed writes exact input/output evidence and name transcript beside run.json; repeat on --check/--install
echo                                    --check verifies saved inputs/preview/publication without writes; --install publishes reviewed preview with NO backup or rollback
echo                                    decisions bind by photo ID and content; generated identities/automatic locks are not seeds; missing measurements or ambiguous manual decisions refuse
echo    likeness-shadow.cmd --run "ABSOLUTE-RUN-DIR" --out "ABSOLUTE-REPO-TMP-DIR" [--dry-run ^| --apply ^| --check] [--compare-order]
echo                                    receipt/cache-only Vale + named-outlier scope; full original candidate competition; --apply writes experiment JSON only, NEVER installs
echo                                    --dry-run verifies scope and original cast-score parity; --compare-order tests repeat/reverse stability; --check verifies saved evidence read-only
echo                                    first contract: applied core-seed baseline with empty manual seed and all-workflow reset; --max-photos refuses scope overflow, never truncates
echo                                    separate global limits: --max-candidates 2500 and --max-json-mib 128 by default; raise only explicitly, never shrink competition silently
echo    likeness-review-packet.cmd --experiment "ABSOLUTE-SHADOW-DIR" --out "ABSOLUTE-REPO-REPORTS\likeness-reassessment\NAME" [--dry-run ^| --apply ^| --check]
echo                                    visual final-baseline placements, own/rival examples and optional individual-pair label export/import; NEVER moves photos or changes rules
echo                                    preview checks saved final-score arithmetic and displayed source hashes; apply writes bounded report thumbnails/HTML only; check is read-only
echo                                    all seed identities plus --neighbours 12 distinct competitors by default; explicit 100-case / 700-photo report cap
echo    likeness-character-packet.cmd --experiment "ABS-SHADOW" --review-packet "ABS-PAIR-REPORT" --feedback "ABS-EXPORT.json" --clarifications "ABS-OVERRIDES.json" --out "ABS-REPORT" [--dry-run ^| --apply ^| --check]
echo                                    validates completed pair labels and separate chat overrides, then builds Angelica plus five contrasting cast shortlists; NEVER changes library
echo                                    apply writes effective-labels.json and full-photo/face character review; autosave plus export/import; preview/check read-only
echo                                    --check --answers "ABS-CHARACTER-EXPORT.json" validates character decisions without installing; no fixed reference-photo quota
echo    likeness-reference-trial.cmd --experiment "ABS-SHADOW" --character-packet "ABS-CHARACTER-REPORT" --answers "ABS-CHARACTER-EXPORT.json" --out "ABS-REPORT" [--compare-order] [--dry-run ^| --apply ^| --check]
echo                                    full saved-population frozen-reference comparison and existing membership-policy probes; self excluded even across folders; no intake or library mutation
echo                                    apply writes experimental reference-seed.json, result.json, member-outcomes.json and browsable proposals/holds; no auto-growth, new thresholds, models or installation
echo                                    --max-photos 4000 refuses population overflow; --compare-order requires identical reverse-order result; check/repeated apply verify unchanged evidence
echo                                    --realign additionally rebuilds ALL provisional reference sets, general member candidates, face-view hypotheses and separate lookalike links
echo                                    realignment.html is the whole-library landscape; realignment.json + evaluation.json bind proposals and label-blinded diagnostics; NO locked Review, physical moves or installation
echo    likeness-fragment-trial.cmd --experiment "ABS-SHADOW" --candidate "ABS-REALIGNMENT-REPORT" --feedback "ABS-24-ANSWERS.json" --context-checkpoint "ABS-LOCAL-ViT-B-32.safetensors" --out "ABS-REPORT" [--dry-run ^| --apply ^| --check]
echo                                    full-population coherent-subgroup evidence; 30-40 distinct-photo review separates current/target/both/neither and exact reference exceptions; NEVER merges or installs
echo                                    preview checks evidence/sources but no context inference; apply uses ONLY local cached CLIP on below-face context, not identity; NO downloads or accepted fusion threshold
echo                                    --check --answers "ABS-FRAGMENT-EXPORT.json" validates new review labels; repeated apply verifies receipts; --max-photos 40 is a display/measurement budget, not scoring truncation
echo    likeness-reconcile-trial.cmd --source "ABS-FRAGMENT-REPORT" --answers "ABS-FRAGMENT-ANSWERS.json" --out "ABS-REPORT" [--dry-run ^| --apply ^| --check]
echo                                    preview binds direct pairs and proposes reference-use repair; apply compares label-control/repair/association/combined across all saved photos; no model, merge or installation
echo                                    repeat apply checks immutable receipt; exact conflicting labels stay uncertain, associations never certify unseen members; no accepted automatic routing
echo    likeness-disposition-trial.cmd --source "ABS-RECONCILIATION-REPORT" --out "ABS-REPORT" [--dry-run ^| --apply ^| --check]
echo                                    derives direct-member appearance/separate-lookalike/unresolved handoffs; no rescoring, model calls, family types, folder unions or installation
echo    likeness-candidate-replay.cmd --source "ABS-RECONCILIATION-REPORT" --out "ABS-REPORT" [--dry-run ^| --apply ^| --check]
echo                                    connects label-blind original/repaired subgroup scoring to existing membership policy; full saved population, new 30-40-photo visual comparisons
echo                                    apply runs scoring/reverse checks plus existing local context only; no downloads, installed moves, full intake or accepted accuracy claim
echo                                    repeat/check verify receipts without rescoring; --check --answers "ABS-FRAGMENT-EXPORT.json" validates returned feedback
echo                                    --reuse-result "ABS-FROZEN-CANDIDATE" republishes verified results after publisher-only changes; analysis/helper changes refuse reuse
echo                                    --prior-answers "ABS-FRAGMENT-EXPORT.json" restores exact image labels in reused review; action agreement/reasons start separate and unevaluated
echo                                    --check --evaluation "ABS-CANDIDATE-EVALUATION.json" validates packet/result-bound action judgments plus image labels
echo                                    --split-evaluation "ABS-CANDIDATE-EVALUATION.json" --reuse-result "ABS-FROZEN-CANDIDATE" investigates supported group pairs and every member; bounded photos, no merge or model
echo                                    split preview/apply/check uses the same arguments; frozen group centroids, exact cross-pair distributions, member support/holds and saved routing history stay separate
echo                                    --reform --reuse-result "ABS-FROZEN-CANDIDATE" constructs actual cross-folder person/face-view/residual state; optional --split-evaluation binds latest safety labels
echo                                    reformation apply publishes before/after viewer with frozen support, full rivals, bounded reference withdrawals and reverse checks; no physical moves or runtime activation
echo                                    --reform-view "ABS-REFORMATION-REPORT" with --reform republishes unchanged verified state after wording-only changes; same source/reuse/evaluation arguments, no scoring
echo                                    --assess-membership with --reform assesses own identity and all rivals, withdraws weak reference influence and regroups non-core/released photos in a shadow pool; no installed moves or named singleton people
echo                                    bounded reference continuation freezes discovery/rivals, withdraws invalid references and reassesses dependent members; inline ledger images plus filename links
echo    likeness-observe.cmd --setup [--dry-run ^| --apply]  explicit pinned SmolVLM-500M Apache-2.0 download and isolated optional CPU runtime; ordinary library dependencies unchanged
echo    likeness-observe.cmd --source "ABS-ASSESSED-REPORT" --out "ABS-NEW-REPORT" [--dry-run ^| --apply ^| --check]  up to six below-face crops, two invocation orders, local-only observations; NO identity labels or placement changes
echo    likeness-diagnostics.cmd --source "ABS-ASSESSED-REPORT" --out "ABS-NEW-REPORT" [--dry-run ^| --apply ^| --check]  same-evidence category/core diagnostics plus bounded existing-CLIP crop/cache ablation; NO moves or threshold activation
echo    likeness-entrance-trial.cmd --source "ABS-ASSESSED-REPORT" --out "ABS-NEW-REPORT" [--dry-run ^| --apply ^| --check]  eight ordered entrance/core/retention ranges with separate protection and staged frozen-core growth; NO installed policy change, moves, models or intake
echo                                    --coalesce adds two paired mutual-reference-view union variants; every photo still requires individual admission; existing names and separate cast slots preserved
echo                                    --directed compares the current ordered-middle control with four historical plus three corrective directed recipes; separated core/retention/reference/release evidence; writes a non-installable report only
echo                                    --reuse-result "ABS-VERIFIED-ENTRANCE-REPORT" republishes byte-identical scored evidence after publisher-only changes; no rescoring, changed analysis refuses reuse
echo    likeness-hypothesis-trial.cmd --source "ABS-ASSESSED-REPORT" --baseline "ABS-VERIFIED-COALESCED-REPORT" --out "ABS-NEW-REPORT" [--dry-run ^| --apply ^| --check]  reuse middle/coalesced controls; reconcile fully witnessed sibling views, show exceptions and retain all outside rivals; NO installed changes or intake
echo    likeness-view-associations.cmd --source "ABS-ASSESSED-REPORT" --baseline "ABS-VERIFIED-HYPOTHESIS-REPORT" --out "ABS-NEW-REPORT" [--dry-run ^| --apply ^| --check]  per-photo non-core association state for smaller views; tentative is NOT assigned or core; unchanged full rivals, no installed changes or intake
echo    sandbox-rebase.cmd "SANDBOX\Working" "RUN-DIR" --dry-run  inventory ALL immutable inputs; no models, reports or matching
echo                                    --profile fast^|lean^|full: FAST keeps original pixels, defers editing/944x1104, uses original-backed viewers; LEAN/FULL preserve standard preparation. No implicit recovery change
echo                                    --baseline working freezes current galleries plus Various for a fresh Production-like rehearsal; historical Source stays untouched
echo                                    --regroup --cast-seeds core enables member-first identity/appearance lifecycle and maintained stage viewers in every profile
echo                                    --dry-run --core-selection-preview separates originals from derivatives; JSON is complete, HTML filters/pages 24 original-backed cast cards and bounds diagnostics
echo                                    Various stays incoming/excluded; metadata tiers are not measured eligibility or trusted cores; no face analysis, intake or matching
echo                                    --include-current-various adds current Working\Various inputs via a hash-bound run-local recovery overlay
echo                                    --intake-only --apply prepares all images and stops for review; --check verifies without writes
echo                                    --recovery-mode disposable binds sandbox/LEAN reset-only recovery to intake/matching; full retains backup/undo
echo                                    --workers N sets parallel intake processes ^(default: up to 3 by free memory; ST_INTAKE_WORKERS overrides^); matching stays single-process
echo                                    new runs default to LEAN installed original/selected native reuse, retaining differing originals; omitted resumes the recorded mode; --storage-mode full keeps richer diagnostics
echo                                    same command with no flags prepares/resumes then previews fresh-cache matching; --apply installs only a saved preview
echo                                    originals + all kept variants follow assigned photos; --cast-seeds all retains cast membership ^(default^); Artists prepared separately; --undo restores exact pre-run bytes
echo                                    --cast-seeds core retains protected/core/workflow-selected cast photos and previews non-core release with existing thresholds; inspect moves before apply
echo                                    --replan reuses only this run's prepared measurements, including a failed matching preview with verified intake; never installs
echo                                    --resume-install --check verifies completed unpublished staging; --resume-install --apply reuses it without recopying or rewriting outputs
echo                                    --preserve-legacy-derivatives explicitly journals unowned cast collisions byte-for-byte for undo; edited owned derivatives still refuse
echo                                    no matcher-only legacy preview can be installed
echo    rebase-recap.cmd "RUN-DIR" [--dry-run ^| --check] [--out FILE] [--expectations FILE]  per-run HTML of every move, rename, Review hold, cast gain/loss, new identity, other-run differences
echo    rebase-recap.cmd "SIMPLE-RECEIPT.json" [--dry-run ^| --apply ^| --check] [--compare OTHER.json] [--bind-red-natives]  saved-run audit; optionally hash and bind red/native core evidence; no scoring or membership changes
echo    movement-history.cmd --root WORKING --receipt RECEIPT --audit AUDIT.html --current-review DIR --report-id ID --release FIRST [--release NEXT ...] [--corrected-receipt RECEIPT] [--expected-cohort COUNT] [--dry-run ^| --apply ^| --check]  ordered Sandbox history; report only
echo                                    optional --retirement-journal WORKING_RELATIVE --retirement-digest PREVIEW_SHA256 verifies a bound retirement after the corrected rebase; fixture-tested, not installed-verified
echo                                    --inspect-workflow-selections binds current base/flow configuration only, not live workspace consumers; repeat flag on --check
echo                                    --workflow-configuration FILE inspects an alternate configuration with that flag; this does not isolate or modify workflows
echo                                    automatic after every sandbox-rebase preview/replan/apply/check/undo; Working\_reports\library\rebase-recap\RUN.html + index.html
echo                                    "Looks like" picks and expected placements: SANDBOX\rebase-expectations.json beside Working ^(kept by resets^), scored on every run
echo    storage-retention.cmd --root "SANDBOX\Working" preview       read-only inventory; unknown, incomplete, latest accepted and report-linked runs stay
echo    storage-retention.cmd --root "SANDBOX\Working" register --all --apply  register receipt-backed runs as review/keep; unsupported directories stay unregistered
echo                                    accept RUN --reason TEXT --review-cleared --audit-cleared --apply; supersede RUN --reason TEXT --review-cleared --undo-cleared --audit-cleared --apply
echo                                    delete RUN --apply is separate; rechecks report references and approved content fingerprint, refreshes intake history, writes a receipt
echo                                    repair-history RUN --apply retries history publication only after a recorded deletion; never restores or deletes run data
echo    likeness-actions.cmd validate FILE.json  check staged actions against current photo IDs, hashes, folders and catalogue
echo    likeness-actions.cmd preview FILE.json   show intended destinations; never moves photos or edits metadata
echo    likeness-actions.cmd apply FILE.json --apply  verified backup, then apply staged moves and metadata decisions
echo    likeness-actions.cmd undo [BATCH_ID] --apply  verified backup, then undo the newest action batch
echo    likeness-actions.cmd quality APPLIED_RUN [--dry-run ^| --apply ^| --check] [--undo]  Sandbox-only measured unusable intake via existing guarded Junk actions; scoped recovery, retained preparation and bound conservation receipt; no models
echo    likeness.cmd crops              one web page with every cropped photo, the uncropped original beside it ^(likeness.cmd crop --undo --apply reverses the last batch^)
echo    likeness.cmd                    general roots ONLY: Angels, Sisters, Models, Prospects, Potentials, Various; Artists are excluded
echo    likeness-artists.cmd --root "SANDBOX\Working" --dry-run group --singles  shared engine, artist-only preview; --check scans without cache/history writes
echo                                    artist scan, junk, crop, group, folder inspection, diagnostics and index reuse the same code; artist state lives in Working\_likeness\artists
echo                                    general state lives in Working\_likeness\general; default post-move originals stays scoped and does not retarget selected workflows
echo    duplicates.cmd [--apply]        the same picture kept twice anywhere in the library ^(any folder, any name^)
echo    originals.cmd --check           are the scaled copies and headshots in step with every gallery?
echo.
echo  WORKSPACES
echo    render-reference.cmd preview BATCH.json --root DIR --dry-run   validate exact source-bound reference/character requests offline
echo    render-reference.cmd prepare BATCH.json --root DIR [--apply]   freeze inputs only under _generation; NO workflows, deploy or queue
echo    render-reference.cmd check BATCH-ID --root DIR --check         verify frozen evidence without reading current source or contacting ComfyUI
echo    render-reference.cmd probe URL --input-root DIR --output-root DIR [--require-node CLASS]  read-only GET diagnostics; NO upload or queue
echo    render-reference.cmd catalog                                  list provisional supported and disabled recipes by stage
echo    render-reference.cmd compile BATCH --root DIR --endpoint URL --input-root DIR --output-root DIR [--apply]  bind/copy isolated pilot inputs and graphs; no queue
echo    render-reference.cmd submit BATCH --root DIR --job ID [--apply] one explicit job; never silently retries uncertain submissions
echo    render-reference.cmd run BATCH --root DIR [--limit 4] [--timeout 3600] [--queue-depth 1] [--apply]  bounded selected batch (limit up to 64); waits existing queue, no interrupt
echo                                    --queue-depth N keeps up to N owned jobs queued at the tail (2..16); every submit refuses at the 200-job server queue capacity
echo                                    --timeout accepts 1..21600 seconds (six hours), including waiting behind existing jobs; default 3600
echo                                    --allow-busy-queue explicitly appends owned jobs at normal tail behind other callers; no priority or cancellation
echo    render-reference.cmd status BATCH --root DIR [--refresh]        local receipts; refresh explicitly reads server history
echo    render-reference.cmd reconcile BATCH --root DIR --job ID [--apply]  find one exact uncertain prompt in recent scoped history; NO resubmit
echo    render-reference.cmd retain BATCH --root DIR --job ID --output-sha SHA [--apply]  copy ONE reviewed synthetic result outside ComfyUI
echo    render-reference.cmd manual-prefixes --root DIR [--apply]       preview/back up clone manual save-prefix correction; no prompts/settings changed
echo    render-reference.cmd cleanup-batch --root DIR [--hint H] [--sources SCAN.json] [--recipe R] [--samples 2] [--id ID] [--apply]  requests for intake photos flagged for ComfyUI cleanup; never queues
echo                                    --per-person N samples assigned original gallery photos by resolution instead of cleanup hints; exact duplicates only, no outfit elimination
echo    render-reference.cmd compare BATCH --root DIR [--batch OTHER] [--dry-run ^| --check ^| --apply]  frozen sources beside outputs by person/recipe/seed; human review, never identity assignment
echo    render-reference.cmd overlay-scan --root DIR --inputs RAW-DIR [--id ID] [--apply]  rescan raw intake images for overlays and map hits to Gallery sources
echo    render-reference.cmd outputs --root DIR [--workspace WS] [--dry-run ^| --check ^| --apply]  browse ALL ComfyUI outputs: filters, full view, pull-manifest export
echo    render-reference.cmd pull MANIFEST.json --root DIR [--apply]   copy chosen outputs to _generation\library with standard names, 944x1104 copy and sidecar
echo    render-gallery.cmd --root DIR [--dry-run ^| --check ^| --apply]  stage-grouped request export and server-output result browser
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
echo    backdrop.cmd --repo ^| -w "WS" ^| --workspaces [--dry-run ^| --check]   swap the old cream studio-backdrop wording for light grey in hand-made workflows ^(zz_Shots, curated, captured^); backs up first
echo    finals.cmd ACTION "WS"          candidates and finals: status, sort ^(files them where their name says; never deletes^), promote, pull, deploy, reclassify ^(repo cleanup^)
echo    deploy-templates.cmd / pull-templates.cmd     the ST stage templates, to and from Sovereign Territories
echo    inputs.cmd [status ^| pull -w WS ^| reset --hero H ^| photos ^| set HERO --photo F ...]  which images each hero's workflows read; pull keeps the default images you chose in ComfyUI in workspaces.json (do it before reset); photos re-points a chosen photo that was renamed
echo    compare-primes.cmd [HERO ...]   Prime renders side by side, Qwen and FireRed, normal and configured alternate flows, with a face score against the photo each started from  ^(docs\art\prime-flows.md^)
echo    originals.cmd [--dry-run] [--only NAME] [--no-headshots] [--archive-old]   the photo library: name originals after their folder, scale to 944x1104 into PERSON\944x1104\full,head,chest ^(former gallery_/headshot_944x1104 folders are moved in^) ^(reel screenshots cut to the picture^), make face headshots, move old copies to _archive, re-point chosen photos  ^(docs\art\original-photos.md^)
echo    likeness.cmd diagnostics --out DIR [--policy FILE]  active standalone report utility: one-pass calibration + active-person folder checks; CSV/Markdown; no identity or photo changes
echo                                    --root, --cache, and --out are required; sandbox paths stay under Working; report output is new and cache reads/writes are separate
echo    likeness.cmd family-preview [--policy FILE] [--out DIR]  active standalone report utility: direct reference scores, surname reuse and naming collisions ^(JSON + HTML; suggestions only^)
echo    likeness.cmd sandbox-reset       preview restoring only Models, Prospects, Potentials from the verified sandbox Source snapshot; --apply to restore ^(requires --root ...\Working^)
echo    likeness.cmd sandbox-reset --full  read-only exact Working reset preview against current Production; --apply stages and verifies the baseline, preserves unique active photos and review metadata
echo    sandbox-rebase.cmd "SANDBOX\Working" "SANDBOX\Working\_sandbox-state\RUN" --cast-seeds core --record-core-protection [--dry-run ^| --intake-only --apply ^| --apply ^| --check]  approved run-local core thresholds, automatic protection and final own/rival audit; keep the flags on every step
echo    likeness.cmd audit-core ^| calibrate ^| folder ^| clean ^| sisters ^| pairs ^| alike ^| compare ^| like ^| sort --singles ^| reconcile ^| singles ^| junk ^| review --out ^| loosen ^| lookalikes ^| names ^| index ^| profile ^| who ^| merge ^| retire ^| retire-empty ^| archive-list ^| promote ^| rename ^| undo   core and explicit maintenance operations; moving commands preview before --apply  ^(docs\art\likeness.md^)
echo                                    likeness.cmd retire-empty is the legacy direct move with NO journal or recovery; prefer retire-empty.cmd after a SIMPLE rebase
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
echo    test.cmd                        workflow, rendering, gallery, retained-preparation and prompt tests
echo    check.cmd                       every commit hook (or the same checks directly when pre-commit is not installed)
echo.
echo  See workflows\README.md for the model: one home workspace per set, temporary copies where a workspace accepts them, zz_ items mastered in the workspace.
echo.
