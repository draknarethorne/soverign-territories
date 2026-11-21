---
name: decision-guidance
description: "Use when making autonomous architecture, coding, documentation, data, or operational decisions while executing Sovereign Territories plans; classify risk, choose conservative or assertive action, and know when to ask."
---

# Project decision guidance

Use this workflow for implementation choices and uncertainty during an
authorized project task. It helps choose an approach; it does not grant
permission, replace the active plan, or override domain-specific rules.

## Procedure

1. Establish current authority using the
   [decision policy](../../../docs/guidelines/ASSISTANT-DECISION-POLICY.md), its
   [structured matrix](../../../docs/guidelines/config/assistant-decision-policy.yaml), the active
   [planning agreement](../../../docs/plans/README.md), project instructions
   and affected canonical contract.
2. Inspect the current worktree, relevant prior art, evidence, and any live
   process or receipt before proposing a change.
3. Define the objective, accepted scope, options, constraints, risks,
   reversibility and exact user-only decisions.
4. Apply the matrix's highest-risk tier. Proceed on bounded, reversible work
   with clear acceptance evidence; record only minor assumptions that preserve
   scope and behavior. Ask before material policy, architecture, product or
   priority choices. Never infer permission for destructive, Production,
   shared-workspace, publication, commit/push or external actions.
5. Prefer a small complete solution that follows existing patterns. Preserve
   behavior outside the request, use supported tools, surface failures, and
   verify the requested result with the smallest applicable quality gates.
6. Record the outcome and evidence in the existing owning plan/status/handoff.
   Separate implementation, tests, installation, human acceptance and
   publication; retain unresolved decisions with an owner.

When blocked, preserve state, explain the evidence and stop only the affected
action. Continue independent authorized work without widening scope. Do not
duplicate a fact already owned by a canonical domain document.
