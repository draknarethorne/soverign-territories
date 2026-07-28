# Map and Territory Progression

**Last updated:** July 2026
**Status:** Long-term design gate; not an MVP implementation specification.

## MVP boundary

The MVP uses linear campaign stage selection and an 8×8 battle board. It does not include
an explorable Realm map, hex movement, fog of war, occupation, resource nodes, castles,
or territory buffs. Campaign presentation may use illustrated stage art, but it must not
create strategic-map dependencies.

## Long-term hierarchy

The future vision can expand in layers:

1. **Battle:** an 8×8 tactical encounter.
2. **Realm:** a small PvE region with optional exploration and local strategic choices.
3. **Territory:** a set of Realms with opt-in conflict and cooperative objectives.
4. **World:** seasonal alliance-scale territory competition.

This is a conceptual hierarchy, not a numerical content promise. Map size, resets,
buff magnitudes, player counts, procedural generation, and server regions must be chosen
only after a prototype and live-operations feasibility review.

## Design guardrails

- Strategic maps must create meaningful choices, not a check-in obligation.
- PvP must be opt-in or have a complete safe PvE path.
- Territory advantage must not compound into irreversible power gaps.
- Resource production, raids, and social mechanics need anti-griefing, catch-up, and
  absence protections before implementation.
- New map layers must reuse proven battle, content, and data pipelines rather than
  multiplying them prematurely.

## Admission gates

| Layer | Prerequisites |
| --- | --- |
| Realm prototype | Stable campaign loop, reusable encounter data, and evidence that players want navigation/exploration choices. |
| Territory prototype | Realm prototype, economy simulation, persistence model, anti-griefing design, and backend capacity plan. |
| World seasons | Moderation, alliances, operations staffing, load testing, fair matchmaking/placement, and seasonal recovery rules. |

Any map feature needs a data contract in `data/schemas/` and an implementation plan that
identifies save, validation, and abuse cases before it becomes active work.
