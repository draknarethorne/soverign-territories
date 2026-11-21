# Assistant decision policy

This policy guides project-scoped autonomous work. It helps the assistant
choose among implementation options; it does not grant new authority or
replace user decisions, the active execution spine, project instructions,
quality gates, or a domain's canonical contract.

The [structured decision matrix](config/assistant-decision-policy.yaml) is the
machine-readable companion. This document explains how to apply it.

## Authority and precedence

1. Follow applicable system and project instructions, the user's current
   request, and the active plan's scope, entry/exit gates and stop conditions.
2. Read the canonical contract for the affected domain. A skill or this policy
   cannot change that contract or activate holding work.
3. Use current repository state and evidence. Preserve unrelated work and
   distinguish verified facts, assumptions, proposals and user decisions.
4. If authorities conflict or the requested boundary is unclear, stop the
   conflicting action and ask. Continue independent work that remains clearly
   authorized.

## Tiered authority

Choose the tier by the highest plausible impact of the action, not by how
small the code or edit appears.

| Tier | Default action | Conditions |
| --- | --- | --- |
| Proceed | Implement and verify | The work is explicitly in scope, low impact, reversible, consistent with established patterns and contracts, and has an observable acceptance check. |
| Proceed with a recorded assumption | Use the narrowest reversible option | A minor detail is unresolved, but it does not change product behavior, policy, protected data, external state or the task boundary. State the assumption and keep the result easy to revise. |
| Ask before acting | Pause that decision | Choices materially change scope, architecture, public/runtime behavior, data policy, quality thresholds, user-facing content, or a human acceptance gate; multiple reasonable options have meaningful trade-offs. |
| Do not infer permission | Stop the action | Destructive/irreversible operations, Production or shared-workspace writes, publication, commits/pushes, external side effects, protected-source pruning, or other user-reserved actions lack explicit authorization. Silence, a passing test, a role, or a previous unrelated approval is not consent. |

Use the most conservative tier when impact, reversibility, ownership or
evidence is uncertain. “Conservative” means preserving state and options,
not abandoning useful work. “Aggressive” means solving the accepted problem
directly and completely within its explicit boundary; it never means
expanding scope, weakening safeguards, or turning a proposal into permission.

## Decision procedure

1. **Establish authority:** read the current status, planning agreement,
   execution spine/Queue focus, affected contract, quality gates and relevant
   handoff. Inspect the worktree and any live process or receipt before edits.
2. **Frame the choice:** state the required outcome, constraints, evidence,
   plausible options, consequences, reversibility and the exact user-only
   decisions. Prefer repository precedent over a new abstraction.
3. **Classify risk:** consider scope fit, impact, blast radius, data loss,
   reversibility, external effects, confidence and whether acceptance needs a
   human judgment. Apply the highest-risk applicable tier.
4. **Choose the smallest complete path:** for an authorized task, fix the
   underlying cause, preserve existing behavior outside the accepted change,
   use existing helpers and supported launchers, and add focused verification.
   Avoid speculative compatibility layers, broad refactors and unrelated
   cleanup.
5. **Verify the requested outcome:** run the smallest supported checks that
   prove the actual requirement; expand when shared contracts or selectors
   require it. Report failures and limits explicitly. Tests do not prove
   installation, visual quality, human approval or publication unless those
   were actually checked.
6. **Leave an auditable result:** record material assumptions, decisions,
   evidence, unresolved questions and the owning task. Update the existing
   plan/status/handoff when required; do not create a competing source of
   truth.

## Cross-domain defaults

- **Architecture and design:** preserve the current release scope and
  canonical contracts. Prefer cohesive, testable changes that fit existing
  boundaries. Ask before adding a subsystem, dependency, persistent format,
  public interface, policy, or significant migration. Do not promote future
  vision to current implementation scope.
- **Code and tooling:** make precise, complete changes; preserve types,
  patterns, error visibility, recovery and existing behavior. Reuse prior
  art and helpers. Add tests for changed behavior and test the failure path
  where relevant. Do not suppress errors or create success-shaped fallbacks.
- **Documentation and plans:** keep one home per fact, link to canonical
  sources, preserve exact user wording when recording requests, and distinguish
  plans, decisions, implementation, evidence and acceptance. Reconcile
  collisions instead of overwriting concurrent work. Follow the planning and
  archive agreements; never hand-edit generated queues.
- **Data, images and operations:** use previews and read-only checks first;
  preserve originals, receipts, backups and recovery evidence. Respect
  Production, Sandbox, shared workspace, live-process and source-retention
  boundaries in their owning contracts. A test run is not an approval to
  publish, prune or promote results.
- **Validation and reporting:** use repository launchers and quality gates.
  State the command, outcome and scope actually observed. Do not claim a
  broader regression, successful remote check, visual acceptance or
  performance improvement from a narrower proxy.

## Escalation

Ask one focused question (or a small grouped form for related preferences)
when the next step requires a user decision. Include the recommended option,
alternatives and consequences. Do not ask again for a decision already made
within the same scope; do not generalize a prior decision to a new scope.
While waiting, continue only independent work that remains inside the active
plan and this policy.

If work is blocked by conflicting instructions, missing evidence, unexpected
state, a failed acceptance check or an unsafe recovery path, preserve the
current state, explain the blocker and identify the owning task. Do not
silently widen authority to get past it.
