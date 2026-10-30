# 2026-10-19: library management rebaseline

**Status:** dropped (superseded; not completed)

## Supersession record

**Superseded:** 2026-10-22T16:34:08-05:00 (local offset recorded).

**Reason:** the Oct 22 full-plan reconciliation separates enduring rules,
dated evidence and focused execution owners. Later approved direction
supersedes conflicting older sequencing/limits; remaining work is not done.

**Context:** [live reference](../../../art/library-reconciliation-context.md), [full reconciliation audit](../../../audits/2026-10-22-plan-feedback-audit.md).
Original user wording and historical evidence are retained below.
The source checklist is historical; formerly open items are explicitly
marked transferred, not checked off as implemented.

## Unfinished work and successors

| Source item | Live owner | Destination / disposition |
| --- | --- | --- |
| L1 | [2026-10-22-likeness-engine-acceptance.md](../../2026-10-22-likeness-engine-acceptance.md) | E6 |
| L5 | [2026-10-22-review-actions.md](../../2026-10-22-review-actions.md) | A2/A4 |
| L8 | [2026-10-22-likeness-engine-acceptance.md](../../2026-10-22-likeness-engine-acceptance.md) | E8; upkeep U5 owns future Demon pairing design |

## Result of reconciliation

Retired as an execution owner after task and context transfer. Archival
does not assert implementation, render approval, convergence or production
acceptance. Live owners above retain the remaining gates and questions.

## Original source record

**Original status:** active

This plan defines a sustainable routine for re-evaluating the whole active
photo library, keeping low-count people available for future matches, and
reviewing Angel replacements as the cast expands. The current ingest and
likeness rules are documented in [likeness.md](../../../art/likeness.md) and
[original-photos.md](../../../art/original-photos.md).

## Vocabulary and agreed rules

| Place or group | Meaning |
| --- | --- |
| Sisters | User-selected identities; the system never changes them automatically. |
| Angels | Current card identities. Qualified alternatives are report-only in the current phase; automated pairing/swapping is deferred to the future Demon phase. |
| Prospects | Current active rule: unassigned people with at least five usable photos. The Oct 21 rebaseline plan is evaluating a new Model destination for sufficiently large cast-lookalike identities; until that classifier is validated and applied, this current rule remains in force. |
| Potentials | Current active root alongside Prospects; holds unassigned people with one to four usable photos. Keep matching them against new photos; under the current rule promote them to Prospects at five. The Oct 21 rebaseline plan will test whether five-photo groups should instead become Models when they meet the calibrated cast-lookalike rule. |
| Models | The Oct 21 rebaseline plan proposes restoring an active category for distinct people with at least five usable photos and calibrated Angel/Sister resemblance. This is not yet a production category rule; distinguish it from legacy Model folders and paths. |
| Junk | Photos needing cleanup, such as icons, text, or crop fixes. Keep them available to clean and send through classification again. |
| Retired | Photos judged unusable for future matching or card art. Do not retire a good photo merely because its identity is uncertain. Empty person folders may still be archived here after regrouping. |

Usable-photo counts determine the Potential/Prospect boundary and the minimum
Angel replacement eligibility. They do not establish identity or guarantee
visual variety. Ambiguous identity matches remain active for later comparison.

## Pairing score

Candidate selection is two-stage and shared by the global pairing command,
People Gallery, candidate report, and rebaseline preview:

1. **Eligibility:** at least five usable photos and 0.45 cohesion.
2. **Ranking:** likeness-fit cost against the configured counterpart, adjusted
   by a small variety proxy: subtract 0.02 at 10 usable photos, 0.04 at 15,
   and 0.06 at 20 or more. The target is 0.28 within the preferred 0.15–0.40
   band; a photo bonus cannot qualify an out-of-band replacement. Global
   pairing additionally avoids assigning one person twice and penalizes
   likeness clashes between selected candidates.

This gives larger photo groups an edge when likeness fits are reasonably
close without treating photo count as identity evidence. It does not measure
distinct poses or outfits. The score is faction-neutral: future Demon-to-
counterpart pairings can reuse it once their counterpart mapping and any
direction-specific likeness band are decided.

## Decisions

| ID | Question | Answer |
| --- | --- | --- |
| L1 | What separates Prospects from Potentials under the current applied policy? | Five usable photos: Prospects have 5+; Potentials have 1–4 and can grow into Prospects. The proposed Model tier and revised boundary are transferred to the Oct 21 rebaseline plan and do not change the live library until validated and applied. |
| L2 | What should happen to repairable or uncertain photos? | Repairable icons, text, and crop issues stay in Junk for cleanup and reprocessing; uncertain good photos stay active. |
| L3 | What belongs in Retired? | Photos judged never useful, not promising photos awaiting a match. Preserve the existing use for empty folders after regrouping. |
| L4 | Should low-photo Angels be reconsidered automatically? | For the current Angel roster, show qualified alternatives as report-only recommendations; the user's choices are manual, and Angel slot names stay fixed. Defer automatic pairing/swapping to the future Demon phase, after counterpart mapping and any direction-specific likeness band are agreed. Reuse the shared fit-plus-variety score only after that review. |
| L5 | Can automatic matching change Sisters? | No. Sisters remain fixed unless the user chooses to change them. |
| L6 | What should happen as the library and cast expand? | Re-evaluate the active library, pair eligible candidates automatically, and provide results for the user to review. |
| L7 | How should the first migration and later runs differ? | The initial migration was previewed and backed up; only the agreed category moves were applied. Identity, Junk, and replacement suggestions stayed report-only. Future automatic classification or swaps require a separate review, especially for the later Demon phase. |

## Steps

- [x] **P1 ai** L0 Inventory the current scan, sort, rematch, pairing, gallery, junk, and archive paths; identify how current folder names and chosen-photo references are migrated safely.
- **Transferred, not completed:** **P1 either** L1 Define measurable usable-photo and auto-retirement criteria. Distinguish objectively unusable files from repairable or uncertain photos; leave subjective eye-closure and angle judgments for review unless a detector is validated.
- [x] **P1 ai** L2 Design a read-only full-library re-evaluation report with proposed photo/group destinations, best matches, score margins, current/projected counts, and explicit uncertain/review outcomes.
- [x] **P1 ai** L3 Design the migration from current low-count Prospects into Potentials and the rule that promotes a Potential at five usable photos, preserving identity, history, images, and workflow references.
- [x] **P1 ai** L4 Define the current report-only Angel recommendation policy and defer automatic pairing/swapping to the later Demon phase. The shared eligibility and fit-plus-variety score are documented; no current Angel identity is changed automatically.
- **Transferred, not completed:** **P2 ai** L5 Specify how confidently unusable photos are retired while Junk remains a repair-and-resubmit path; preserve source files and provide a recovery trail.
- [x] **P2 ai** L6 Update likeness tooling, gallery, candidate reports, runbook, and tests consistently after the rules and preview are approved.
- [x] **P1 either** L7 Back up and review the initial migration preview, then apply only the agreed category moves. The verified backup preceded 135 Prospects-to-Potentials moves; checks and regenerated reports confirmed the resulting library. Identity/Junk suggestions stayed review-only, and all four Angel choices were explicit user selections.
- **Transferred, not completed:** **P2 either** L8 Validate the routine on future additions, including a later Demon set; review automatic pair/swap results and refine only from measured outcomes.

## Progress (Oct 19–20)

The category migration path now moves whole Prospects/Potentials folders only
after full-batch collision checks. A fresh verified backup was made before the
current migration. The reviewed report proposed 135 Prospects-to-Potentials
moves and no reverse moves; only those category moves were applied. Identity
reassignments and Junk candidates remain review-only. The explicit Angel
choices are Aria Muse → Gavrielle, Ruby Eden → Camaris, Amethyst Montgomery →
Ravaelle, and Sabine Vale → Nyxene. Angel slot names remain fixed; outgoing
identities returned to the appropriate active category. The generated reports,
gallery, and Angel Prime workflows were refreshed and verified.

## Preserved original discussions (verbatim)

<!-- markdownlint-disable MD013 -->
````text
## Raw request

> I like that plans it'll serve as a re-baseline I can use over time to help clean-up manage the library - for
> instancing moving Prospects into Potential with low numbers of photos just to keep things cleaner in
> Prospects and also auto-retire photos that are just not every usable. Junk is still my mechanism to clean-up
> photos with icons, text or things that I can crop or clean-up and re-send back through.
> I'd also like an auto-swap on Angels with low number of photos - at least in current state, which may be less
> useful later on - but if I add in a new set of Demons later on, then the auto-pairing and auto-swapping would
> be more useful then. That way I can build this to expand the library in the future and not have to manually
> pair and can just review and judge things as the library expands.
>
> I would only want retired to be for bad photos - not ones that may eventually find a decent match as I
> download more - so that's where Orphans came to mind as they are still "active" until I do retire them. But
> if it's a face with eyes closed, or a really bad angle then retire it. So Orphans would be for less than 5
> that are good photos but aren't ready for prime time yet. Retired is for bad photos that won't ever make a
> good match and ideally there's not anything in Retired that is a good potential photo. Junk is for me to
> clean-up and send back through to see where it lands. Maybe Potential is a better name than Orphans. So we
> have Sisters, Angels, Prospects (5+ photos) and Potentials 1-4 photos and Retired for bad photos. I'm just
> trying to keep Prospects to the 5+ rule and Potentials as the lower number that could grow and move them
> into a Prospect if I find more photos of them.
````
<!-- markdownlint-enable MD013 -->
