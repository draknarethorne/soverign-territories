# 2026-10-22: identity families and safe naming

**Status:** active (family metadata/naming not delivered or accepted)

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
