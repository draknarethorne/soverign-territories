# Agent Selection Guide

Choose a specialist only when its bounded context is useful. Simple lookups,
single-trace debugging and small changes stay with the current assistant;
this guide does not mandate delegation or identify the currently active agent.

## Shared working contract

All seven agents follow [Copilot instructions](../copilot-instructions.md).
Their role descriptions do not override scope, approval or safety gates.

- **Current authority:** read [STATUS](../../docs/STATUS.md), the
  [documentation map](../../docs/README.md) and affected owning plans.
  MVP/design rules and runtime schemas beat the game bible's future vision.
  The current release is local-first PvE Sovereign Dawn; Unity is planned,
  and Nakama/PvP/alliances/territory/AFK systems remain later-phase scope.
- **One work order:** [the plan index](../../docs/plans/README.md) owns
  scheduling. The [generated queue](../../docs/todo.md) shows active focus
  and links deferred work. Holding is not completion; pinned handoffs in
  [the recap index](../../docs/recap/README.md) own current resume details.
  Do not change priorities merely because another agent is available.
- **Feedback and filing:** preserve chat/raw sources word for word with
  per-request coverage in the primary plan. Verify preservation/coverage and
  reread each source before individual filing. Follow
  [the archive guide](../../docs/archive-guide.md) for matching physical
  groups, indexes and references; archival does not close implementation.
- **Bounded execution:** one primary milestone, with only the independent
  analysis/quality slices allowed by the plan index. Delegation needs a
  concrete scope and stop condition; do not recursively hand a task around.
  A read-only assignment remains read-only even for an edit-capable agent.
- **Tools:** use only tools actually exposed by the current host; discover
  deferred tools before calling them. Frontmatter uses documented aliases,
  not copied extension-specific IDs. Capability is not guaranteed by a model
  name. Use Windows paths for tool access and preserve unrelated dirty work.
- **Validation:** preview supported [launchers](../../bin/help.cmd), run
  the smallest relevant checks and follow
  [quality gates](../../docs/QUALITY-GATES.md). Distinguish actual test/build/
  browser results from instructions for a human to run later. Keep scratch
  under the repository's verified ignored temporary area.
- **Publication:** no automatic commit/push for large changes, passing tests
  or a role handoff. Follow the user's publication authorization and scoped
  day-close requirements; stage only intended files, run required checks,
  preserve other work and include the repository coauthor trailer.
- **Protected data:** no source pruning, blanket intake, Production writes,
  pipeline default changes or dependency installation merely to exercise an
  agent. Do not create art assets or upload private repository/image data.

## Roles

| Agent | Best fit | Boundary |
| --- | --- | --- |
| [Beast Mode](Sovereign-Beast-Mode.agent.md) | Approved game-design analysis, cross-system trade-offs, canonical design docs | Not production code or automatic publication |
| [Balance Master](Sovereign-Balance-Master.agent.md) | Formulas, probabilities, progression and reproducible balance analysis | No invented numeric rules or unapproved economy |
| [Code Mode](Sovereign-Code-Mode.agent.md) | Approved Unity/C# logic, algorithms, debugging and focused tests | Verify project/toolchain; no speculative scaffolding |
| [Data Factory](Sovereign-Data-Factory.agent.md) | Approved schema-driven batches and structured transformations | No invented fields, IDs, balance or unsafe bulk moves |
| [Network Ninja](Sovereign-Network-Ninja.agent.md) | Explicitly authorized later-phase backend scope | Not a dependency of current PvE or sandbox acceptance |
| [Unity Builder](Sovereign-Unity-Builder.agent.md) | Approved scene, prefab, component and UI integration | Requires a real approved Unity project/editor |
| [Visual Analyst](Sovereign-Visual-Analyst.agent.md) | Read-only image/UI critique and comparison | Requires inspectable evidence; no mutation or identity sign-off |

Model selections remain in each agent's frontmatter; this guide deliberately
does not duplicate a second model roster or claim relative speed/quality.
Existing selections were retained during the Oct 30 refresh. Availability,
permissions and modality must be checked in the host when used. If a pinned
model is unavailable, report it and obtain a selection decision; do not
silently substitute a model or claim a runtime smoke test passed.

## Handoff result

Return the bounded outcome, changed files (if authorized), evidence/checks
actually executed, remaining gates and owning plan/task. A proposed follow-up
is not permission to start it. Reuse the same verified run evidence across
acceptance owners instead of rerunning heavy operations for each agent.
