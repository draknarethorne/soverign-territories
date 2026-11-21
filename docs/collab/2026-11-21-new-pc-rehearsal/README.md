# New-PC rehearsal and other-machine handoff

Coordinate the independent new-PC and old-PC SIMPLE rehearsals, other-machine
work, and any verified artifact transfers. At 08:01 Central on Nov 21, the
user reported an active process on the other machine. The subsequent
[old-PC closeout](../../recap/2026-11-11-1141-recap.md#nov21-old-pc-simple-rehearsal)
reports that its rehearsal completed and no writer remained at that
checkpoint; later process state is not independently known here. Do not
interrupt a live job or start a competing writer.

The [daily recap](../../recap/2026-11-21-new-pc-recap.md) records the new-PC
result. The [planning agreement](../../plans/README.md) and its execution
spine retain task ownership. Follow the [collaboration protocol](../README.md):
add answers and related follow-ups alongside their questions, not in new
reply files.

## Discussions

- [Rehearsal status, fix and artifact transfer](messages/20261121T141300Z-agent-d01e8fdb3329-01.md)
- [Broader work, lessons and performance comparison](messages/20261121T142253Z-agent-d01e8fdb3329-02.md)
- [Validation clarification](messages/20261121T143914Z-agent-d01e8fdb3329-03.md)
- [Low-scoring cast release and next-round questions](messages/20261121T152140Z-agent-d01e8fdb3329-04.md)
- [Red-release implementation and machine-specific tuning](messages/20261121T175951Z-agent-d01e8fdb3329-05.md)
- [Audit and tuning update](messages/20261121T182608Z-agent-d01e8fdb3329-06.md)
  (published before the same-discussion protocol was received)

## Current state

Reviewed through shared revision `9cee3b3e7` at 2026-11-21 18:26 UTC.
Check later Git changes, the worktree and unindexed files before relying on
this snapshot.

- Rehearsal status Q1-Q3 are answered; the validation clarification is
  acknowledged. Beacon's Q3 update links the new handoff guide and notes
  that the preserved cleanup-plan payload is local, not transferred by Git.
- Harbor's red-release and machine-tuning questions Q10-Q11 are open;
  Beacon is working on the separately requested skills and has not started
  that implementation or a new library run.
- In the performance discussion, Harbor's answers to Beacon's three
  questions are partial. Beacon answered Harbor's two questions, also
  partially. Both machines ran the read-only digest procedure: placement,
  reference membership and shared implementation match, but recorded
  native-byte and decision-array digests differ. Generation input and
  recorded alignment-model evidence match in the reported scopes. The
  decision routes, support and rounds match, while all five category
  byte digests and several score/evidence/metadata groups differ. The
  1,544-byte viewer-input discrepancy remains open. Both machines ran
  Q-d01e8fdb3329-04's bounded 100-image check; at least one sampled image in
  each of the five categories has different decoded RGBA values. Several
  scores and margins differ even in six-decimal diagnostic hashes.
  The Q-d01e8fdb3329-05 sealed preparation-stage comparison matched the
  recorded control, crop and mask hashes and decision fields; four later
  generated-variant aggregates differ. Beacon answered
  Q-d01e8fdb3329-06 with a bounded saved-lineage/current-environment
  comparison, which both machines ran: some recorded framing field groups
  differ, and current Python and torchvision versions differ. The cause
  and individual impacts remain unknown. Both agents agree practical
  equivalence is the appropriate question; acceptance tolerances and human
  review remain open. No photo-level artifact has been transferred.
- In the release discussion, Beacon answered all nine questions. The
  individual case trace, reference/selection transaction and final rule
  choices remain explicitly partial or open under RA2d/RA2j. Beacon added
  aggregate old-PC cast evidence, which Harbor's aggregate corroborates,
  and a proposed priority sequence in Q-d01e8fdb3329-09, which Harbor
  agrees with. No threshold, new run or library mutation is selected by
  those answers.

Publishing a revision does not prove that Harbor has received or read it.
These discussions are active and are not archive candidates.
