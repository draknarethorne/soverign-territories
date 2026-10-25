# Likeness processing contract

**Reconciled:** 2026-10-25. Approved target rules, not a claim that all
acceptance gates have passed. The [engine acceptance plan](../plans/2026-10-22-likeness-engine-acceptance.md)
owns execution; [installed evidence](likeness-sandbox-trial.md) owns the
dated run record; [likeness guide](likeness.md) owns runnable command syntax.
The older phase/example command names below are design illustrations, not
additional shipped CLI contracts. Production remains unapproved.

## Latest precedence and ownership

- The retained-cast prepared clean-start flow is implemented (`d27098a`,
  `2340157`): inventory, intake-only preparation/check, safe resume into a
  fresh-cache matching preview, reviewed installation and exact undo use the
  existing sandbox launcher. All retained cast images are prepared without
  changing their membership; named/loose Various share the planner, while
  Artists remain preparation-only in their domain. Verified one-to-one
  continuity carries curation/name/family/override decisions; ambiguous,
  missing, unknown or stale inputs hold. No real rebase or production change
  ran. Real recipe/lineage acceptance, optional cast release and incremental
  production cutover remain open.
  Replacement of already-owned prepared cast outputs is individually inventoried,
  hash-checked and reversible; it is not permission for a broad cast-root reset.
- Prepared natives bypass legacy screenshot cleanup in the maintained
  derivative-rendering/crop path, not in every direct legacy originals caller.
  Keep exact original bytes and actually retained alternatives distinct from
  generated standard derivatives; preparation does not authorize pruning.
  The launchers use the modern CPU runtime documented in the
  [photo-library runtime guide](original-photos.md#python-runtime-and-dependencies);
  historical runtime assumptions are not current setup requirements.
- Oct 25 autonomous implementation extends protection acquisition and virtual
  family naming through the existing reconciliation transaction. The working
  policy remains draft: implementing configurable defaults is not production
  calibration or permission to apply them. Person/photo protection, own-core
  evidence and family resemblance remain separate concepts.
- Preserve original/current person-name provenance independently of character
  slots. Family surnames are catalogue presentation metadata, not face evidence
  or a reason to rename fixed directories, workflow keys or source files.
  Recorded family changes are reversible with the reconciliation journal.

- Oct 23 foundation work is ordered in the
  [plan index](../plans/README.md#current-library-work-order-oct-23).
  The new [intake plan](../plans/2026-10-23-image-intake-preparation.md)
  owns implemented sandbox preparation and remaining real acceptance; the
  [cast experiment](../plans/2026-10-23-cast-seeded-library-rebase.md)
  owns configurable seed/retention/release design. Retained-cast preparation
  is delivered, but optional seed/release policy is not approved or a blanket
  override of D10/D14/D15. Preparation includes retained cast
  images; membership protection does not authorize destructive preprocessing.
  Any release requires an explicit recoverable experiment and exact preview;
  ordinary automation retains its current protections.
- The policy separates evidence, grouping, matching, classification and
  authorization. A cast threshold, display band or action-support count
  never becomes an unrelated candidate-grouping gate.
- Identity protection blocks automation, not applicable explicit manual
  identity actions. The [action plan](../plans/2026-10-22-review-actions.md) owns remaining
  all-category support; the [layout plan](../plans/2026-10-22-gallery-review-layout.md) owns the
  proposed temporary unlock. Relocking semantics remain undecided.
- Fixed cast slots are separate from recorded names. Protected rename is
  delivered with confirmation, not with the proposed checkbox.
- Catalogue ownership is root-specific: production tracked metadata is
  separate from the sandbox-local `.likeness-library.json`. Never write
  production metadata while inspecting/applying a sandbox action.
- The saved `.3` installed scenario and later `.4` maintenance draft are
  different evidence. Neither is production acceptance. No clean reset
  may silently discard new non-cast rejection/identity decisions.

## Approved direction and constraints

| ID | Decision |
| --- | --- |
| D1 | Use Option A: retain category roots and represent family/lookalike grouping virtually in the people gallery and tracked identity metadata. Do not add physical Families, Twins, or Lookalikes roots. The user wants a reintroduced active `Models/` category alongside Angels, Sisters, Prospects, and Potentials, controlled by the rebaseline classifier and distinguished from legacy Model paths. |
| D2 | Use a shared surname for identities grouped as lookalikes/family while retaining distinct first names. The earlier shared-first-initial preference is not implemented by the Oct 25 draft, which preserves existing first names; new-name preference remains family-plan design/acceptance work. An approved looks-like threshold may automatically associate a group and assign family surnames; naming is never a matching rule. |
| D3 | Apply family naming across cast, Models, Prospects, and potentially Potentials. Reuse a surname only within a threshold-associated or user-associated lookalike group; an unrelated new identity must use an unused surname. Preserve explicit user-approved existing names, including Angelica Vale, without inferring a family link from surname alone. Existing names are candidates, not evidence that people are related. |
| D4 | Names, folder names, and family labels do not influence face matching, identity merges, character-slot assignment, or ComfyUI workflow keys. |
| D5 | Preserve fixed Angel/Sister character-slot paths and each person's recorded `z_<name>.txt` history. Audit incomplete or conflicting records; never overwrite a person's recorded name/history based on a guess. New or renamed non-cast identities may receive threshold-assigned first/last names through the sandbox-tested naming workflow. |
| D6 | Keep family members as separate identities. A validated similarity threshold may automatically associate and name a lookalike group, but that association is organizational evidence—not biological truth or a same-person identity decision. It must be visible, reversible, and excluded from matching inputs. |
| D7 | Artists and historical Model folders/paths must be explicitly traced. A reintroduced active `Models/` category is a distinct-person destination, not permission to ingest every legacy Model path; migrate any legacy source only through an audited, explicit mapping. |
| D8 | Sandbox copies may run the real workflow, including repeatable category resets, moves, and automatic family-name assignment, after verifying isolation from production. The user may iterate on sandbox configs and thresholds without approving each photo assignment. Normal-library changes require an inspectable result, explicit approval, recoverable backup, and focused tests. |
| D9 | Add a likeness rebaseline mode/flag and versioned JSON configuration for classification rules, thresholds, source scopes, and supported grouping options. Validate the config against a schema; do not use executable expressions or arbitrary plugins for the initial POC. |
| D10 | Sandbox iterations may reset only generated Model/Prospect/Potential output directories from the immutable source snapshot. Never delete the source snapshot, production library, Artists, archives, or unrelated sandbox content as part of reset. |
| D11 | Use separate run-scoped matching state: only configured cast roots seed identity references by default; generated categories never become references on the next clean rebase. New clean experiments start an empty run-local embedding cache. An explicit replan may reuse that run's validated measurements; identity references and assignments are always rebuilt. |
| D12 | Keep classification stored with stable person identity and reflected in category directory placement. Gallery controls may filter/show/hide family groups or classifications for browsing. An explicit sandbox-config control may enable/disable a class for the next rebase, but must export a validated config and cannot change existing assignments until that sandbox rebase runs. |
| D13 | Use one likeness engine for clean rebase and ongoing incremental processing. Sandbox and production share scoring, decision semantics, and default policy; differences are limited to explicitly configured and versioned sandbox overrides recorded with each run. A full rebase is a recovery/calibration tool, not the normal intake loop after the initial baseline. |
| D14 | Configure category hierarchy/order and category-specific thresholds and action permissions declaratively. Unprotected Potentials and Prospects may merge/split organically with lower configurable thresholds; Models use an intermediate policy with more Review; Angels and Sisters remain conservative and are not automatically stripped of low-scoring photos. Adding a category such as Demons must not require a separate matcher implementation. |
| D15 | Identity Protection blocks automatic changes to Gallery membership, including merge/split and category moves. Incoming candidates may be proposed for separately permitted identity-associated Review without joining the protected core. Photo Protection blocks automatic removal and Review routing of that protected photo but does not force core membership. Workflow-selected photos are automatically photo-protected. Display identity and photo protection distinctly. |
| D16 | After the first sandbox rebase, test incremental organic growth by adding the user's separate batch of 200+ images to the sandbox and running the ordinary likeness process without resetting/rebasing. Also preview the normal likeness process immediately after the rebase and report any proposed changes; do not silently apply them. |
| D17 | The sandbox is a test environment, not the product boundary. A clean-full production rebase of the approved scope is required after acceptance; sandbox-only installation and category-only reclassification are insufficient. |
| D18 | Separate evidence, candidate grouping, identity matching, category assignment, and action authorization. Cast protection and cast-match thresholds must not become candidate-clustering thresholds. A minimum evidence count for an action must not discard valid pair/singleton evidence. |
| D19 | This reference owns the unified engine contract. The focused engine, action, family and layout plans own execution; metadata/manifest/recovery remain shared foundations. Earlier audit-only limits do not override tier-aware automation. |

## Unified processing contract (Oct 21 reconciliation)

This section replaces conflicting earlier design prescriptions in the two
likeness plans. It specifies the target behavior, not a claim that the current
code implements it. Original user discussions remain unchanged in the retired
source records; current constraints and unresolved decisions are retained here.

### One engine; deliberate boundary differences

| Mode | Starting identity references | Candidates | Apply boundary |
| --- | --- | --- | --- |
| Clean sandbox rebase | Source Angels/Sisters only by default; no old non-cast memberships | Flattened selected source photos, plus optional explicitly scoped low-core cast candidates | Verified isolation, immutable snapshot, scoped staging, manifest and rollback; real experimental placements are permitted without per-photo approval |
| Clean production rebase | Same cast-only initialization and accepted algorithm | Approved production source inventory, flattened independently of existing non-cast folders | Fresh verified backup, exact-batch approval, stale-state checks, recoverable installation and verification |
| Incremental maintenance | Frozen established eligible identity cores | Incoming, Review, and policy-eligible affected-identity outliers | Same decision semantics; sandbox experiment authorization or accepted production policy, with preview/audit/backup/undo |

Paths, candidate selection and authorization differ at the boundary. Scoring,
clustering, matching, core rules and category decisions do not fork by mode.
Artist isolation is an explicit source/target constraint, not another matcher;
legacy Model inputs require the audited mapping already required by D7.

### Ordered decision flow

1. **Resolve configuration and inventory.** Validate one effective policy and
   source scope before writes. Record algorithm/version, overrides, exclusions,
   stable IDs, hashes, anchors, protection, and workflow-selected photos.
2. **Measure and freeze evidence.** Use one recorded scoring/centering context
   for the run. Build robust reference cores without Review or excluded
   outliers. A suspected outlier cannot define the core judging itself.
3. **Evaluate existing matches and form candidate groups.** Compare photos
   and groups against eligible references, using separately defined metrics.
   A blocked cast Gallery action does not discard candidate evidence:
   consider cast Review or continue grouping where appropriate. Retain
   coherent pairs and singleton candidates; do not require three photos
   merely to preserve a group.
4. **Resolve against existing and provisional references.** Freeze new
   provisional reference vectors, compare remaining candidates with both
   reference sets, and perform bounded deterministic follow-up. Do not grow
   established cores mid-run, create order-dependent chains, or assign a
   photo repeatedly. Keep ambiguity distinct from a genuine no-match.
5. **Plan tier-aware maintenance.** Evaluate affected identities for coherent
   merges, splits and outliers using both source and destination evidence,
   margins, core safeguards and protection. A low score alone is not a move.
   Preserve multiple appearance-group evidence without treating every
   expression group as a distinct person or merging lookalikes by one score.
6. **Classify planned identities.** Resolve plausible same-person/cast cases
   before classifying a distinct person as a Model. Count final eligible
   planned members, not only the seed cluster. Apply category rules after
   follow-up; Review photos never count as active core/Gallery members.
7. **Name and produce one complete action plan.** Preserve source/name history
   and stable identity continuity. Family links and names are outputs, never
   matching inputs. Record proposed action, destination/state, supporting
   evidence, applicable rule and authorization separately.
8. **Authorize, stage, apply and verify.** A preview computes the same proposed
   decisions as apply. Draft status prevents unapproved production execution;
   it must not erase proposals or disable the authorized sandbox experiment.
   Verify conservation, conflicts, hashes, protection, history and rollback.
   Publish diagnostics and galleries from actual results.

### States and protection

- **Gallery member:** belongs to an identity; core eligibility is a separate
  decision. Review and hold candidates never strengthen its active core.
- **Identity-associated Review:** a plausible destination exists, but the
  candidate is not an accepted Gallery member. Cast Review admission has a
  separate permission from protected Gallery attachment.
- **Unresolved hold:** the evidence does not select a reliable destination or
  establish a distinct new identity. Preserve group IDs, alternatives and
  provenance. Do not give every held photo a new person name or manufacture
  Review-only identities. Choose and test an explicit recoverable physical
  representation before implementing the installer; the GUI must expose it.
- **New identity:** a coherent distinct-person candidate group, including a
  valid pair or genuinely unmatched singleton. Small size alone does not
  mean unresolved, unusable, or unsuitable for future matching.
- **Protection:** identity protection blocks automatic Gallery changes and
  whole-identity actions; photo/workflow protection blocks automatic movement
  of that photo. Neither makes a low-scoring image mandatory core evidence.
  Anchors, protection and workflow choice remain separate metadata.

### Tier behavior, not a global caution switch

| Tier | Membership and maintenance policy | Core policy |
| --- | --- | --- |
| Unprotected Potentials/Prospects | Allow configured automatic attachment, coherent merge/split and category growth; use selective Review for ambiguity, not blanket manual approval | Orange can contribute; red is excluded, with the singleton exception. Minimum evidence for destructive outlier actions is independent of forming an identity |
| Models | Intermediate action thresholds/permissions, stronger supporting evidence and more Review than lower tiers | Green/yellow core starting hypothesis; uncertain resemblance cannot establish a distinct Model by itself |
| Angels/Sisters | No routine automatic Gallery stripping or candidate Gallery admission initially; plausible incoming candidates may enter separately permitted Review | User anchors/core control; retained low-score photos need not define identity |
| Explicitly protected identity/photo | Apply the relevant protection regardless of tier | Retention and core membership remain separate |

Configure thresholds and permissions by action and category, including both
ends of a merge. A display color is a visual cue, not authorization or a
universal identity threshold. Adding a category using supported predicates
must not require hardcoded cast/non-cast branches throughout the planner.

### Configuration ownership and threshold separation

The versioned policy owns behavioral parameters: grouping method/threshold,
small-group handling, photo-to-core matching, group-to-core matching,
identity-to-identity merge/split evidence, tier rules, margins, Review
admission, core construction and classification. Workspace configuration
continues to own paths and workflow selections; the catalogue owns identity,
anchor and protection decisions. Compatibility settings/anchor patterns must
be explicitly migrated or resolved with provenance, not silently override the
policy. Conflicting values fail before writes. Algorithm constants may stay
in code; tunable identity/action behavior may not hide in code defaults.

Every effective value must have a defined comparison metric, scope, units,
owner and override provenance. Separate pairwise average-linkage similarity,
photo-to-core similarity, group-to-core similarity, and identity merge
evidence. Equal numeric values do not make those rules interchangeable.
Group size for classification, core viability, independent merge evidence
and permission to move are separate parameters.

The migration must replace the primary routine's separate legacy Review,
sort, singles and rematch decisions with the shared planner before claiming
unification. Preserve launcher compatibility; retain a legacy path only for
a documented distinct operation with explicit scope and regression coverage.
Helpers in a common package alone do not constitute a shared engine.

## Historical Oct 21 investigation: code versus target

The Oct 21 investigation found four coupled failures: the cast-level 0.55
value was independently introduced as a conservative clustering floor
without action-specific validation; the inherited minimum-three gate
discarded pairs; draft execution policy suppressed matching proposals; and
the rebase adapter converted many held photos into new Potential identities.
At that investigation point the ordinary library launcher still executed
legacy decisions, and the merge/split policy evaluator had only test callers. Plans accumulated
historical additions without revising older constraints or completion claims.
These are implementation/design and plan-maintenance failures, not unclear
user goals or a validated reason to keep two engines.

The earlier fragmentation run had 698 Potential folders: 659 single-photo folders
and 502 Review-only folders. Its 1,144 eligible candidate vectors yield the
following **clustering-only** counterfactuals in the saved scoring context:

| Average-linkage threshold | Groups | Singletons | Pairs |
| --- | ---: | ---: | ---: |
| 0.55 | 671 | 508 | 93 |
| 0.40 | 383 | 217 | 80 |
| 0.30 | 217 | 58 | 69 |
| 0.25 | 159 | 25 | 48 |

These counts do not prove identity accuracy. Fewer folders is not acceptance.
A runtime reproduction also showed a perfect two-photo pair becoming two
held candidates under the minimum-three gate. Correct group preservation,
proposal/authorization separation, hold representation and routine wiring
before installing another threshold experiment.

## Calibration starting points (not production approval)

The tracked versioned policy is
[`data/art/likeness-engine-policy.json`](../../data/art/likeness-engine-policy.json),
validated against
[`likeness-engine-policy.schema.json`](../../data/art/_schema/likeness-engine-policy.schema.json).
Its current draft is `draft-2026-10-25.1`, with draft automatic protection and
direct-reference family association enabled for authorized experiments, not
accepted production use. The installed scenario's saved status is `draft`,
version `draft-2026-10-21.3`; the later `.4` and Oct 25 drafts are distinct. The installed
Oct 22 experiment uses 0.25 average-linkage grouping with minimum size one;
it does not reuse the 0.55 cast gate for candidate formation. Runtime settings
now resolve from the policy, and conflicting workspace overrides fail.
The following records the older trial's calibration starting points, not an
inventory of every current draft setting or production approval. In particular,
its disabled family association is historical: the Oct 25 draft implements
conservative direct-reference association and reversible catalogue presentation
names. Earlier shared-initial/new-name proposals are not the shipped algorithm;
the [family plan](../plans/2026-10-22-identity-family-naming.md) owns that distinction
and labelled acceptance.

| Policy area | Draft value | Meaning |
| --- | --- | --- |
| Display bands | Green >=0.55; yellow >=0.30; orange >=0.15; red <0.15 | Preserve the existing gallery color boundaries. |
| Lookalike suggestions in the saved trial | >=0.30; automatic association off in that saved policy | Historical starting point, not today's draft enabled state. Family association never establishes same-person identity. |
| Candidate grouping | Compare 0.25 average linkage, the older baseline, against 0.30/0.40 and recorded 0.55 | Trial values only. Preserve pairs; do not transplant a cast assignment gate. Validate contamination and expression coverage, not folder count alone. |
| Category assignment | Distinct 1-4-photo identities: Potentials; 5+ and cast likeness <0.40: Prospects; 5+ and 0.40-<0.55: Model hypothesis | Apply after same-person resolution and planned-member follow-up. Count alone or crossing 0.55 does not prove identity. |
| Lower-tier photo attachment | Compare the historical 0.40 score / 0.10 margin baseline with labelled alternatives | Separate photo-to-core calibration from grouping; preserve proposed routes when execution is not authorized. Own-core lead applies to a candidate leaving an existing identity, not an unmatched singleton. |
| Cast Review admission | Test 0.30 evidence cue, 0.40 stronger candidate, 0.10 destination margin | Calibrate individual/group evidence separately. Ambiguous matches retain alternatives; blocked Gallery admission does not imply no-match. |
| Cast Gallery admission | Automatic admission disabled initially | Protection is an action permission, not a 0.55 grouping floor. User-staged approval remains available. |
| Identity merge | Historical 0.48 rematch and earlier 0.55 proposal are comparison points, not accepted cutoffs | Calibrate by tier using both identities, margin and independent support. Define independence; multiple near-duplicate shots alone are not independent evidence. |
| Split candidate | Own-core <=0.15, alternative >=0.30, margin >=0.10, at least 2 independent photos | Proposed outlier evidence; automatic split remains disabled by draft status. |
| Model action thresholds | Intermediate between lower-tier and cast permissions; exact values require labelled trials | Do not invent a second global threshold or let the Model classification band authorize a merge. |
| Category protections | Sisters/Angels protected by category; explicit identity/photo and automatic workflow-photo protection | Block Gallery-membership changes, not evidence generation or separately permitted incoming Review. |

The earlier sandbox calibration is evidence only: existing-folder labels are
assumed ground truth, and the saved report conflicts with an older inline
accuracy comment. In particular, the proposed 0.55/0.10 route is not accepted
as an automatic-action threshold until representative gallery examples and
action-specific error targets are reviewed. A clean sandbox run has since
been installed, but remains unaccepted (see the installed evidence); production is unchanged.
The verified pre-run Working backup is
`B:\Sovereign Territories Sandbox\Working\_backup\library-20261021-172221`
(17,582 files; 5,827,811,555 bytes).

## Vocabulary

| Term | Meaning in this plan |
| --- | --- |
| Person identity | One independently tracked person with stable identity and photo history. A folder name is not its stable ID. |
| Character slot | The fixed Angel/Sister directory and workflow identity. It is not interchangeable with the recorded person name. |
| Model | Active sandbox category under draft rules for a distinct, non-cast person with at least five usable photos and a qualifying resemblance to an Angel/Sister. This category conveys resemblance and card-use preference, not same-person identity. |
| Prospect | Category for an independent person with at least five usable photos and no qualifying cast resemblance under the draft classifier; Prospect-to-Prospect families may still be grouped. |
| Potential | One-to-four usable photos; a holding category until the identity has enough photos for full classification. Show likeness scores without automatically promoting based on a cast resemblance. |
| Legacy Model path | Existing/historical folder or source using a Model name before this proposal. It is not automatically an active Model identity or an eligible matching source. |
| Family/lookalike group | A human-facing association among distinct person identities; it does not mean biological relation or one identity. |
| Family surname | The shared human-facing surname used only for identities deliberately associated in a family/lookalike group. |
| Suggested association | A score-based candidate shown before the selected threshold is met; it is not yet a family group or a match assignment. |
| Threshold-assigned family | A reversible, score-derived lookalike group with shared-surname naming; it is not a biological claim or a same-person match. |
| Clean rebase | Rebuild selected non-cast memberships from a fixed source inventory and cast-only initial references, in sandbox or approved production. Category-only reclassification is not a clean rebase. |
| Source scope | The exact set of roots, folders, files, and photo statuses eligible to score or route in one run. |
| Rebase configuration | Versioned declarative JSON that defines supported source pools, identity-reference roots, category rules, score thresholds, family grouping, and display behavior. |
| Sandbox source snapshot | Immutable, verified copy of the selected original library inputs from which each sandbox iteration is rebuilt. Generated category outputs are not sources for later clean runs. |
| Incremental self-healing | Ordinary intake that scores new photos against existing identities and updates only affected identities/categories without resetting the library to a source snapshot. |
| Identity Protection | Stable policy blocking automatic Gallery-membership changes and identity merge/split/category actions; incoming Review admission is separately controlled. |
| Photo Protection | Per-photo policy that blocks automatic removal and Review routing but may exclude the photo from trusted/provisional identity-core construction. |

## Sandbox rebase operating model

The following is the enduring target model, including the separately gated
optional cast-release experiment. It is not an executable recipe or a claim
that every proposed source mode is implemented. Today's supported retained-cast,
all-image prepared flow is described above and in the runnable guide; it
supersedes matcher-only raw-source operation as the next acceptance run.

The sandbox is the real-world proof environment. It is allowed to make actual
directory placements and generated identity names inside the sandbox so the
user can inspect the result in Explorer, ComfyUI, and the people gallery.
This replaces a preview-only cycle for primary iteration; reports remain
available as diagnostics, not as the required user interface.

Each rebase run must:

1. Verify the configured sandbox root is distinct from and not nested under
   any production photo, ComfyUI workspace, or repository-controlled source
   root that the run could write to.
2. Verify a manifest/hash inventory for the immutable source snapshot.
   Refuse to run if the snapshot is missing, changed, or contains ambiguous
   identity/photo IDs.
3. Prepare a fresh sandbox working copy from the immutable snapshot for each
   run. Stage source candidates separately from destination roots so existing
   Prospect/Potential folders can be inputs while clean Models/Prospects/
   Potentials folders are outputs. A reset replaces only allowlisted
   generated outputs and per-run identity state; it never recursively erases
   broad roots or touches snapshots, logs, reports, and unrelated files.
4. Rebuild the run's identity references from Angels/Sisters only by default.
   Never seed from the previous run's Models/Prospects/Potentials. Rebuild
   identity centroids/reference indexes from this cast-only set. Start a new
   run-local embedding cache for a new clean experiment. An explicit replan
   may reuse that run's hash-validated measurements; it still rebuilds
   references/memberships and records reuse. Embeddings are not identities.
5. Select the candidate pool by explicit mode: all selected source
   Prospect/Potential photos, optionally plus cast Gallery photos below a
   configured own-core score. Cast anchors and protected photos remain
   excluded unless a separately named override is explicitly implemented and
   enabled. In the optional mode, remove a cast candidate from its sandbox
   source Gallery only when the run assigns it elsewhere; preserve it in its
   original cast location in the immutable snapshot for the next reset.
6. Run the configured category/family rules, write actual directory
   assignments only inside the sandbox, and emit run ID, config version,
   source scope, excluded items/reasons, score evidence, and reversible action
   history. Preserve original photo IDs and source-folder/name history in the
   run manifest; generated family names must be deterministic for the same
   snapshot/config and must not rewrite the immutable source snapshot.
7. Build/refresh the people gallery from the resulting directories and retain
   the prior run's config/report/log metadata so two configurations can be
   compared after each result is inspected. Classification is recorded
   against stable person identity and reflected in the corresponding
   category directory; family membership remains a separate relationship.
8. Run the complete agreed diagnostic suite against each completed sandbox
   result, including library-wide calibration, eligible per-folder consistency,
   and the existing identity-core audit. Record scope, thresholds, exclusions,
   per-photo/per-identity evidence, and elapsed time. Publish machine-readable
   CSVs and a human-readable Markdown report linked from the run manifest.
   Keep diagnostic scores separate from assignment scores; diagnostics do not
   independently trigger moves unless a separately approved rule says so.
9. Feed the saved diagnostic evidence into both gallery views: library-level
   quality/calibration in the overview, key per-person results on both the
   overview card and Review heading, and separately labelled per-photo
   evidence in Review. Do not combine distinct diagnostics into an unexplained
   single score.

Use the existing sandbox launcher and the runnable guide for exact supported
syntax. Earlier `rebaseline --sandbox-root ... --reset-generated` and
`--include-low-cast-candidates` sketches were design illustrations, not shipped
interfaces. Optional cast release still requires explicit policy/source
selection, cutoff and anchor/protection decisions recorded with the experiment;
the implemented prepared flow retains cast membership. Production roots must
be rejected by the sandbox apply path; a later production operation uses the
separate approved manifest and verified-backup workflow.

The first config schema should support named classes with stable IDs, display
names, output category roots, priority, usable-photo bounds, permitted
comparison types/targets, score and margin bounds, same-person precedence,
family-name policy, enabled/disabled state, and explicit fallback behavior.
Expose the existing likeness tuning values that affect outcomes—individual
assignment, margin, cluster distance/minimum size, cast-lookalike/category
thresholds, rematch/single handling, and any new group-to-group parameters—
as validated config values. Every run records the complete effective config.
Add classes through validated data when they fit supported rule types. A new
comparison algorithm or unsupported predicate still requires code and tests.
The GUI's view toggles filter presentation only. A separate explicit
sandbox-config action may export a changed class-enabled state for the next
rebase; it must not silently edit identity decisions or existing directory
placements.

## Acceptance and safety criteria

- No Artist or legacy Model photo enters identity matching through an
  unbounded or accidental parent-folder scan.
- Every run records exact sources, exclusions, configuration, and report
  version; repeated runs on the same snapshot are deterministic.
- Production thresholds remain unchanged until labelled results meet
  approved action-specific criteria. Sandbox configs may vary all supported
  scoring parameters between clean runs; record each effective config.
- A family association never implies a same-person merge; names never feed
  matching; family links target stable identities, not mutable folders.
- Missing or conflicting `z_` names are surfaced for user resolution, never
  guessed. Name changes preserve prior history and do not change character
  slots or workflow keys.
- Review is an explicit routing destination and is excluded from trusted
  identity cores. Review is selective, not a catch-all for all uncertainty.
- Preserve valid pairs and singleton evidence; do not use an action-support
  minimum to break them apart. Unresolved holds do not manufacture identities.
- Assert that grouping and cast thresholds can change independently. A
  protected cast destination must not change unrelated candidate formation.
- Validate photo attachment, pair formation, group classification, whole-person
  merge/split and family association separately; passing one is not evidence
  that the others are safe. Same-shoot support is not automatically independent.
- Compare preview and apply decisions under the same evidence/configuration.
  Every denied execution still has its qualified proposal and denial reason.
- A Model band, display color or family association never authorizes membership.
- Require full-path tests through the ordinary launcher and actual sandbox
  incremental growth before accepting production execution; isolated policy
  unit tests and draft-gated zero-move reports are insufficient.
- All bulk photo/name changes require an inspectable manifest, verified
  backup, explicit user approval, stale-state checks, audit log, and undo
  when applied to the normal library. Sandbox runs instead require verified
  isolation, a protected immutable source snapshot, a scoped reset allowlist,
  per-run logs, and repeatable restore; they may make real changes without
  per-photo approval.
- Any feature sunset has a verified replacement, caller/launcher audit,
  migration plan where needed, and tests for retained behavior.

## Decisions still needed

| ID | Question | Owner |
| --- | --- | --- |
| Q1 | Does the trial Model group-to-cast band [0.40, 0.55) distinguish labelled distinct lookalikes from unresolved same-person cases? Calibrate this separately from candidate clustering and action permissions. | either |
| Q2 | What action-specific precision/recall and maximum Review-volume targets are acceptable for same-person assignment and Review routing? | you |
| Q3 | Which existing Model paths are historical inputs versus reusable active Model people, and how should each be migrated? | either |
| Q4 | Should Potentials receive automatic family names before reaching five usable photos, or only show likeness/family candidates until classified? | you |
| Q5 | Which missing/incomplete `z_` first/last names can be recovered from source history, and which need a new user-provided name? | you |
