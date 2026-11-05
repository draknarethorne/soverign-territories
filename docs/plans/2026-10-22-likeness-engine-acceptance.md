# 2026-10-22: likeness engine acceptance and production rebuilding

**Status:** active (Nov 5 E18 implementation/tests delivered; E18/E19 saved-case and installed acceptance remain)

**Queue focus:** E18, E19, E13, E14, E15, E16, E17

**Broader scope:** calibration, convergence, the separate incremental batch
and Production remain holding under the resume gate below.

**Resume gate:** consume the accepted cast-rebase baseline and labelled
placement review before calibration/convergence or the separate incremental
batch. Reactivate a narrow proven engine blocker if needed; holding never
waives existing thresholds, protection or Production approval requirements.

## Nov 5: final-audit coverage and Briar Cruz feedback

**12:46 pickup failure:** `postrun-lean-preview2` stopped before writing a
valid preview/install at the final route validator. Final-membership
refinement changed retained cast flags to released without updating
`castSeedDecision`, contradicting the policy evidence. The reported Camaris
photo was an initial core member in the original run; this is evidence
bookkeeping, not proof of an incorrect likeness threshold. Refinement now
updates the release decision/reason while preserving original seed score,
threshold and core evidence. Tests reproduce the contradiction and verify
the corrected transition passes strict route validation; deliberately
contradictory decisions still fail. All 108 focused refinement, routes,
cast, continuation and flow tests pass. No retry or installation has been
started for this correction; actual preview acceptance remains open.

The user selects these bounded investigations before the next full rebase.
Raw feedback and numerical approvals live in
[naming's Nov 5 09:36 source](2026-10-22-identity-family-naming.md#nov-5-0936-approvals-and-next-rebase-feedback-verbatim).
No saved run or source pixels were changed by this analysis.

**09:44 implementation request:** the additional `finalMembershipRefinement`
pass now uses the same core builder and comparison function as final audit,
without acquiring protection during matching. It evaluates retained cast as
well as provisional/preserved rows, removes the own-minimum shortcut in this
additional pass, requires independent destination support and existing
admission/quality/rejection/lock gates, and records bounded pass/oscillation
holds. Final naming follows membership changes. A post-continuity confirmation
blocks installation while qualifying residuals remain and prevents those
photos acquiring new automatic locks. The recap exposes moves and hold reasons.
Focused tests include a Model above its own minimum, an unlocked retained cast
photo, changed cores after a move, exact cast thresholds, locks, pass caps,
oscillation, collision safety and report escaping.
Validation: 81 focused refinement/clean-rebase/recap tests pass; the frozen
library selection passes 47 modules before an unrelated existing
test-inventory guard fails because the unchanged full launcher omits the
existing `test_rebase_flow` module. The two remaining quality/isolation
modules pass separately (20 tests). Routine hygiene/data checks pass.
Do not describe the broader validation command as green.

E18 remains open for all 35 saved-case traces, post-continuity residual review
and C12/C13 integration; E19's mixed Briar scenario remains open. This is
tested implementation, not evidence that the installed run was re-refined.
The user explicitly forbids starting a re-run while review continues.
The [pinned recap's reuse boundary](../recap/2026-11-04-1130-recap.md#nov-5-0944-prepared-input-reuse-no-re-run-authorized)
owns what can be skipped later and the unavailable applied-run replan route.

In `fresh-20261104-lean2`, `higherRivalCount: 270` means only that a final
own score is available and some rival scores higher. It is not a count of
approved moves or wrong identities:

| Disjoint audit reason | Photos |
| --- | ---: |
| Gallery disagreement without protected/anchor/workflow reason | 201 |
| Review/unassigned, not an accepted Gallery member | 64 |
| Protected/anchor/workflow retention reason | 5 |

Only 35 meet `followupCandidate` (Gallery, no photo lock/anchor/workflow
selection, rival lead >=0.10); 20 are cast (16 Sisters, four Angels),
15 non-cast. Even these are flags, not proof of quality/rejection/admission
eligibility. There are 52 higher-rival rows with at least 0.10 rival lead
across all locations/protection states.

Refinement ran two passes, made six moves and no merges, then stopped
`stable`; `nextPassNeeded` is still true in the final audit. "Stable" means
no changes under that refinement's scope/gates, not global convergence.
It operates on provisional candidates, keeps cast references frozen and
skips photos meeting category own-score minima (for example Models >=0.50).
Final audit uses separately rebuilt final Gallery cores, includes retained
cast and Review, and does not run a further reassignment pass. More passes
of exactly the same scope need not change anything.

- [ ] **P1 ai** E18 Verify saved-case and installed final-audit/refinement
  results, including C12/C13 integration; code/tests are delivered, all
  35 follow-up traces and final residual reasons still require evidence.
  Retained implementation contract:
  Nov 5 09:40 clarification: user explicitly requires refinement logic
  aligned with the final audit before that audit runs, not merely a report
  of mismatches afterward. Build shared final-membership comparison evidence,
  evaluate eligible residuals in bounded frozen passes, then run an independent
  final audit over the resulting state. Every residual must have an explicit
  reason (manual lock, rejection, quality, insufficient margin/support,
  oscillation/cap or diagnostic-only resemblance); do not suppress audit
  warnings to claim success. Test cases where a Model passes its own minimum
  but has a qualifying stronger rival, retained cast was outside provisional
  refinement, and final-core rebuilding changes the ranking.
  report all 35 margin-qualified follow-ups with exact blocked/move reasons;
  include retained cast, workflow reset C13 and approved Sisters admission
  C12 without weakening manual protections/rejections/quality. Share scoring
  definitions/frozen references where appropriate; expose differing scopes
  explicitly. Add a bounded final-membership follow-up or explicit per-row
  hold as required by the verified cases, with deterministic ties, pass cap,
  oscillation detection and re-audit. Do not claim convergence from `stable`,
  equate all 270 with errors, or route solely on a tiny higher score.
  Tests must show qualified residuals addressed/held, manual locks respected
  and caps/oscillation clearly reported; E7 broader convergence remains gated.

**Briar Cruz evidence:** the final Model holds 93 photos, including 92
Various arrivals. Initial cluster-to-Sammara score is 0.4692, below the
existing high-cast hold threshold of 0.55, so it became a coherent Model
and inherited Sammara's Cruz surname. Individual initial/final scores are
not the normalized cluster-centroid score. The final audit has usable scores
for 90 photos; Sammara occurs in 84 saved top-three cast lists, scores
0.103610..0.435089, none >=0.50. Omission from a top-three list is not a
zero score. Seventy Briar audit rows report photo protection, requiring
manual-versus-automatic provenance scrutiny before any follow-up.
At 09:40 the user clarifies **many, not all**, are Sammara. Treat this as
photo-level labelled scenario evidence, not identity-wide merge authority.

Verified routing sequence (`planner.plan_candidates`, `classify_category`,
then `refinement.refine`):

1. Each candidate is ranked against frozen cast cores. A best cast match
   goes into the unresolved grouping pool, not directly into cast Review,
   even when its individual score is high. This is not a recorded expulsion
   from Sammara; these 93 sources are one Rina Banks photo and 92 arrivals.
2. Average-linkage grouping at 0.25 builds provisional groups; group-core
   vectors are ranked against cast again.
3. Groups of at most four get the special >=0.40 cast-Review hold; larger
   groups need >=0.55 to trigger high-cast Review. Briar's 93-photo group
   scores 0.4692, so the >=5-photo 0.40..0.55 Model rule applies.
4. Refinement can reconsider provisional members, but skips a Model member
   once own leave-one-out similarity reaches 0.50. Otherwise its cast-Review
   move still needs cast similarity >=0.55 and margin >=0.10 (existing rules).
   Thus a group can keep many strong internal matches despite the user's
   identification of some members as Sammara.
5. Final cores/protection/audit are rebuilt later. Audit reports differing
   scores without moving photos. Automatic final protection is not proof
   that the preceding grouping decision was correct.

No evidence here supports saying one per-photo threshold "kicked them out."
There are different individual, group-size/classification and refinement
gates. E19 must trace them by stable photo ID and generalize the scenario
across cast; do not lower one global number or send the whole group to Review.

- [ ] **P1 ai** E19 Trace Briar Cruz -> Sammara/Adrianna Cruz as a required
  next-run acceptance scenario. Compare representative measured/aligned
  faces, all cluster members, Sammara's frozen cores and per-photo/group
  scores; test detection/preparation, pose/core coverage and rival/margin
  effects. Explain why the group forms separately and why auto-protection
  may freeze it. Use saved measurements first; broader pixel changes require
  targeted proof, not another full intake for diagnosis. Sisters C12 >=0.50
  does not apply to Angel Sammara, and even extending that value alone would
  not admit these saved comparisons. Preview any justified cluster-level
  Review route separately from Gallery auto-accept; do not hardcode a name
  override, globally lower unrelated thresholds, or force-merge a family.
  Gate: measured explanation and explicit justified route/hold before rebase.

## Nov 3: rebase protection and final-membership audit

The 12:46 request selects E13/E14 as narrow prerequisites to a new
Production-source sandbox rehearsal under layout LY10. Broader engine
calibration/convergence and Production gates stay holding. Implementation
records one final frozen-membership audit, top-three rivals, explicit missing
scores, quality/protection/anchor/workflow state, and whether margin-qualified
unlocked Gallery disagreements need follow-up. The audit itself does not move
photos; since 14:17 the E15 refinement pass runs before it, and the audit
reports what remains (no convergence claim). Category trial values are bound
to `--record-core-protection`, with a distinct run policy version; ordinary
policy defaults are unchanged. Independent support, rival and quality gates
still report their holds when the category minimum alone is insufficient.

The [cast plan's approved threshold table](2026-10-23-cast-seeded-library-rebase.md#nov-3-cast-feedback-after-the-fresh-sandbox-rebase)
owns category values. E13 owns acquiring and recording automatic per-photo
protection during rebase, including its provenance, frozen independent support,
manual overrides and exact undo. The user has approved core-only acquisition
and category trial values; do not ask for those same decisions again. Remaining
support/rival/quality gates must be reported explicitly and tested, not silently
replaced by a score-only lock on all folder members. Protected Prospect cores
can participate in a valid same-person merge; protect evidence and preserve
the oldest original identity's name through naming N14, rather than freezing
the entire folder or losing locks during a merge.

The latest [recap feedback](2026-10-22-gallery-review-layout.md#nov-3-fresh-rebase-recap-feedback)
asks whether membership changes cause other photos to be rescored. Do not
claim repeated reassignment or convergence from one initial cast-reference
pass and final classification. E7 remains the bounded-convergence owner;
the following audit must expose residual disagreements before enabling a
follow-up move pass.

- [ ] **P1 ai** E14 Audit every eligible photo against its final own identity
  (leave-one-out) and rival identities after the run. Record score meanings,
  best rivals, margins, evidence/support, core/automatic/manual protection,
  quality exclusions and affected identity IDs. Flag higher-rival scores as
  possible grouping errors, not proof of wrong identity; relatives and
  lookalikes can legitimately be close. Include Drakness/Nyxene, Angelica,
  mixed Prospect clusters and newly formed or changed identities. Expose
  results through recap L23 and record whether another comparison pass is
  needed. Gate: stable final membership and verified features.
- [ ] **P1 ai** E15 Under E7, run a bounded in-place refinement inside the
  rebase plan (14:17 request below): frozen references per pass, existing
  route/merge/category gates, deterministic ties, maximum passes, oscillation
  detection and explicit unresolved outcomes, including identity merges as
  membership evolves. Implemented and unit-tested in
  `likeness_library/refinement.py` (moves, held-Review attach, cast lookalikes
  to cast Review only, reciprocal-best cluster merges with oldest-name
  continuity, reclassification/dissolution, locked/protected/rejected photos
  frozen); evidence is in the plan's `membershipRefinement`, the audit state
  `refined-then-audited` and recap section `refinement`. Remaining: inspect
  the Nov 3 source rehearsal's refinement and audit output, then tune.
  Gate: E14 evidence reviewed against the user's visual review.
- [ ] **P1 you** E16 Decide how released cast photos that re-form their own
  cluster are handled. In the Nov 3 `fresh-20261103-core` preview, retained
  cast members score higher against clusters built from that same cast
  member's released photos: Draknora vs Potentials/Neve Ellery (.61-.66 vs
  own .43-.45), Drakniss vs Models/Vienna Remington, Evangeline Blackwell and
  Fiorella Inglewood (up to .71 vs own .42-.60), Draknara vs Octavia Hensley,
  Fiorella Dunn and Eloise Preston, Drakneta vs Brynn Adler, Draknoxa vs Quinn
  Iverson, Ravaelle vs Models/Lena Easton. 26 of the 38 audit follow-ups are
  this pattern. Options: such clusters go to the cast's Review instead of a new
  identity; raise or lower the .40 core minimum per cast; or accept them as
  separate people after visual review. Gate: user's visual review of these pages.
- [ ] **P2 either** E17 Refinement reclassification demoted Models/Neve
  Ellery to Potentials after it lost one photo (5 to 4). Decide whether
  refinement may lower an identity's category or should keep the category it
  had at the start of refinement (hysteresis). Gate: E16 decision.

## Oct 27: auto-protection note incorporated

`auto_protection_thoughts.md` is covered by E13 below: separately calibrated
own-core/support/rival gates, false-positive holds, persistent manual opt-out,
workflow constraints and recoverable metadata transactions. High similarity
is not identity certainty or permission to freeze all candidates. Draft
implementation exists; threshold acceptance and real self-healing/rebase
tests remain open. No new automatic protection is enabled by archiving this
incorporated note.

### Auto-protection feedback (verbatim)

Source: `feedback/auto_protection_thoughts.md`.

```text
# Auto Protection Thoughts

## Overview

I am wondering if it makes sense with the way we have scoring during the likeness process if we should just auto-protect high scoring images that make the person's likeness together.  Today, they are all candidates, but I don't want to have to auto-protect images that we are certain through the likeness scoring process are a cluster together.  It's really the lower scoring ones that I would not want protected and they could move in/out of galleries based on the normal self-healing and updating process we defined.

## Considerations

- We need to define what constitutes a "high scoring" image in the likeness process and determine the threshold for auto-protection.
- Consider the impact on gallery management and self-healing if high scoring images are automatically protected.
- Evaluate if there are any edge cases where high scoring images might still need to be unprotected or moved.
- Assess the potential for false positives and ensure that auto-protection does not interfere with the normal updating process.
- Determine if there should be a manual override option for auto-protected images in case of errors or special circumstances.
- Consider how auto-protection interacts with other image management features, such as tagging, categorization, and user permissions.
```

## Oct 25, 12:33: evidence-based automatic protection

The user's new direction is to stabilize established identities and qualifying
photos automatically rather than require manual protection on each one. Full
feedback is preserved in [family/naming](2026-10-22-identity-family-naming.md#follow-up-chat-oct-25-2026-1233--0500-verbatim).
This extends protection acquisition; it does not weaken protection enforcement,
approve thresholds, permit production changes or settle rebase migration.

At the planning checkpoint, the draft policy specified protection's blocking behavior, not
automatic score/support acquisition. `0.55` is used by display/merge decisions,
not a calibrated auto-protect gate; five usable photos is a category boundary,
not proof of five independent observations. Family association was disabled.

Implementation continuation: draft `draft-2026-10-25.1` now adds a separate
automatic-acquisition section. Working preview gates are own-core similarity
at least 0.55, rival margin at least 0.10, four independent OTHER core references
and five independently qualifying observations to establish a person. These
are explicit uncalibrated defaults, not inherited proof from category counts.
Self/duplicate support, stale hashes, Review/multiple faces, pending membership
changes and explicit manual opt-outs hold. A person opt-out suppresses new
automatic photo locks. Explicit protect re-enables automation.

Protection and family/name patches share the existing reconciliation metadata
transaction and exact undo, including metadata-only runs. The frozen source
inventory is bound once per transaction rather than repeated in every locked
photo. Automatic locks preserve only already-eligible frozen core members;
they do not create anchors or promote new reference authority. Gallery and CLI
audits share that eligibility helper. The prepared sandbox rebase now migrates
override/name/family provenance through verified one-to-one stable-ID continuity
and refuses ambiguous destinations. No real matching,
protection apply or rebase has run for this feature.

Proposed safety requirements for E13, pending policy approval:

- Assess photos against a frozen, independently supported own-person core;
  prevent self-inclusion and near-duplicate inflation from certifying identity.
  Record recipe/model/core version, source hash, score, rival margin, support,
  policy version and reason. Missing/stale/ambiguous evidence yields a visible
  hold, never success-shaped protection.
- Protect an established person and qualifying Gallery photos; do not blindly
  protect every file in the folder, Review candidates, known rejects or outliers.
  New arrivals to a protected person still respect separately permitted Review
  admission; high score is not permission to alter protected Gallery membership.
- Identity protection, photo protection, core eligibility and identity approval
  stay distinct. Protection does not force core membership or prove identity.
- Define persistent manual-unprotect opt-out before enabling automation, so a
  user's correction is not immediately reversed. Do not overload `false`
  (possibly merely a default) as an explicit opt-out. Preserve workflow-selected
  protection and report conflicts rather than silently bypassing it.
- Plan in shared reconciliation after validated membership, using frozen evidence;
  no mid-pass core growth/protection feedback loop. Preview, recovery, stale
  refusal, apply/undo and idempotent repeat must use existing transaction paths.
  Rebase preserves manual decisions and name/family lineage.

- [ ] **P1 either** E13 Approve photo confidence/support/rival-margin and identity
  establishment gates plus persistent manual override semantics. Review the
  delivered shared policy/schema/provenance and preview/apply/undo against
  labelled cases, including exact boundaries, duplicates, self-scoring,
  protected Review, stale hashes, manual opt-out, workflow conflicts and
  repeat/rebase preservation; automated implementation tests are not calibration.
  Calibrate on labelled sandbox cases before enabling a mutating policy.
  Nov 3: category trial thresholds and automatic persistence during rebase
  are approved in the cast plan; implement that bounded rebase slice with
  boundary tests, distinguish acquired locks from manual locks, and preserve
  Prospect merge eligibility. Other support/quality/rival calibration remains
  open; do not imply the existing installed all-seeds run already recorded
  these automatic photo locks.

The user was unavailable for the first policy question. Working proposal:
explicit unprotect is a persistent opt-out until explicitly re-enabled, including
across rebase. A person opt-out suppresses new automatic photo protection within
that identity but does not clear existing photo locks or workflow-selection
constraints. This is implemented in the draft for review, not a production-approved default.
Do not infer confidence/count values from existing merge/category thresholds.

## Oct 23 foundation-first dependency

[Intake preparation](2026-10-23-image-intake-preparation.md) is Phase 1,
[upkeep](2026-10-22-library-upkeep.md) is Phase 2 and the focused
[cast-seeded rebase](2026-10-23-cast-seeded-library-rebase.md) is Phase 3.
This plan remains the Phase 4 acceptance/production owner. Labelled cases and
boundary inventories may support earlier phases; old raw-input scores/run
counts do not accept a new preparation recipe. Keep the installed `.3` trial
as historical evidence, never silently overwrite it or migrate its scores.

**E4 scope reconciliation:** repeatable scenario infrastructure stays here.
Its optional eligible low-core cast-candidate design/implementation now belongs
to cast plan C1-C7, expanded to explicit configurable seeds, retention/release
and all-image preparation. That portion is transferred, not completed.
Ordinary D14/D15 protection and reset boundaries remain unchanged until
the separately previewed experiment is approved. E6/E7/E8/E10 and production
P1-P6 consume the accepted new baseline; none has passed by this scheduling change.

## Review and questions: 2026-10-22 16:26 -05:00

Activated in the full-plan reconciliation, replacing the umbrella's engine
queue after verified transfer. The
[processing contract](../art/likeness-processing-contract.md) retains D1-D19,
the full ordered flow, safety/source/reset rules and Q1-Q5.
E10 must settle Q1's Model band, Q2's action-specific error/Review targets and
Q3's legacy Model source migration before the affected production decisions.
Q4 Potential naming and Q5 incomplete recorded names belong to family N2/N3.
Ask these individually; no numerical acceptance was invented by this split.
E7's six residual moves remain unapplied and need explanation before claiming
convergence. The source discussions remain preserved, not discarded.

## Scope

One shared policy engine for clean rebuilding and ordinary intake/maintenance.
This plan owns source isolation, policy completeness, labelled calibration,
convergence, the incremental batch, and the separately approved production
clean-full rebuild. It does not own GUI formatting, manual action development,
family metadata, or secondary-model selection.

- [Processing contract](../art/likeness-processing-contract.md#unified-processing-contract-oct-21-reconciliation): approved target
  rules, not a claim of complete implementation.
- [Installed sandbox evidence](../art/likeness-sandbox-trial.md#installed-unified-sandbox-trial-oct-22): actual trial,
  residual proposals and limits.
- [Command guide](../art/likeness.md): shipped commands and safe usage.
- [Family/naming](2026-10-22-identity-family-naming.md),
  [manual actions](2026-10-22-review-actions.md),
  [layout](2026-10-22-gallery-review-layout.md),
  [face analysis](2026-10-22-face-analysis-evaluation.md), and
  [tool structure](2026-10-20-art-tools-structure.md) own their distinct work.

## Current checkpoint

Installed scenario: `unified-rebase-20261022-01` in the sandbox Working tree.
The clean run used an empty cache, 21 cast-only initial cores and 1,155
flattened candidates. It created 16 Models, 35 Prospects and 89 Potentials,
with 55 cast Review additions and 21 Various holds. Reports show 2,667 photos.
The ordinary follow-up preview proposed six physical moves and was not applied.
Synthetic maintenance tests are not labelled real-batch convergence acceptance.
Saved `.3` scenario policy and later `.4` draft must not be conflated.
Production remains untouched; ingest remains paused pending acceptance.

Several former checkboxes mixed implemented mechanisms with unpassed acceptance
gates. Their successors below describe the remaining evidence, not an instruction
to reimplement working code or an assertion that its broader gate passed.

## Remaining work and legacy coverage

Source IDs below refer to the Oct 21 umbrella unless prefixed otherwise.
These are verified transfers of unfinished scope, not completed implementation.

| Live successor | Source open tasks | Remaining scope |
| --- | --- | --- |
| E1 | 0.3a, 0.3c | Complete isolation/reset and unsupported-command boundary acceptance |
| E2 | 1.1, 1.2, 1.3, 1.5, 3.4, 7.1 | Entry points, source roots, caller inventory and regression boundaries |
| E3 | 2.8, 4.1a, 4.3a, 4.3b, 4.10, 4.15, 5.1b | Effective policy, declarative classes, precedence and exported sandbox config |
| E4 | 3.1, 3.3, 3.5, 3.6, 3.7, 3.9 | Repeatable clean scenarios; optional cast-mode execution transferred to cast plan C1-C7 Oct 23 |
| E5 | 4.3, 4.4, 4.5, 4.6, 4.9, 4.12, 4.16, 4.17, 4.18 | Shared grouping/routing/protection/hold contract and full-path tests |
| E6 | 0.4, 4.2, 4.7, 4.19; Oct 19 management L1 | Labelled action-specific targets, quality criteria and error metrics |
| E7 | 4.11, 4.13, 4.20 | Real-batch idempotence, bounded follow-up and final-core verification |
| E8 | 4.14; Oct 19 management L8 | Separate 200+ batch and future category/pairing validation |
| E9 | 3.2, 3.10, 5.1k, 7.2 | Actual-directory viewer, integrated saved diagnostics and explainable destinations |
| E10 | 0.5, 3.8, 4.8, 5.1g | User-labelled gallery acceptance and remaining policy decisions |
| E11 | 1.4, 1.6, 1.7, 7.3 | Engine sunset/caller matrix and approved removal, coordinated with structure plan |
| E12 | 7.4; Oct 20 H5 | Directly related documentation and generated queue |
| P1 | 6.1 | Exact production manifest |
| P2 | 6.2 | User approval of the exact batch |
| P3 | 6.3 | Verified backup and restore |
| P4 | 6.4 | Recoverable production adapter and clean-full installation |
| P5 | 6.5 | User inspection of the resulting library and references |
| P6 | 7.5 | Explicit acceptance before ordinary production ingest resumes |

- [ ] **P1 ai** E1 Verify isolated roots, caches, outputs, workspace access,
  reset allowlists and restore behavior through every supported mutating
  launcher. Reject production paths and unsafe legacy apply flags before writes.
- [ ] **P1 ai** E2 Finish the command/caller and source-root inventory.
  Distinguish new Models from legacy Model aliases; test Artists, Various,
  Gallery, Review, retired/archive/junk, duplicates and unsupported sources.
- [ ] **P1 ai** E3 Audit every behavioral setting against one validated
  effective-policy resolver with provenance and conflict refusal. Verify
  category precedence, supported predicates, overlap/gap errors and data-only
  addition/enablement of a supported class. A viewer config export affects
  only a subsequent explicit sandbox command, never current placement.
- [ ] **P1 ai** E4 Verify repeatable clean scenarios from the same immutable
  snapshot after Phase 3 evidence is available. Consume the cast plan's
  optional candidate mode; do not duplicate its seed/release implementation. Preserve
  per-photo source/hash/destination, names, exclusions, config and timing.
  Keep old names only for continuity after scoring, never as reference seeds.
- [ ] **P1 ai** E5 Complete full-path shared-engine acceptance for frozen
  evidence, appearance subgroups, group-to-group comparisons, singleton/pair
  preservation, four/five-photo transitions, margins/ties and final membership
  classification. Verify selective Review, recoverable grouped holds, proposal
  versus authorization, anchors/workflow protection and distinct category
  permissions without introducing a sandbox-only matcher.
- [ ] **P1 either** E6 Label Fia/Amara, Jacinta/Freya, Sophie, unrelated
  lookalikes, perfect pairs, same-shoot duplicates and poor-face cases.
  Define usable-photo versus repairable/uncertain criteria and action-specific
  precision/recall targets. Measure missed matches, false merges, fragmentation
  and hold/Review volume separately; folder labels are not ground truth.
- [ ] **P1 ai** E7 Explain and test the six residual post-rebase moves,
  including the Uma Merritt hold. Prove bounded no-reset convergence on
  labelled real data with affected-identity merges/splits and final-core
  checks; never infer convergence from draft-disabled moves or cascade
  recursively through established cores without an approved rule.
- [ ] **P1 you** E8 Stage the separate 200+ image batch after the baseline
  review; exercise ordinary intake without reset. Inspect merges, splits,
  promotion/demotion, Review and protected cases. Keep later Demon
  classification/pairing validation explicit rather than assuming current
  tests authorize a new category or automatic swap.
  Oct 23 update: the forthcoming batch is now 400+ images and can include
  recovered uncropped originals from the user's separate storage. Keep their
  import/replacement provenance and preparation version; do not mistake them
  for unchanged already-processed photos or silently overwrite current sources.
- [ ] **P1 ai** E9 Integrate calibration, eligible-folder consistency and
  core-audit outputs into each run manifest and both galleries. Preserve
  independent score meanings, per-photo/person CSVs, exclusions and cold/warm
  timing; diagnostics do not authorize movement.
- [ ] **P1 either** E10 Review actual sandbox placements and score
  presentation, label errors and accept or reject action/category thresholds.
  Resolve remaining source/config decisions before another installation.
  Family acceptance remains separately owned.
- [ ] **P2 ai** E11 Finish the engine sunset/replacement matrix and
  behavior-preserving extractions with the structure plan. Obtain approval
  before visible removals, migrate references and retain excluded-source
  regressions. Do not silently consolidate CLI commands.
- [ ] **P2 ai** E12 Update the command guide, original-photo runbook,
  schema/tool documentation, current status and queue with each accepted slice.

## Production gate: not authorized by sandbox progress

- [ ] **P1 ai** P1 Freeze accepted rules, source scope and approved naming
  output; generate the production clean-rebase manifest from current
  production inputs, retaining provenance and before/after evidence.
- [ ] **P1 you** P2 Approve the exact visual preview and batch, including
  holds, Review, categories, family names, selected/protected photos and exceptions.
- [ ] **P1 ai** P3 Verify a fresh external backup, restore procedure and
  immediate source/hash revalidation before applying any production move.
- [ ] **P1 ai** P4 Implement and run the recoverable production adapter only
  after P1-P3. Use cast-only initialization and flattened candidates with the
  shared engine; never apply sandbox paths or substitute category-only moves.
  Verify conservation, histories, catalogue references, Review and undo.
- [ ] **P1 you** P5 Inspect refreshed production galleries and ComfyUI
  references; report false assignments or missing history before the next batch.
- [ ] **P1 either** P6 Explicitly accept the guarded incoming path before
  resuming ordinary production photo ingest.

## Closure

Close only after labelled clean and incremental acceptance, approved production
rebuilding, verified recovery and user inspection. Task transfer is not evidence
that any of these gates passed. Historical source words and execution records
remain preserved in the retired records. This successor is active after
context/task transfer verification; durable rules and evidence are in the
live references linked above. No production apply is authorized by archival.

## Nov 3: audit and refinement follow-up

The user asks whether final auditing and affected-image re-comparison can
improve assignments. Yes: newly formed or changed cores can change the best
supported destination after the initial frozen matching pass. E14 records
those disagreements; auditing alone does not change galleries. E15/E7 owns
bounded affected-identity follow-up, using verified existing measurements
instead of repeating intake, frozen references per pass, existing routing/
merge/split and protection gates, deterministic ties, a pass limit and
oscillation detection. Only accepted moves change membership/history and
refresh derivatives, processing links and galleries; ambiguous cases remain
explicit Review/diagnostic outcomes. A higher rival score alone is not enough,
especially for relatives/lookalikes. This question does not independently
authorize an automatic follow-up recipe or a competing run; inspect this
source rehearsal's audit first.

### Follow-up question (verbatim)

<!-- markdownlint-disable MD013 -->
````text
It almost seems like an audit is necessary after the run to look for instances where things do seem mis-aligned and we'd want to figure out what to do with those images in the process or re-run them through the likeness again to see where they land?  Basically, iterating and auditing and refining any assignments.  Would that make sense or not end up actually having any impact no the galleries, assignments, and such?
````
<!-- markdownlint-enable MD013 -->

### Nov 3, 14:17: bounded refinement in place

The user authorizes automatic refinement applied in place after rebase
routing, including identity merges. Implementation runs inside the plan
before naming, so install, undo, history and recap use the refined plan; the
final audit then reports what remains. Rules: one pass freezes provisional
cluster cores and fixed cast cores; a photo moves only if the existing
`auto-route` gate passes for a cluster (cast gains go to the cast's Review
folder, never straight into a core gallery); category-protected cores,
anchors, workflow inputs and rejection history stay put; a reciprocal-best
pair merges only when similarity reaches the survivor category's merge
minimum with the route margin, every loser photo meets the route minimum and
the loser has no locked or rejected photos; the larger cluster survives and
naming keeps the oldest original name. Passes stop when stable or at four.

<!-- markdownlint-disable MD013 -->
````text
I want to see the bounded automatic refinements working in place so that after a rebase - we believe that it's as clean as it's going to get.  This could also include merging more identities as the identities evolve.  It's not just where do individual photo's go - but do we end up realizing that two identities are now the same when images move in/out in this last phase of the likeness.
````
<!-- markdownlint-enable MD013 -->
