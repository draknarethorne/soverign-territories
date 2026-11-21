---
name: diagnostics-tuning
description: "Use when investigating Sovereign Territories failures, unexpected behavior or performance bottlenecks, or planning a bounded comparable tuning experiment. Preserve live-run evidence and distinguish measurements from hypotheses."
---

# Diagnostics and measured tuning

## Reproduce and trace

Read [status](../../../docs/STATUS.md), the active task and stop conditions
through the [planning agreement](../../../docs/plans/README.md), the affected
runbook, [quality gates](../../../docs/guidelines/QUALITY-GATES.md) and
[launcher help](../../../bin/help.cmd). Establish the actual root, input,
revision/config, error or observable mismatch, process state and authorized
scope. A report, peer question or isolated test does not authorize a live
write, new library run, dependency install or changed policy.

Use the lightest available evidence: existing receipts and bounded log tails,
symbol references and diagnostics, then a focused fixture/runtime check or
debugger when necessary. Use available language intelligence for type,
caller and execution facts; treat guesses as hypotheses. Trace the actual
producer, reproduce the failing boundary, and distinguish a test fixture
from real installed behavior. Preserve exact errors and failure receipts;
never rewrite an old binding or hide a missing/ambiguous result.
For a quiet process, inspect the identified PID's CPU/I/O progress and
suspension state before calling it stuck; never stop processes by name.

For an authorized fix, follow the existing implementation workflow and add a
focused regression that would fail without the change. Verify the supported
launcher and affected consumers; do not bypass guards or relax thresholds to
make a test pass. Use [long-run acceptance](../long-run-acceptance/SKILL.md)
for live Sandbox process monitoring, recovery and browser acceptance.

## Measure before tuning

- Identify one bottleneck and a safe bounded workload; record source hashes,
  code, configuration, model/recipe, cache state, worker/thread settings,
  machine, storage, concurrent load and the exact operation timed. Verify
  existing writers and avoid competing heavy I/O.
- Obtain authority for sidecar writes, benchmarking or production effects.
  Use the supported preview/fixture and isolated output locations; a
  read-only analysis is not permission to start a new library or render job.
- Change one variable at a time, repeat and vary order when practical, and
  separate startup, preparation, matching, publication and verification.
  Record elapsed time, sample size, failures, parent-plus-child memory and
  I/O when actually measured. A sampled peak may miss a true peak.
- Verify output/decision parity against the same source and required
  tolerance; identical placement is not automatically pixel equality.
  Describe cache warmth and failed/reused stages. Different code, inputs or
  runtimes prevent a clean hardware speedup claim.
- Report the observations, uncertainty, reversible recommendation and
  remaining acceptance gate. Do not change defaults or claim whole-run gains
  from a small sample without the required broader proof and approval.
