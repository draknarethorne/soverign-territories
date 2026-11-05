# Collaboration practices and lessons

[Review index](README.md) | [Evidence](evidence.md) | [Proposal](proposal.md)

## What is already working

- Supported launchers give the user and assistant the same command/defaults.
- Preview/apply/check boundaries, immutable run receipts and per-image
  recovery protect expensive work and distinguish proof from assumptions.
- Feedback is preserved verbatim with explicit coverage before filing.
- Routine hygiene is separated from targeted/deep regression acceptance.
- The new execution spine removes competing active domain queues and
  preserves every transferred contract rather than pretending it is done.
- Explicit user gates prevent similarity scores becoming identity approval,
  sandbox experiments becoming Production changes, or a useful pilot
  becoming unreviewed deployment.

These should be retained when reducing overhead. Fewer checks without
dependency/ownership proof are not an efficiency improvement.

## Friction observed in this session

| Pattern | Evidence / limitation | Better practice |
| --- | --- | --- |
| Multi-day conversation accumulates many objectives | 55 compaction-completion events; original task expanded through recovery, matching, UI, performance, planning and machines | Finish one milestone slice; hand off verified state instead of carrying every topic indefinitely |
| Human-facing collapse mistaken for smaller context | 50-58KB planning/recap documents still contain history and raw sources | Read targeted current sections; later split current execution from dated reference only with preservation/link repair |
| Repeated custom verification commands | Transfer/link/task checks were constructed directly in this session | Put recurring mechanical invariants into a tested read-only tool; retain one-off diagnostics until they actually repeat |
| Oversized result handling | 274 marked outputs; even regex on a single-line JSON search result offloaded again | Parse selected fields, narrow ranges, summarize counts; do not use content matching that returns an entire huge JSON line |
| Multiple micro-edits followed by repeated checks | The milestone rollout needed heading, wording, queue and navigation follow-ups | Batch a coherent edit, review once, run relevant validation once; rerun when changed output invalidates the proof |
| Model orchestration used for waiting | 616 shell-read starts over the whole session; not all were polls | Prefer one bounded waiter/completion event and phase-boundary reads; no active conversational polling loop |
| Domain-specialist catalogue mismatches current task | Seven specialists mostly describe Unity/game/art roles; current runtime is Python tooling | Stay in the main assistant for a continuous trace; use a bounded read-only helper only for substantial independent context |
| Conservative selector overreaches on instructions | The documentation rollout's `.github` Markdown triggered a full test proposal | Keep required hygiene; propose narrow known-customization classification with tests later, never broad `.github` exemptions |
| Instructions repeat full procedures | Project entry point still ~11KB, plus plugin/tool guidance | Keep critical invariants always-on; reference reusable procedures and load their detail on demand |

These are contributing patterns, not a claim that every repeated read,
tool failure, compaction or minute of processing was unnecessary.
The photo pipeline's CPU/disk runtime is a separate performance problem:
speeding image processing does not directly measure model-token savings.

## Instructions, skills, prompts, tools and agents

[VS Code skills documentation](https://code.visualstudio.com/docs/agent-customization/agent-skills)
describes task-specific procedures/resources loaded when relevant.
[Custom instructions](https://code.visualstudio.com/docs/agent-customization/custom-instructions)
guide behavior but do not guarantee compliance; test them in a fresh chat.
Harness support/locations must be verified, not inferred from model choice.

| Mechanism | Put here | Do not put here |
| --- | --- | --- |
| Always-on project instructions | Canonical authority, current-work entry point, protected roots/raw-source invariants, validation/publication boundaries, supported command/scratch rules | Entire migration runbooks, dated counters, every launcher argument |
| Targeted file instructions | Actual language/schema/workspace-specific constraints, only where their file selection is reliable | Hidden cross-cutting protection rules that must apply before any edit |
| On-demand skill | Repeated multi-step feedback filing, milestone transfer/handoff, scoped long-run diagnosis/acceptance; links to canonical rules plus scripts/examples | A second copy of policy or a way to make unsafe work implicitly authorized |
| Prompt file | A concise repeatable user entry point invoking a skill/task contract | A competing source of truth or mandatory boilerplate for every question |
| Deterministic launcher/tool | Counts, hashes, task ownership, link/queue checks, process/run status and bounded evidence extraction | Identity judgment, design approval or fabricated success-shaped summaries |
| Custom agent | A substantial independent context needing a bounded outcome | Simple lookup, a continuous bug trace, or an excuse to activate future-phase systems |

Candidate skills should compose existing commands, not paste the whole
working agreement. Their descriptions need recognizable trigger phrases;
scripts need explicit paths, failure behavior and focused tests.
Keep essential safety guidance accessible even if a skill is not selected.

## Sessions and context

Use **milestone-sized sessions**, not arbitrary time/token limits:

1. Save a coherent tested/committed checkpoint where authorized.
2. Record current task, exact run/receipt, command, process owner, code
   binding, pending gate and safe restart instructions in the owning handoff.
3. Record what must **not** be repeated: reset, intake, shared publication,
   threshold changes or source cleanup.
4. Open a new session only when the handoff is sufficient to continue
   without reconstructing the entire conversation.
5. Keep the old session/log for recovery; do not delete it to make costs
   disappear. Avoid starting another worker on the same live job.

Do not reset sessions before every small task: reloading/cache writes and
lost tacit context can cost more. Long sessions can benefit from cached
prefixes. Compare completed-work quality, model calls and re-read volume
before deciding a particular handoff cadence is better.

## Q&A and autonomy

Ask before irreversible/high-impact ambiguity: identity acceptance,
Production/shared publication, changed quality rules, uncertain source
retirement or a major scope choice. Batch related operational preferences
in a short form; handle distinct design decisions one at a time.

For already approved scope, act without repeatedly asking permission to
perform the same test/preview. When the user is away, use conservative
defaults only within explicit authority and label assumptions. A failed
question delivery is not user approval for a wider mutation.

An unattended contract needs: objective, allowed changes, protected data,
retry/restart budget, existing worker ownership, evidence location,
success criteria and escalation conditions. A few hours of autonomy should
mean useful local work plus event-driven waits, not continuous model
generation or indefinite retries. Stop a retry cycle when evidence ceases
to improve; preserve the blocker for the user's return.

## Tools that deserve selective use

- Existing semantic/Pylance tools for actual symbol/type/runtime questions;
  simple known-file reads do not need a large semantic expansion.
- Session history for bounded prior-work evidence, not unfiltered exports
  or a substitute for the current plan. This review found limited matching
  history, so it did not infer missing sessions.
- Browser inspection for real Gallery/Overview/Review links, loaded images,
  framing/filter behavior and console/network failures, not just file existence.
- SQL for dependencies and batch evidence, not a second durable task queue.
- Existing launchers for preview/check/resume; PowerShell for bounded
  observation when no equivalent launcher exists.
- Subagents only when their isolated work is genuinely independent;
  use returned results instead of repeating their exploration in the parent.

Disabling a tool may reduce exposure but remove valuable capability. Measure
tool-definition/request context and task success before changing exposure;
do not disable diagnostics/browser safeguards simply because they have cost.
