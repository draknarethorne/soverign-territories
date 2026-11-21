---
name: comfyui-rendering
description: "Use when preparing, inspecting or troubleshooting source-bound ComfyUI reference batches, server compatibility, queue receipts and operator-led rendering. Keep rendering, workspace publication and output acceptance separately gated."
---

# ComfyUI reference rendering

Read the current Queue focus through the
[planning agreement](../../../docs/plans/README.md), the
[reference-rendering contract](../../../docs/plans/2026-10-25-reference-rendering.md),
the [workflow runbook](../../../workflows/README.md) and
[launcher help](../../../bin/help.cmd). The rendering backlog is not
activated just because a batch can be prepared. Identify the authorized
source/root, workspace/server, recipe, bounded batch, outputs, recipients
and active writers; keep source images and prior receipts intact.

## Prepare and inspect

- Use the supported `bin\render-reference.cmd` lifecycle. Validate exact
  source paths/hashes, domains, supported catalog recipes, seeds and batch
  bounds. Offline preview does not freeze inputs; preparation writes
  immutable batch evidence only when explicitly authorized.
- Compile has separate workspace/input writes and server checks; its
  `--dry-run` still contacts the selected local server. Confirm endpoint,
  node/model compatibility, input/output roots, collisions and current
  workspace ownership before applying anything. Frozen inputs-only evidence
  is not an executable API graph.
- Inspect local status and, when authorized, refresh read-only server
  history. A compiled graph or queued request is not a finished image, a
  quality decision or a real-world identity claim.

## Guide the operator and preserve queue evidence

Do not create art assets or submit rendering requests yourself. For an
authorized artist/operator, explain the supported bounded submit/run steps
and exact receipt/status checks from the runbook; preserve their control
over queueing and acceptance.

Never clear, reprioritize or interrupt another caller's queue. If submission
is uncertain or an accepted job is still pending, inspect its existing
receipt and use the supported reconciliation guidance; do not retry a POST,
guess an output filename or remove a lock. A lost history or ambiguous match
stays a hold, not a rejection or permission to resubmit.

Describe selected output review, retention and pullback as separate,
explicitly authorized stages. Verify receipt-bound source and output hashes,
and keep human likeness/visual approval separate from transport success.
Use [visual review](../visual-review/SKILL.md) for supplied results, not
automatic identity decisions or unwarranted quality claims.
