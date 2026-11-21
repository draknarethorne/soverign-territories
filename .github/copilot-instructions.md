# Sovereign Territories - Copilot Instructions

Local-first PvE card strategy game; the first release is Sovereign Dawn.
Unity, PvP, alliances, territory maps, AFK systems and Nakama are future scope.

## Project authority

- Start with [current status](../docs/STATUS.md), the
  [documentation map](../docs/README.md), the
  [planning agreement](../docs/plans/README.md) and its linked execution
  spine. Check [the generated queue](../docs/todo.md) before proposing next
  work; never edit it directly.
- Read only the active plan, canonical contract and evidence needed for the
  task. MVP/design rules and runtime schemas outrank the game bible's vision.
- Keep each fact in its canonical home. Plans select work; they do not replace
  design/data contracts. Follow [guidelines](../docs/guidelines/README.md)
  for cross-cutting policy and quality gates.

## Working boundaries

- Use the matching on-demand procedure; load no unrelated skills. If a
  needed skill was not discovered, read its entry file and linked reference.
  Skills guide execution but do not grant authority.
- Preserve unrelated dirty work and existing evidence. Do not mutate
  Production, prune source images, start blanket intake, install dependencies,
  publish externally, or commit/push without explicit authorization.
- Analysis is not permission for runtime or policy changes, new intake or
  competing heavy I/O. Follow the active execution lane and reuse verified
  evidence. Agent roles do not widen authority; follow the
  [shared agent contract](agents/AGENT-SELECTION-GUIDE.md#shared-working-contract).
- Ignore `_archive` for ordinary work. Never create art assets; describe
  needs or use the approved prompt pipeline.
- Ask before material design/policy changes. Follow the repository's
  [decision policy](../docs/guidelines/ASSISTANT-DECISION-POLICY.md).
- Use absolute paths with file tools; read before editing. Put scratch under
  verified ignored `tmp\`; use another explicitly designated, verified-ignored
  path only. `reports\` is for generated review output, not scratch. New
  scripts/tests must follow the same scratch rule. Preserve legacy feedback
  there and durable receipts in their documented locations. Do not create
  root `files\` or `session files\`.

## Execution and quality

- Use supported `bin\*.cmd` launchers; inspect [bin help](../bin/help.cmd)
  before inventing commands or routines. Repeated workflows need a tested,
  repeat-safe, documented launcher listed in help/menu with a preview and
  read-only check. For photo-library work, follow the
  [original photos runbook](../docs/art/original-photos.md).
  Follow [quality gates](../docs/guidelines/QUALITY-GATES.md) and run
  targeted tests; do not commit failing changes.
- For game data, follow the order: approved rule, schema, validator/tooling,
  implementation, tests. Data/art changes require `cmd /c bin\check.cmd`;
  schema/validator changes also require isolated validation.
- Before end-of-day commit/push, use the checklist in
  [the planning agreement](../docs/plans/README.md). A passing check alone
  does not authorize publication.

## On-demand procedures

- [AI collaboration](skills/ai-collaboration/SKILL.md) — cross-session and
  cross-machine questions, answers and artifact handoffs.
- [Decision guidance](skills/decision-guidance/SKILL.md) — risk and escalation.
- [Milestone handoff](skills/milestone-handoff/SKILL.md) — plans and closeout.
- [Feedback filing](skills/feedback-filing/SKILL.md) — coverage and safe filing.
- [Long-run acceptance](skills/long-run-acceptance/SKILL.md) — monitoring and recovery.
- [Domain analysis](skills/domain-analysis/SKILL.md) — design and balance.
- [Implementation workflows](skills/implementation-workflows/SKILL.md) — code,
  Unity and explicitly authorized backend tasks.
- [Data batch](skills/data-batch/SKILL.md) — approved structured data changes.
- [Visual review](skills/visual-review/SKILL.md) — supplied visual evidence.

For long jobs, use the matching workflow, verify checkpoints and check
suspension before calling a process stuck. For large changes, batch work,
verify each phase and preserve originals; use bounded read-only helpers only
when useful. Use tables/bullets when useful; keep answers concise and use no
emojis unless the user does. Do not claim unexecuted tests, editor checks,
measured performance, skill behavior or cost/token savings.
