# 2026-10-21: likeness rebaseline, family naming, and matcher simplification

**Status:** active (Oct 22 sandbox trial installed; established maintenance implemented; calibration, family naming and production clean rebase unfinished)

## Executive summary

The current sorter has contributed to Prospect/Potential sprawl. This work
will deliver one configurable engine for clean rebuilding and ongoing
self-healing. The sandbox is the real test bed, followed by a required,
separately approved clean-full production rebase of the selected scope.
Each clean run starts from a verified, unchanging
source snapshot and clean category outputs. The matching reference set
contains only Angels/Sisters by default; an option can add eligible
low-scoring Angel/Sister photos as candidates without turning them into
identity references.

The chosen organization is **Option A**: keep category folders and add
virtual family/lookalike groups to the people gallery. The proposed active
categories are Angels, Sisters, Models, Prospects, and Potentials. Models
are distinct people with at least five usable photos and a calibrated
cast-likeness score in a separate classification band (initially 0.40-0.54 when
displayed to two decimals). Prospects have at least five usable photos
without qualifying cast resemblance. Potentials remain the one-to-four-photo
category for coherent small identities, after same-person matching and
cast-Review decisions. A photo count never overrides unresolved identity
evidence. Valid pairs retain their grouping; a genuine unmatched singleton
can become a Potential, while an unresolved match is a hold, not automatically
a new person.

Use shared surnames for identities in the same looks-like family, with
distinct first names and preferably a shared initial when a unique name is
available. For example, a Prospect related to Cleo Gray could be Clara Gray;
a Model resembling Angelica could use Angelica's family surname. Similarity
thresholds may automatically group distinct people and assign family names.
The results must be reviewable in the gallery and names never act as matching
signals. Family association never authorizes an identity merge. A separate
same-person decision may permit a merge under the category's validated action
policy; lower-tier automation does not require per-identity manual approval.

The user wants an explicit likeness-processing flag and data-driven category
configuration, so classifications and thresholds can be toggled and compared
without hand-routing identities. Repeated sandbox rebases must start from the
same verified source snapshot, rebuild real Models/Prospects/Potentials
folders, and expose actual results in Explorer and the viewer. Category rules
should be declarative so another tier can be added by configuration using
validated rule types; configuration must not execute arbitrary code. This
is tested in the sandbox before the approved production run. Existing
legacy `Models` folders/paths must be distinguished from the new active
Models category.

The rebase is the initial foundation, not the intended routine. The same
configurable likeness engine must support ordinary incremental intake and
self-healing after the sandbox baseline: merge/split and route more freely
among unprotected Potentials and Prospects, use an intermediate action policy
for Models, and keep Angels/Sisters conservative. Category-specific thresholds
and action permissions must be data-driven so a new category (for example
Demons) can be placed in the hierarchy without a sandbox-only classifier.
Sandbox and production use the same engine and default policy; sandbox-only
overrides are explicit and recorded, not a separate implementation.

Protection is an action policy, not a likeness override. Protecting an
identity prevents automatic Gallery-membership changes in or out. Attaching
an incoming candidate to that identity's Review is not Gallery membership
and must have its own permission. Protecting an individual photo
prevents automatic removal or Review routing, but does not force it into the
identity core: a protected low-score image can remain available for workflow
use while being excluded from core construction. Identity and photo protection
must be visible in both gallery surfaces.

Testing is not restricted to simulation. A real copy of the selected library
may be reprocessed in an isolated sandbox (for example
`B:\Sovereign Territories Sandbox\`), including actual file moves and name
assignments on that copy. Inspect the resulting gallery and run undo/restore
checks there. The normal library requires a separate clean-full rebuild after the sandbox
results and exact source scope are accepted; category reclassification alone
does not satisfy that deliverable.

The initial sandbox now exists at `B:\Sovereign Territories Sandbox\`: `Source`
is the preserved baseline, `Working` is the writable test copy, and
`source-manifest.json` inventories every included file by relative path, size,
and SHA-256. The initial snapshot and working copy were content-matched at creation;
Working now contains experimental outputs and is not identical to Source.
An Oct 21 read-only baseline scored the 2,667 Gallery/Review photos in 261
folders using a sandbox-local cache. It proposed one existing category move
(`Potentials/Lia Joyce` to `Prospects`, 35 usable photos), 26 confident
photo-reassignment candidates, and three Junk-rule candidates; nothing was
applied. The baseline People Gallery is available under the sandbox
`Working\_reports\library` directory. These are current-rule baselines, not
the new Model/family classification.

Oct 21 temporary-storage benchmark: C: was excluded because it is the
operating-system drive. Equal 256 MiB durable sequential-write and 512-file
(32 KiB each) create/read tests compared A: (ADATA SP900 SATA SSD, NTFS),
B: (Samsung T7 USB SSD, exFAT), and D: (Toshiba external USB drive, NTFS).
Sequential durable writes were 155.4, 296.3, and 65.8 MiB/s respectively;
small-file create/write took 0.20, 0.20, and 4.14 seconds. Warm-cache reads
are not used to rank the drives. All benchmark files were removed. B: is the
current choice for sandbox reports and temp outputs; A: is a viable alternate
if B: is busy or its exFAT/filesystem behavior causes trouble. D: is not
preferred for thumbnail-heavy work. The C: scratch copy used to generate
reports was removed after publication to B:.

| Stage | Outcome | Gate |
| --- | --- | --- |
| 0. Unblock and reconcile | Identify true prerequisites, verify sandbox isolation, and preserve an immutable source snapshot. Keep production ingest paused during baseline work. | Source scope, current plan state, isolation, and test corpus are known. |
| 1. Simplify before extending | Trace every matching/sorting path, including Artist and legacy Model sources; identify duplicate or obsolete behavior with evidence. | Root/exclusion behavior and safe sunset candidates are documented and tested. |
| 2. Define categories and family names | Audit `z_` identity names, collisions, family-link semantics, category destinations, and rename/history behavior. | Model/Prospect/Potential boundaries and naming are explicit, reversible, and previewable. |
| 3. Build the sandbox rebase loop | Add a likeness-processing flag and data-driven config to rebuild real sandbox directories from the immutable source snapshot, with cast-only references by default and an optional low-scoring cast-photo candidate pool. | Repeated runs reset only generated sandbox categories, compare modes/configurations, and expose actual results in Explorer and the gallery. |
| 4. Refactor and improve routing | Simplify matching, add distinct-person lookalike scoring and config-driven category/family assignment, and build the shared incremental self-healing engine with protection-aware merge/split and selective Review routing. | Tests prove source exclusions, deterministic category transitions, and safe same-person versus lookalike handling across rebase and ordinary intake. |
| 5. Build the people-gallery review surface | Preserve useful statistics, add cross-category likeness references and full-library rankings, and provide summary/full details in the overview and identity context in the review gallery. | The user can evaluate actual sandbox categories and rankings from the nine-photo cards without relying on separate reports. |
| 6. Clean-full production rebase | Rebuild selected production memberships with the accepted shared engine and cast-only initial references, not a category-only reshuffle. | The user approves the exact source scope and production batch; backup, provenance, and rollback are verified. |
| 7. Prevent recurrence | Validate future imports, document supported paths, and remove only proven-dead features. | Labelled acceptance cases pass and no unrelated workflow regresses. |

**What remains before processing:** reconcile the source-scope and command
flow; prove sandbox commands cannot write to production or workspaces; define
the sandbox reset boundary; identify the outstanding likeness tasks this work
replaces or depends on; and establish labelled validation examples. The
265-person full-name audit and initial, checksummed source/working copies are
complete. Unrelated chest-crop review, manual prompt work, game data, and
independent art tasks do not block this plan. Real file processing, category
resets, and name assignment are expected in the sandbox. Changes to the
normal library remain a separate run gated on reviewed results and a verified
backup.

## Approved direction and constraints

| ID | Decision |
| --- | --- |
| D1 | Use Option A: retain category roots and represent family/lookalike grouping virtually in the people gallery and tracked identity metadata. Do not add physical Families, Twins, or Lookalikes roots. The user wants a reintroduced active `Models/` category alongside Angels, Sisters, Prospects, and Potentials, controlled by the rebaseline classifier and distinguished from legacy Model paths. |
| D2 | Use a shared surname for identities grouped as lookalikes/family, while retaining distinct first names and preferring a shared first initial when a unique name is available. An approved looks-like threshold may automatically associate a group and assign family names; the naming convention is never a matching rule. |
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
| D19 | This plan owns the unified engine contract below. The Oct 20 plan owns metadata, staged user actions, review UI, and recovery foundations; its earlier audit-only limits do not override the later tier-aware automation scope. |

## Unified processing contract (Oct 21 reconciliation)

This section replaces conflicting earlier design prescriptions in the two
likeness plans. It specifies the target behavior, not a claim that the current
code implements it. Raw user direction remains unchanged at the end.

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

## Current code versus target; reason for the drift

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

The first versioned policy is
[`data/art/likeness-engine-policy.json`](../../data/art/likeness-engine-policy.json),
validated against
[`likeness-engine-policy.schema.json`](../../data/art/_schema/likeness-engine-policy.schema.json).
Its current status is `draft`, version `draft-2026-10-21.3`. The installed
Oct 22 experiment uses 0.25 average-linkage grouping with minimum size one;
it does not reuse the 0.55 cast gate for candidate formation. Runtime settings
now resolve from the policy, and conflicting workspace overrides fail.
The following records calibration questions, not production approval.

| Policy area | Draft value | Meaning |
| --- | --- | --- |
| Display bands | Green >=0.55; yellow >=0.30; orange >=0.15; red <0.15 | Preserve the existing gallery color boundaries. |
| Lookalike suggestions | >=0.30; automatic association off | Show distinct identities for visual review/family consideration; never treat this score as same-person evidence. |
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
been installed, but remains unaccepted (see Phase 3); production is unchanged.
The verified pre-run Working backup is
`B:\Sovereign Territories Sandbox\Working\_backup\library-20261021-172221`
(17,582 files; 5,827,811,555 bytes).

## Vocabulary

| Term | Meaning in this plan |
| --- | --- |
| Person identity | One independently tracked person with stable identity and photo history. A folder name is not its stable ID. |
| Character slot | The fixed Angel/Sister directory and workflow identity. It is not interchangeable with the recorded person name. |
| Model | Proposed active category for a distinct, non-cast person with at least five usable photos and a qualifying resemblance to an Angel/Sister. This category conveys resemblance and card-use preference, not same-person identity. |
| Prospect | Proposed active category for an independent person with at least five usable photos and no qualifying cast resemblance; Prospect-to-Prospect families may still be grouped. |
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

The likeness entry point should expose an explicit mode/flag plus a required
sandbox root and config, for example a future `rebaseline --sandbox-root ...
--config ... --reset-generated --apply` interface. A separate
`--include-low-cast-candidates` option enables the optional cast-photo source
pool; its score cutoff, anchor/protection policy, and source selection are
recorded in the config/run manifest. A run without that option uses
Prospect/Potential photos only as candidates. Exact option spelling is a
Phase 0/1 implementation decision. Production roots must be rejected by the
sandbox apply path; a later production operation uses the separate approved
manifest and verified-backup workflow.

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

## Work phases

### Phase 0 — reconcile current work and unblock safely

- [x] **P1 ai** 0.1 Reconcile the active self-healing plan and affected library
  plans against this scope. For each open task, record whether it is a
  prerequisite, transferred here, still independent, or superseded. Do not
  duplicate an existing implementation task or close unrelated plans.
  E1/E5, F1b-F1d/F2-F4, C6, and Phase I are now transferred here; preserve
  completed F1a and E2-E4. C7 remains a separate, independent report-lifecycle
  need: the new viewer does not replace dated report retention or stable
  directory replacement. C1-C5 remain implemented; do not close unrelated
  portions of the self-healing or tooling-debt plans.
- [x] **P1 ai** 0.2 Keep new photo ingest paused while the baseline and routing
  behavior are being validated. Record the exact conditions for resuming it;
  do not pause unrelated art or game work. Resume library ingest only after
  sandbox category/routing results are reviewed, reset/restore and production
  boundary tests pass, and the accepted source/configuration are recorded.
- [x] **P1 ai** 0.3 Record the actual library roots, current report/cache
  locations, effective likeness settings, active identity catalogue state,
  command sequence, and current backup/restore path. Separate repository
  state from the external photo library, legacy Model paths, and proposed
  active Models destination. Trace the current `PHOTO_ROOTS` and
  `SISTER_ROOTS` aliases: the legacy `Models` root is presently treated as
  Sisters, so do not expose it as the new active Model tier until source and
  destination roots are explicitly separated. Capture the full current
  score/config baseline, including assignment threshold, margin, cluster
  distance/minimum size, cast merge, singles, rematch, and related workspace
  overrides. Oct 21 baseline: production photo root is
  `B:\Sovereign Territories`; repository settings are in
  `workflows/workspaces.json`; the identity catalogue is empty (0 people, 0
  photos); default reports are under `<work>\\_reports\\library`; the default
  embedding cache/model directory is
  `%LOCALAPPDATA%\\sovereign-territories`. Current effective values are
  `assign=0.40`, `margin=0.10`, `cluster=0.25`, `minCluster=3`, `odd=0.15`,
  `alike=0.30`, `minFace=60`, `multiFace=0.30`, `singles=0.35`,
  `rematch=0.48`, `rematchCast=0.50`, and `castMerge=0.55`; the workspace
  overrides also set `keepPhoto`, three Angelica anchor IDs, and a
  Prospect/Sister `different` pair. `PHOTO_ROOTS` includes Artists, Various,
  and legacy Models; `SISTER_ROOTS` treats both Sisters and Models as
  Sisters. There is no Models directory in the copied source. The latest
  existing production snapshot is
  `B:\\Sovereign Territories\\_backup\\library-20261020-222038`, with
  `work-root`, `comfy-inputs`, and `repository-config` trees plus a complete
  manifest. `library_backup.verify_backup` provides checksum verification;
  no restore has been run as part of this sandbox work.
- [ ] **P1 ai** 0.3a Verify how to create an isolated sandbox copy of the
  selected library (using `B:\Sovereign Territories Sandbox\` if suitable).
  Inventory path/configuration/cache/launcher overrides and prove that
  sandbox commands cannot write to the normal library or its workspaces.
  Read-only `rebaseline` was proven safe only with explicit `--root`,
  sandbox-local `--cache`, sandbox-local `--out`, `--no-renders`, and no
  apply flag. `--root` alone does not isolate all commands: the tool still
  reads repository workspace configuration and the default cache is global.
  Do not use `--apply-categories`: despite its help text, that path currently
  does not create/verify a backup. Add enforced path guards and regression
  tests before any mutating sandbox command. A dedicated `sandbox-reset`
  command now refuses non-sandbox roots, verifies all Source files against the
  manifest, and has a category-only reset preview plus an explicit `--apply`
  path. It does not make the existing rebaseline command safe; isolation for
  classifier and workspace/config writes is still open. The new batch
  diagnostics command also requires its sandbox cache and report output to
  stay inside Working.
- [x] **P1 ai** 0.3b Create an immutable source snapshot and inventory for
  sandbox inputs only after the full-name audit is clean. Completed Oct 21:
  `B:\Sovereign Territories Sandbox\Source` and `...\Working` each contain
  8,845 files / 5,570,978,132 bytes. `_backup`, `_archive`, and `_reports`
  were excluded; `_junk` and `_retired` are included as inert reference data,
  not matching inputs or reset targets. Root metadata is retained.
  `source-manifest.json` records each relative path, size, and SHA-256; every
  included file hashes identically across production source, snapshot, and
  working copy. The original library was not modified by the copy.
- [ ] **P1 ai** 0.3c Define a sandbox-only reset allowlist for generated
  category outputs. Test that reset affects only Models, Prospects,
  Potentials, and per-run identity state, while refusing production paths,
  workspace inputs, Artists, archives, and the source snapshot.
  `likeness sandbox-reset` now restores only Models, Prospects, and Potentials
  from the verified Source snapshot, with temporary staging under
  `Working\_sandbox-state`. It preserves Angels, Sisters, Artists, reports,
  and the embedding cache. Run-scoped identity-state cleanup remains
  undefined, so this gate stays open.
- [ ] **P1 ai** 0.4 Build a bounded, labelled acceptance set from known
  same-person, lookalike, unrelated, former-cast, and poor-quality examples.
  Include the visually reviewed Drakness/Drakniss examples as labelled cases,
  not authorization to move those photos.
- [ ] **P1 either** 0.5 Review the remaining P1 likeness decisions in
  `2026-10-20-likeness-library-self-healing.md`; ask only for decisions that
  block policy or source scope. Keep already approved metadata, manifest,
  backup, undo, and gallery foundations.

**Exit:** work dependencies and independent tasks are explicit; no ingest or
photo changes are made; baseline sources and known examples are reproducible.

### Phase 1 — audit and simplify the matching/sorting system

- [ ] **P1 ai** 1.1 Trace all entry points and call paths for pool ingest,
  `sort`, `review`, `singles`, `rematch`, `group`, rebaseline, reconciliation,
  Artist grouping, and relevant gallery/index refreshes. Record which steps
  read, score, cluster, write, or only report.
- [ ] **P1 ai** 1.2 Inventory active and historical source roots, including
  Angels, Sisters, Prospects, Potentials, Review, Various, Artists, old Model
  folders, and any prior `Sisters (formerly Models)` paths. Verify actual path
  filters and classify each as an allowed source, explicit exclusion,
  view-only source, or unresolved legacy input. Specify a separate, new
  active Models destination; never infer that all legacy Model folders should
  be imported into it.
- [ ] **P1 ai** 1.3 Map matching, clustering, category assignment, and
  threshold configuration to their implementation modules and tests. Identify
  duplicated rules, special-case branches, stale compatibility paths, and
  hidden ordering dependencies.
- [ ] **P1 ai** 1.4 Produce a sunset/deprecation matrix for overlapping or
  obsolete features touched by this work: current owner, callers, data
  produced, migration/recovery needs, replacement, and tests to remove or
  retain. Remove nothing until call sites and user-facing launchers are
  verified.
- [ ] **P1 ai** 1.5 Add regression tests for every confirmed source boundary,
  especially Artist and legacy Model exclusion, archive/retired handling,
  supported category roots, and the proposed active Models destination.
- [ ] **P2 ai** 1.6 Refactor only the confirmed complex matching seams into
  small, testable functions/modules while preserving current behavior and
  `bin\*.cmd` entry points. Record behavior changes separately from
  behavior-preserving moves.
- [ ] **P2 either** 1.7 Review the sunset matrix and approve any user-visible
  feature removal or permanent source-category policy not already established
  by repository rules.

**Exit:** matching scope is explicit; Artist/Model leakage is ruled out by
tests; complexity and sunset candidates are evidenced, and the first
refactor preserves baseline behavior.

### Phase 2 — complete identity names and define family metadata

- [x] **P1 ai** 2.1 Audit every active Angel, Sister, Model, Prospect,
  Potential, and Artist-person `z_<name>.txt` for a usable first and last
  name, file/name mismatch, empty history, and recoverable prior names.
  Audited 265 active identities: four needed completion; after the approved
  corrections all 265 have one full-name record and a matching `z_` filename.
- [x] **P1 either** 2.2 Resolve the four incomplete names using the file,
  folder, or user-provided evidence; preserve existing history and fixed
  character-slot paths. Angelica is now Angelica Vale (user-approved);
  Potential Camaris is Camaris Bloom (distinct from the cast character);
  Mia's blank file is now Mia Wolfe from her folder; Draknora's blank file
  is now Jade Santos from its existing `z_jade_santos.txt` filename. The
  two existing histories were retained; the two empty files now have the
  recovered full-name line. No person folder or photo was renamed or moved.
- [ ] **P1 ai** 2.3 Inventory case-insensitive surname reuse and folder-name
  collisions across the whole active person library. Classify confirmed
  lookalike reuse, unrelated reuse, and unresolved reuse in a no-write report.
  Vale already appears on six active identities; Angelica Vale is explicitly
  user-approved, bringing that surname to seven. Do not infer family links
  from this approved name reuse; validate those links from likeness evidence.
- [x] **P1 ai** 2.3a Add a read-only direct-reference and naming preview
  through `bin\likeness.cmd family-preview`, using frozen cores and stable
  IDs. The saved `.3` sandbox scenario inventories 232 identities: 138
  closest-reference suggestions, 52 reused surnames, no existing full-name
  or folder collisions, 71 Artist-person exclusions from matching, and no
  core diagnostics. One proposal conflicts with an existing full name and
  two proposals conflict with each other. All surname reuse remains
  unresolved rather than being labelled confirmed from scores alone.
  The HTML has 414 validated local Review links; JSON retains alternative
  scores and core evidence. A repeat launcher run preserved all 5,932 active
  sandbox-file and 8,270 production-file inventories, all recorded-name
  hashes, the sandbox catalogue hash and saved policy hash. Production has
  no local catalogue. This advances 2.3, not its confirmed/unrelated
  classification, the family contract, automatic naming or the family GUI.
- [ ] **P1 either** 2.4 Specify how threshold-assigned family groups and
  below-threshold suggestions are represented, including evidence, version,
  reversibility, and surname/first-name assignment. Threshold-driven
  association and naming are approved; they must be explicit in the preview,
  not silent or confused with identity matching.
- [ ] **P1 ai** 2.5 Specify the smallest stable-ID-based catalogue
  representation for family groups, membership history, and confirmed versus
  suggested state. Test splits, joins, promotion/demotion, and a character
  slot changing occupants without making names or slots identity keys.
- [ ] **P1 either** 2.6 Approve a collision-safe naming/migration table for
  existing identities, unrelated surname reuse, and new family members.
  Existing names remain unchanged until individually resolved.
- [ ] **P2 ai** 2.7 Update the schema, validator, name/history helpers, and
  focused tests only after the metadata contract is approved. Keep `z_`
  history, catalogue identity, and fixed character-slot names consistent.
- [ ] **P1 ai** 2.8 Define a versioned JSON rebase-config schema for named,
  ordered classifications, usable-photo bounds, score/margin predicates,
  comparison targets, output roots, source options, family naming, and
  enabled state. Validate unsupported or contradictory rules explicitly;
  initial configs must not execute code.

**Exit:** each active person has a reviewed name state; family links and
below-threshold suggestions are distinct from identity; threshold-assigned
names are deterministic and reversible; collision behavior is explicit and
validated before any production rename.

### Phase 3 — build and exercise the sandbox rebase loop

- [ ] **P1 ai** 3.1 Preserve the corrected cast-only Prospect/Potential
  counterfactual as a baseline diagnostic, verify source exclusions, and
  retain original folder/import provenance. It is a comparison aid, not the
  main iteration interface.
- [ ] **P1 ai** 3.2 Build the people viewer from actual sandbox output
  directories. Show each identity's classification, family, source history,
  cast/other-person likeness scores, photo count, and full-size photos;
  retain flat, source-grouped, and family views without presenting score as
  identity truth.
- [ ] **P1 ai** 3.3 Add rebase mode/config selection for repeatable sandbox
  variants: cast-only identity references with all Prospect/Potential photos
  as candidates; and the same mode with an explicit option to include
  eligible low-own-core-score cast photos as candidates. Show the exact
  source set, score cutoff, anchors/protections, and exclusions per run.
  Compare actual category folders with the relevant mode/config switched,
  rather than asking the user to predict each destination.
- [ ] **P1 ai** 3.4 Ensure Artist, legacy Model paths, archived, retired, duplicate,
  and otherwise ineligible photos are either explicitly excluded or shown as
  excluded with a reason. Test that widening a parent path cannot pull them
  into scoring.
- [ ] **P1 either** 3.5 Inspect actual sandbox folders and the gallery for
  labelled acceptance examples, including known non-cast cases and the
  Drakness/Drakniss examples. Correct source-label or viewer defects before
  drawing conclusions from results.
- [ ] **P1 ai** 3.6 Compare scenarios by per-photo destination, family
  candidate, review/hold status, new-cluster count, and source-group
  integrity. Do not use aggregate counts alone as acceptance.
- [ ] **P1 ai** 3.7 Once the sandbox boundary and reset allowlist are verified,
  run the actual
  end-to-end pipeline on a copied, representative library subset or full
  selected copy using the explicit rebaseline flag and JSON config. Rebuild
  sandbox outputs from the immutable snapshot, allow real category moves and
  threshold-based family-name assignment, generate the viewer from resulting
  directories, then verify logs, undo/reset, provenance, and no writes
  outside the sandbox.
- [ ] **P1 you** 3.8 Review the sandbox gallery and actual placements. Label
  false assignments, missed family groups, surname collisions, and Review
  overload; revise the threshold or rules and rerun the sandbox as needed.
- [ ] **P1 ai** 3.9 Support repeated clean runs with different configs and
  source modes from the same snapshot. Keep each run's config, category
  counts, assigned identity IDs, score evidence, and output manifest so
  actual destination folders can be compared without hand-identifying them.
  Re-running must not require a new user-authored photo assignment list.
- [ ] **P1 ai** 3.10 Run the complete diagnostic suite after each sandbox
  rebase: library-wide `calibrate`, per-folder `folder` consistency for
  eligible identities in Sisters, Angels, Models, Prospects, and Potentials,
  and the existing identity-core audit. Preserve each diagnostic's own score,
  thresholds, eligible/excluded counts, and conclusions; diagnostics inform
  inspection but do not silently change assignments. Measure each stage's
  elapsed time on the same snapshot, recording cache state and cold/warm runs
  where practical. Compare overhead with rebase time before deciding whether
  any diagnostic needs an opt-out or separate on-demand mode. Write per-photo
  and per-identity CSV evidence plus a readable Markdown run report linked
  from the run manifest.
  A pre-rebase warm-cache baseline was generated on Oct 21 at
  `Working\_reports\diagnostics\sandbox-baseline-20261021-161618`: 2,543
  calibration comparisons and 89/194 active folders evaluated. The combined
  calibration/folder pass took 15.22 seconds (0.73 load/cache, 14.49 scoring).
  That pre-rebase bundle did not include the identity-core audit. After the
  sandbox category-only pass on Oct 21, diagnostics were rerun in
  `Working\_reports\diagnostics\diagnostics-20261021T233723319309Z`: 2,543
  calibration photos, 89/194 eligible folder checks, and 2,265 per-photo
  folder scores in 15.73 seconds. These results are post-category-move
  evidence, not a complete post-routing diagnostic bundle. The existing
  identity-core audit was run for all 261 folders and saved as
  `identity-core-audit.txt`, linked from `diagnostics.md`. At that historical
  stage no full rebase-run manifest existed. The later clean run below has
  one; automatic diagnostic integration and gallery consumption remain open.

**First actual clean rebuild, Oct 21:** installed and verified
`Working\_sandbox-state\clean-rebase-20261021-2210`. The empty-cache run used
21 cast-only identity cores and 1,155 flattened candidate photos; the corrected
preview was replanned from those fresh measurements before installation.
Its manifest and CSV retain every source/hash/destination, initial per-photo
cast scores, exact policy/settings, and reasons. Previous category trees are
retained and installation/undo are regression-tested. Fia's four photos and
three of Amara's four photos physically entered Angelica Review, never her
Gallery/core. This global run produced 27 Prospect and 698 Potential folders,
no Models, and 564 candidate Review placements: fragmentation reflects the
structural defects identified above as well as unvalidated calibration; this
is not an accepted result. The earlier isolated
Jacinta/Freya examples do not predict this global result.

The regenerated overview/Review pages contain 817 identities and 2,667 photos.
The post-run ordinary reconciliation preview held all 564 candidates and
assigned none under the draft policy; no incremental moves were applied.
Calibration/folder diagnostics took 13.03 seconds, and the full identity-core
audit is saved in the run directory. These artifacts now exist for the actual
clean rebuild, not just the prior category-only operation. The checkboxes
remain open where family naming, alternate source modes, integrated diagnostic
consumption, organic incremental actions, and user acceptance are still needed.

### Installed unified sandbox trial, Oct 22

The fragmentation run above was verified and undone before installing
`Working\_sandbox-state\unified-rebase-20261022-01`. This is the current
inspectable trial, not acceptance of all plan deliverables. Its embedding
cache started empty, initial references were only the 21 Angel/Sister cores,
and all 1,155 non-cast candidates were flattened before scoring. A replan
reused only this run's fresh measurements. Old folder names were used after
scoring for display/name continuity, not as matching memberships.

| Actual destination | Identities created | Candidate photos |
| --- | ---: | ---: |
| Models Gallery | 16 | 155 |
| Prospects Gallery | 35 | 737 |
| Potentials Gallery | 89 | 187 |
| Angels Review | Existing cast | 31 |
| Sisters Review | Existing cast | 24 |
| Various Review holds | Not identities | 21 |
| Total | 140 lower-tier identities | 1,155 |

The 89 Potentials comprise 24 singletons, 43 pairs, 11 triples and 11 groups
of four. This repairs fragmentation mechanically; it does not establish
identity accuracy. All four Fia Hadley photos and all four Amara Berkley
photos now physically reside in Angelica Review, outside her Gallery/core.
Sophie's 39 source photos were distributed among nine destinations; inspect
the source/destination rows rather than assuming any resulting folder is a
confirmed person. The generated overview has 232 people, including 71 Artist
people; Review contains 2,667 unique photo records and 21 unresolved holds.

Run-local `run.json`, `photos.csv`, `report.md`, `policy.json`, `catalog.json`
and the saved centering mean preserve the scoring context and provenance.
Working now has an isolated `.likeness-library.json` with stable generated
identity IDs and migrated explicit configured anchors. Galleries and staged
actions use that local catalogue, not the production catalogue. Rebuild
install/undo tests cover restoring exact previous catalogue bytes, removing
a newly created catalogue, Various holds, and refusing undo after edits.

The shared candidate planner now serves both clean rebuilding and ordinary
incoming/Review reconciliation. Normal `library.cmd` no longer runs the old
Review/sort/singles/rematch decision chain. Artist-scoped grouping remains a
distinct provenance-constrained operation. Production apply refuses a draft
policy before housekeeping; draft previews still expose qualified proposals.
Reconciliation apply has verified backup, permission/hash revalidation,
journalled reversible moves and explicit rollback errors. Undo rechecks the
catalogue after backup before changing any files.

The saved **preview only** in `post-rebase-reconciliation.json` has 76
candidates, 228 frozen cores, five assignments, 71 held photos, one new
candidate cluster and six physical moves. No such move was applied.
Ambiguous photos already in an identity's Review remain there unless a
specific destination qualifies: zero existing Review-to-Various moves.
The six remaining proposals mean incremental convergence is not proven.

Implementation progress against 4.15-4.20 is partial: shared resolution,
small-group preservation, provisional four-to-five reclassification,
proposal/authorization separation, holds and real incoming execution are
implemented and tested. The subsequent continuation adds reciprocal disjoint
whole-identity merges, red-outlier reassignment, optional unmatched-outlier
splits and existing-identity category transitions. IDs, merge ancestry, name
histories, Review photos and derivatives are preserved through apply/undo;
complete source and merge-target inventories are checked again after backup.
Empty directory shells no longer prevent a later reverse category transition.

The current `.4` draft adds an independent-support diversity ceiling and
explicit unmatched-outlier permissions. They are uncalibrated draft settings,
not identity labels. The cast-review size gate is now configurable separately
from clustering and action support. The installed trial retains its saved
`.3` policy; the separate `maintenance-v4-preview.json` still reports 76
candidates, five assignments, 71 holds, six file moves and no identity actions.
Neither preview was applied.

After an approved apply, one read-only affected-core check records remaining
maintenance candidates without cascading further moves. Synthetic tests cover
residual work that must not be called convergence. Three full command-path
tests now apply real temporary-file moves, rebuild cores from final disk
membership without a reset, and require an empty second preview: four-to-five
promotion, unmatched-outlier splitting with source demotion, and reciprocal
merging. Only face measurements and external backup are stubbed; matching,
core construction, action planning, file moves and catalogue updates run.
The post-apply check also excludes staged mixed-pool photos using the same
source filter as the ordinary engine. Full labelled calibration, global
convergence and the separate
200+ incremental batch remain unaccepted. The old no-policy API adapter is
now isolated in `legacy_reconciliation.py`; command orchestration is extracted
to `reconcile_command.py` and established actions to `identity_maintenance.py`.
The broader CLI/library extraction is still open.

The GUI now offers an explicit chosen-identity Review move with closest
preselection, stable destination ID, protection/hash validation and undo.
Both generated pages' executable scripts compile; all 2,376 eligible numeric
score records have closest-other evidence, and restricted photos offer no
reassignment. Family naming/virtual groups, the actual secondary-model
comparison and separately approved production clean-full adapter/rebuild
remain open.

The full validation launcher passed; after the latest transaction changes
all 148 likeness-library tests passed and the installed run's `--check`
passed. Generated HTML has machine-checked evidence, but visual/browser
acceptance remains unverified: the integrated browser refused the external
B: location as outside its trusted folders. Do not bypass that restriction.

Current-run diagnostics are now saved under this run's `diagnostics` folder:
2,515 leave-one-out comparisons, 94/161 eligible active-folder checks and
2,235 per-photo folder scores. Load/cache took 0.67 seconds, scoring 12.57,
total 13.23. The separate `identity-core-audit.txt` covers 228 folders using
the saved policy and centering context. Calibration ranks the current folder
first for 2,301/2,515 comparisons (91.5%) and flags 44 confident alternative
matches at 0.40/0.10. These assume current folder labels are truth; they are
not labelled identity accuracy or a reason to move protected cast. Automatic
diagnostic attachment to the manifest and gallery consumption remain open.

**Exit:** two or more full sandbox runs from the same source snapshot produce
real, inspectable category directories and viewer results under different
configs/source modes; reset and isolation tests pass. The user can judge
actual placement by scanning the directories/gallery rather than predicting
destinations from a report or routing photos by hand. Each run also completes
the diagnostic suite, records measured runtime and evidence, and publishes
machine-readable and human-readable results.

### Phase 4 — improve matcher, cluster evidence, and routing

- [x] **P1 ai** 4.1 Reconcile the two plans into the unified processing
  contract above, separating grouping, matching, classification, protection,
  core evidence and authorization. Completed Oct 21 as documentation only;
  implementation and behavioral acceptance remain open below.
- [ ] **P1 ai** 4.1a Specify category precedence for a frozen run: resolve
  confident same-person matches first; hold unresolved identity cases that
  plausibly match cast for Review rather than declaring a new Model; then
  hold identities with fewer than five usable photos in Potentials; classify
  remaining 5+ photo groups as Models only when their group-to-cast
  resemblance is in the configured Model band, otherwise as Prospects.
  Record ambiguous multi-cast results for deliberate handling. A high
  resemblance score alone never proves same-person identity.
  Historical experiment `2026-10-21.2`: a 1–4-photo candidate group scoring at
  least 0.40 to cast is held for cast Review before Potential classification;
  its proposed Review destination requires a 0.10 lead over the next cast
  identity. A closer result remains an ambiguous cast hold. In a
  counterfactual using Fia's four source photos as Pool candidates and
  excluding Fia and all Prospect/Potential cores, their group score is 0.461
  to Angelica versus 0.159 to the next cast core, so the draft flow proposes
  Angelica Review. This is a test hypothesis, not an approved threshold or
  historical explanation: the immutable Oct 21 Source snapshot already
  contains Fia's Potential folder, and the earlier assignment-time run record
  is unavailable. Do not claim the post-state leave-one-out scores explain
  the original assignment.
- [ ] **P1 either** 4.2 Calibrate and document the looks-like threshold and
  action-specific match/margin policies against labelled and sandbox results.
  Family assignment may be automatic in the sandbox; keep production routing
  thresholds unchanged until the evidence and acceptance criteria support a
  documented change.
- [ ] **P1 ai** 4.3 Add group-to-group and person-to-cluster comparison
  evidence where validated, retaining independent identity cores. Ensure
  multiple appearance clusters can inform a candidate without silently
  merging people or adding uncertain photos to an established core.
- [ ] **P1 ai** 4.3a Implement the config-driven category evaluator for
  supported declarative predicates. Classify by ordered rules and frozen
  evidence; validate duplicate IDs, overlapping rules, gaps, unreachable
  classes, missing roots, and deterministic precedence. Keep algorithms in
  code and category policy in JSON.
- [ ] **P1 ai** 4.3b Prove a sandbox-only JSON edit can change supported
  thresholds and enable a new classification class, then rerun from the same
  snapshot to produce changed real directories. Invalid/ambiguous configs
  must fail before reset or photo writes.
- [ ] **P1 ai** 4.4 Integrate selective Review routing into the primary
  pool-to-identity flow so uncertain plausible candidates have an explicit
  destination. Keep unrelated/no-match photos eligible to become ordinary
  Prospects/Potentials; do not send every uncertain photo to Review.
- [ ] **P1 ai** 4.5 Use a frozen pre-run snapshot for scoring and deterministic
  same-run candidate clustering. Provisional groups must not mutate trusted
  cores or cause order-dependent cascades; each photo is assigned at most
  once per run.
- [ ] **P1 ai** 4.6 Add focused tests for ties, margins, small groups,
  category transitions at four/five usable photos, cast-like Model
  classification versus same-person routing, Prospect-to-Prospect families,
  Potential score display, mixed-source clusters, noisy/poor photos,
  duplicate IDs, protected/anchor images, source exclusions, and repeated
  deterministic runs.
- [ ] **P1 either** 4.7 Compare previews against user-labelled decisions and
  report action-specific precision/recall and review volume. Adjust design or
  scope until the targets agreed in Phase 4.2 are met.
- [ ] **P1 either** 4.8 Accept or reject the sandbox-calibrated threshold
  based on viewer results and measured errors. A rejected calibration
  returns to Phase 3/4 for another sandbox iteration, not a production run.
- [ ] **P1 ai** 4.9 Refactor the rebase classifier and ordinary likeness
  intake to call the same engine and category-policy evaluator. Keep path
  guards, reset, run manifests, and sandbox overrides at the boundary; do not
  fork matching or merge/split behavior for sandbox. Record the shared default
  config and any explicit sandbox override per run.
  This includes replacing the primary `library_sync.py` Review/sort/singles/
  rematch sequence, not just adding a read-only `reconcile` command. Each
  retained legacy operation needs a documented distinct purpose or a tested
  compatibility adapter; no ordinary launcher may silently bypass policy.
- [ ] **P1 ai** 4.10 Add declarative per-category hierarchy/order, thresholds,
  match margins, merge/split/routing permissions, Review policy, core policy,
  and protection behavior. New categories such as Demons must be addable via
  validated config when they use supported rule types. Algorithms remain
  shared code; fail invalid or unsupported policy before moves.
- [ ] **P1 ai** 4.11 Implement incremental, idempotent self-healing on newly
  ingested photos and affected identities: evaluate both directions of a
  candidate merge/split, avoid chain cascades and oscillation, retain
  provenance, and produce a preview/action manifest before any production
  apply. The clean rebase remains a separate baseline/recovery command.
  Reciprocal disjoint merges, supported red-outlier splits, final-membership
  category transitions and one bounded read-only final-core check are now
  transaction-tested. Three measured synthetic command scenarios now reach
  a no-change second pass without reset. This box stays open for labelled
  real-batch idempotence; no recursive established-core cascade is authorized.
- [ ] **P1 ai** 4.12 Implement the agreed protection contract. Identity
  protection blocks automatic Gallery-membership and identity changes;
  incoming identity-associated Review has separate admission permission. Photo
  protection suppresses automatic removal and Review routing but keeps the
  photo's score visible; protection does not force core inclusion. Workflow
  selection confers photo protection automatically. Add tests for low-score
  protected photos, independently selected anchors, protected identity
  destinations, workflow availability, and explicit gallery badges.
- [ ] **P1 ai** 4.13 Immediately after the sandbox rebase, run the normal
  likeness process in preview mode against that result. Save the proposed
  changes and compare them with the rebase manifest; do not apply them
  automatically. Use the differences to verify the shared policy and
  incremental idempotence.
- [ ] **P1 you** 4.14 After the initial sandbox rebase and preview comparison,
  add the separate 200+ image batch to the sandbox and run ordinary likeness
  intake without reset/rebase. Review organic merges, splits, category
  transitions, Review routing, protected cases, and directory-level results.
- [ ] **P1 ai** 4.15 Replace competing settings with one schema-validated
  effective-policy resolver. Inventory every consumed value and caller,
  distinguish comparison metrics, move behavioral defaults out of `engine.py`,
  and provide explicit migration for workspace overrides. Report provenance,
  reject conflicts before writes, and test that both modes resolve the same
  rules when given the same scope/evidence. Complete before threshold trials.
- [ ] **P1 ai** 4.16 Preserve singleton/pair/group evidence through planning.
  Separate group formation, action-support minimums, core viability and
  category photo counts. Define deterministic ties and robust provisional
  cores, preserve appearance subgroups, and reclassify from final planned
  memberships. Regress the perfect pair and four-to-five-photo transition.
- [ ] **P1 ai** 4.17 Separate proposed decisions from authorization. A
  draft/preview must expose the same qualified destinations and reasons as
  an authorized apply; approval controls writes, not similarity evidence.
  Test explicit sandbox experiment authorization, production refusal, and
  selective cast Review without cast Gallery/core admission.
- [ ] **P1 ai** 4.18 Define, document and implement recoverable unresolved
  holds in the manifest, filesystem adapter and both galleries. Preserve
  group IDs/alternatives; do not name every held photo as a new identity or
  split a held group. Genuine unmatched singletons/pairs remain eligible
  identities. Test no loss, no duplicate placement, retry and undo.
- [ ] **P1 ai** 4.19 Build action-labelled regression cases before another
  installation: Fia's confirmed sequence, Amara, Jacinta/Freya diagnostics,
  Sophie's mixed membership, perfect pairs, unrelated lookalikes, poor faces,
  same-shoot near-duplicates, anchors/protection and workflow selections.
  Do not use current folders as unquestioned truth. Compare the grouping
  trial values and tier-specific attachment/merge/split rules; report false
  merges, missed matches, hold/Review volume and fragmentation separately.
- [ ] **P1 ai** 4.20 After 4.15-4.19 and shared routine integration in
  4.9-4.12, verify the full launcher path before replacing the sandbox result.
  Compare planner evidence across modes with controlled references, test
  bounded follow-up and final-core consistency, then preview normal intake
  immediately after a clean run. Zero changes from a disabled action path
  do not establish idempotence. Test the 200+ batch through ordinary intake
  after the user stages it; do not substitute a second clean rebase.

**Exit:** source-to-destination behavior is explainable, repeatable, and
meets user-approved action-specific validation before any automatic routing
expands.

The initial category hypothesis is at least five usable photos plus
group-to-cast likeness in the unrounded interval `[0.40, 0.55)` for Models;
the viewer may display these values as 0.40-0.54. A score at or above 0.55
does not by itself prove same-person identity and must not automatically
become a Model or be assigned to cast. Apply the separate same-person
assignment policy first; unresolved plausible matches go to Review/hold.
Calibrate score, margin, and precedence using labelled sandbox results
before treating this interval as a production rule.

### Phase 5 — family gallery and safe naming workflow

- [ ] **P1 ai** 5.1 Add family/lookalike grouping to the local people gallery
  using stable identity metadata. Show whether a link is suggested or
  threshold-assigned, preserve category/person filters, and retain the flat
  view. Show cast-likeness scores for Models, Prospects, and Potentials in
  candidate browsing; score visibility must not imply same-person identity.
- [ ] **P1 ai** 5.1a Add gallery controls to include/exclude classifications
  and family groupings from the current view. A viewer toggle must not mutate
  person classification, directory placement, or likeness-processing config.
- [ ] **P1 ai** 5.1b If supported in the POC viewer, allow enabling/disabling
  a classification for the next sandbox rebase by exporting a validated
  config file. Do not let the browser write library files or silently change
  current directories; require the explicit rebase command to apply the new
  config.
- [x] **P1 ai** 5.1c Preserve the useful existing People Gallery statistics
  and add a shared cross-reference for every identity: likeness scores to
  Angels and Sisters (including Angels versus Sisters), plus the strongest
  relevant library matches. Keep identity similarity distinct from family
  association and same-person evidence.
- [x] **P1 ai** 5.1d Retain the pairing-specific Top Prospect alternatives
  for Angels and Sisters, but make full rankings cover the whole candidate
  library, including Models, Prospects, and Potentials where eligible. Show
  alternatives as separate, readable lines rather than one long sentence.
- [x] **P1 ai** 5.1e Add a Summary/Full details selector to the main People
  Gallery. Summary is the routine view; Full details exposes cross-reference
  scores, complete rankings, and the retained diagnostics without removing
  existing meaningful stats. Keep the selected view presentation-only.
- [x] **P1 ai** 5.1f Add useful per-identity cross-reference and classification
  details to the Review Gallery so users can inspect scores alongside the
  existing nine-photo identity evidence and review actions. Show filename-derived
  Photo ID separately from stable person Identity ID, and expose core mode,
  size, membership, face evidence, scoring method, and applicable thresholds.
  Use bullet details and color cues; make face size/count open a cached face crop.
- [ ] **P1 either** 5.1g Evaluate the controls and score presentation against
  actual sandbox category directories, including Angels, Sisters, Models,
  Prospects, and Potentials. Confirm the nine-thumbnail view, summary/full
  switch, and full-library rankings are understandable before accepting a
  classifier configuration.
- [x] **P1 ai** 5.1h Align both gallery pages on Sisters → Angels → Models →
  Prospects → Potentials ordering; concise copy; one relationship per line;
  consistent category and similarity badges; Review-first name links with a
  score-direction triangle for in-gallery jumps; presentation-only colored
  adjusted-fit cost; subsection spacing before alternative rankings; and a
  direct chosen-source link when that image is outside the top nine. Keep action
  previews out of the overview, photo actions in Review, and retain the distinct
  Prime-start photo score. Highlight a visible workflow photo with a strong
  score-colored border and place category/status tags below the identity name.
- [x] **P1 ai** 5.1j Add a staged workflow-photo selection for Gallery photos
  belonging to configured Angels/Sisters. Apply through the existing workflow
  repoint helper with verified backup and audit history; support stale-state
  validation and undo, leave flow-specific overrides separate, and refuse
  application against an isolated sandbox root.
- [x] **P1 ai** 5.1i Add person-wide Protection for Models/Prospects separately
  from photo Protection. Follow the cast protection contract: protect the
  identity from automatic category/routing moves while leaving it visible to
  scoring and cross-references; per-photo protection continues to exclude only
  that photo from its identity core. Key the person action by stable person ID
  so it survives renames/category moves, and use staged preview, backup,
  stale-state checks, and undo. Do not imply the current photo action protects
  a person.
  Implementation contract: separate `person-protected` / `person-unprotected`
  actions carry the stable person ID, current folder and expected protection
  state, without borrowing a photo ID or hash. Initially expose these controls
  for registered Models/Prospects only. Cast protection cannot be disabled.
  Reject duplicate identity decisions and mixed photo/person decisions for the
  same identity in one batch; apply and undo preserve the full person snapshot
  and revalidate catalogue changes across backup. This changes automation
  permission, not identity scores, core membership or workflow selection.
  Implemented Oct 22 morning with schema, backend, manifest export, preview,
  verified-backup apply/undo and full person-state history. Synthetic browser
  checks cover export, cancel and conflicts in both staging orders; engine
  tests confirm category changes are blocked without changing core scores.
  Actual sandbox reports expose controls for all 16 Models and 35 Prospects,
  never cast, Potentials or mixed sources; active catalogue and saved policy
  remain byte-identical after regeneration.
- [ ] **P1 ai** 5.1k Show rebase diagnostic results consistently in both
  gallery pages. Put library-wide calibration and run-quality summaries in
  the People Gallery; repeat concise per-person consistency/quality indicators
  in both the overview card and Review heading. In Review, expose separately
  labelled per-photo evidence and thresholds in the detail view. Keep
  different measures distinct and do not imply that similarity proves
  identity. Consume the run's saved CSV/Markdown evidence rather than
  recomputing diagnostics when a page opens.
- [ ] **P1 ai** 5.2 Add a read-only preview for threshold-assigned family
  names. Display current `z_` name, proposed first/last name, reason, family
  members, collisions, and any source-history mismatch. Do not rename from
  browser code or infer a relationship from the surname.
- [ ] **P1 ai** 5.3 Reuse the existing staged person-action manifest and
  preview/apply/backup/undo path for approved rename and family-link changes.
  Validate stale state, collisions, fixed slot paths, and preservation of
  prior `z_` history.
- [ ] **P1 you** 5.4 Review the sandbox family groups and assigned names in
  the generated preview; identify exceptions and whether the threshold is
  ready for the normal-library batch. Similar first initials are preferred
  when unique, but no name may overwrite fixed character slots or erase
  recorded `z_` history.
- [ ] **P2 ai** 5.5 Refresh the people index, gallery, and documented
  ComfyUI-facing references after a successful apply without changing fixed
  character-slot workflow keys.
- [ ] **P2 ai** 5.6 Show intended card-use guidance by category in the
  gallery: Models are not the user's common/uncommon choice; Potentials are
  suitable to browse for common/uncommon; Prospects are candidates for
  broader card use. This is descriptive guidance only, not automatic card
  assignment or a game rarity rule.

**Exit:** the user can see useful identity-wide likeness evidence and related
identities together, switch between summary and full rankings, inspect
per-identity review details, tell suggestions from confirmed links, and
approve reversible names without changing matching or workflow identity.

### Phase 6 — required clean-full production rebase

- [ ] **P1 ai** 6.1 After accepted sandbox clean and incremental tests,
  freeze the rules, source scope and family naming output. Build the
  production clean-rebase manifest from current production inputs while
  preserving original source path, import group, identity history, and
  before/after evidence.
- [ ] **P1 you** 6.2 Review the complete visual preview and manifest,
  including hold/review groups, automatic family names, category boundaries,
  selected/protected photos, and all exceptions. Approve the exact batch or
  return it for changes.
- [ ] **P1 ai** 6.3 Verify a fresh external-library backup and restore
  procedure before applying; verify every manifest hash and current source
  location immediately before moves.
- [ ] **P1 ai** 6.4 Perform the clean-full production rebuild of the approved
  scope using the same engine, cast-only initial references, flattened
  candidates and approved manifest through a recoverable production adapter.
  Do not apply sandbox paths to production or substitute category-only moves.
  Log each change and verify
  resulting folder counts, identity history, catalogue references, Review
  routing, and undo.
- [ ] **P1 you** 6.5 Inspect the refreshed gallery and selected ComfyUI
  references; report any false assignment or missing history before the next
  batch is considered.

**Exit:** the approved production scope has actually been clean-rebuilt and
verified, with preserved choices/history, refreshed galleries, auditable
action history and tested rollback. The ordinary shared intake path is ready
for subsequent batches; no unapproved photo moves are applied.

### Phase 7 — prevent recurrence and close obsolete paths

- [ ] **P1 ai** 7.1 Run labelled future-batch tests through the actual
  `bin\library.cmd` and `bin\likeness.cmd` entry points, covering Gallery,
  Review, Various, Artists, old Model, archives, Prospect, and Potential
  boundaries. Exercise ordinary processing separately from sandbox rebase
  mode and reject sandbox reset flags against production paths.
- [ ] **P1 ai** 7.2 Ensure generated reports explain destination and
  evidence, Review receives only selected uncertain candidates, and
  unmatched identities remain manageable rather than proliferating from
  within-batch ordering.
- [ ] **P2 ai** 7.3 Remove or retire only features approved by the sunset
  matrix after replacement behavior, launcher compatibility, data migration,
  and focused tests are complete. Delete obsolete tests only with the feature
  and its callers; retain regression coverage for excluded sources.
- [ ] **P1 ai** 7.4 Update the likeness guide, affected runbooks, active plan
  checklists, `docs/STATUS.md`, and generated `docs/todo.md`. Record completed,
  transferred, superseded, and independent tasks without closing unrelated
  plans.
- [ ] **P1 either** 7.5 Resume ordinary photo ingest only after the user
  approves the acceptance results and the guarded incoming path is verified.

**Exit:** future imports use the validated flow; retired behavior is gone
without breaking supported commands; all linked documentation and queues
reflect actual state.

The Oct 19 library-management plan's five-photo Potential-to-Prospect rule
remains the current applied policy until this plan's three-tier classifier is
validated and deliberately applied. Do not silently change existing folder
categories while building or testing the new Model destination.

## Existing-plan reconciliation

- The [self-healing likeness plan](2026-10-20-likeness-library-self-healing.md)
  remains the implementation foundation for metadata, stable IDs, review
  galleries, manifests, backup, apply, and undo. Its open tasks are not
  presumed complete. Its rebaseline-related E1/E5, F1b-F4, C6, and Phase I
  name work now point here; C7 stable report-directory replacement remains
  open pending the Phase 0 review. Its H1/H3 planner integration and behavioral
  configuration work are also transferred here to 4.9/4.15; H2/H4/H5 retain
  incremental extraction, compatibility and documentation support. E2-E4
  describe a read-only prototype, not completed end-to-end self-healing.
- The prior report-only cast audit and corrected source-labelled forecast
  remain evidence. Their counts are not a new policy or movement approval.
- Finish only existing likeness items that are genuine prerequisites. The
  independent chest-crop sample, manual prompt review, artist art review,
  game/MVP work, and unrelated workflow tasks can continue separately.
- The [art-tools structure plan](2026-10-20-art-tools-structure.md) remains
  the home for broad package refactoring. This plan permits only targeted,
  behavior-preserving modularization required to simplify matching safely.
- The [tooling-debt plan](2026-10-12-tooling-debt.md) retains independent
  readiness/status work. Any likeness-specific threshold, source-scope, or
  sunset task transferred here must be marked there rather than duplicated.
- The Oct 19 library plans stay active for independent outstanding work;
  neither is closed by this rebaseline.

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

## Immediate execution order after reconciliation

1. Preserve the installed unaccepted run as evidence and retain its rollback.
   Do not rerun placements merely to lower its folder count.
2. Implement 4.15-4.18: one effective policy, preserved small groups,
   proposal/authorization separation, explicit holds and selective cast Review.
   Develop the labelled regressions in 4.19 alongside those changes.
3. Wire and test 4.9-4.12 through the actual normal launcher, including
   operational merge/split planning, protection and affected-identity handling.
   Extract touched responsibilities into modules; do not build a third engine.
4. Complete 4.20 and the remaining Phase 3 evidence work: compare controlled
   threshold trials, then install inspectable clean sandbox results, publish
   diagnostics and galleries, and test ordinary post-run maintenance.
5. Test the staged 200+ batch without resetting. Compare actual placements,
   missed matches, contamination, holds, category transitions and recovery.
   Keep family naming and GUI work connected to these results, not as a
   substitute for correct membership.
6. Obtain acceptance of the tested scope/configuration, then complete the
   required clean-full production run in Phase 6. Resume ordinary intake
   through the validated shared path.

Open numerical calibration and naming decisions remain explicit review gates,
not excuses for duplicate engines or for suppressing sandbox experimentation.
The documentation reconciliation is complete; the implementation is not.

## Raw user direction (Oct 21)

Ok - so is this a working plan or what needs to be done to define all the details behind what we need to do - I'll go with Option A and the sub-option as my choice and want to be able to get to work on this tomorrow - which means wrapping up any of the "we must do this first" loose ends from existing work before jumping into the full body of work.

I think we need the detailed docs/plan with proper check-list items for the iterations of work so we can update the plans, docs, code and tests all in parallel - just like we were doing today.  And I also feel like I need an executive summary of what all the work we need to do is - just so I get both the detailed and the high level view of the phases, steps and such.

Today we accomplished a lot and now we're pivoting as we learned through this entire process - but it does mean re-working things that already exist as well as building out things new.  The last thing I would add is that if we identify more things like excluding Artists and the old Model folders and addressing complex code areas since we will be touching the core sorting and matching - we should do that as well and not throw more complexity on top of something already overly complex.

If there are any features we can sunset - that should be called out to help simplify code and tests - for things we're touching anyway.  Refactoring is always a preference in my mind when we're making changes - unless they are truly tactical and we don't want to risk a larger changed - but eventually that comes back to bite you as the Artists did for a bit today.

## Raw user follow-up (Oct 21)

I am ok with auto-assigning family names based on looks-like with the
threshold, we will preview the results and if I can view them in a viewer
that's fine - if we need to stand up a sandbox on B:\Sovereign Territories
Sandbox\ and run things for real there so it's not all simulation - that's
fine as well.  Just food for thought on how we can test things without doing
all simulation or preview only mode.

## Raw user direction: config-driven sandbox rebaseline (Oct 21)

I'd like to see it implemented as a flag on the likeness processing so it's
automated in the sandbox and we can test it both ways without me guessing who
goes where.  That way I can see it more directly instead of using it by hand.
This work well in the gallery as a classification we keep tied to the
identity and we can enable or disable those groupings or classifications in
the GUI - but we keep it tied to the directory structure as that'll make
things easier when I am using ComfyUI to pull images for testing how they
render.  That'll be the best real-world test.  I'm less concerned about being
cautious and putting the burdeon on me to have to remember or focus on
reports or just the GUI to test.  Scanning the directories is an easy way for
me to see how things are working.  I'm actually thinking we might eventually
want to add in another classification tier and conditions as well.  If we
can drive some of this from data or config options for likeness then it would
be easy for me to add a new classification with conditions.  In fact, even
being able to adjust the numbers for all the pieces within the sandbox and
re-running a rebase (blowing them all away) and trying again to reset the
entire Models, Prospects and Potentials in the sandbox is actually 1000%
better that previews and reports.  Since it's a sandbox, we can be more
liberal about how we run that without worrying about messing things up.  So
I'd want to approach this as a true POC area where I see the final/end
results and not be so conservative about should or shouldn't I.  We'll then
be able to learn and fine tune ALL the scoring without you being concerned
that I'll break things.  So if I want a new classification - I just add in a
config, give it a name - fill in the parameters and rebase the entire library.
This is part of self-healing and would allow me to just reset everything and
verify where things land.  What that solves for me is that each run - we
start with clean cache of only angels and sisters.  This also gives me the
ability to test out pulling the lower scores from angels and sisters (with
the option I mentioned I wanted for that as well) and see the actual results
of what happens.  Not simulation or reports - but real results. Combine all
this into the plan and then give me a recap of what I need to address first
after we get the plans finalized and actionable.

## Raw user direction: complete rebase diagnostics and gallery evidence (Oct 21)

I do think that since we need to work on the rebase that we should
incorporate those into the process - at least we can check the timings on
them and ensure they don't cause too much delay - but those items would be
great diagnostics and if we need to put the outcome into both .md and .csv
files for the GUI and human reading - we should do that. Ideally a rebase is
an entire re-run of all the various diagnostics so that the GUI can show all
the data and tell me all the quality and ratings. We can make some of the
per-image ratings for different diagnostics separate if we run two separate
analysis on photos with scoring - surfacing everything all together at a
entire repository on the gallery or the per person at the top and the per
image where there are images. Any key per person items can appear on both
the gallery and the review (top) so I don't have to flip back and forth from
review to gallery to see useful information that should really carry into
the header of the gallery. IF there are photos we need to adjust in a
per-person view or if they are all good. That's all useful information
summarized on the gallery and in much more details on the person review page.

## Raw user direction: incremental likeness and protection policy (Oct 21)

Yes - that action boundary is right.  It allows for organic growth
merging/splitting at the bottom with lower threshold (which we can configure)
and not require manual intervention because until the are prompted to an
Angel or a Sister those files are not in use by a workflow, so it's less
important to "worry" about how they grow/split.  Once they reach the point of
a Model and they look like a Sister or an Angel, we'd want more caution, but
still an intermediate threshold for auto merge/split and use Review more
often.  All layers of identity can also be protected as a way to prevent
something moving in/out at the lower threshold, basically it moves that
identity to the same level of protection as an angel and we'd want to ensure
we shot the protected "tag" in the GUI for both identity and images - so
it's clear.  Basically all the meta-data about an identity or their images
can be used in the auto-merge.  So if there is a low scoring image for a
Sister and I protect it specifically, it should not go to Review in the
likeness process, but I can prevent it from being part of the core identity.
Basically, that would be a pose, laugh or some other thing driving the score
lower - but I would use it in a workflow due to body, side of face or even
the laugh expression.  I understand there is risk at the lower levels - but
I don't care as much about them until I promote or protect them.  As long as
the configuration is able to drive the different values at a category level
that will allow me to add new categories like Demons and set them in the
hierarchy either at same level as Angels or even if I decide on another
category I can configure it's values.  That's the likeness engine I am
looking for.  A full rebase should eventually become a last resort, but right
now that's where we are starting from and it's the foundation for building
out the layers in a first run.  The reason I want to do this is I have
another batch of 200+ images to bring into the Sandbox after we rebase and
then I want to see how the organic growth works there.  Not a full rebase.
It should match at different levels in the hierarchy and will test out these
changes in the sandbox.  It's possible the Sandbox may have slightly
different rules - but honestly, I feel like they should be 99% aligned on how
they evaluate things.  One additional test will be to run the normal likeness
process directly after the rebase to see if that logic changes anything.  I'm
interested to preview that and see what happens as well.  Yeah - the logo
idea was separate and not meant to clutter this discussion, I was just
taking notes as it does impact the likeness process if we engage the
"cleanup" (not just cropping) logic.

## Raw direction retained from the superseded working draft

The draft's discussion options are superseded by the approved direction in
this plan. These original user paragraphs are retained unchanged apart from
line wrapping.

It might also make sense to re-review all the other docs/plans for anything that was defined that is or isn't completed and factor that into our overall plans - because this could change the course of what we were doing or it might require we expedite things we deferred or finish off existing plans while working this through.

In my ideal world - if we do the automatic rebase, it would automatically pull all the Prospects and Potentials back - and possibly even low scoring Angel or Sister pictures directly into the large pool for the rebase (because some of the lower ones I put by hand in the Angels and Sisters would either go back to the Angel or Sister or would end up in a Family) - that's maybe an additional parameter to preview to determine just how much that would do.
I think we already identified a few images in Drakness that would end up in Drakniss if we did that.  So there's already evidence - and I did visually confirm that was probably valid to do from the previous report we ran.

I think now we're finally getting down to brass-tax here on what's been bugging me and why I wanted the gallery and reviews to start with - I could see we had clustering issues when I was trying to sort things out and it wasn't so obvious until we got this far into the work.
But all of this is beneficial for the long term health and growth of the image library.
Even if we kept and keep going in circles around the core problem of our matching is causing sprawl in the current library and it NEED to be fixed and more with automation and placement automatically with some need for review - just not so much that I am having to do now!

## Raw user clarification: production and unified engine (Oct 21)

One more thing to clarify - the sandbox is just the test bed, but a clean-full rebase also needs to happen in production when we're done.  Please re-read the C:\Soverign-Territories\soverign-territories\docs\plans\2026-10-21-likeness-rebaseline-and-family-naming.md for the problem statement and the issues we're trying to solve.

I think the policy is misguided in an attempt to use the .55 rule to trying to protect the Angels and Sisters from direct assignment and dropping them should have allowed them to cluster and/or go into review for that angel.  I did not ever think it was applied to formation of new clusters where the did not match.  It feels like we have 2 engines right now vs. a more unified system.  Wow - the work earlier today was supposed to reconcile all of this - but the clustering at 0.55 I think is conflated with other rules and now we're in a bad state due to this work and someone being ultra conservative about the sprawl that was happening.  So we need to come up with a proper approach and figure out what makes the most sense using rationale numbers and ensure that our tiered system is working and that we don't have conflicting rules engines or at least if they differ - it's a very clear reason.

If you can reconcile and update the plans with proper approach that seems to unify things across the engines and doesn't conflate rules with each other that would be great.  I can't undrestand how we ended up in this spot.
