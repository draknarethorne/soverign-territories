---
name: feedback-filing
description: "Incorporate chat or raw feedback into Sovereign Territories plans and safely file covered notes. Use for feedback triage, exact source preservation, request coverage, task transfers or feedback archival. Never bulk-clear feedback or legacy tmp notes."
---

# Feedback incorporation and filing

## Decide ownership before filing

1. Read the current [planning agreement](../../../docs/plans/README.md) and
   affected domain contract. Use the existing owning plan; the execution spine
   selects executable work. Do not create a new active plan for every note.
2. Read the exact supplied source. Ordinary work excludes `_archive`; only
   inspect history for an explicitly scoped filing/collision/link check.
   Treat legacy raw notes in repository `tmp` as protected feedback.
3. Split requests into decisions, implementation, acceptance and deferred work.
   Reuse existing task IDs/contracts where equivalent. Do not mark code done
   because the note has been captured. Identify uncovered requests explicitly.
4. If a necessary major/behavioral decision exceeds delegated authority, stop
   that slice and use the question tool, one decision at a time. While the
   user is away, proceed with reversible authorized choices; record assumptions
   and defer unsafe/human-only decisions instead of inventing consent.

## Preserve and verify

- Keep the user's words verbatim at the end of one primary owning plan,
  including relevant chat. Choose a fence longer than fences in the source;
  do not rewrite spelling, punctuation or historical claims.
- Map every request to its task/decision/explicit deferred owner. Use tagged
  checkboxes for open work and explicit transfer records for other homes.
- Re-read the plan's saved source and compare it with the original, then
  verify coverage. A matching filename or a summary is insufficient.
- Sensitive material must not be copied into tracked documentation; leave
  the original protected and report that preservation needs a safe disposition.
  Never export private content to an external service for review.

## File individually only when ready

Follow the [physical filing rules](../../../docs/archive-guide.md).
Unresolved, uncovered or explicitly review-pending notes stay in place.
Neither feedback nor tmp must be empty.

For each covered ignored source: re-read it **immediately before** filing;
resolve the exact source/destination paths and proper topic group; refuse
an existing destination rather than overwrite it. Capture original bytes
and SHA-256, perform a non-overwriting move, then verify destination bytes/
hash and source absence. On any failure, preserve both available copies and
report the actual state; never delete a competing copy to force success.

Tracked historical moves use `git mv` and preserve prose/raw blocks. Update
physical folders, archive/index/source ledger, incoming links and affected
generated readers together. Regenerate `cmd /c bin\todo.cmd` after plan
changes; follow the [quality contract](../../../docs/QUALITY-GATES.md).

Report incorporated/filed/retained separately, exact task owners, checks
performed and remaining questions. Filing closes source intake only, not
implementation, human acceptance or permission to prune source galleries.
