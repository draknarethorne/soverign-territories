# Game design and architecture review

## Authority and scope

- Read [STATUS](../../../../docs/STATUS.md), the affected active plan and
  relevant canonical rules identified by the
  [documentation map](../../../../docs/README.md).
- The current release is local-first PvE Sovereign Dawn. PvP, alliances,
  territory maps, AFK economy and Nakama are later-phase vision, not implied
  requirements. Do not invent a current engine/backend version.
- MVP/design rules and runtime schemas outrank
  [the game bible](../../../../docs/game-bible.md), which supplies vision only.
  Update the owning rule document, not a duplicate blueprint in the bible.

## Method

1. Establish the player's problem, current behavior and explicit constraints.
   Read affected sections, not the entire vision document by default.
2. Trace dependencies across combat, deck progression, card data, tutorial
   and player experience. Distinguish implemented facts from proposals.
3. For significant decisions, compare a small number of options with concrete
   examples, edge cases, fairness and technical trade-offs. Do not invent
   monetization targets, unlock levels, rarity tiers or numeric budgets.
4. Obtain approval for major design changes. Record the approved rule before
   schema/tooling/implementation changes; a proposal does not authorize
   delegated implementation.
5. Preserve every user request and assign coverage in the owning plan under
   the canonical feedback process. Verify terminology and affected links.
6. Hand off the agreed behavior, dependencies and measurable acceptance cases.
   Do not claim feasibility, balance or performance without evidence.

## Review lenses and output

- Core-loop clarity, meaningful choices and tutorial cognitive load.
- Cross-system consistency, power creep, progression bottlenecks and
  unintended repeatable reward loops.
- Accessibility and fairness; distinguish supported measurements from
  external comparisons or hypotheses.
- Implementation cost and reversibility within current scope, rather than
  speculative future scale.

Summarize the recommendation, rationale, trade-offs, open user decisions,
owning document/task and acceptance examples. Keep simple answers short. Do
not create art assets, silently change numerical rules, or commit/push because
a change is large.
