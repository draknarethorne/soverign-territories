---
name: milestone-handoff
description: "Use when preparing or resuming an agent, session, machine or milestone handoff; choosing next work; reconciling task ownership; or advancing Queue focus. Preserve required artifacts, run evidence and human gates without activating holding backlog."
---

# Milestone handoff

## Establish current authority

1. Read the current sections of the [planning agreement](../../../docs/plans/README.md)
   and [pinned recap index](../../../docs/recap/README.md). Follow their linked
   execution spine, not a hardcoded run/date or the newest recap filename.
2. Read the spine's current milestone, Queue focus and latest closeout, then
   the focused task's domain contract. Use bounded ranges; do not read every
   holding plan, archive, raw session log or dated narrative.
3. Check actual worktree/process/receipt state before acting. Record any
   conflict with the handoff; do not infer completion from an applied receipt,
   a progress counter or a previous summary. Missing authorization/evidence
   blocks that action, not unrelated safe work.

## Execute or transfer one bounded slice

- Keep one executable owner. Transfer stable task IDs and complete contract/
  dependency/evidence links into the spine before activating domain work.
  Replace source checkboxes with destination records; transfer is not delivery.
- Respect current scope, roots, live-process freeze and publication permission.
  Read-only analysis does not authorize intake, runtime edits or Production.
- Reuse existing verified results across acceptance owners. Consult the
  [quality contract](../../../docs/guidelines/QUALITY-GATES.md) and
  [launcher catalogue](../../../bin/help.cmd) before inventing commands.
- Close a task only when its exact output/threshold/shape is verified.
  Distinguish implemented, fixture-tested, installed-verified and human-accepted.
  Put residuals under explicit owners; holding is not completion.

## Package an agent handoff

Follow the [handoff guide](../../../docs/handoffs/README.md) for a unique
topic folder, compact continuation, and any required private payload.
Verify the actual current baseline and all required artifact bytes, not just
historical instructions. Record a recipient, exact hashes, transfer status
and acknowledgments; a Git-ignored payload is neither synchronized nor
delivered by committing its handoff. Preserve source evidence and never
publish private data or invent a transfer channel.

Use [AI collaboration](../ai-collaboration/SKILL.md) for questions and
responses with another agent; keep answers in their existing discussion.
A communication-only handoff does not itself transfer plan ownership,
advance Queue focus, authorize a run or require a new milestone closeout.

## Leave one concise continuation

For a milestone transfer or closeout, update the spine's closeout and Queue
focus together, then regenerate with `cmd /c bin\todo.cmd`; never edit
generated tasks. Update the existing pinned recap and its index if needed,
not another competing dashboard. Preserve historical/raw words; follow the
[archive guide](../../../docs/guidelines/ARCHIVE-GUIDE.md) for any authorized
move.

The handoff must state:

| Field | Required content |
| --- | --- |
| Work | Current milestone/task, verified result and exact next entry gate |
| Authority | Allowed roots/actions, user-only decisions and publication limits |
| Evidence | Run/profile/config/code IDs; tests/exit codes/browser checks actually observed |
| Processes | Existing PID/run/receipt/log/waiter, or confirmed no remaining job |
| Exceptions | Unresolved failures/ambiguity, preserved sources and owning task IDs |
| Resume | Supported command if needed; explicitly say when no reset/intake is needed |

Use completion notifications for existing jobs; do not launch another writer
or completion waiter. Do not copy whole logs or claim token/cost savings from
shorter prose. A fresh-session discovery/behavior test is separate from file
format/link validation.
