# 2026-10-22: identity families and safe naming

**Status:** active (draft metadata/naming implemented; real acceptance and rebase migration remain open)

## Oct 25 implementation continuation

The user explicitly requested implementation rather than another planning stop.
Working defaults are selected for isolated draft-policy previews, not declared
calibrated or production-approved. The earlier approval questions remain
acceptance work, not blockers to building schema/helpers/tests.

Implemented for draft-policy preview/apply/undo:

- Optional catalogue `names` records preserve original/current person name and
  original-name source. Earliest recognizable explicit rename history is retained;
  an unknown original is labelled unavailable, never replaced by a cast key.
- Optional per-person `family` metadata records stable family/reference IDs,
  surname, similarity, policy version, previous person name and explanation.
  Families are organizational direct-reference groups, not biological assertions.
- New family groups require reciprocal, unambiguous direct references and five
  independent current core photos per identity. The draft automatic band starts
  at 0.40 and ends below 0.55 or either identity's stricter merge threshold.
  Reference lead is at least 0.05. Same-person ambiguity, stale evidence,
  insufficient diversity, pending membership changes or name collisions hold.
- Existing-family joins require direct evidence to the established founder;
  no surname-based or transitive association. Preserve first names rather than
  invent shared-initial replacements; collisions remain diagnostic.
- Family surnames change catalogue current-person presentation, not physical
  folders/history/workflow keys. Manual rename/swap retains immutable original
  provenance and exact undo. Galleries display character/current/original names
  separately, with family surnames appended to character display only.

Shared reconciliation composes protection, names and families into one full-record
metadata patch per stable ID, with source/hash checks and an existing backup/
journal transaction. Names-only migrations use that same path. No independent
family writer or alternate scoring engine is added.

Overview, Review (including mixed-photo grids), identity detail and family preview
use the shared presentation helper. Explicit protection reasons and persistent
manual-unprotect opt-outs are visible. Earliest recorded pre-rename catalogue
snapshots can recover original names; missing evidence stays unavailable.

N7's real labelled acceptance and broader migration remain open. Do not represent
an unrun library batch or a guarded rebase as completed identity continuity.

## Oct 25, 12:33: established identities, family names and original-name continuity

The user requests automatic protection of sufficiently supported identities and
their high-confidence photos, coordinated with reversible family naming and
gallery presentation. The full message is preserved below. Automatic protection
belongs to [engine E13](2026-10-22-likeness-engine-acceptance.md);
manual override/undo belongs to [actions](2026-10-22-review-actions.md).

Agreed direction, with numerical and override decisions still to be approved:

- Keep separate stable person IDs for distinct lookalikes. A family association
  is an organizational resemblance group, not confirmed kinship or a merge.
  Ambiguous same-person cases must be resolved/held before family auto-naming;
  a score below a merge gate alone does not establish distinctness.
- Preserve the earliest reliably recorded supplied or generated person name,
  its provenance and subsequent rename history. Do not overwrite it on family
  join/leave or replace it with a cast slot. Missing/conflicting history must
  remain explicit, not be reconstructed from a surname or folder guess.
- Show **character name** (where assigned), **current person name** (including
  assigned family surname), and **original person name** as separate labelled
  facts. Non-cast identities need no fabricated character name.
- Family assignments must retain prior names, stable IDs and exact recovery.
  Shared-initial first-name generation must never destroy the original name.
  Existing explicit name approvals and collision checks still apply.
- Family/name changes and protection must not influence matching evidence.
  Do not let family naming silently rename fixed cast directories/workflow keys,
  or let a rebase discard original names, overrides or family history.

Before implementation, the verified gaps were: the catalogue person schema had `displayName`,
folder history, anchors and protection, but no original/current-person-name or
family-membership fields. The read-only family preview uses direct reference
suggestions and flags possible same-person matches; automatic association is
disabled in the current draft policy. These are prerequisites, not delivered
behavior at that planning checkpoint. The implementation above closes the
schema/display gap; N2/N3's calibration and historical migration questions remain.

- [ ] **P1 ai** N9 Specify original/current/character-name provenance and
  migration in the existing catalogue contract; inventory reliable history and
  conflicts before populating fields. Extend schema/validators, rename/swap/
  undo and family transitions without losing original supplied/generated names.
  Test repeated rename, family join/leave, cast swaps, missing history and rebase.
- [x] N10 Wire the three-name display and family/protection reasons
  into Overview, Review and identity detail through shared payload helpers.
  Display unknown provenance explicitly; keep Artist domain boundaries.
  Coordinate layout parity instead of adding another independent name resolver.

N9 progress: schema, history recovery, rename/swap provenance, exact undo and
combined metadata transactions are implemented and unit-tested. Stable-ID
clean-rebase migration and explicit family leave/reassignment coverage are not
completed; the guard refuses destructive loss rather than claiming continuity.

## Review and questions: 2026-10-22 16:26 -05:00

Verified successor to the family portion of the former umbrella.
Approved D1-D7/D12 and Q4/Q5 remain in the
[processing contract](../art/likeness-processing-contract.md).
Before N2/N3 ask one at a time: may one-to-four-photo Potentials receive
automatic family names, or only suggestions? Which incomplete names can be
recovered from history, versus supplied by the user? What threshold/evidence
creates a reversible relationship rather than just a suggestion?
Preserve existing user-approved names (including Angelica Vale) until resolved.
No family relationship or rename is inferred merely from surname reuse.

## Scope and decisions

This plan owns virtual family/lookalike relationships, threshold-assigned
family naming, collisions, stable metadata and their gallery presentation.
Keep category folders: no physical Families/Twins root. Shared surnames and
preferably distinct first names with a shared initial are naming outputs,
never identity evidence. Family resemblance never permits a same-person merge.
Fixed cast slots remain separate from the recorded real-person name.
Production naming still requires the [engine acceptance gates](2026-10-22-likeness-engine-acceptance.md).

Manual rename is shipped through staged JSON, backup/apply/undo. Protected cast
renames change only the recorded name/history; non-cast folder renames refuse
unsupported references. Swaps and broad action availability belong to
[manual actions](2026-10-22-review-actions.md); presentation structure belongs
to [layout](2026-10-22-gallery-review-layout.md).

## Evidence, not acceptance

The full-name audit corrected four incomplete records and reported 265 complete
names at that historical stage; it is not today's catalogue count.
`family-preview` is read-only. The saved `.3` scenario inventory had 232 people,
138 closest-reference suggestions, 52 reused surnames, 71 Artist-person
exclusions and no current full-name/folder collisions. One proposed name
conflicted with an existing name; two proposals conflicted with each other.
Surname reuse is not confirmed kinship. The preview neither saves accepted
family metadata nor performs automatic naming.

## Remaining work

| Live task | Oct 21 source tasks | Retained work |
| --- | --- | --- |
| N1 | 2.3 | Classify surname reuse, not just count it |
| N2 | 2.4, 2.5 | Relationship contract and stable-ID schema |
| N3 | 2.6 | Approved collision-safe migration |
| N4 | 2.7 | Schema/helpers/tests after contract approval |
| N5 | 5.1, 5.1a, 5.2 | Family viewer, classification filters and naming preview |
| N6 | 5.3 (family-link/name portion) | Staged family changes; manual swaps owned separately |
| N7 | 5.4 | Actual family/name acceptance |
| N8 | 5.5 | Refresh index/reports/references without changing cast keys |

- [ ] **P1 ai** N1 Classify surname reuse as confirmed resemblance,
  unrelated or unresolved, and inventory case-insensitive name/folder collisions.
- [ ] **P1 either** N2 Specify and approve suggested versus threshold-assigned
  family links, evidence/version/history, reversibility and naming thresholds.
  Use stable IDs; cover splits/joins, promotion/demotion and changed cast
  occupants without making slots or names identity keys.
- [ ] **P1 either** N3 Approve a deterministic naming/migration table,
  preserving existing names until resolved and rejecting collisions.
- [ ] **P2 ai** N4 Implement approved family schema, validators and helpers
  in contract-first order. Preserve exact prior name/history on undo and test
  stale decisions, collisions and rollback.
- [ ] **P1 ai** N5 Show suggested/assigned family links, members, current
  and proposed names, evidence and source-history mismatches in the gallery.
  Preserve flat/category/person views, classification/family filters and
  cast-likeness evidence without implying identity confirmation.
- [ ] **P1 ai** N6 Wire approved family-link and family-name changes through
  the existing manifest/preview/verified-backup/apply/undo boundary, not browser
  filesystem writes or a second naming engine.
- [ ] **P1 you** N7 Review actual sandbox family groups, exceptions and
  proposed names; accept thresholds before the production batch.
- [ ] **P2 ai** N8 Refresh the people index, galleries and documented
  workflow-facing references after apply/undo, preserving fixed cast keys.

## Closure

Close only when family metadata, viewer, reversible writes and user acceptance
are complete. Existing manual rename and the read-only preview do not close it.
The retired umbrella retains the original family discussions verbatim; current
rules, rationale, definitions and open decisions have live homes above.

## Follow-up chat, Oct 25, 2026, 12:33 -05:00 (verbatim)

Coverage: E13 owns automatic protection and calibration; N2-N6/N9-N10 own
family naming, provenance, migration and display; actions owns override/undo;
cast C2 preserves the decisions across rebase. No live batch is authorized here.

<!-- markdownlint-disable MD013 -->
```text
I would like to auto-protect photos in a protected person that reach a high enough likeness score so that I don't have to manually do that.  For an unprotected identity - if we determine that we have enough photos to establish an itentity, we should also auto-protect that person and the photos.  It'll be easier for me to unprotect and move images out and rebase if that's required in order to keep things clean - but I feel like that's a solid enough plan - and that would go along with the family relationships we establish for high likeness to another person, but not enough to merge them but establish the family name.  When we do that - I think we need to keep the original name of the person that was either provided and/or randomly assigned as well as the new person with their family name.  We display character name (with family) along with a note on the original name.  Sort of like we do with the sisters, but if we also have the person join a family we'd have the character name, person name (now) and original person name.  We'll need to update plans and get this work going as I think all this is critical in order to complete the intake and likeness process as a whole and retain the proper identities along the way and show them in the gallery views where it makes the most sesnse.  Think deeply and let's get this going.
```
<!-- markdownlint-enable MD013 -->
