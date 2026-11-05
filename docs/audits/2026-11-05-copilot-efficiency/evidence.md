# Evidence, attribution and cost limits

[Review index](README.md) | [Practices](practices.md) | [Proposal](proposal.md)

## Dataset and method

Local current-session telemetry, Oct 29 17:00 UTC through Nov 5 approximately
23:14 UTC, was streamed rather than loaded wholesale. The session remains
active, so counts below are a snapshot, not immutable final totals.
Usage records were deduplicated by source-session/sequence where present,
otherwise API-call identity. Only numeric categories and aggregate event
metadata were retained; no message bodies or private runtime instructions
are reproduced.

Recent-history queries were attempted with a seven-day repository scope,
then a bounded wider discovery when no matching rows appeared. They did
not produce an attributable comparison set for this repository. Available
VS Code debug-session folders were months old, not evidence for this run;
they were excluded. Current CLI session events supplied the usable evidence.
These limitations do not prove history is absent or logging is broken.

## Observed usage

| Measure | Snapshot | Interpretation |
| --- | ---: | --- |
| Unique usage records | 5,758 | 4,989 attributed to the parent session, 769 to sub-agent sources |
| User-message events | 233 | Includes operational/skill deliveries; not 233 billable user prompts |
| Summed input tokens | 707,384,928 | Repeated context processed across calls, **not unique content** |
| Summed output tokens | 3,302,842 | Do not add reasoning tokens separately without checking provider semantics |
| Reported cache-read tokens | 668,644,919 | Approximately 94.5% of reported input volume; cached does not mean free |
| Reported cache-write tokens | 38,724,217 | Part of input accounting; do not add input + cache reads + cache writes as independent volume |
| Median input per record | 122,782 | Large recurring request context, not a 122K-token new task every time |
| Median output per record | 334 | Final-answer brevity alone is unlikely to remove the main volume |
| Input maximum | 246,325 | Long-context events occurred; pricing tier must be assessed per call/model |
| Summed recorded model duration | 78,189,412 ms | About 21.7 hours of reported API duration, **not elapsed project time**; calls/agents can overlap |
| Tool-definition tokens per reported request | 2,026 minimum; 12,090 median; 15,028 maximum | Tool exposure has context cost; not proof every tool can safely be removed |

Recorded usage-model labels/counts: GPT-6 Luna 680, GPT-6.1 Sol 3,428,
GPT-5.6 Luna 44, Claude Opus 5.5 1,606. These are historical observations,
not a preference change, recommendation to override subagent defaults, or
a controlled quality/cost comparison. Different dates/tasks/cache states
prevent a fair model ranking from these totals.

## Tool and context signals

| Measure | Snapshot | What it establishes / does not establish |
| --- | ---: | --- |
| Unique started tool calls | 9,718 | Substantial orchestration; some parallel-wrapper child tools add useful work per round trip |
| Completed tool events | 9,708 | A live snapshot can have starts without completions; not automatically lost work |
| Completions with explicit failure flag | 149 | About 1.5%; not every shell nonzero or intentional negative test, and not every failure is avoidable |
| Results containing oversized-output/offload markers | 274 | Repeated output-management friction; marker count is not total wasted tokens |
| Serialized result characters | 38,606,149 | Diagnostic proxy, **not tokens actually delivered/billed**; wrappers/truncation differ |
| Exact repeated view path/range requests | 268 beyond first reads | Some necessary after edits/compaction; a candidate for reduction, not 268 proven mistakes |
| Compaction-completion events | 55; 51 explicit successes | Long-session context maintenance recurred; unsuccessful/other outcomes need separate diagnosis |
| Latest successful compaction | 227,660 -> 44,889 reported tokens | Context reduced sharply, but rebuilding omitted details can incur more reads |
| Completed subagents | 16 | Reported aggregate 1,042 tools / 36,340,939 tokens; **do not add to usage totals**, which already include sub-agent records |

Top tools by starts: view 3,312; PowerShell 2,367; rg 991; apply_patch 809;
read_powershell 616; edit 403; grep 301; SQL 137; glob 118; browser
Playwright 101. Tool failures include view 37, Python syntax diagnostic
tool 22, patch 20, rg 20, shell-read 13 and browser 12. These counts locate
investigation opportunities, not a license to remove the verification tools.

There are 30 skill-invocation events: Python fact-grounded coding 23,
agent customization four, troubleshooting two, profiling one. Repeated
invocation can follow compaction or a genuinely new scope; the event count
alone does not prove a skill was reloaded unnecessarily.

## Repository inventory

Measured before this report's additions:

| Surface | Size / count | Implication |
| --- | --- | --- |
| Project Copilot entry point | 10,993 bytes | Review always-on versus on-demand procedures; bytes are not exact tokens |
| Planning agreement/index | 57,852 bytes | Collapsed HTML helps people, **does not hide text from a full file read** |
| Reset execution spine | 57,400 bytes | Good single ownership, but history/raw sources still make full reads expensive |
| Pinned resume recap | 52,596 bytes | Target current ranges; avoid rereading the entire day's accumulated narrative |
| Launcher help | 28,431 bytes | Established commands exist; selective help/discovery beats full repeated dumps |
| Launchers | 78 `.cmd` files | Prefer existing commands; more launchers are not inherently simpler |
| Repository specialists | Seven `.agent.md` files | Several roles target future Unity/game work, not the current Python photo pipeline |
| Repository skill definitions found under `.github` | Zero | Plugin skills are available; no matching local SKILL.md found in that search |

## Billing: what can safely be said

[Official model pricing](https://docs.github.com/en/copilot/reference/copilot-billing/models-and-pricing)
describes input, output, cached input and, for some models, cache-write
rates, plus model/context tiers. The fetched documentation states usage
is converted to AI credits. The
[legacy request-billing page](https://docs.github.com/en/copilot/reference/copilot-billing/request-based-billing-legacy/copilot-requests)
explicitly applies only to qualifying legacy annual-plan subscribers.
Therefore **"one prompt means one charge" and "every tool call is another
premium request" are not universal statements**.

This assessment does not establish the user's plan, billing entity,
allowances, discounts, model/tier rates at each historical call, adjustments
or actual overage. A generic telemetry `cost` field is not a dollar invoice.
Do not multiply the 707M input total by an uncached rate: most input was
reported cached, writes have distinct semantics, and models/tiers changed.
Do not double-count checkpoint/shutdown cumulative totals, compaction
statistics or subagent summaries on top of deduplicated usage records.

To establish financial savings later, compare provider billing/usage
exports for equal-quality task cohorts, with model/tier, cached/uncached/
write/output categories, active allowances and timestamps. Keep that export
local; no account credentials are needed in repository docs. Until then,
targets are **measured overhead reductions**, not promised dollars or credits.
