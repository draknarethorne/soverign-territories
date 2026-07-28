# MVP Tutorial Flow

**Last updated:** July 2026
**Authority:** MVP onboarding sequence
**Goal:** A player understands the first tactical loop without a forced long tutorial.

## Principles

- Teach only the systems in the MVP baseline.
- Use a stable starter collection; never require a randomized draw to create a legal party.
- Prefer one meaningful action, then let the player continue.
- Make optional help available from a compact help/Codex screen, not through a 28-step gate.
- Do not introduce shops, persistent health, fusion, economy cards, PvP, alliances, or map exploration before they exist in the shipped baseline.

## Required path

| Step | Player experience | System outcome |
| ---: | --- | --- |
| 1 | Start a local profile and accept the appropriate terms. | Create local save state and grant the validated starter collection. |
| 2 | Open or review the starter collection. | Highlight the hero, supports, HP/Mana/ATK/DEF, and card roles. |
| 3 | Build a six-card formation. | Enforce exactly one hero; explain any invalid selection. |
| 4 | Begin the first authored encounter. | Show the 8×8 grid and pre-battle formation. |
| 5 | Move one unit and make one basic attack. | Explain turn order and deterministic `max(1, ATK - DEF)` damage. |
| 6 | Use one simple Mana ability when affordable. | Explain Mana cost and that basic attacks remain free. |
| 7 | Complete the encounter and claim a basic reward. | Save campaign progress; unlock the next encounter. |
| 8 | Return to stage select with optional help links. | Player chooses whether to continue, inspect cards, or adjust formation. |

The target is comprehension in roughly 5–10 minutes, not a fixed timer. Testers may skip
non-essential explanatory text after they see it once.

## First encounter safety

- The first encounter is deliberately forgiving but remains a real battle.
- A defeat offers an immediate retry with the same clear state; it does not introduce
  resurrection currencies or persistent damage.
- Reward failure, invalid formation, or save failure are defects, not tutorial outcomes.

## Optional help

The first slice may include short, searchable entries for:

- card stats and rarity;
- building a legal one-hero formation;
- movement, attack, Mana, victory, and rewards;
- campaign progression and save state.

Add broader Codex, achievements, contextual tooltips, account systems, or accessibility
expansions only after the required path has been tested.

## Validation

A new tester should be able to complete the first battle without developer guidance and
state, in their own words, why a formation needs one hero, how HP is lost, and what Mana
is used for. Record where testers hesitate; those points determine the next tutorial
iteration.
