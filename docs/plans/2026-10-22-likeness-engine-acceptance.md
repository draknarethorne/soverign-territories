# 2026-10-22: likeness engine acceptance and production rebuilding

**Status:** holding (engine contracts/calibration backlog; current acceptance transferred)

## Milestone transfer record

Nov 5 16:45: E18/E19 execution transfers with the same IDs to the
[reset spine](2026-11-05-priority-reset.md#execution-spine).
The full saved-case contracts, rules, decisions and evidence below remain
the technical reference; no code/scenario acceptance is inferred by moving
the checklist. Other engine/calibration/Production tasks stay holding
until the spine selects a specific dependency or later milestone.

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

**Transferred contract: E18 -> [reset E18](2026-11-05-priority-reset.md#m1-execution-and-transfer-ledger); completion tracked only in the spine.** Verify saved-case and installed final-audit/refinement
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

   **Nov 6 stable-ID continuity:** all 93 original Briar rows now land in
   the 96-photo `Models/Noelle Cruz` Gallery in installed preview3. Their
   saved final dispositions are 70 automatic-protection holds (not manual
   locks), 16 with no higher rival, four insufficient-margin holds and
   three ineligible single-face measurements. Across the complete 96-photo
   Noelle cohort, 83 saved top-three cast references mention Sammara,
   0.112203..0.432019; none reaches even the proposed Angel Gallery 0.45.
   That is not a claim about missing top-three scores or human identity.
   Lowering the Gallery-specific gate alone cannot resolve the user's
   many-but-not-all correction. Carry all 93 stable IDs into the next
   comparison and preserve per-photo protection/rival/quality dispositions;
   do not force the entire identity into Sammara or call this human-verified.

   No evidence here supports saying one per-photo threshold "kicked them out."
There are different individual, group-size/classification and refinement
gates. E19 must trace them by stable photo ID and generalize the scenario
across cast; do not lower one global number or send the whole group to Review.

**Transferred contract: E19 -> [reset E19](2026-11-05-priority-reset.md#m1-execution-and-transfer-ledger), not completed.** Trace Briar Cruz -> Sammara/Adrianna Cruz as a required
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

## Nov 6 follow-up: core coverage and unresolved destinations

E19 now additionally owns a saved-measurement comparison of Noelle's
96 photos against Sammara's 15 frozen seed-core photos and remaining
Gallery members: normalized core versus best individual reference,
core coverage, quality/preparation, protection and route/merge gates.
Scores do not establish alteration or human identity. Do not silently add
unreviewed Noelle members to Sammara's core or force a whole-group merge.

The separate preview's 40 Various Review photos divide into 21 ambiguous
cast candidates and 19 quality-ineligible photos (16 multiple-face,
one no-face, two too-small). This routing question is distinct from the
199 total Review photos across all folders. Compare one explicit
candidate-Review destination with retained rival/uncertainty evidence;
quality-ineligible photos cannot inherit an invented measured identity.
Any changed destination policy needs an explicit rule, tests and a
separate preview; installed receipts remain immutable. The existing
report-verification/publication closeout stays first.

### Measured Noelle/Sammara core coverage

The read-only
[comparison with exact recognizer crops](file:///B:/Sovereign%20Territories%20Sandbox/Working/_reports/library/policy-previews/2026-11-06/noelle-sammara-diagnostic.html)
and [structured evidence](file:///B:/Sovereign%20Territories%20Sandbox/Working/_reports/library/policy-previews/2026-11-06/noelle-sammara-diagnostic.json)
bind preview4, the original saved cache and installed catalogue by SHA-256.
All 153 displayed observations have verified prepared-input bytes; 152
have verified exact aligned-face PNGs, and the no-face case explicitly
has no alignment. The browser loads all 392 image elements without a
broken image. Only the strongest pair's crops were visually inspected;
this is not visual identity acceptance of the whole cohort.

Of Noelle's 96 Gallery photos, 93 satisfy the final single-face quality
gate; three contain multiple detected faces. Reconstructing centered,
normalized vectors reproduces all 84 saved Sammara top-three references
within `4.967e-7` rounding error. The initial frozen core has 15 references;
the final core has 17. Maximum eligible Noelle similarity rises only from
`0.432019` to `0.437214`: none reaches the current Angel Gallery minimum
of `0.45`, before considering margin or protection.

Best-individual-reference comparisons rule out averaging as the only
explanation: of 93 eligible photos, 12 reach `0.40`, three reach `0.45`,
one reaches `0.50`, and none reaches `0.55` against any initial seed.
The two additional final references do not increase the count reaching
`0.45`. These pair scores are diagnostics, not substitutes for core-based
Gallery admission. The strongest three pair matches are still closer to
their own Noelle core. Removing automatic protection alone cannot fix
the current core-score shortfall.

The prior group/protection trace still applies: provisional-cluster merges
do not wholesale merge a Model into a fixed cast identity. Low similarity
does not prove alteration or a different person. Next calibration needs a
small human-labelled positive/negative subset, not an arbitrary global
threshold reduction or adding all Noelle photos to Sammara's core.

The diagnostic also exposed a recap evidence defect: collection read only
top-level `coreReferences`, but actual final references are nested in
`finalMembershipAudit`. The recap now prefers the final ordered records,
including an explicit empty list, with legacy records/seed flags retained
for older runs. Two regression tests first fail; all 25 recap tests then
pass. Both real recaps are regenerated through the supported launcher's
preview/apply/check without changing receipt, catalogue or cache bindings.
Overview/Photo review readers are untouched; this report-only module is
not part of their freshness dependency set.

### Remaining Various destination decision

All 21 quality-eligible Various holds have final per-photo cast references,
but their best scores range from `0.258221` to `0.471198`; only four
reach `0.40`. The group-level best cast agrees with the final per-photo
best in only 10 of 21 cases. A close group-level match is not a strong
individual match, and blindly routing by the group label would be
misleading.

One tentative best-candidate cast **Review** destination could retain the
runner-up, score and explicit uncertainty without Gallery/core admission.
However, routing all 21 this way would intentionally accept weak candidate
destinations below existing matching gates. Obtain the user's focused
choice before changing that behavior. The 19 quality-ineligible photos
need a distinct quality/provenance disposition, not invented measured
identities. No destination-policy change, new replan or installation has
occurred in this diagnostic.

## Nov 8: Angelica/Freya Review attribution

The user asks whether enabling easier Angel/Sister Gallery acceptance
also expanded Review. This read-only analysis compares all 3,290 stable
photo IDs, not totals alone. No photo, policy, receipt, cache or viewer
was changed, and no intake, matching replay or installation was run.
This extends E19's group-versus-photo investigation; it is not identity
acceptance or approval for a new routing rule.

### Separate the three baselines

| Saved run | Total Review | Angelica Gallery | Angelica Review | Freya Hadley photos in Angelica Review |
| --- | ---: | ---: | ---: | ---: |
| Original saved-intake matching result, `fresh-20261104-lean2` | 266 | 31 | 35 | 6 |
| Installed `postrun-lean-preview3` | 230 | 30 | 55 | 6 |
| Uninstalled `postrun-review-preview8` | 199 | 41 | 45 | 6 |

Latest admission/family change, installed preview3 to preview8:

- All 3,060 Gallery photos remain in Gallery; two change from a non-cast
  Gallery into Angel Gallery. **Zero Gallery photos enter Review.**
- Thirty-one Review photos enter Gallery; 199 stay in Review, with
  **zero Review-owner changes** among those remaining.
- All 33 additional Angel admissions reconcile: 29 Angel Review, one
  Sister Review, one Various Review, one Model Gallery and one Prospect
  Gallery. Sisters retain 78 admissions; the total staged admissions rise
  from 78 to 111.
- Every cast slot's Review count stays the same or falls. Angels fall
  104 -> 75, Sisters 85 -> 84, Various 41 -> 40.
- Angelica gains 11 Gallery photos: ten from her existing Review and one
  from Drakniss Review. She gains no new Review photos or former Gallery
  demotions in this comparison. Her total grows 85 -> 86 only because of
  that one cross-slot Gallery admission.

The older original-result-to-installed-preview3 comparison is different:
83 Review photos entered Gallery, **47 Gallery photos entered Review**,
and 183 stayed in Review. Twenty of those 47 new holds went to Angelica:
nine originally Angelica, seven Jacinta Alden and four Fia Hadley.
Thus lower net Review totals did hide earlier Gallery-to-Review traffic.
Freya's six were already held in the original result, not among these 20.

The older continuation included workflow selection reset and changed
core/protection/refinement behavior, not just easier admission. The
receipt records reset mode `all`; for example Angelica's previous selected
photo `image_7513773530805044436` was originally retained solely as
workflow-selected, then released and regrouped. Fia/Jacinta's earlier
Model group had saved cast score 0.5139; the later group containing
released Angelica candidates has 0.5551, crossing the unchanged 0.55
group-Review boundary. This identifies the changed seed/group context,
not an isolated counterfactual proving which individual reset caused
every one of the 47 changes.

### What actually changed in the latest policy

The complete installed-preview3-to-preview8 policy diff is:
Angels `galleryAdmissionEnabled=true` and explicit Gallery minimum 0.45;
Sisters explicit Gallery minimum 0.50 (same effective minimum as before);
secondary surname inheritance disabled; and the policy version.
Runtime `settings` are equal. The Review rules did not change:
high group similarity >=0.55, small groups of up to four at >=0.40,
and cast Review destination margin >=0.10.

Commit `0ead7c186` changes `evaluate_cast_admission`, not
`classify_category`'s Review thresholds. A focused execution of the
eight-photo, 0.5925 classification against all three saved policies
returns the same Angelica Review result. That fixture supplies margin
0.10 to isolate the policy boundary; it is not a reconstruction of the
original group's exact runner-up margin.

### Why Freya goes to Angelica despite weak individual matches

All six Freya photos share saved cluster `f7d685f303de16a3` with one
released Angelica photo and one Various photo. The eight-photo group's
saved Angelica score is **0.5925** in all three receipts. The planner
classifies its normalized group/core representation against cast,
crosses 0.55 and gives every group member the same cast Review owner.
It does **not** require each member to independently clear a per-photo
cast-Review score or all-category rival margin at that boundary.

Initial and final photo scores must not be substituted for that group
score. Here are the saved final Angelica scores against the final core:

| Stable photo ID suffix | Final Angelica similarity | Final Angelica lead over strongest other identity |
| --- | ---: | ---: |
| `image_7518040364541922309` | 0.372602 | -0.049225 |
| `image_7518040823226708895` | 0.339679 | -0.033080 |
| `shot_20261019151807` | 0.198142 | -0.091997 |
| `shot_20261019152007` | 0.381498 | 0.000678 |
| `shot_20261019152019` | 0.316649 | -0.045029 |
| `shot_20261019152059` | 0.490720 | 0.086539 |

None qualifies for Angel Gallery under the separate >=0.45 score and
>=0.10 all-category margin gate. Four have a stronger non-cast rival;
the other two fail score and/or margin. The strongest photo clears the
score minimum but not the margin. These are likeness measurements, not
proof that the photos are Angelica, Freya, altered, or different people.

The group hold also persists: final membership refinement explicitly
holds Review/unassigned members pending admission, and `_admit_cast`
only changes a destination after an `admit` decision. A failed Gallery
admission leaves the earlier group-derived Review association intact;
it does not repair it or return the photo to its historical identity.
The reason text "high cast similarity" describes the **group**, although
it reads like a claim about each individual photo.

### This is broader than one example

All 45 remaining Angelica holds are quality-eligible in the final audit.
Thirty-three have final own-cast similarity below 0.40, and 24 have a
stronger non-cast best candidate. Origins: 16 Angelica, eight Jacinta,
six Freya, four Fia, eight Various and one each Ariadne, Arwen and Bea.
Thirty-four carry the high-group-similarity reason; 11 the small-group
resemblance reason.

Across all cast Review, 159 holds remain: 85 high-group and 74 small-group
resemblance reasons. Of the 157 final-quality-eligible holds, 112 have
own-cast similarity below 0.40 and 60 have a stronger non-cast best
candidate. These counts describe the unresolved association problem;
0.40 is a diagnostic band here, not a newly approved per-photo threshold.

**Disposition:** the latest Gallery relaxation did not open a new Review
door, but the older group-to-cast Review rule can over-associate weak
individual members, and reducing net totals was insufficient acceptance.
Do not install preview8 as a resolution of this concern, revert safe
Gallery admissions merely to hide it, lower Gallery gates further, or
return all held photos to historical owners as if those were ground truth.
The next focused proposal should separate:

1. Group resemblance/candidate evidence from an actual per-photo cast
   Review association, including non-cast rivals and explicit uncertainty.
2. Admission-only changes (require no new Gallery-to-Review or remaining
   Review-owner changes) from deliberately approved quality/core releases,
   which need their own before/after cohort accounting.
3. Failed admission from final disposition: keeping an uncertain photo
   unresolved must not imply a verified cast identity or invent a new one.

Any different destination/threshold needs a separately agreed rule and
saved-input comparison. Merely moving holds back to Various or renaming
Review would not reduce actual human uncertainty. Dedicated Review
association calibration remains open under E19; no new rule is activated.

Receipt SHA-256 bindings:

- Original result: `ecb91eafc362511cd72e515a224aa69015bb4624f518206bff8b7b200c204cdb`
- Installed preview3: `60679f89990ce4e395a9c2cfb7863c017204f2e735d6883c46d74079575987f3`
- Preview8: `e9d95427b1db8748565b0ba5e7c42fd912f1ee10fb452e246f912c5f72076a10`

## Nov 8: extended chronology, naming and clean-rebase question

The user's follow-up correctly challenges the limited comparison above.
There "original result" meant `fresh-20261104-lean2`, not the earliest
trial. Historical receipts now establish that Freya **was** a separate
Model before the Nov 4 LEAN runs. Looking only at preview3 -> preview8
could not identify when that changed.

### Historical route timeline

| Run name (not local completion date) | Matching photos | Initial cast policy | Angelica Gallery / Review | Freya's six destinations | Freya group score | Lujan non-cast family members |
| --- | ---: | --- | --- | --- | ---: | ---: |
| `fresh-20261102` | 2,814 | all cast retained | 61 / 14 | Models/Freya Hadley Gallery | 0.5056 | not recorded |
| `fresh-20261103-core` | 2,814 | cast cores plus then-retained selections | 28 / 23 | Models/Freya Hadley Gallery | 0.5003 | not recorded |
| `fresh-20261104-lean` | 3,517 | cast cores plus then-retained selections | 29 / 50 | Angelica Review | 0.5938 | 26 |
| `fresh-20261104-lean2` | 3,290 | cast cores plus then-retained selections | 31 / 35 | Angelica Review | 0.5925 | 31 |
| Installed `postrun-lean-preview3` | 3,290 | cast cores, workflow reset all | 30 / 55 | Angelica Review | 0.5925 | 29 |
| Uninstalled preview4 through preview8 | 3,290 | cast cores, workflow reset all | 41 / 45 | Angelica Review | 0.5925 | 7 |

Preserved Nov 2/3/4 receipts live in
`Working\_reports\reset-review-bundle\rebase-runs`, not their retired run
folders. The Nov 3 recap records an actual reset from Production, without
the preceding rebase outputs as input. Nov 2/3 matching receipts have
missing IDs on some unrelated records; comparisons of their full input
populations therefore use unique source paths, not a dictionary that would
collapse missing IDs. All six Freya IDs are present and stable throughout.

**First observed transition:** Nov 3 core -> Nov 4 LEAN. The six-photo
Freya group becomes eight photos by joining:

- released Angelica `shot_20261019152041`;
- incoming Various `shot_20261023110958`.

The group's score crosses the **unchanged** 0.55 cast-Review threshold.
The six Freya original and selected-prepared SHA-256 values are unchanged
across every receipt above. This is not evidence that the later performance
fixes reprocessed Freya differently. At this transition the input grows by
703 rows, 101 common-source original/prepared bindings change, the saved
centering mean changes and Angelica's recorded initial core membership
changes from 27 to 28 photos. The planner and first-refinement implementation
hashes are identical across those two receipts; relevant score, clustering
and core thresholds and runtime settings are also equal.

At the receipt-only investigation stage this identified a changed input/
reference/group context, not an isolated cause. The subsequent
[saved-vector ablations](#nov-8-causal-probes-two-distinct-candidate-bridges)
below recover the relevant historical vectors through their SHA-256
alignment bindings in the surviving cache and isolate the candidate bridges.
This does not recover the complete original input/cache tree.
The 3,517-row run also included exact duplicates;
the later 3,290-row run corrected alias intake, so those rows are not all
distinct new photos or identities. Surnames and count totals are not
sufficient identifiers for this comparison.

### What happened to the old workflow photo

The recorded old Angelica selection is
`photo:image_7513773530805044436`, not
`photo:shot_20261019152041`. Its actual visual identity is not established
by the user's tentative Freya attribution or by these measurements.

- Nov 3/4 receipts mark it `castSeedCore=false`: it was kept in Gallery
  because it was workflow-selected, not because it qualified for the
  initial scoring core.
- Preview3 resets that selection, removes selection-only retention, and
  releases it to ordinary matching. It lands in Angelica **Review** in
  cluster `cac88bd590615b5b`, group score 0.5551.
- Preview4 through preview8 leave it **in Review**, with
  `castSeedCore=false` and `castSeedWorkflowSelected=false`. It did not
  return to Gallery or become an initial seed during the performance runs.
- The different Angelica photo `shot_20261019152041`, from Freya's
  eight-photo group, does enter Gallery in preview4 onward under the
  separately enabled admission gate. That is a real later return of a
  different photo, not proof the old workflow selection was resurrected.

Removing a workflow photo from initial reference evidence is not deleting
it from the dataset. It remains a candidate and can form a group under
the same rules. Also, current centering uses all usable input faces,
not only the cast seed faces. Thus "not a core seed" must not be reported
as "cannot influence any matching calculation." Excluding it entirely
from the population would be a different, unapproved behavior.

### What the continuations actually reuse

Direct receipt and seed-file checks for preview3 through preview8 find:

- All six completed continuations reference **the original**
  `fresh-20261104-lean2`, not the preceding preview.
- Every seed catalogue is the same empty catalogue: zero people, photos
  and actions, SHA-256
  `3d181f272d6c783f4ce369b902f66ffdc90f2171d55a59f9a3ee61e65b5c4fce`.
  Generated memberships, family names and automatic protection are not
  carried in as identity seeds in these actual runs.
- Configuration snapshots match; all reset mode `all`; all have exactly
  the same 1,041 recorded initial core photo IDs, all from Angels/Sisters.
  No reset old selection without manual protection occurs in that set.
- The immutable matching source paths, original/prepared bytes and saved
  measurements are reused, but the code recenters the population, builds
  cast cores, clusters candidates, refines, admits, then names them again.
  Original folder names support provenance/name continuity, not initial
  non-cast face-reference cores.
- No source input is cast Review; no resulting route is a retained-source
  cast-Review hold, an explicit named-person override, or a protected/
  workflow candidate-preservation route. The current 199 holds were not
  imported from installed Review just because the folder existed.
- `postrun-lean-preview` and `postrun-lean-preview2` have no completed
  `run.json`; they are failed attempts, not intermediate accepted
  membership baselines. Continuation rejects chained sources and incomplete
  reuse rather than treating those attempts as success.

Three existing focused tests pass: original-pixel continuation/install
isolation, generated family/name/automatic-metadata exclusion from seeds,
and explicit manual-photo protection rebinding. These do not replace a
full independent clean-install equivalence trial, but support the actual
receipt evidence against the stale-generated-seed hypothesis.

### Where family naming fits

Nov 4's requested resemblance surnames were implemented after membership
planning, using the yellow band (0.30) and transitive peer connections.
That explains Lujan's connected-family explosion; a family was never meant
to assert one identity. Later direct >=0.40 / peer >0.35 rules and finally
direct-only surname inheritance reduce Lujan 31 -> 29 -> 7 in the
3,290-photo sequence.

The same period also changed the input population, selection resets,
core/protection and admission rules. These were not a naming-only
controlled experiment. However, the actual family application changes
non-cast presentation names after routing/admission, not the cast folder
or bucket of the six Freya photos. The unchanged planner and explicit
group evidence put their first transition before surname assignment.
Later empty-seed continuations do not feed generated surnames or their
automatic locks back into initial matching. This does not claim that every
historical tool or a future rebase from current Working is equally isolated.

### Revised conclusion and safe next execution gate

The user's recollection of earlier separate identities is correct, and
the first answer's time window was insufficient. Multiple workstreams
obscured which input/policy/identity change each run represented. The
evidence does **not** show the later performance continuations retaining
old generated clusters or restoring this workflow photo as an initial
seed. That rules out one mechanism, not the workflow photo's influence
through candidate grouping: the subsequent causal probes below demonstrate
that second mechanism for Fia/Jacinta, separately from Freya's earlier shift.

A clean end-to-end rebase is appropriate as final acceptance **after**
the association/seed contract is fixed and frozen, not as a speculative
way to clear a rule-driven result. With the same inputs, measurements,
cores and rules, rebuilding them again is expected to reproduce it;
fresh preparation is not yet demonstrated necessary. Before execution:

1. Freeze one input/alias manifest and explicitly identify the allowed
   Angel/Sister reference photo IDs. Exclude old workflow choices as
   choices, preserve only explicitly approved manual exceptions, and
   verify actual eligible seed membership rather than assuming an
   automatically inferred core is human-correct.
2. Resolve group-level resemblance versus individual cast-Review
   association, plus any per-photo Gallery-return concerns. Compare all
   affected cohorts, not just Angelica or Lujan, without inventing identities.
3. Perform an independent clean matching/publication rehearsal without
   generated non-cast membership/family/protection seeds, with workflow
   reset explicit; compare against the saved-input result by stable IDs,
   seed membership and exact pixels. Preserve the installed baseline
   until the guarded replacement is ready; never use current Review
   folders as presumed ground-truth seeds.
4. Separate semantic policy changes from performance-only changes and
   require exact route equivalence for the latter. Record every new Review
   entry, exit, cast owner and workflow-photo disposition, then verify the
   actual viewers. Do not equate lower net Review totals with acceptance.

This is the investigation and execution gate, not authority to start full
intake or overwrite the sandbox now. No image, policy, seed, runtime code,
cache, receipt or installed catalogue changed for this analysis.

Additional historical receipt SHA-256:

- Nov 2: `4b7a9ff2d3ccdbe04892f980c59b88cb3a1bec81274d075eea3c2adf57654431`
- Nov 3 core: `68d5dbaf93bfe6b68ee86a19ac898b23834d390957e69c842924e129704da931`
- Nov 4 LEAN: `bf1cb7414021a289d3a2739163ed20c599e503e3bbfd1d6f25edfff0daf94a08`

## Nov 8 causal probes: two distinct candidate bridges

The user's 21:39 follow-up asks for an explanation of the previously
verified separation, not another statement that the final reruns agree.
The earlier answer was incomplete: **excluding a photo from cast reference
cores does not stop that photo joining a candidate group and changing where
the other members are routed.** That is now demonstrated, not hypothetical.
No routing change or live rebase was performed to obtain these results.

### Locate the user's known-good review

The preserved [Nov 4 family request](2026-10-22-identity-family-naming.md#nov-4-chat-family-names-after-the-fresh-20261103-core-review-verbatim)
explicitly says the user was happy with Fia/Freya falling out of Angelica
as Models and wanted surname relationships. The core-trial receipt agrees.
That is the accepted separation the investigation must explain losing.

The preserved [Nov 5 workflow-reset request and approvals](2026-10-22-identity-family-naming.md#nov-5-0908-chat-family-cast-admission-and-workspace-reset-verbatim)
postdate the Nov 4 family implementation. This distinguishes the earlier
core-only trial from the later reset-all-selected-photos implementation.
In the earlier trial Angelica's selected photo already failed core
eligibility, but selection-only retention still kept it in her Gallery.
The later reset actually released it into the common candidate pool.
There is no completed retained receipt in this sequence showing reset-all
with Fia/Jacinta still separate; that does not invalidate the user's
earlier successful core-trial review.

### Probe method and limits

The surviving `fresh-20261104-lean2\likeness-cache.json` has face vectors
bound by `alignmentEvidence.sourceSha256`. These bind to selected-prepared
SHA-256 values in the historical receipts, not current filenames or later
folder labels. All 27 old and 28 new Angelica initial core vectors and
the relevant Freya/bridge vectors are available. Of the full Nov 3
population, 102 selected-byte bindings are unavailable, so no complete
Nov 3 replay is claimed.

The read-only diagnostic reconstructs each recorded centered vector as
`normalize(rawVector - recordedMean)`, then reconstructs the recorded
initial cast reference from its `castSeedCore` IDs. It runs the actual
planner and average-linkage grouper, without naming, final-membership
refinement, Gallery admission, publication or model loading. It asserts
the baseline cluster IDs, scores, Review destinations and relevant complete
group membership against the actual receipts before accepting a
counterfactual. Diagnostic names are placeholders, not proposed renames.

For each candidate-removal probe, the saved mean, all cast reference
vectors, every other candidate and policy stay fixed. Thus an observed
change isolates candidate participation rather than fresh detection,
centering drift, revised thresholds or family surnames. It is not a
proposal to delete those photos or a full install-equivalence test.

### Transition A: Freya changes in the first Nov 4 LEAN run

The incoming Various photo `photo:shot_20261023110958` was absent from the
Nov 3 receipt by stable ID, original SHA-256 and selected-prepared
SHA-256. It scores 0.863136 against the already released Angelica photo
`photo:shot_20261019152041`, using the Nov 4 saved mean. This is measured
resemblance, not proof they depict the same person.

The full Nov 4 candidate-pool probe proves the grouping effect:

| Fixed Nov 4 reference/policy context | Candidates | Freya group | Group-to-Angelica score | Initial planner result |
| --- | ---: | ---: | ---: | --- |
| All actual eligible candidates | 2,418 | eight | 0.5938 | Angelica Review; exact recorded group `f7d685f303de16a3` |
| Remove only new Various `shot_20261023110958` from candidate participation | 2,417 | original six | 0.5063 | Separate Model; exact original group `3c798cab0d46106f` |
| Remove that photo and released `shot_20261019152041` | 2,416 | original six | 0.5063 | Same separate Model |

With the bridge absent, `shot_20261019152041` participates in a different
group (`349379d171140879`, score 0.8318), not Freya's. Average-linkage
chooses from the whole candidate pool: adding a strong neighboring photo
can change which grouping wins. A calculation restricted to only the
six or eight displayed photos is insufficient to reconstruct that choice.

Separate numerical ablations isolate score effects once membership is
known:

| Membership / reference / mean | Exact group-to-Angelica score |
| --- | ---: |
| Freya six, old 27-photo Angelica core, old mean | 0.500323813 |
| Same six, new 28-photo core, new mean | 0.506312236 |
| Eight members, old 27-photo core, old mean | 0.587653390 |
| Eight members, new 28-photo core, new mean | 0.593786623 |

Both historical rounded scores reproduce. Mean/reference changes alone
leave the six below the 0.55 cast-Review gate. The membership expansion
crosses it even with the old core and old mean. The changed initial
Angelica core adds `shot_20261019151900`, **not** the workflow selection.
The old workflow photo is neither in those initial cores nor in Freya's
eight-photo group.

### Transition B: the workflow reset joins Fia and Jacinta in preview3

This is the missing workflow-photo effect. After the reset releases
`photo:image_7513773530805044436` as a candidate, the planner forms group
`cac88bd590615b5b` containing:

- all ten photos in the earlier Fia Hadley Model group;
- all seven photos in the earlier Jacinta Alden Model group;
- the old workflow selection itself;
- another released Angelica photo, `shot_20261019151745`.

The **19-photo group's** score is 0.5551, just above the unchanged 0.55
gate. The planner routes the whole group to Angelica Review. It does not
require each photo to qualify individually for that cast association.

| Fixed preview3 reference/policy context | Candidate participation | Fia / Jacinta result |
| --- | --- | --- |
| Actual 2,230 eligible candidates | Old workflow photo included as ordinary candidate | Exact recorded 19-photo group, 0.5551, Angelica Review |
| Same context, omit only that one candidate | Other 2,229 candidates and every cast core unchanged | Fia ten stay separate Models, 0.5139; Jacinta seven stay separate Models, 0.4136 |

The second probe restores the original ten/seven membership IDs and group
IDs (`5a2e0bcdf6544080` / `4c8dce9f6230e1b5`). Angelica's initial 30
core IDs are identical between lean2 and preview3: this particular change
does not need her core to be contaminated or restored. The suspect photo
influences the result **as a candidate bridge**, despite successful initial
core exclusion. No change to its mean contribution is made in this probe.

This means the workflow reset did have an unintended grouping consequence
in the direction the user objected to. The earlier conclusion that it
never returned to the core was true but insufficient, and should not have
been used to imply it could not pull other photos back toward Angelica.

### Cohort history, without relying on changed surnames

These are the fixed membership IDs from the Nov 3 destinations, not
same-name folders assumed to mean the same membership in later runs:

| Nov 3 cohort | Nov 3 core | Nov 4 LEAN and lean2 | Installed preview3 and preview8 |
| --- | --- | --- | --- |
| Freya Hadley, six | Separate Model | Six Angelica Review | Six Angelica Review |
| Fia Hadley, ten | Separate Model | Separate Fia Vale Model | Ten Angelica Review |
| Jacinta Alden, seven | Separate Model | Separate Jacinta Vale Model | Seven Angelica Review |
| Arwen Preston, five | Separate Prospect | Four remain outside cast, one Angelica Review | Same four outside cast, one Angelica Review |

Thus there was not one moment when "the Hadleys" all returned. Freya
changed in the family-era full run with new input; Fia/Jacinta stayed
separate through both LEAN runs and changed in the later workflow-reset
continuation. Later performance-only previews preserved both decisions.

A bounded screen of common non-null stable IDs also finds 47 former
Gallery photos entering cast Review across **11 cast destinations** in
Nov 3 core -> first LEAN: Angelica 13, Drakniss nine, Draknoxa eight,
Draknara five, Camaris three, Sammara/Ravaelle/Draknava two each, and
Drakness/Nyxene/Remiah one each. Examples include six Evangeline Blackwell
photos -> Drakniss and five Quinn Iverson photos -> Draknoxa. This is not
an exhaustive all-input accounting or proof those cohorts share Freya's
specific bridge cause; their causal ablations remain open.

### What this changes in the decision

The causal concern is substantiated. It is not answered by empty seed
catalogues, no Gallery-admission regression, or exact agreement among later
previews. Those checks missed an unintended consequence of releasing
selected photos into group matching. Family surname changes did not
implement either demonstrated transition; bundling input changes, resets,
naming, refinement and performance acceptance obscured them.

For visual context, the uninstalled preview8 recap has verified targets
for [a Freya member](file:///B:/Sovereign%20Territories%20Sandbox/Working/_reports/library/rebase-recap/postrun-review-preview8.html#review-photo-074f040175a0)
and [the old workflow photo in the Fia/Jacinta group](file:///B:/Sovereign%20Territories%20Sandbox/Working/_reports/library/rebase-recap/postrun-review-preview8.html#review-photo-8fae6321a780).
These show the current disputed grouping, not a newly installed correction.

Repeated end-to-end reruns alone are not a fix for the demonstrated
behavior, but the user's request for an independent complete rebase
acceptance must not be replaced by component or saved-input equivalence
claims. First agree the group-versus-individual association contract, then
test both bridges and the other affected cast cohorts as explicit
before/after acceptance cases, and perform the independent rebase with
frozen sources, reset semantics and seeds. No automatic photo deletion,
identity assertion, threshold change, new intake or install is authorized
by this explanation. E19 and final clean-rebase/viewer acceptance stay open.

The five planner probes completed in about 24 seconds total under
single-thread BLAS limits. All exact baseline/reversal assertions passed.
This is measured diagnosis from cached data, not a rebase performance
benchmark. Scratch probe/evidence are under ignored
`tmp\session-logs\2026-11-08-freya-cause`; the durable findings are recorded
here rather than relying on that disposable directory.

## Nov 8 21:57 scoring-path review and legacy-rule assessment

This is the requested deeper read-only review, not approval of a new
threshold or matching design. Actual preview8 policy, source, saved vectors
and executable gate behavior were examined. The repository base policy is
not identical to that preview: core-rebase overlays use cast core >=0.40,
and preview8 additionally enables Angels Gallery >=0.45, Sisters >=0.50,
both with >=0.10 all-category rival margin. Base-file-only analysis would
misstate the tested system.

### The numbers represent different questions

| Stage in this rebase | Current mechanism | What it does not prove |
| --- | --- | --- |
| Candidate grouping | Average-linkage >=0.25, then provisional leave-one-out core >=0.15 | Same person rather than relatives; every pair need not pass 0.25 |
| Individual attachment / provisional group attachment | Category-specific photo score and rival margin; group attachment also checks incoming members against the frozen target | These stricter attachment gates are not retroactively applied to all members formed by initial linkage |
| Group-to-cast classification | Normalized group core >=0.55 and cast-only owner margin >=0.10; small groups up to four have a separate >=0.40 Review rule | Every member individually fits that cast, or beats a non-cast alternative |
| Provisional non-cast refinement | Bounded photo reassignment, reciprocal merges and category reclassification | Cast-owned Review groups are not included in its recovery pool |
| Final Gallery membership refinement | Own leave-one-out, rival score/margin, independent references, quality and decision metadata | Review holds are explicitly excluded; a low own score alone is not an ejection rule |
| Cast Gallery admission | One frozen all-category pass, >=0.45 Angel / >=0.50 Sister, >=0.10 lead, >=4 diverse eligible references and quality/decision guards | Failed admissions are not automatically reassociated, and missing non-cast groups cannot compete as cores |
| Final audit / automatic protection | Record residual evidence and acquire qualifying core protection | Zero eligible moves is stability under these gates, not human identity correctness |

These are centered cosine similarities, not identity probabilities.
Photo-to-core, group-to-core and leave-one-out values cannot be calibrated
as if a common 0.55 meant a common error rate. A normalized average vector
can legitimately have a higher score than any individual member. The error
is treating that group score as sufficient evidence for every member's cast
association, not the normalization arithmetic itself.

### Measured 0.60 sensitivity: it does not restore separate people

Three trials reconstruct all 2,230 original eligible candidates, the same
initial cast cores and mean, and execute the real initial planner plus
provisional refinement. Baseline sample cluster IDs/scores match the
receipt; all trials conserve candidates. Final Gallery refinement,
admission, naming, protection and publication are **not** rerun, so these
are not predictions of a complete replacement library.

| Trial | Changed photo destinations at this stage | Outcome |
| --- | ---: | --- |
| Actual 0.55 baseline | reference | Freya eight and Fia/Jacinta nineteen remain Angelica Review |
| Only raise `highCastSimilarityMinimum` to 0.60 | **0** | All 27 still go to Angelica Review: Models stops at 0.55, so they fall through to no matching category rule |
| Raise that limit and Models' upper band to 0.60 | **27** | Same eight-member and nineteen-member groups become Models; all 27 were Angelica Review, no other destinations change in this measured stage |

The original six/ten/seven groups do **not** return in either 0.60 trial.
Cluster membership is identical for the disputed cohorts. All three
trials have two provisional passes, seven moves and zero merges/dissolutions.
Thus 0.60 is a possible *cast-association sensitivity experiment*, not a
group separation fix. It does not change the separate 0.25 clustering or
non-cast merge thresholds. The uncovered 0.55..0.60 category gap also
demonstrates why changing a single policy number without its neighboring
contracts is unsafe.

### Concrete scoring and revalidation gaps

1. **A group's strong aggregate hides weak cast membership.** In preview8,
   Freya's eight members average **0.395735** against the initial Angelica
   core. Normalizing their mean produces **0.592512**; five members are
   below 0.40. The nineteen-member group averages **0.337230**, but its
   normalized score is **0.555148**. Its strongest individual cast score is
   only **0.453139**, and sixteen are below 0.40. Neither centroid proves
   that the low members belong in Angelica.
2. **The core cleanup asks the wrong identity question for this case.**
   All eight and all nineteen survive the provisional 0.15 core filter.
   Their within-group leave-one-out scores range 0.4393..0.6578 and
   0.4142..0.7091 respectively. The workflow photo scores **0.601247**
   against the other eighteen, but **0.369553** against the initial
   Angelica core and **0.345101** against her final core. It is not a
   red outlier of its candidate group; it is a questionable *association
   of that group with Angelica*. Throwing it out of that group just
   because its Angelica score is low would confuse the two questions again.
3. **Cast Review is effectively an absorbing state for refinement.**
   Provisional recovery only considers unowned holds, and final membership
   refinement returns early for non-Gallery membership. In the actual final
   audit, **159** photos are cast Review: **157** quality-eligible rows are
   held with `Review/unassigned membership requires explicit admission`;
   two have quality holds. **112** have assigned-cast scores below 0.40,
   all unprotected; **67** have a higher rival. This is not a remaining
   pass-count problem. Raising the iteration cap would hit the same guards.
4. **The competitor set can lose the alternatives we need.** When the
   nineteen are held together under Angelica, separate Fia/Jacinta Gallery
   identities are never created. Later all-category comparison includes
   extant Gallery cores, not these absent subgroups. A strong margin against
   the surviving roster is therefore not proof the candidate beat the
   alternative grouping that was discarded earlier. In the final audit
   147 of the 159 cast Review photos have a non-cast best rival, but only
   67 have any rival higher than own; do not conflate those counts.
5. **Support count measures diversity, not positive votes.** The current
   four-reference gate removes self/same bytes/near-duplicates and counts
   eligible distinct core references; it does not require four separate
   photo-to-reference scores above the admission threshold. Centroid score,
   quality and rival margin still apply, so this is not an arbitrary
   admission bypass. The label must not be interpreted as four affirmative
   identity observations. Whether a positive-support requirement improves
   precision without losing valid pose/lighting variation needs labelled
   testing.

The initial/provisional stage has 43 cast-owned Review groups containing
265 photos before subsequent Gallery/refinement/admission changes; 39 groups
contain a member below 0.40 against their assigned initial cast core.
This identifies wider test coverage, not 265 wrong identities or final
Review size. The final Gallery has no measured own score below 0.15;
this snapshot does not demonstrate a library-wide red-Gallery-outlier leak.

### Older rules: retain, revise, or investigate

| Existing rule | Assessment under newer changes | Bounded response |
| --- | --- | --- |
| High group resemblance consumes the entire group into cast Review instead of preserving a provisional identity | Protective when cast arrivals were deliberately Review-only; now suppresses alternative groups and leaves weak members attached after selective admission | First correction candidate: separate group resemblance suggestion from per-photo membership/ownership |
| No automatic re-evaluation of cast-owned Review holds | Prevents unreviewed admission but also prevents harmless reconsideration of a failed automatic suggestion | Preserve no automatic Gallery approval; distinguish machine-proposed Review associations from explicit human decisions and re-evaluate the former |
| Provisional own-score >= category protection minimum skips rival comparison | Intentional older core-retention shortcut, explicitly covered by an existing test; final Gallery refinement was later added to compare stronger rivals anyway | Candidate for consolidation, not blind removal. Measure differences; retain manual locks and verify temporary category/merge decisions do not rely on the shortcut |
| 0.25 linkage and 0.15 provisional cleanup | Useful recall mechanism, not a validated same-person certificate; can build stable related-person groups before stricter attachment gates run | Retain candidate discovery; do not let initial linkage bypass downstream member/competitor checks. Calibrate only with labelled cases |
| Separate legacy individual cast Review minimum (Angel 0.55 / Sister 0.50), lower newer Gallery minima (0.45 / 0.50) | Deliberate compatibility choice; two overlapping paths are now hard to reason about and do not mean Review requires stronger identity evidence than Gallery | Make decision roles explicit and test shared evidence without silently equalizing every threshold |
| Source-wide centering | Adding usable input can alter all scores/core eligibility even when existing pixels do not change | Keep a frozen recorded mean for comparisons; do not call cached-input identity equality proof of fresh-population equivalence |
| Near-duplicate exclusion, frozen evidence, leave-one-out, rival margins, quality/stale-byte guards | Still necessary; help prevent self-evidence, duplicate support and feedback loops | Keep; consider clearer support semantics rather than deleting the safeguards |
| Manual protection, anchors and persistent identity rejection | Human intent must remain stronger than automatic re-grouping | Keep content/stable-ID binding and explicit migration; do not erase locks to make a run appear converged |
| Bounded passes, oscillation refusal and draft/Production authorization | Still appropriate | Keep; explicitly report blocked versus eligible residuals instead of equating stability with correctness |

Established-library `reconcile` also checks member support in both directions
for reciprocal identity merges; provisional rebase refinement checks the
moved loser members against a survivor and has its own minima/shortcuts.
These are not interchangeable guarantees. This is an identified policy
parity risk, not proof another command was involved in the two reproduced
transitions or permission to replace one path wholesale.

The latest final audit has zero eligible Gallery moves, with higher-rival
holds accounted for by 181 margin holds, twelve draft-policy holds and one
cast-admission hold. Its 111 staged Gallery admissions have no final
higher-rival flags. A post-protection reread calls 105 admitted photos
protected, not newly failed similarity admissions; do not misreport those
as 105 regressions. None of these safeguards answers the cast-Review
absorbing-state issue.

### Smallest proposed correction and what the user needs to decide

Recommendation: **correct the decision contract before retuning global
numbers.** Keep grouping as a hypothesis. Preserve a proposed non-cast
identity/subgroup and its evidence even when its centroid resembles a cast.
A group may nominate a target, but must not transfer all weak members'
identity association merely through a normalized centroid.

For an individual who initially fails, a later reconsideration is valid
when independent accepted evidence grows: compare that photo again against
the updated frozen identity references and rivals, without counting itself
or a same-pass admission. Group support should trigger that reconsideration,
not certify membership. Strong coherent subgroups may need a narrowly
tested group-assisted path for pose variation; that requires independent
support/member consistency/rival checks and labelled positives, not simply
reimposing the same individual threshold on everyone or lowering it.

Revalidate both ends: keep qualified members, withdraw unsupported
machine-generated cast associations, and reassess Gallery members against
changed cores. A questionable photo can remain in its natural provisional
group or an explicit unresolved hold without being declared Angelica.
Weakness against Angelica is not a reason to delete the photo or eject it
from an otherwise coherent different identity. Manual decisions stay
separate. Merely making Review movable is insufficient: this workflow
photo's best final rival is Paloma Goodwin at 0.508723, but it has only two
independent references versus four required, so the existing Gallery move
gate would still hold it. Do not lower support globally to force that move.

For this case the user's useful input is a small **identity judgement**,
not setting every numeric threshold: which authentic Angelica examples
are trusted; whether representative Freya/Fia/Jacinta/workflow images are
the same person, different related people, or uncertain. Use actual aligned
face/native images rather than surnames or scores as truth. Do not blanket
protect the mixed nineteen, delete bridge photos, or apply a preview as
accepted. Once confident about an individual non-match, the existing
content-bound **Reject identity permanently** action can preserve it;
ordinary Reject-to-Various does not. Any such action changes the installed
catalogue and requires supported preview/apply and regeneration of stale
rebase previews. No manual action is being requested or executed here.

Acceptance before another independent full rebase:

1. Keep the two reproduced bridge cohorts as negative/ambiguity cases and
   add genuine same-person cross-pose positives so the remedy does not
   merely block useful recovery of previously missed photos.
2. Test proposed-Review reconsideration, subgroup preservation, member
   evidence and competitor availability; keep quality/manual/rejection/
   duplicate/frozen-evidence guards. Compare old/new cast and non-cast
   grouping/refinement on all saved inputs, not only net Review counts.
3. Inventory every moved-in/moved-out/changed-owner photo, intact/split/
   merged group, and newly unsupported member. Review all eleven
   cast destinations already identified rather than assuming this is unique.
4. Only after the user agrees the behavior, implement the smallest shared
   producer correction with focused regressions. Then freeze sources/seeds/
   policy and perform the requested independent complete-rebase plus
   Gallery/Overview/Review acceptance. Matching-only probes do not waive it.

All three sensitivity-trial assertions pass; 40 existing policy,
refinement and cast-admission tests pass. Scratch diagnostic/evidence live
under ignored `tmp\session-logs\2026-11-08-scoring-review`. Source receipt/
cache hashes are checked unchanged. No runtime policy, implementation,
photos, installed catalogue, intake or rebase publication changed.

### Raw follow-up source

<!-- markdownlint-disable MD013 -->
````text
Keep on monitoring what you are doing and don't stop if you have more work.  When you're done with the other changes - you can help me as I don't understand why Noelle Cruz did not merge into Adrianne Cruz (Sammara)  It's odd since most of them are supposed to be her - unless they are altered and truly don't match her.  But that's one thing that was not yet figured out.  I also think so many for review in Various is a problem and we need to pick one place where to put them instead of leaving them in Various for review.  What I wonder is if there are some photos in Sammara that aren't able to pull these others of her into the library?
````
<!-- markdownlint-enable MD013 -->

### Raw Nov 8 extended-history question

<!-- markdownlint-disable MD013 -->
````text
You may need to look back farther and how the family names were being handled as well as other changes - it's not just the last run, it's a series of updates and fixes and we weren't focused on Angelica - but on the Lujuan family name explosion.  So it's a bit more complex than just this past 1 run and it might have happened earlier in some series of updates and runs.  So make sure you look at more series of updates and how things were working and what we may have changed that allowed it.   We were working multiple changes in parallel and I suspect that some of my directions may have caused it.    So our partial re-runs might have not cleared things and we need to really do a full re-base with only the sisters and angels cores included and not the workflow photo (which I think is actually Freya in Angelica's)  It did drop out at one time as expected ... but then subsequent runs caused issues with our attempt to work on performance and not do a full-rebase.  How does this align with what you just figure dout.
````
<!-- markdownlint-enable MD013 -->

### Raw Nov 8 Angelica/Freya question

<!-- markdownlint-disable MD013 -->
````text
I am curious why so many of the images ended up with Angelica in this run - like Freya Hadley and others that previously were not.  I know we changed what would automatically be accepted into Angels and Sisters, but did that then open up a door to allow more to go into Review?  The idea was to try to keep the Review photos less - but should not have allowed move things to move into Review.  Seems like we changed something that went the wrong way?  We need more analysis of what was changed and what actually happened and why.  This is just one example - but I feel like something didn't work quite right.
````
<!-- markdownlint-enable MD013 -->

### Raw Nov 8 21:39 causal-history question

<!-- markdownlint-disable MD013 -->
````text
I dont understand why when most previous run that Freya and many hadley sisters remained outside Angelica and when we excluded the workflow photo from the core it also pulled that core away from her.  So, I need to understand that issue more indepthly and where it actually happened.  When I had asked for the full rebase to exclude workflow selected photos - it then was working properly for Angelica.  We then shifted to the family names and might have run another full rebase and I did not catch the shifts in Angelica.  This is just one instance I am noticing, but maybe others shared same pattern.  So, without me truly understanding when and why that happened for Freya and Angelica.  I am unclear at your explanation.  Then we can address other issues I am seeing.  I think that trying to skip steps of re-running another full-rebase complicated things as well - since we were then focusing on family names and performance without seeing the Angelica related issue.
````
<!-- markdownlint-enable MD013 -->

### Raw Nov 8 21:57 scoring review and follow-up

<!-- markdownlint-disable MD013 -->
````text
So, in this case a .60 group rating would have kept them separate - but then I don't know what else that excludes that merges with other groups - which is a portion of the testing and tuning.  Yes, we were making more and more changes to organicially adjust the groups and bring photos into groups that might be mis-placed and we are dealing with images that are family relation and not identical to the entire group individually - but were also excluded from the group as individuals - which has a higher bar, but we were also tuning that somewhat in auto-accpeting things in review that individually meet the group.  So if you look at the current scoring for how it works do you see flaws in the scoring system and how things are initially accepted, but then later allow a larger group to join or what I might do in this particular case - which also likely impacts so many other groups.  Ultimately the goal is - if we know it's the same person, get the photos into a group properly.  If we later think that some photos of a person that didn't pass the individual threshold do actually represent that person we'd bring them in - but then the system should also throw out lower scoring items as we would have done with some of the Freya photos individually - like the workflow photo - which scores higher with those other Freya photos than with Angelica.  So, maybe we have some numbers that are not yet right in the system as a whole.  Can you take a much deeper review of that all - and ultimately, I want to understand what I need to do in this case without blowing up the entire system.
````

````text
Also, is there something we put in place a while ago that with the newer and more recent changes might be unnecessary or actually detrimental to how things are working overall.  Include that with the previous work you are doing right now.
````
<!-- markdownlint-enable MD013 -->

### Nov 8 approved individual-association implementation

The following approval selects the narrow producer correction, not a
blanket threshold increase: keep cast-like candidate groups as provisional
identities; retain cast resemblance as advisory evidence; reconsider
automatic associations through existing individual gates; remove the
legacy own-score shortcut only in the new mode. Historical policy receipts
without the new control retain their semantics. Explicit manual decisions,
quality/content binding, independent-reference and rival-margin checks
remain authoritative. Test first, then rebuild matching from the verified
original saved intake under a new receipt; no chaining previews or fresh
pixel processing merely to change grouping. Publication is sandbox-only,
after route/count/report checks. No human identity acceptance is implied.
The execution spine's E19 remains open for human identity judgments even
after implementation and installed-run verification pass.

**Iteration evidence:** preview9 conserved all 3,290 photos and 1,041
initial cast core IDs, changed no prepared bytes or policy thresholds, and
preserved workflow reset inputs. Its apparent initial convergence was
insufficient: after the single frozen Gallery-admission pass, the final
continuity comparison found one newly qualifying Drakness Review move.
Installation correctly refused before mutation; the installed catalogue
remained `dd276e95f873a2747657b59dd39061ac1dc211125faa7f79a0c9bc9c20a2be5f`.
Do not install or reinterpret that receipt as accepted. The narrow follow-up
runs a second bounded membership phase **after** admission, carrying prior
visited memberships and oscillation holds, then names/re-audits normally.
It does not recursively admit new Gallery members, lower gates or bypass
publication checks. A regression reproduces changed evidence after an
initially stable pass and verifies continued moves and cross-stage
oscillation prevention. The final targeted suite passes 133 tests; Pylance
confirms all 15 `refine_membership` callers remain signature-compatible.
Preview10 rebuilds from the original intake, not preview9, with this fix.

**Preview10 verified matching result:** all 3,290 sources, content hashes,
prepared hashes and the 1,041 initial core IDs match preview8. Workflow
reset **inputs** match; two automatically chosen replacement workflow
photos change as an output of the new membership. Policy changes are
limited to the association-mode switch/version; Angels/Sisters minima,
all-category margins, independent-reference counts and direct-only surname
policy are unchanged. Final refinement takes five of at most eight passes,
makes 17 moves and has zero eligible residual or post-continuity moves.
The supported preview check passes. Preview10 was installed as an
intermediate baseline; final acceptance is superseded by the browser
protection correction below.

| Comparison with preview8 | Result |
| --- | --- |
| Population | 3,290 -> 3,290; no photo deletion or fresh intake |
| Gallery / Review | 3,091 / 199 -> 3,270 / 20 |
| Review traffic | 179 Review -> Gallery; no Gallery -> Review |
| Changed destination paths | 531, including 352 Gallery -> Gallery; names are not identity proof |
| Distinct owner folders | 251 -> 301; mostly former group holds now remain candidate identities, not 50 verified new people |
| Frozen cast Gallery admissions | 111 -> 23; 88 previously admitted photos instead retain stronger provisional alternatives |
| Freya six | All leave Angelica Review for Models/Freya Vale; the eight-member candidate group remains intact |
| Fia ten / Jacinta seven | Both leave Angelica Review for Models/Mira Vale; their combined 19-member hypothesis, including the old workflow photo, is **not** forcibly split |
| Angelica | 41 Gallery / 45 Review -> 30 Gallery / 0 Review; her initial 30 core IDs remain intact |
| Larger cross-cast effect | Draknora's 51 former additional Gallery photos stay together in the Sabine Santos hypothesis; their new own scores are 0.582-0.891, median 0.812, not 51 singleton fragments |
| Weak/unsafe Gallery output | Zero quality-held Gallery photos and zero final Gallery own scores below 0.15 |

These are routing and convergence results, **not identity truth**. A lower
Review count largely reflects preserved non-cast candidate groups instead
of cast ownership; it must not be presented as 179 independently verified
identity corrections. Draknora/Sabine, Drakness/Cerys and Fia/Jacinta remain
important human comparisons. Do not recover the old names/groups by
deleting bridge photos or raising thresholds. The new draft removes
whole-group ownership, not the underlying uncertainty about relatives,
pose changes or the initial 0.25 discovery linkage.

**Nov 9 browser protection correction:** real Overview/Photo review
navigation verified Freya's eight and Mira's nineteen thumbnails and the
intentional nine-photo Overview limit. It also exposed a remaining legacy
interaction: automatic establishment labelled the new Mira candidate
identity **protected**, which would recreate the lock under a different
owner. Preview10 is therefore not the final accepted handoff.

The shared protection producer now keeps numeric, independent
leave-one-out evidence for unconfirmed Models/Prospects/Potentials but
does not acquire identity/photo locks from that candidate group's own
members. Explicit manual identity/photo protection, opt-outs, anchors,
rejections and cast-core acquisition keep their existing behavior. Existing
stored decisions are not silently unprotected: the authorized fresh
original-input rebuild discards generated seed locks through the existing
manual-intent filter, then applies the revised acquisition policy. Legacy
policies retain the old acquisition behavior.

The final shared library selector runs 1,020 tests successfully (one
skipped), including manual trust versus automatic provenance, preserved
cast protection, family-metadata apply/exact undo and final audit
integration. Isolated mutation smoke is 19/19 and routine hygiene passes.
After the date/version update, 33 policy/protection tests pass again.
Preview11 is rebuilt from original intake and passes the supported preview
check: all 3,290 destination paths are identical to preview10, as are seed
catalogue and pixels; all candidate identity/photo automatic locks are
absent, and every cast photo's protected/unprotected state is unchanged.
No eligible post-continuity moves remain. Preview11 installation and
viewer rebuild finish successfully. Browser verification confirms no
automatic identity lock on Mira, all 8 / 19 / 54 photos available in the
Freya/Mira/Sabine filters, zero broken thumbnails, 20/20 Review rows and
the applied recap's expanding/new-tab links. Overview intentionally shows
nine of Mira's nineteen, with a working full-Review link. Supported
installed-receipt and Gallery checks both pass: applied continuation
verified, zero renames/derivatives pending, zero actionable diagnostics.
The 143 intentional framing exclusions retain their photos; they are not
missing Gallery entries. Gallery sealing verifies 30,834 files in 589.56s.
Against the formerly installed preview3, all 3,290 photos remain and
Review falls from 230 to 20: 210 Review-to-Gallery, zero Gallery-to-Review.

Coverage: stronger competing identities, relative-versus-pose ambiguity,
legacy group ownership, retained shortcut and automatic candidate-group
lock reacquisition are covered by implementation
and focused regressions; the original-input rerun measures the historical
Freya, Fia/Jacinta/workflow cohorts plus all-cast/global changes. Unresolved
identity labels remain explicit human-review items rather than inferred
success from a lower Review count.

<!-- markdownlint-disable MD013 -->
````text
So, restating - I the automatic admissinon of a group into review blocked all future improvements we've made to help organically adjust the system and ensure that photos end up with the person they are most likely associated to.   Ultimately, that's what I want and the group casting was a way to catch things I saw were falling out that I knew were a person well ahead of all many other newer features.  So, it should not "lock" a photo if there is a mathmatical higher association to someone else that a group "might" be similar to.  Ultimately, I don't want to many things in review because they might look like someone if there is proof they look like someone else and I don't want to cluster the Hadley family if they don't really belong together - even though they are similar.  But I also don't want dozens of Hadleys when it's just a side photo or facial expression or something that brings it to a separate group.  I understand it's tricky, but seems like you have a core understanding of my requirements.  If this doesn't change your opinion, help me figure out what to do next and implement it.  I'll be back in the morning to see how it worked and you can run a rull re-base if that is necessary based on the rule changes or pickup after the intake or where ever makes sense.
````
<!-- markdownlint-enable MD013 -->
