---
name: long-run-acceptance
description: "Monitor, resume and verify authorized long-running Sovereign Territories sandbox jobs. Use for rebase-flow, LEAN continuation, per-image recovery, process liveness, final checks or Gallery/Overview/Review acceptance. Preserve receipts and distinguish disposable from FULL recovery."
---

# Long-run acceptance and recovery

## Establish the job contract

Read the current spine/closeout through the [planning agreement](../../../docs/plans/README.md),
then the affected [likeness runbook](../../../docs/art/likeness.md) and
[quality gates](../../../docs/QUALITY-GATES.md).

Record one objective/task, explicit roots/run/profile, implementation/config/
input IDs, allowed fixes/restarts and commit/push authority. Keep human
identity/quality approval and Production/shared-workspace publication separate.
Read [launcher help](../../../bin/help.cmd); reuse supported commands.

Before launching anything, identify the existing process tree, flow receipt,
step log and completion waiter from current evidence. Reuse an existing job;
do not start duplicate writers or waiters. Inspect small receipts/log tails
at phase transitions and wait for completion notifications, not a tight
model polling loop. A long-lived service needs readiness proof, not an exit.

## Diagnose without destroying evidence

- Silence is not a hang. Check the exact PID's CPU/I/O progress and thread/
  suspension state before stopping anything. Kill only a known PID/process
  tree if justified and authorized, never by executable name.
- Keep hash-bound runtime modules and library inputs frozen while their job
  runs. Lightweight planning is not permission for competing heavy I/O.
- On failure, capture exact step/exit/error plus code/input IDs. Preserve
  failure receipts/logs with non-overwriting, hash-verified copies **before**
  a supported resume overwrites them. Do not edit receipts to bless changes.
- Trace the demonstrated failing producer; reproduce it with a focused test
  or read-only sample, fix narrowly after the writer exits, then test affected
  consumers. Do not relax crop/quality guards or suppress diagnostics.
- Retry only with new evidence and the supported recovery path. After a
  repeated identical failure without progress, stop that slice and report.

## Resume the right scope

Disposable LEAN has no rollback promise; a partial-publication/reset-required
state needs its documented reset procedure and authorization, not fake undo.
FULL retains its backup/rollback/content-seal requirements. Do not substitute
one profile's guarantees for the other.

For a completed install with only a failed check, preserve the failure and
preview supported check-only flow resume. Verify that completed install/
intake steps stay skipped. Do not reinstall, reset or rerun detectors just
to satisfy another acceptance owner. A changed unpublished engine may require
a new preview/run; never bypass implementation-hash bindings.

## Prove completion

Record exact install/installed-check/gallery-check exit codes, run/profile/
code IDs, phase/wall/read/byte/space counts and retry attribution. A successful
seal alone does not mean zero actionable diagnostics. Classify intentional
unavailable framings separately from missing/stale/corrupt expected outputs.

Open the actual Gallery/Overview/Review and recap in a browser: verify count
conservation, representative loaded thumbnails, current-native/detail/history
links, required named cases and honest missing/unavailable states. Do not
stage UI actions or infer real identity from scores. Static file existence
and fixture tests alone do not prove browser acceptance.

Update one spine closeout, share its evidence across tasks, regenerate
`cmd /c bin\todo.cmd` and leave remaining human/performance gates explicit.
Stop self-contained helper processes when done; preserve recovery receipts
in their documented library locations, not disposable scratch.
