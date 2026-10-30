# 2026-10-22: gallery and Review information layout

**Status:** holding (Oct 30 scheduling; delivered navigation retained, broader UI work deferred)

**Resume gate:** reactivate only the relevant slice if actual installed
Gallery/Overview/Review/history UAT exposes a blocker; otherwise after baseline
acceptance. Current viewer verification remains T16/I59, not a new layout
redesign. Separate Intake entry, pruning and I/O requests remain open.

## Oct 25 continuation: retained evidence is now integrated

Sandbox assignment now publishes exact originals and retained alternatives
beside the destination photo. People/Review prefer that checked retained detail
over historical comparisons, including named and unassigned Various photos.
Relative links are resolved against the generated gallery directory, not
tested by searching for an absolute file URI. Historical staged intake-only
runs remain labelled separately in the run browser.

Retained detail now identifies itself as retained evidence rather than an
unassigned pilot. It links current native, domain main gallery, Review and
Intake runs, plus verified available full/head/chest derivatives. The shared
move/rename/manual-action path carries the set and its return navigation.
Missing/stale claims remain explicit; no version is regenerated on viewing.

This delivers L12's stored-lineage integration in synthetic end-to-end tests.
L19's broader separate unassigned entry experience and real gallery acceptance,
L18's library-scale I/O and L20's pruning policy remain open. No real library
republish or rebase was used as a substitute for those acceptance gates.

## Oct 25, 12:33: protection reasons and three-name identity display

Full feedback and name-field ownership live in
[family N9/N10](2026-10-22-identity-family-naming.md).
Overview/Review/detail parity must display assigned character name, current
person/family name and original supplied/generated person name as separate
facts, plus family association and automatic/manual protection reasons where
verified. Do not infer biological relationships or manufacture missing history.
Engine E13 supplies protection evidence; N9 supplies names/provenance. This
extends L2 parity, not permission to guess values from folders or action exports.

The subsequent studio-gallery clarification is preserved in the
[intake plan](2026-10-23-image-intake-preparation.md#oct-25-incremental-scope-and-the-next-clean-start-acceptance).
Shared chrome now has a native keyboard-accessible mobile Menu disclosure and
a dark/gold gradient footer with a stable Gallery UI version. The same renderer
is reused by the existing gallery/intake pages; no frontend framework or external
CSS dependency is added. Header/menu controls must not imply an execution server.

Gallery, Review, Rendering and Outputs use the shared masthead outside
`.site-page` and the shared footer inside it, keeping the footer aligned with
page content at desktop and mobile widths. Section labels, active navigation
and page-specific read-only guidance remain distinct; this is shared chrome,
not a change to source scope or execution.

The shared desktop header and mobile Menu include **Comparison** beside
Rendering/Outputs, linking to `_generation/comparison.html` relative to each
gallery surface. Comparison marks itself active and retains return links to
the other sections; it remains a read-only human-review page.

Rendering labels distinguish the existing 0d legacy studio pose pilots from
bedroom Deluxe. The shared relaxed and forward-foot Prime outfit recipes are
selectable under `1_Alpha`; recipe IDs and existing artifact paths are unchanged.

## Oct 25, 11:35: browsable intake-run history

The complete user message is preserved at the end. This supersedes the expanding
multi-run chooser delivered at 09:13, not the source-verification contract.

- Multiple exact traces now open a separate `intake_runs.html` page, scoped by
  source path and hash. A single checked trace still opens its detail directly.
- People Overview/Review and Artist Overview/Review have an **Intake runs**
  navigation entry. Their supported generators publish the browser alongside the
  galleries; Artist ownership/check manifests cover the extra page.
- Select a run from a naturally sorted run list to see its summary and photo
  cards. Run/recipe/source search, recipe and verification filters, photo search,
  counts, empty states and 60-photo incremental display support longer histories.
  Selected-run URLs are linkable; a scoped view can return to all-photo history.
  A source-scoped run list shows all photos in the selected run by default, marks
  the linked photo and offers a **Linked photo only** filter. Stored preview cards
  use the recommendation's variant when available and explicitly label fallback
  previews; no transformation is run to make them.
- History independently verifies each discovered run, without the continuity
  index's global run-count cutoff. Per-run manifest/row safety budgets remain.
  Invalid/oversized runs are visible as unverified diagnostics without links;
  no claim that these runs match today's sources is made.
- Photo/domain scoping remains in force. An original run overview is offered only
  when all its photos belong to the browsing domain; mixed-domain runs expose only
  scoped photo details. Discarded candidates do not become a retained version set.

L20 owns future run inventory/pruning: agree keep rules, show protected
dependencies and estimated savings, preview/check, then deliberate apply only.
No age-based deletion, automatic cleanup or new execution service is delivered.
L19's separate unassigned Intake gallery and I21/I23's assignment lineage remain
open; this history page is not a substitute for either.

Validation checkpoint: 117 focused gallery/provenance/rename tests pass.
Browser UAT checks seven real runs, 84 reachable detail links, no broken history
thumbnails and no overflow at 1440/760/375/320px. A browser-only synthetic fixture
checks 250 selectable runs and 60/120/125-photo paging; first render took about
4 ms on this machine. This is not an artifact-verification I/O benchmark.
The Artist repeat/check test caught filesystem-dependent navigation output;
an explicit standalone-preview mode fixed it, preserving deterministic report
bytes across first publish, check and repeat. Real source and v16 manifest hashes
remain unchanged.

- [ ] **P2 either** L20 Define safe intake-run retention/pruning with dependency
  checks for retained sets and gallery links, disk estimates, preview/check and
  explicit apply. Do not delete runs while reviewing the policy. Oct 28 sizes:
  ~85 GB under `Working\_sandbox-state` (full intake runs 24-29 GB each), ~8 GB
  of pilot reports; see T4 in the [intake performance plan](2026-10-28-intake-performance.md).

## Oct 25, 09:23: gallery-first navigation and retained image detail

This clarification defines the target experience, not a claim the comparison
bridge completes it. The complete user message is preserved at the end.

- Start from a main gallery page and navigate to every supported browsing/detail
  surface from there, with return navigation. Standalone report URLs must not be
  required knowledge.
- Intake/Various is a separate unassigned gallery, not a person identity or a
  hidden subset of the assigned-person gallery. Both are reachable from main
  navigation; Artist identity-domain separation remains intact.
- Open an image from its gallery to one image-detail surface showing the current
  source, retained original and all versions actually stored for that image.
  This includes retained crop/cleanup, denoise, lighting/tone and standard
  derivatives where available; do not restrict it to the recommended version.
- After assignment/copy/move, that image's retained set is reachable from the
  destination person's gallery. Use verified lineage, not basename/hash guesses.
  Discarded intake candidates do not reappear as available versions. Historical
  experiment reports are separate comparison evidence, not the retained set.
- Never silently regenerate a discarded/missing version on opening detail.
  Distinguish unavailable/discarded/not-attempted states where recorded.

L12 owns navigation and presentation; intake I21/I23 owns stored version-set
membership and verified source/publication lineage. This supersedes treating
per-run trace links or the separate preview as the finished integrated GUI.
The precise retention/backup policy remains unresolved: regenerable does not
mean permission to discard a currently retained denoise/tone variant.

The future direction is image-centred workflow execution: select an image and
eventually a workflow/output destination without manually finding/loading it
and adjusting prefixes in ComfyUI. Manual-action A8 owns that roadmap, pending
the user's write-up. No execution server, workflow/prefix changes, GPU job or
browser filesystem permission is approved by this clarification.

- [ ] **P1 ai** L19 Add gallery-first navigation with a separate Intake/Various
  gallery and return links to the main browsing surfaces. Cover unassigned and
  assigned images, empty states and domain separation; reuse existing evidence
  and detail renderers without triggering processing or implying publication.
  Coordinate retained-version detail with L12 and intake I21/I23.

## Oct 25, 09:13: intake integration and next safe work

The user's complete continuation request is preserved at the end. Image-review
feedback is not a prerequisite for read-only navigation, shared rendering,
profile/history parity, bounded refactoring or documentation classification.
Templates/generation follow completion of the image-processing work; this is
priority ordering, not acceptance of any intake recipe or publication contract.

**Integration truth:** People overview renders preparation evidence per displayed
photo; People Review and Artist Review render it per photo; Artist overview opens
the group's photo browser and summarizes evidence states. Exact per-photo links
already resolve checked traces. No generic run index is substituted for a detail.
However, current v9 has no published People/Artist main pages, and rename/move/
accepted-source lineage remains I21-I23/L12. Do not call the full experience done.

Delivered this continuation:

- An obvious `Open intake detail` entry for one checked run. Multiple exact runs
  offer `Compare intake runs`, with every verified alternative and no newest winner.
- Review and Artist Review now share one DOM renderer in
  `preparation_provenance.py`; Overview's server-side renderer carries the same
  original/crop/mask/skip/recommendation and comparison-only explanation.
- A read-only integration preview at
  `_reports/gallery-intake-preview/people_gallery_review.html` reuses all 12 real
  v16 sources and existing thumbnails/retained inputs. All 12 have seven exact
  checked run alternatives (84 trace links); evidence indexing took about 8 s
  on this sample. This is not the old 2,421-photo L18 benchmark.
- The preview explicitly has no scoring/identity/action authority and does not
  generate headshots, thumbnails, sources or intake transforms. Original source
  hashes and the v16 manifest are unchanged.
- Launcher help and preparation console output no longer describe v16 as
  rejected-eraser-only or promise that apply cannot download models.

Validation: 113 focused gallery/provenance/rename tests and 58 preparation tests
pass; markdownlint and scoped diff checks pass. Browser UAT confirms 12 entry
points, 84 reachable trace pages, zero broken images and zero overflow at
1440/760/375/320px. The `203951` choice opens its exact v16 photo with the
recorded step labels. The temporary HTTP helper was stopped; the saved local
HTML remains available.

Other owners scanned: structure D1/D2/E2 retain behavior-preserving extraction;
CLI simplification remains proposed (no option/launcher removal); tooling-debt
D13 owns document classification. Historical Oct 9/10 reorganisation reports now
warn against replay, and the docs index no longer treats one as canonical guidance.
No historical evidence or raw notes were removed.

## Oct 25: identity panels and feedback reconciliation

The user is reviewing v16 cropping independently. Continue presentation work
without processing intake, applying actions, refreshing face scores or changing
protected-action/ranking policy. The current chat is preserved at the end.

L1 inventory against the raw feedback:

| Information | Overview today | Review disposition |
| --- | --- | --- |
| Name/category | Separate title and category badge | Name and category separated in Identity details |
| Recorded name versus cast slot | Person label versus folder | Separate recorded-name and fixed-slot rows; unavailable snapshot is explicit |
| Reference photo and score | Workflow-pinned photo and score | Read-only primary reference always visible, even when also in the grid; core score shown |
| Counts/core | Gallery count and Review text | Full-report Gallery/Review totals, filtered/page count, core size/mode |
| Profile tags/history | Profile summary and history link | Still missing from Review payload; L2 remains open for parity |
| Cross-reference evidence | Closest-by-category, full rankings, pairing | Closest-by-category and full rankings inside Identity details; no ranking changes |
| Identity actions | Link to Review | Dedicated Manual actions panel; existing confirmations/conflict/export checks unchanged |
| Photo details/actions | Up to nine photo thumbnails | IDs on separate lines, face/core evidence, three closest matches and photo controls retained |

Implemented the responsive Reference / Identity details / Manual actions panels.
At <=1050px actions span both columns; at <=600px all panels stack. The reference
remains read-only; showing it does not duplicate staging controls or images on disk.
Counts describe the report, not a fresh filesystem inventory.

Overview now has a clickable amber `in review` badge immediately after the photo
count, opening that person's Review-only filter. Removed the duplicate count from
the caption. No new count thresholds. L11 guidance shares one mapping across both
people pages: Potentials common/uncommon, Prospects broader use, Models not the
preferred common/uncommon pool. Explicitly not automatic assignment or a rarity rule.

Plan scan: action A1/L6 still own unsupported/protected identity actions;
upkeep U1/U3/U6 still own derivatives/refresh/recovery; intake I21-I23 still own
retained sets and resume/publication. None are marked done by this layout change.
L12's old fixed trace order is corrected below: the linked report owns its recipe's
order (v16 crops before repainting); the GUI must not imply the v15 order is current.
L18 performance work and L15/L17 visual acceptance remain open.

Validation: 148 focused gallery/provenance/action/rename tests pass, including
the existing Node confirmation/cancel/export tests adapted to the new panel
container. Browser fixture checks cover responsive layouts, 100/200/211 pagination,
all four orders, grouping, Review-only references, staged-action retention/cancel,
search and disabled protected photo controls. These are synthetic UAT, not real
library acceptance. Only `_reports/preparation` currently exists in the v9 sandbox;
the historical People preview mentioned below is not present there. No real People
or Artist pages were republished; no thumbnails, caches or sources were changed.

## Oct 23, late checkpoint: read-only preparation bridge

L12 now links exact current path/hash, available photo ID and source domain
to verified immutable preparation traces across People overview/Review and
Artist generators. Missing/stale/unverified/ambiguous states are explicit.
Multiple checked runs remain alternatives, never an invented newest/best
source. This does not complete accepted publication or historical rename
lineage; L12 stays open. No new image copies are needed for these links.

The four-source unassigned preview contains both motivating screenshots and
the exact Angelica sources ending `7513772466838834360` and
`7513772617730547310`. Evidence alternatives are 5/5/3/3 respectively.
The saved 2,421-row general Review preview has 2,320 missing, 24 ambiguous
and 77 unverified rows. Those 77 lack proven current-path/rename continuity;
they are not silently treated as verified or reported as manifest errors.
All historical photo staging and identity rename/protection actions are
disabled. Browser UAT confirms no horizontal overflow at 1440/760/375/320px,
working source-to-trace navigation, correct named cases and no enabled
staging controls. The four-source view has no broken images.

69 focused integration tests pass, including 11 new provenance tests.
The full quick checkpoint passes 27 suites / 652 tests and 19/19 mutations.
Actual Artist republishing with this bridge was deferred: evidence indexing
took about 99 seconds on the historical Review build. L18 owns reducing that
I/O without weakening verification. Existing Artist pages are not claimed to
contain the new evidence bridge merely because their generator now supports it.

## Oct 23, 18:08: presentation is an independent workstream

Shared gallery presentation may proceed across People, Review, Artists and
comparison pages independently of intake recipe acceptance. Reuse header/footer,
navigation, spacing and common presentation components where their behavior is
actually shared; do not constrain this work to an Artist-only experiment.
L1-L4/L7 own that work, not the intake plan. Preserve each page's distinct
controls, scoring explanations and read-only versus staged-action behavior.

Only L12's verified intake-data linkage depends on the provenance contract;
ordinary layout/shared-component work does not. This authorization does not
process Various/gallery, change matching or accept a cleanup recipe. Validate
presentation on fixtures or existing report evidence without triggering intake.

## Oct 23, 17:29: Artist prototype and consistent report navigation

This replaces L14's earlier GUI deferral: build a basic separate Artist overview
and photo-review browser now, without people relationships, staged actions,
matching or source maintenance. Use it to evaluate a cleaner header/footer,
separate navigation and responsive filtering before broader layout adoption.
The user's follow-up also authorizes consistent navigation/footer treatment on
people pages; it does not approve unfinished protected-action or ranking rules.

Artist pages share one content-addressed 240x300 thumbnail per distinct source,
not independent overview/review caches or full-size copies. Publish only below
`_reports/artists`, report count/bytes, and support preview/check/repeat.
Existing face cache is read-only; unknown face results remain unassessed.
No processing of current Various/gallery, source moves, quarantine, production,
core changes or ComfyUI retargeting is part of this work.

Storage/recovery is owned by upkeep U6, not a blanket `_reports` exclusion.
Only exactly hash-owned generated browser files may be omitted from routine
snapshots. Keep manifests, face caches, source placement, catalogue/history,
unrecognized/edited files and retained preparation inputs. FULL/transaction
snapshot behavior remains explicit. Old unmanifested report assets are not
retroactively declared disposable.

**Delivery evidence:** separate sandbox pages show four artists, 71 source
groups and 279 photos. One shared thumbnail per image: 279 JPEGs, 4,427,932
bytes; complete browser output is 282 files / 4,670,943 bytes. Browser checks
cover search/no-results, Artist filtering, overview-to-filtered-detail links,
60-card pagination and narrow/wide overflow; corrected the hidden pagination
button's CSS precedence. Existing 853 Artist source/metadata/derivative records
and captured cache/catalogue/origin state remain unchanged. Final actual launcher
preview/apply/check/repeat passes; report hashes/mtimes repeat exactly.
Full quick validation passes 26 suites / 631 tests and 19/19 mutation cases.
Broader people layout acceptance is not implied. Existing real people reports
were not refreshed, so their new navigation/footer will appear on the next
supported refresh; current Various/gallery was not analyzed.

## Review and questions: 2026-10-22 16:26 -05:00

Retained with complete acceptance feedback. Before L6, ask one question:
what should relocking a protected identity do to already-staged actions?
No answer was assumed. Before ranking eligibility changes in L10, review
evidence with the engine/action owners; labels alone cannot change policy.
L11 now owns the transferred Oct 21 5.6 card-use guidance. These are planned
controls/layout, not a claim that the real-library GUI has passed user review.

## Scope and ownership

This plan owns presentation and information grouping across the gallery and
Review pages. Identity actions and their transaction semantics belong to the
[manual-action plan](2026-10-22-review-actions.md); automatic decisions follow
the [processing contract](../art/likeness-processing-contract.md).
It does not duplicate matching, calibration, family naming or production gates.
Keep closely related layout work together; split a genuinely independent
topic into its own plan with explicit links rather than expanding either
engine plan indefinitely.

## Agreed direction

- A person header is a readable summary, not one blended block of controls
  and diagnostic text.
- Separate the reference/workflow image, identity details/statistics, and
  manual actions into clearly labelled panels.
- Keep identity name, fixed cast slot and category distinct. Do not imply
  a person's recorded name is the character slot.
- Preserve overview/Review ordering and useful information consistently.
- Identity-level manual actions must be available across identity categories;
  protection adds a deliberate safeguard, not a blanket manual-action ban.
  Each action still validates ownership, conflicts, references and recovery.
  This does not silently change the separate photo-protection contract.
- Layout work is recorded now, not silently included in rename delivery.

## Protected identity actions: proposed interaction

Prefer an explicit per-identity checkbox in the Actions panel:
**Enable manual actions for this protected identity**. Protected identities
start with manual controls disabled and an explanation of how to unlock them.
Checking it enables manual controls without clearing protection, authorizing
automation or repeatedly asking the same protection-confirmation question.
The unlock is temporary UI state, scoped to that identity, and resets on reload.
Unprotected identities need no protection unlock. Action-specific validation,
preview, backup and undo remain mandatory; a protection unlock does not bypass
unsupported references or make unfinished actions executable.

This is a proposed replacement for the current protected-rename confirmation,
not a description of shipped behavior. Before implementation, settle how
relocking handles already-staged actions. Never silently discard staged work
or conceal pending decisions behind disabled controls.

## Work

- [x] **P1 ai** L1 Inventory the current overview and Review person-header
  content against raw acceptance feedback. Map image, details, tags,
  diagnostics and actions into distinct panels without dropping existing
  information or duplicating its source.
  Result: Oct 25 inventory above; gaps stay explicitly assigned to L2/L3/L10.
- [ ] **P2 ai** L2 Implement a responsive reference-photo panel, identity
  details panel and actions panel. Align name/tags/stat order with the
  overview; stack cleanly on narrow screens and keep controls accessible.
  Oct 25: three panels implemented and fixture-tested. Remains open for
  profile tags/history/workflow-selection and full overview-stat parity, then
  regenerated real sandbox pages. Do not infer those facts from rename eligibility.
- [ ] **P2 ai** L3 Audit photo-detail grouping and category/name repetition,
  clickable tags, history links, separators and visual hierarchy across both
  pages. Preserve scores and the distinction between evidence and actions.
  Oct 25: header category/name split and clickable Review count delivered;
  per-photo IDs already use separate lines. Full repetition/grouping audit remains.
- [ ] **P2 ai** L4 Validate both sort modes, filters, primary references,
  stage/cancel/export and protected-action safeguards after the layout
  changes, including narrow/wide synthetic browser checks.
- [ ] **P1 you** L5 Review the regenerated actual sandbox pages after L2-L4;
  confirm the image/details/actions separation is usable.
- [ ] **P2 either** L6 Settle relocking/staged-action behavior, then implement
  and test the per-identity manual-action unlock in L2's Actions panel.
  Cover disabled defaults, independent identities, reload reset, visible
  pending actions and unchanged automatic protection. Audit identity-level
  controls and backend handlers for blanket category/protection refusals;
  resolve these in the linked action-owner plans, not by bypassing validation.
- [ ] **P3 ai** L7 Review shared theme, colors, spacing, typography,
  placeholder/header treatment and optional sticky navigation across both
  pages. Style all tags consistently; give clickable history/review-count
  tags a clear hover target and proposed count-color ranges for user review.
  Oct 23 continuation: shared badge sizing/category/score palettes and
  underlined, hover/focus-visible tag links are implemented. Existing score
  thresholds and semantic state badges are unchanged. Compact page navigation
  sticks on wide/tall screens; it scrolls normally at <=760px width or <=500px
  height and when printing. Category targets remain visible below it.
  Oct 25: clickable Review count delivered with the existing amber Review palette.
  Count-color ranges remain open;
  no new thresholds or actions were inferred from this cosmetic work.
- [x] **P2 ai** L8 Add a presentation-only Mixed/Split grouping choice
  separate from Location and Order. Split Gallery/Review into labelled
  groups, or retain mixed score ordering with unmistakable Review styling.
  Preserve filters, staging and both existing sort modes.
  Delivered Oct 23 after 20:18: Mixed remains the default. Split labels the
  currently rendered Gallery/Review subsets within each person or flat view;
  sorting and the 100-photo page boundary are preserved. Review cards retain
  their explicit badge plus an amber left border. No membership changes.
- [x] **P3 ai** L9 Make move selection category-first then identity while
  retaining stable destination IDs, validation and current stage/export behavior.
  Delivered Oct 23 after 20:18: choose an eligible category, then a person.
  Closest-target preselection is retained across categories; option labels show
  names while values keep exact folder keys. Source/uncatalogued destinations
  stay excluded. Rejected conflict changes restore both selectors; existing
  rename/protection guards, stable-ID/hash export and CLI validation stay intact.
- [ ] **P2 either** L10 Audit ranking labels and explanations with the engine
  owner: who is compared to whom, adjusted fit versus identity similarity,
  Models/Potentials coverage and workflow-occupied eligibility driven by
  configuration. Do not change pairing or target eligibility as a cosmetic
  rename. Include concise Angel labels/order and requested visual separators.
- [x] **P2 ai** L11 Show descriptive card-use guidance by category: Potentials
  can be browsed for common/uncommon, Prospects for broader use, and Models
  are not the user's common/uncommon choice. This is not automatic card
  assignment or a gameplay rarity rule. Verified destination for Oct 21 5.6;
  no separate engine implementation owns this presentation task.
  Result: Oct 25 shared mapping rendered in Overview and Review; no matcher,
  category policy, rarity budget or assignment behavior changed.
- [ ] **P1 ai** L12 Integrate verified preparation comparison/detail links into
  the people overview/Review pages after the intake provenance contract is
  accepted. Distinguish retained original, current Gallery source, prepared
  alternative and padded/head/chest derivatives, with larger per-photo views,
  source/hash/recipe labels and explicit missing/held/rejected/no-op outcomes.
  Intake I9 owns the standalone pilot pages now; do not duplicate rendering or
  imply a browser selection applies a source change. Current source and verified
  uncropped original may differ. Raw words and fallback policy are in the
  [intake follow-up](2026-10-23-image-intake-preparation.md#follow-up-chat-verbatim).
  Oct 23 clarification: show original/enhanced status and why (clean original,
  overlay left for ComfyUI, failed/rejected enhancement, recipe applied).
  An overlay or enhancement failure does not itself block a readable image
  or require manual review; source treatment is separate from identity evidence.
  Per-photo entry must open that image's existing intake trace, not just a
  generic report index: retained original through the recipe's recorded steps
  to its recommendation, including masks/skips/reasons and
  full/head/chest views where available. Resolve stable photo ID plus verified
  source hash/provenance through renames/moves; do not guess by basename or
  silently show a stale run for changed bytes. Label no report/stale report
  explicitly. Link/reuse verified sidecars rather than duplicate image copies;
  opening the view never triggers processing, acceptance or publication.
  Oct 25 reconciliation: v16 records first crop -> second crop -> eraser ->
  composition -> comparisons; earlier linked reports retain their own step order.
  Oct 23, 21:21 authorization permits a conservative read-only comparison
  bridge now, without accepting the live preparation/publication contract.
  Delivered first slice: shared evidence index and per-photo states
  `verified`, `ambiguous`, `stale`, `unverified`, `missing`; exact current
  source path/hash and domain/artist scope are checked, and available stable
  photo IDs must agree. No basename-only or hash-only rename inference.
  Validated alternatives show recipe, retained input hash, cleanup decision,
  reasons and direct detail links. Multiple exact runs remain ambiguous and
  all verified alternatives are shown; no latest-run winner is invented.
  People overview/Review and Artist Review display evidence; Artist overview
  summarizes evidence counts. This is comparison provenance, not proof a
  recommendation was applied. Old unverified/failed checks withhold links.
  L12 stays open for accepted source-to-prepared-to-published lineage through
  real renames/moves, and final post-assignment full/head/chest integration.
- [x] **P1 ai** L13 Keep Artists out of normal people overview/Review pages,
  category controls and relationship displays. Intake I17 owns the shared
  discovery/scoring/caller boundary and its tests; this item owns presentation
  verification, not a second engine implementation. Legacy `--artists`
  inclusion must diagnose the changed boundary rather than silently mix domains.
- [x] **P1 ai** L14 Deliver the now-authorized basic Artist overview and
  photo-review browser, shared bounded thumbnails, header/footer/navigation
  prototype, accessible filters and paged/lazy rendering. No relationships,
  staged actions or matching. Validate preview/check/repeat, source/cache
  preservation, responsive navigation and disk accounting; coordinate U6's
  exact managed-report backup omissions. User visual acceptance remains L15.
  Complete raw feedback lives in the
  [intake handoff](2026-10-23-image-intake-preparation.md#oct-23-1705-review-handoff-and-incoming-batch-pause).
- [ ] **P2 you** L15 Review the Artist overview/photo-review navigation,
  filters, header/footer and narrow/wide layout. Identify which presentation
  concepts to adopt in the people gallery; simple shared navigation/footer
  availability is not acceptance of the full L1-L10 redesign.
- [x] **P2 ai** L16 Shared gallery theme and banner (Oct 23). Result:
  `likeness_library/gallery_chrome.py` owns one design system (CSS variables,
  masthead, page header card, navigation, footer, responsive rules) used by the
  People overview, People Review, Artist overview/review, family preview and new
  intake preparation runs. The banner is a 1024x360 crop (54 KB) of the ComfyUI
  title art `ST/title/SovereignTerritories_Title_00001_.png`, packaged as
  `likeness_library/assets/gallery-banner.jpg` and published once to
  `_reports/_assets/gallery-banner.jpg`; a replaced file is never overwritten and
  a missing one falls back to a gradient. Intake runs only reference it, and
  existing runs stay hash-verified. Sticky navigation and tag styling stay in L7.
- [ ] **P2 you** L17 Review the themed look on
  `_reports/library-style-preview/` (People overview and Review copies) and the
  refreshed Artist pages; then decide whether to regenerate the real People
  pages (re-scores the library), whether Artist pages keep the People link in
  the masthead, whether to keep the compact sticky navigation and unified tag
  treatment, and delete the preview folder (about 44 MB, not manifest-owned).
  Preview copies retain historical data/scripts, including old Artist entries;
  they demonstrate presentation, not the current general-domain filter.
- [ ] **P2 ai** L18 Improve preparation evidence-index I/O without weakening
  hash/path/scope checks. Current 2,421-row saved-evidence preview verification
  takes about 99 seconds because full referenced runs are checked; build once
  per render, retain explicit limits/errors, and benchmark selective per-photo
  artifact verification or a safely invalidated reusable verification index.
  No timestamp-only trust, silent latest-run selection or automatic acceptance.

### Oct 23, 19:36 continuation: presentation-only checks

Continued L7/L16 after restart without processing incoming images or rebuilding
People evidence. Removed duplicated badge palettes from page styles so the
shared stylesheet owns their appearance. Browser checks exposed count-label
overflow at 320px and Large Review tiles wider than their container; counts
now wrap and preferred grid widths can shrink to fit. Existing workflow-photo
outline colors and semantic state badges are retained.

The two historical People preview copies have refreshed styles and page
navigation, with original scripts and original links/image paths preserved.
At 1440/760/375/320px all four People/Artist pages have zero horizontal overflow,
including Large Review tiles. Wide navigation stays at the top while scrolling;
narrow/short navigation is static. Category jumps, history hover/keyboard focus,
Artist search/reset and pagination (60 to 120) pass. Focused gallery, Review,
family and intake tests pass: 113 tests. No new thumbnails were generated for
this continuation. User visual acceptance remains L15/L17; no commit or push.
Actual Artist launcher `--check` exits 0 with 0 pending files: 279 shared
thumbnails / 4,427,932 bytes, complete generated output 4,680,025 bytes. Cache
SHA256 is unchanged across that check. Markdownlint (existing cached CLI) and
scoped `git diff --check` pass; the generated queue is refreshed. The temporary
local HTTP helper used for browser checks was stopped.

### Oct 23, 20:18 continuation: Review grouping and move destinations

L8/L9 are implemented without scanning sources or applying actions. The current
Review preview was regenerated from its saved JSON evidence, excluding historical
Artist rows (2,421 of the previous 2,667 records remain). Unlike the earlier
style-only checkpoint, this updates the Review controls/script, not its evidence.
Its warning explicitly identifies historical data and mandatory fresh CLI
validation. The overview preview still has its older rows and script.

135 focused Review/gallery/action/rename tests pass. A disposable 209-record
browser fixture passes 50 assertions covering Mixed/Split in people and flat
views, all four orders, unchanged within-bucket sequence, 100/200/205 pagination,
Location and low-score filters, Review markings, closest-target preselection,
source exclusion, category/identity selection, staging across regrouping/filters,
cancel, exported IDs/hash/source bucket, and source/destination protection plus
standalone-rename conflict safeguards. Historical-preview checks show no
horizontal overflow at 1440/760/375/320px with Split and Large tiles.

The protected-action unlock/relock decision is still L6, not implemented by these
controls. No live People report, cache, original, selection or active undo was
changed; no new thumbnails were generated. L15/L17 remain user visual acceptance.

### Oct 23, 21:21 continuation: preparation evidence in galleries

The user's combined intake/GUI request is preserved word for word in the
[primary intake note](2026-10-23-image-intake-preparation.md#oct-23-2121-visual-uat-and-gallery-trace-continuation).
I11/I18-I20 own observed overlay misses and reconstruction/crop experiments;
L12 owns the read-only gallery bridge, not a second cleanup renderer.

The shared index bounds discovery to 32 runs, 5,000 rows, 8-MiB manifests and
five diagnostic errors; current source hashes are cached within a build.
Eleven focused provenance regressions cover missing/stale/renamed/scope/
tamper/ambiguity/HTML-safety cases and integration; the test is wired into
the validation launcher. No new image copy or thumbnail is needed.
Existing report hashes are checked without modifying immutable runs.

Historical Review preview now displays preparation states across 2,421 saved
general rows: 2,320 missing, 24 ambiguous and 77 unverified. It is explicitly
historical, not action authority. It does not rescan faces, infer identities,
change matching or refresh the live People report. Artist publication was
deferred after the roughly 99-second index check rather than hiding its I/O
cost behind repeated apply runs. The code integration appears on the next
supported Artist refresh; current preview UAT does not imply that live output
was rebuilt.

## Raw feedback (verbatim)

Source: `feedback/feedback_on_acceptance_testing.md`, full snapshot, Oct 22.
This is the primary verbatim copy for a note spanning several workstreams.
The [coverage audit](../audits/2026-10-22-plan-feedback-audit.md) maps each
request to its active owner or clearly proposed successor. Sources stay intact.
The complete source text, including indentation and trailing line whitespace,
is preserved below. The source remains safely in place.


<!-- markdownlint-disable MD013 -->
```text
I have been using the GUI while you have been finishing and I have a large amount of initial feedback.  Not sure if we can tackle all these items or what needs to be done - but some are cosmetic and other address functional gaps.  I added a priority to them all, but I feel like we need to come up with a plan on addressing these items ... and as I continue to work there will be more.  We don't need to use a formal github issue and we can just document these items somewhere in the docs/plans and eventually archive the document when it's done.  

Here's a few items I am curious about and what is going on in looking at the latest gallery GUI results.  This feedback was done on the GUI that was deployed for testing at 10/22/2026 1:00 am - so does not account for any work that was completed during you latest coding and testing cycle.  So we can simply document these items as fixed in the new plan document to address usability feedback.  I noticed you were working on the retirement aspects while doing the work - so that's just one case where I can use this as a not to re-test any items already completed.

# Feedback on Acceptance Testing

## Gallery Theme

Priority: Low
The overall gallery theme could be more visually cohesive.  Consider reviewing the color scheme, spacing, and typography to ensure a consistent and pleasant user experience throughout the gallery interface.

At some point I could get a banner for the gallery to make it more visually appealing and to reinforce the overall theme.  For now we can just use any standard placeholder image or simple design element to fill that space.  Or even just a solid color block that matches the gallery theme would work temporarily.

Basically, just trying to look at how we can improve the overall visual cohesion and user experience of the gallery interface and make it look like a professional page.  That might also mean leaving the header area present as we scroll through other sections below.  I think that might apply to both pages (and any future pages we need to add).

## CLI Triggering

Priority: Medium
I am wondering if it's actually possible to support triggering the CLI in a shell or to at least figure out what the actual command is to run when staging actions.  I'm also curious what happens if I stage many actions at once and how the system handles that scenario.  Especially if the actions are across many identities.  I know we are deferring making them directly actionable - but it seems more like an "Apply Actions" would be better than "Download Actions" which just stages the .json.  If we could stage it and run it - even if it takes a long time to run.  That might be useful to test and see whether it's better to just stick with the download and run batches in my own shell or whether we can do it more interactively.  This is probably more an ideation, thought and planning item than an immediate fix item.

I just find myself wanting to use items like Rename Identity to take immediate action vs. other actions where I do want to stage a bunch and Apply them in a batch - but I also would like for that to be more immediate action after I get a batch ready for processing.

If we have some simple things we could do so I can compare and contrast how it works that would be great - but I don't want to go down a rabbit hole on this until it's really a problem.  We have more immediate usability and visual cohesion items to address first.

# Gallery GUI

## Review Photos

Priority: Low
"X in review" should be a tag and showing a color based on how many are there.  It should follow the "x photos" tag.  We should also color "x photos" based on how many photos are present.  We can just make up a range for now, and use the green, yellow, orange, red level and be consistent.

We should make that tag clickable and take you to the Review Gallery with the preselected drop downs to see the review for that person.

## History Link

Priority: Low
Feels like the placement and color of the history link could be improved. It might be better to have it more prominent or in a consistent location across the interface.  Not sure if it should be front, but also removing the underscore from the clickable portion and just making it look like the entire thing is a clickable box instead of the standard hyperlink might be useful.  

That formatting would apply to all tags that become clickable.  Just hover over them to see it's clickable item.

## Tags

Priority: Medium
Protected identity should have a background color to represent it's a tag.  Really ALL tags need a background color that is aligned to what the tag is about.

## Current Angel

Priority: Low
I think it should move up to be after Person: xxxxx in the layout.  We could also change it from "Current Angel: Angels: Nyxene" to just "Angel: Nyxene" to make it more concise and clear.

## Category / Name

Priority: Medium
We should review all places where we display "Category/Name" as a single field and determing if it's important to show the separation or not.  Sometimes it may be fine to keep them together, but other times it might be clearer to separate them visually.  Or just show the Name field only if all we're saying is name.  If we want Category: xxxxx and Name: xxxx on two lines that may be fine.  But I think many places we could just reference the Name only.

This item may need an audit and figure out what makes sense in each spot we see the combined Category/Name field used.

Sometimes it also shows up as Category: Name and the context of the Category is already clear - like in the following where Prospects: is repeated for each identity.

Top Prospect alternatives:
1. Prospects: Tove North ▶ 0.31 Fit -0.028 · Like 0.032 · Variety +0.06 · 63 photos
2. Prospects: Arden West ▼ 0.24 Fit 0.037 · Like 0.037 · Variety +0.00 · 7 photos
3. Prospects: Ruby Eden ▼ 0.21 Fit 0.047 · Like 0.067 · Variety +0.02 · 11 photos

This also makes me wonder if we shouldn't just be showing the Closest other lower tier matches instead of just Prospects - since we have Models and actually Potentials.  I would want to ensure that we cover all non-Prospect categories as well to give a complete picture of the available matches.  Basically, we want to show the closest other identities that do now have a workflow associated with them - since that identity is already in use.  In the future if we add Demons that get workflow, we'd want that configuration to drive it.  I'm sure we have something in the config to drive that already.

## Visual Separator

Priority: Low
I think we'd want a separator between Workflow Photo and Closest by Category line.  Similar to the one for Top Prospect alternatives.

## Full Rankings

Priority: Medium
We need to revisit the Angel-Prospect ranking and better understand what that is providing and ensure it's named properly because we now have Models category as well.  It may still be needed, but I want to revisit it's logic and what it's doing.  We'll need to better explain the purpose at the top and who is being compared to what.  It's not clear when I read it what I can glean from this because the names are confusing.

## Various Photos

Priority: High
I see photos in the Gallery Review section that are categorized under Various, but I don't see anything on the Gallery page about Various.  Probably need to understand why photos are in Various in first place as that should be empty after a run.  At a minimum each photo would be a Potential if no match - otherwise, it would be in junk if totally unusable.

This makes me think there's a gap in the entire process since photos are being left behind.

## Workflow Photo

Priority: Medium
I wonder if on the 3x3 grid if we couldn't alway ensure that the chosen workflow photo would show up.  If it's not part of top 9 photos, we could show it as the 9th photo in the grid.  But we'd want to ensure that it's border was dashed instead of solid.  We could also change "(not shown)" to "(shown last)" or something like that as one more visual indicator on the page that the 9th photo is not actually in the top 9.  The color of the border (likely showing different than green, based on many of my selections) will help with that as well - plus we call out the score of the workflow photo as well.

I also think the existing border around the workflow photo should be thicker than it is.  It's colored to match the existing score, but still a bit faint for some.  It's pretty close to being right thickness, so just maybe a bit thicker.

# Gallery Review GUI

## Identity Overview Section

If you can visually inspect the section you'll see that the section isn't very user friendly and doesn't have all the content that is on the Gallery page about the identity.  I think we'd want it more like the following (this is not formatting, just concept info):
    - Name
    - Tags
    - Photo (workflow selected with score)
  
    - To the right of the picture we have another box with all the same stats as in the gallery - following the same layout and order.  

So it's two boxes side by side - the photo on the left and the stats on the right.

That identity overview is like a summary card for the identity, providing a quick glance at the key information and stats without having to navigate to the Gallery page.  Use your best judgement on formatting and layout to make it clear and easy to read.

## Image Details

We need to revisit the Image Details section and align it more closely with how we organize the image information in the Gallery page, ensuring consistency in the display of photo IDs, identity IDs, core similarity, core size, face size, and closest other matches.  

Here's currently what I see and think it could use work.

Draknara
Photo ID: 7518021302486860967 · Identity ID: person_2224e4265e975dee9965132af6a01d6a
SistersReview photoReview
Core similarity: 0.44
Core size: 97 photos provisional · no trusted anchors
Face: 166 px / 1
Closest other: Models: Brielle Carter 0.36

We could show the Closest Other 3 (or maybe 5) matches instead of just one, to give a better sense of how this image compares to other identities.

This is a case where Category information could be useful to display alongside the identity, especially when showing closest other matches, to provide more context and clarity.

## Various Photos

Priority: High
I see some photos in Various after the run completed. Are these expected, or should they have been categorized differently?  Can you explain what is happening there?

Many should have matched existing identities, but for some reason they ended up in Various.

Photo ID: 7518027271200184433 · Identity ID: not catalogued
VariousReview photoHold
Core similarity: not scored
Core size: 0 photos no usable core
Face: 372 px / 1
Closest other: Prospects: Uma Merritt 0.53

## Image Text

Priority: Low
I see that Identity ID: is showing up in some places as "not catalogued" in the Image Text section, even for photos that should have an associated identity. Or is this because it's photos are in Various, or is there a bug in how the identity is being displayed?  

I also noticed that it's showing up on same line as Photo ID and wrapping, we probably need a newline for that.

Photo ID: 7518027271200184433 · Identity ID: not catalogued

# Staged Actions

## Identity Actions

Priority: Medium-High
We need to start to work on the staged actions for Identity level so I can do some of the following:
    - Rename Identity
    - Protect Identity
    - Retire Identity
    - Reject Identity 
    - Merge Identity (specify target identity to merge into)
    - what else is missing that we have CLI options for at identity?

Some of these are high priority and others are not.

## Review photos

I am wondering if we should have a separator in the box of images for the review photos to be in their own section within the same box of images if we are showing "all" images and not just Gallery or Review specific.  It's really just an easy way for me to view the gallery and review together and know which ones need review vs. which ones are alway accepted into the gallery.  If we mix them within the gallery and review photos together that makes it harder to see them.  Although maybe I do want to see that view as well if we can do something to highlight review vs. accepted.  Maybe all review images need a different border around them if we show them together in mixed as then they would position in order of other images with scores and make it easier for me to see if they are alike other images.  So - I guess I want to see it both ways as long as it's really easy for me to understand either in separate groups of gallery and review or mixed all together.  
That should be some sort of option that we can pick apporpriately.
Maybe it's how we call out the sorting and grouping since it's really just a sub-sort for mixed or separated.  
The Location defines which files and we have another option for Mixed or Split to define the group and the Order defines within that how to order them.  

## Retire Photos

Priority: High
If I wanted to retire individual photos, I don't see a staged action selection to do that.  Some photos in Review need to be retired as part of the process as they aren't really usable and that's one thing we need to support.
    - Retire individual photos for an identity
    - Retire an entire identity
  
## Approve Photo

Priority: High
If I approve a photo from Review to the Gallery, does that protect that photo and how do I determine if I want it to be part of the core or not?  Is that based entirely on similarity score?  I guess, maybe that's the intended behavior, but I need confirmation on how core membership is determined upon approval.

This brings up an interesting thought, maybe we do need a threshold for automatically determining which photos are part of the core vs. part of the gallery, but not core identity.  That way, approval could automatically place photos into the correct category based on similarity score, reducing manual intervention.  We'd just need to define and configure that threshold appropriately and tune it by running some rebases after making changes to existing Sisters and Angels prior to a rebase.

This would also probably help the longer term growth and healing so I don't have to exclude low scoring photos manually, as the system could automatically categorize them appropriately based on the defined threshold.  I can always override it and manually adjust whether or not it's part of the core for any pictures in the gallery.  Doing that on some angels would probably also help how things are working.

## Protect Photos

Priority: High
If I protect a photo that is in Review, what happens?  Does that actually accept it into the identity it belongs to, or does it simply prevent it from being removed or rejected?  I need clarity on the behavior of protecting photos in the Review stage.
    - Protect individual photos for an identity

## Reject Photos

Priority: High
If I reject a review photo, what prevents it from returning to the identity on the next run?  I need a clear staged action to reject photos and ensure they are not reconsidered for the same identity.  We probably need to save that in meta-data about a photo which identity it was rejected from.  As I run each run

## Moving Photos

Priority: Low
Could we optimize the selecting for Moving photos to be a two stage drop-down where you first pick the category and then the identity.  It's not a huge deal
```
<!-- markdownlint-enable MD013 -->

Source: chat, Oct 22, 2026; current clarification (verbatim).

<!-- markdownlint-disable MD013 -->
```text
I should be able to update a protected sisters, angel or any identity name - I want to rename a few sisters identity for instance Drakinsa - Sweet Beauty is actuall Amelia Morgan.  Somehow it was mis-named a while ago and I want to try to correct that and verify in the sandbox that renaming works.  There are a few others as well I can test with to see how it works in general.  I also had some feedback in general about the header section and making separate boxes for the image, details and now the actions.  Basically making that section better.  I'm sure you saw that in my feedback.  So I am just curious where everything is at right now.  We really need to address formatting of various areas and separate different types of information, functionality and such into their own sections so it's not all one blended big blob of data.  We don't need to take immediate action, but want to ensure we have those things ironed out and into a plan somewhere.  AND if the plans are overly complex we'd need to break them down into smaller and more managable plans to cover topics.  But if they are inter-related topics they can stay in one plan.  I have some feedback on that as well.  But first, I just want to make sure I can rename a sister properly, even if she's protected.  A rename is still ok.  The protection should prevent "automatic" actions from happening - but not things I want to do manually.  We could always introduce a warning "Draknisa is protected - are you sure you want to xxxxx?"
```
<!-- markdownlint-enable MD013 -->

The recorded-name correction is shipped as described in the
[manual-action checkpoint](2026-10-22-review-actions.md#delivered-checkpoint).
This does not implement every protected manual action; L1-L5 cover presentation.

Source: chat, Oct 22, 2026; broader manual-action clarification (verbatim).

<!-- markdownlint-disable MD013 -->
```text
Basically any identity level manual action should be allowed for all identities.  We just want to gate the ones for protected a little more to ensure I understand it is protected.  One other option would be to have a selection of somekind to enable the actions for protected.  So if they were in a section for actions - I'd see them disabled and have to select something to enable them.  That would prevent always using a pop-up - are you sure.
```
<!-- markdownlint-enable MD013 -->

Source: chat, Oct 23, 2026, 17:29; Artist prototype, intake-detail and storage
authorization. Coverage: L13/L14 Artist boundary/browser, L7/L14 navigation
prototype, L12 single-photo intake drilldown, upkeep U6 exact generated-report
omissions and preserved recovery state. The intake pause remains unchanged.

<!-- markdownlint-disable MD013 -->
```text
Go ahead and do the safe work on the GUI for Artists while I review and if you want to make a simple artists gui - without all the capabilites in the people gallery that's fine - just a basic main page like people and the review page that digs in.  Just focus on basic navigation and if you want to experiement with the header and footer clean-up and organization there you can do that as well for me to review before we adopt those more finished and polished concepts.  We have a write-up on those ideas in one plan - at least some of the basics - so the new artist pages might be good place to try them out before messing with the people gallery pages.  Also you can plan for a more detailed people gallery page that can view the same items we are doing with the intake ... basically if I want to jump into the intage for a single image I'll be able to do that from the people gallery.  The one concern I have is about the generation of all the thumbnails for the pages - so maybe just check on the size of them from as we do the work so we don't overwhelm the disk storage for the gallery - but for now it's fine to do it as long as we're keeping an eye on it because each backup would include them - unless we are also able to exclude them all since they are generated and "should" be able to regent the galleries at any time as long as we have the actual gallery.  That way backups are a bit leaner than what we were doing.  Really focused on the face cache, original gallery photos and placement and metadata about them.  So we can back-track in the event of a major issue.

Really - any work on all the gallery pages is fine - if you feel you're wanting to make consistent headers and footers and such
```
<!-- markdownlint-enable MD013 -->

Source: chat, Oct 23, 2026, 18:08; independent shared-presentation scope.
Coverage: scope clarification above and existing L1-L4/L7; no new competing
intake task or additional matching permission.

<!-- markdownlint-disable MD013 -->
```text
It's a separate item than the intake so you can work across all the pages if that makes creating re-usable pieces for the gallery pages to share easier.
```
<!-- markdownlint-enable MD013 -->

Source: chat, Oct 23, 2026; shared theme and banner (verbatim). Coverage: L16
delivered, L17 review; L7 keeps sticky navigation and tag styling.

<!-- markdownlint-disable MD013 -->
```text
Go ahead and work on the gallery for all the shared .css and other files to make all the gallery pages more professions and consistent.  If you can generate or fine an image that we can use for it that would be cool.  We do have a generate banner art and some other images that we did create with Comfy UI ... I think it's in the comfy output somewhere ... but not sure.
```
<!-- markdownlint-enable MD013 -->

The `.test-temp-library-backup-*` folder that appeared at the repo root on
Oct 23 was test scaffolding left when a helper ran the suite with TEMP inside
the repo; it was deleted. Run tests with the normal TEMP.

Source: chat, Oct 23, 2026, 19:36; restart continuation (verbatim).
Coverage: L7/L16 presentation work above; incoming processing and unapproved
behavioral decisions remain paused.

<!-- markdownlint-disable MD013 -->
```text
Keep on going - we did crash and had to restart - so if you have more to do then keep on going.  I'll be back in a bit to check.
```
<!-- markdownlint-enable MD013 -->

Source: chat, Oct 23, 2026, 20:18; non-intake GUI continuation (verbatim).
Coverage: delivered L8/L9 above. Other GUI layout/actions remain with their
existing owners; unresolved behavioral decisions are not implicitly approved.

<!-- markdownlint-disable MD013 -->
```text
Keep on going with anything you can do that doesn't require the work on the intake image processing that is in our backlog of plans.  I will check back in a while, but making things professional and polished and adding all the missing actions or other features in the GUI is fine to work on.
```
<!-- markdownlint-enable MD013 -->

Source: chat, Oct 25, 2026, 06:26 -05:00; continued GUI work during crop review.
Coverage: Oct 25 reconciliation and L1-L4/L7/L11/L12; action and upkeep boundaries
remain with their existing plans. No additional intake processing is requested here.

<!-- markdownlint-disable MD013 -->
```text
Great - I can review the cropping aspect and if you have any other items to continue with the GUI in terms of all the outstanding feedback that I had captured you can work on anything that is still needed to be done in C:\Soverign-Territories\soverign-territories\docs\plans\2026-10-22-gallery-review-layout.md  In fact, that document need to be ensured it's being kept up to date with all the comments and summaries through the process.  You can scan other plans for missing updates and continue on all the pieces that still make sense to work on while I am doing the image reviews and will get a feedback there.
```
<!-- markdownlint-enable MD013 -->

Source: chat, Oct 25, 2026, 09:13 -05:00. Coverage: this continuation and L12/L18;
structure D1/D2/E2, CLI inventory and tooling-debt D13 retain their own scope.

<!-- markdownlint-disable MD013 -->
```text
Gerat - are there other items in the plans to work on as well - things that don't require my feedback on the intake?  I do also want to make sure we've incorporated the detailed view into all the intake photos from the main gallery pages so it's a fully integrated experience as we pull this all together?  So many good things to do and other work to do as well - from fixing up the code base, to removing or simplifying the cli actions and parameters, just so many things to do across this intake and work process.  The templates and generation will be the next priority when we get ALL this done for the image processing.  We can also review and clean-up all existing docs as I think there's some dated documents or point-of-time documents cluttering our docs as well.
```
<!-- markdownlint-enable MD013 -->

Source: chat, Oct 25, 2026, 09:23 -05:00. Coverage: L19/L12 navigation and
retained detail; intake I21/I23 storage/lineage; manual-action A8 future execution.

<!-- markdownlint-disable MD013 -->
```text
I want it to be a seamless fully integrated GUI experience where you generally start at a main page gallery page and then you can navigate from there and view everything.  If things are in the intake (Various) directory since they haven't bee run through likeness - that is a different gallery than the main persons gallery - but once the files are copied you should be able to incorporate that into the drive-down view of an image to see all the variations that are stored - not any discarded in the intake.  That may include the denoise, lighting and other variations we do still keep until we can decide how to use them.  I have a grander vision of how to use the gallery pages to drive execution of workflows on specific images instead of me having to go to the review pages and then switch to comfy UI, find a workflow and then go and search/load an image and possibly adjust the filename prefix so it goes to a place I want to view it.  So, I'll do a writeup on that as a start later - but that's how I need to be able to test all the enhancements and our intake processing once it lands in a gallery or is still in various for testing.
```
<!-- markdownlint-enable MD013 -->

Source: chat, Oct 25, 2026, 11:35 -05:00. Coverage: run-history continuation
above, L12/L19 navigation and L20 safe pruning. No source processing requested.

<!-- markdownlint-disable MD013 -->
```text
For intake views - it would be nice to have a quick link to one that had some sort of navigation like the overiew and photo review does on the gallery.  Something where each run is a selectable item that then shows all photos underneath.  Instead of the drop-down. It would open that in a new page when clicking the "x runs" link instead of expanding it.  That might make things a little better in the long run.  I like the integrated experience like that for some summary as well.  So that's the type of experience I want.  Even having "intake runs" at the top of the gallery might also be interesting to be able to link to a specific intake run and see the intake overview as well.  I know we'll have a lot of runs - so the filtering of runs needs to not be an issue when we do that.  Basically that will allow me to see the history of runs - which we'll need to prune over time - especially as we're still doing work on the runs.  But I love this concept and how it's coming together.  Keep going - review the work - think deeply about how it's used and make updates as you see need to be made along the way.
```
<!-- markdownlint-enable MD013 -->
