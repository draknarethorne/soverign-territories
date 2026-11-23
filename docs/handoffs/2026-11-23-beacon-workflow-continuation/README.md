# Beacon-to-Beacon: art and ComfyUI continuation

- **From:** Beacon (`agent-69b7d56fd547`), old-machine session.
- **To:** the next Beacon session on the same machine and repository.
- **Created:** 2026-11-23 19:56 UTC.
- **Baseline:** branch `work/sandbox-rebase-acceptance`, revision
  `5814fb1921d88816124af31a6d00ff05728ef6b5`.
- **Delivery at creation:** local handoff; the next session had not yet acknowledged it.
  It does not change task ownership or grant new execution authority.

## Recipient continuation - Nov 23

The successor Beacon (`agent-c67234b7d95a`) read this handoff. The user
prioritized the revised source-first `0_Edit`/`1_Alpha` plan and will prepare
the current curated workflows on this machine. The existing
[workflow plan](../../plans/2026-10-22-manual-prompts-to-art-library.md#source-first-reset-and-priorities)
records the agreed phase direction, raw feedback, remaining source/approval
gates and the intended first Drakness static pilot for user verification.
No new workflow, workspace deployment or render has been performed.

The successor fetched and fast-forwarded to `12a28095e`; Harbor acknowledged
the earlier library handoff and reported matching verification of two backup
copies, without a restore test. The shared-selection writer remains open in
the [same discussion](../../collab/2026-11-21-new-pc-rehearsal/messages/20261123T194548Z-agent-69b7d56fd547-02.md).
These are collaboration reports, not permission to retire backups or mutate
Production. No process-state claim is made for this later checkpoint.

## Identity and working split

The user named this workflow/art assistant **Beacon**. A new chat can adopt
that name by reading this handoff; it is a continuation of the work, not
automatic access to the prior chat or the same session identity. If the new
session contacts Harbor, create its own participant ID under the
[collaboration protocol](../../collab/README.md#session-identities) and
identify this session as its predecessor.

Harbor leads likeness, Gallery, studios, named intake and image processing.
Beacon helps with those only when Harbor directly requests a bounded task.
The [Harbor handoff](../2026-11-23-library-studio-planning/README.md) is
published, but acknowledgment and its backup-verification question remain
open as of this checkpoint. Check the actual collaboration state before
relying on that observation. Shared source selection, workflow bindings and
generated-image lineage need coordination, not duplicate implementations.

## Resume here

1. Read the current checkpoint in [status](../../STATUS.md), the current
   Queue focus and WF1 in the [execution spine](../../plans/2026-11-05-priority-reset.md#execution-spine),
   and the [Nov 23 workflow direction](../../plans/2026-10-22-manual-prompts-to-art-library.md#nov-23-beacon-workflow-planning-companion).
   Read the [workflow runbook](../../../workflows/README.md) and
   [art-data reference](../../../data/art/README.md) as needed. Use bounded
   sections rather than loading the full likeness history.
2. WF1 is a **read-only planning** companion: map existing static stage
   templates and supported source-bound on-demand jobs against the user's
   desired static category workflows, dynamic person/image jobs, custom
   prompts, and eventual `zz_shots` replacement. Separate implemented
   capabilities from proposed decisions and map the Harbor interface.
   Record its outcome in the existing workflow plan, not a competing queue.
3. The user is still sorting newer refined edit prompts. Preserve the
   existing `0_Edit` sources, curated workflows and hand-tuned shots; wait
   for identified, reviewed source bytes and the relevant gates before
   editing `1_Prime`/`2_Bare` templates or implementing migration. Do not
   assume the proposed Apex/Forge/Lab workflow arrangement is final.
4. No workflow generation, workspace deployment, rendering, library
   mutation, reset or Production work follows from this handoff. In
   particular, composite refresh/animation launchers can regenerate
   prompts even with `--dry-run`; consult the runbook before any launcher.
   Generated images must not vote in likeness cores; Harbor owns the
   Gallery side and Beacon owns workflow/ComfyUI integration.

The user's goal is efficient context use: load relevant sections and
evidence on demand, use focused checks, and batch plan updates and todo
regeneration after decisions rather than after every question. This does
not waive repository quality gates or user approvals.

## State and verification

At 19:56 UTC, no local Python/ComfyUI process was observed after a transient
Python process had exited. Other writer types and new-machine processes
were not independently checked. Recheck actual state before any write or
run; do not interrupt a process or assume the old state still holds.
The baseline commit was pushed and its remote revision verified. Its
routine checks, generated todo, handoff links and tracked-contract hashes
passed; no new render or library run was performed. No separate private
payload is required or transferred for this planning continuation.

For baseline verification, the following sizes and SHA-256 values describe
the tracked Git blob bytes at the revision above, not checkout-dependent
line endings. The recipient should use the current authorized revision and
reconcile any later changes rather than overwrite them with this snapshot.

| Required starting document | Bytes | Git blob SHA-256 |
| --- | ---: | --- |
| [Status](../../STATUS.md) | 344724 | `29060a19a054c567c2d54b26325bcb4fcc31bf89598ff49928e6dc4c50bd6e16` |
| [Execution spine](../../plans/2026-11-05-priority-reset.md) | 235110 | `7cd4eb6ac69919d0be9edd65b25226ec197999d98ab19e0ed26d3d52ebf09a43` |
| [Workflow plan](../../plans/2026-10-22-manual-prompts-to-art-library.md) | 58279 | `64afaa60567908655c66ba5a643daf97ff8c466f34084ea88d4f66d04f9b5a3c` |
| [Workflow runbook](../../../workflows/README.md) | 68848 | `826ac55f80a2f183f1fadce4eafec949d6caa12df89a061c72fb96a05feb3999` |
