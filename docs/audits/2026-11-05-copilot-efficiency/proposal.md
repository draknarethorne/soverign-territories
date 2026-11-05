# Prioritized efficiency proposal

[Review index](README.md) | [Evidence](evidence.md) | [Practices](practices.md)

Nothing below is an implemented skill, new command, model change or waived
acceptance gate. Select a bounded item through the execution spine.

## Ranked changes

| Priority | Proposal / existing owner | Expected benefit | Risk and acceptance |
| --- | --- | --- | --- |
| First | Use the new single milestone spine and focused queue | Less priority reconstruction, contradictory checklists and repeated narration | Already adopted; verify one executable owner and preserved residuals, not just fewer visible boxes |
| First | Implement existing tooling D4 day-close/plan-check slice | Replace repeated task/transfer/link/queue shell snippets with one reproducible check | Medium: parse formats carefully, never auto-close/archive or require empty feedback; prove malformed/missing/duplicate-owner cases fail |
| First | On-demand milestone handoff/transfer skill | Consistent gates, concise resume context and existing-check orchestration | Low-medium: missing context must refuse; fresh-session continuation test must not repeat intake or assume human approval |
| First | On-demand feedback incorporation/filing skill | Fewer repeated preservation instructions and improvised file moves | Medium: exact original words/coverage, immediate source re-read, non-overwriting hash-verified individual filing; no bulk clearing |
| First | On-demand long-run acceptance/recovery skill around rebase-flow | Event-driven monitoring, consistent error diagnosis and final viewer proof | Medium: hash-bound implementation, disposable versus FULL distinction, uncertain publication; no blind restart or receipt editing |
| Next | Reduce always-on entry-point procedures, keep invariants and links | Smaller recurring context and less duplicated rule interpretation | Medium: controlled fresh-session task tests; retain source/protection/approval rules even when skills do not load |
| Next | Separate current handoff from lengthy dated narrative after milestone | Fewer whole-file reads and summary reconstruction | Medium: preserve exact raw sources, links and unresolved task ownership; do not manufacture another current dashboard |
| Next | Read-only usage-summary launcher | Reusable evidence without half-GB log dumps or repeated analysis | Medium: streaming, schema handling, deduplication, privacy and billing caveats; do not export prompts or aggregate unrelated users |
| Next | Narrow quality-selector recognition of known customization Markdown | Avoid inappropriate full-regression proposals for prose-only updates | Medium: explicit allowlist with negative tests; workflow YAML/scripts/hooks/unknown infrastructure remain conservative |
| Later | Trial role-appropriate model choices with user consent | Potential lower cost per accepted task | Unknown until equal-quality comparison; no model ranking from this heterogeneous session and no silent substitution |
| Later | Tool exposure and custom-agent catalogue alignment | Potentially less context/selection friction | Test current host/harness behavior first; preserve required debugging/visual tools and future-role scopes |

## Reuse launchers; do not create a command forest

The repository already has 78 launchers. These are **proposed interfaces**,
not commands users can run today:

| Candidate | Reuse / minimal contract |
| --- | --- |
| `bin\day-close.cmd --dry-run` / `--check` | Existing D4 owner; enumerate evidence requirements, read-only status/index/focus/task-transfer/link checks, explicit unresolved manual gates. No mutation/apply mode is necessary for a checker |
| `bin\copilot-usage.cmd --session PATH --since TIME --check` | Only if adopted: stream one explicitly selected session, deduplicate usage, aggregate categories, report missing fields and attribution; no global session sweep or raw prompt output |
| Existing `bin\rebase-flow.cmd ... --check` | Keep as current flow status; extend only with a demonstrated gap, not a duplicate monitor command |
| Existing `bin\todo.cmd` | Keep the sole generated queue; proposed guard checks owner/focus invariants rather than hand-editing output |

If report-file generation is added, preview exact inputs/output with
`--dry-run`, write only under verified ignored scratch unless a durable
report is explicitly requested, repeat safely and test the launcher itself.
List any accepted new routine in help/menu and its runbook. Do not write a
generic command dispatcher just to hide a handful of explicit operations.

## What to measure in an equal-quality trial

Choose a representative small task in each class: feedback filing,
milestone handoff, focused bug fix, and long-run acceptance. Hold task scope,
fixtures, model/settings and validation expectations constant where possible.

- Unique attributed model calls, parent and child separately.
- Input, cached input, cache-write and output categories; do not sum overlapping
  categories or cumulative checkpoints.
- Tool calls, oversized outputs, repeated reads and avoidable failure/retry loops.
- Human interventions and whether any key question/approval was missed.
- Time to accepted result, regression coverage, missed invariants, source
  preservation and whether a second corrective pass was required.
- Actual billed usage only if an attributable provider export is supplied.

Proposed decision rule: adopt an improvement only if safety/quality gates
remain intact and measured overhead improves over a comparable baseline.
Do not promise a percentage or introduce a performance threshold borrowed
from the image-processing plan: model collaboration has a different budget.
Write down no-gain results as well as successes.

## Unattended-work template

| Item | Required answer before a long autonomous run |
| --- | --- |
| Objective | One milestone/task and concrete outputs/checks |
| Authority | Allowed files/roots, fixes/restarts, commit/push permission; separate human and Production gates |
| Ownership | Existing process ID/run/receipt and completion waiter; no duplicate writers |
| Monitoring | Completion event plus bounded phase/error reads; silence prompts liveness/suspension checks, not immediate kill |
| Recovery | Profile-specific resume versus new preview/reset; preserve failed attempts and original prepared evidence |
| Retry budget | Bounded attempts with evidence improvement; stop/report repeated same failure or unsafe ambiguity |
| Done | Exact exit codes, measured assertions, browser/link checks and deferred human review clearly separated |
| Handoff | Durable current state, commands, remaining blockers, evidence and next focus |

For the currently running installation, the user's explicit permission
allows focused fixes/restarts and inspection while away. It does not
authorize new Production publication, force-merging identities, or modifying
hash-bound runtime modules before the process exits.

## Decisions to revisit when the user returns

1. Select the first implementation: D4 mechanical guard or a small handoff
   skill. Recommendation: D4's smallest useful checker, then package it.
2. Confirm whether the desired budget metric is actual provider credits,
   model-token overhead, human time, or a combined quality-adjusted measure.
   No credentials are needed; optional aggregate usage export is sufficient.
3. Choose a safe session handoff point after current acceptance, not during
   an uncertain active install.

No answer is needed to keep the current run monitoring or to preserve this
assessment. These decisions are not new blockers for LEAN/cast/art progress.
