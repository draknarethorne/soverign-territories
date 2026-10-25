# 2026-10-22: likeness engine acceptance and production rebuilding

**Status:** active (remaining acceptance and production gates; installed trial is not accepted)

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
audits share that eligibility helper. Rebase refuses to erase override/name/
family provenance until stable-ID migration is implemented. No real matching,
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
  establishment gates plus persistent manual override semantics; then extend
  shared policy/schema and catalogue provenance, implement preview/apply/undo,
  and test exact boundaries, duplicates, self-scoring, protected Review, stale
  hashes, manual opt-out, workflow conflicts and repeat/rebase preservation.
  Calibrate on labelled sandbox cases before enabling a mutating policy.

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
