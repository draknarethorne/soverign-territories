# Battle Schema

## Overview
The Battle Schema defines the complete structure for combat encounters, including grid-based positioning, unit stats, terrain effects, and turn-based resolution. This schema enables deterministic combat simulation for both manual and auto-battle modes.

## Key Fields

### battleId
Unique identifier for the battle instance.

### type
Battle category:
- **pve**: Player vs Environment
- **pvp**: Player vs Player
- **alliance**: Large-scale alliance battles
- **tutorial**: Guided tutorial battles
- **event**: Special event battles

### mapId
Reference to the map where battle occurs.

### gridSize
Battle grid dimensions (typically 8x8).

### participants
Array of players/teams involved, including their decks and AI settings.

### units
All units on the battlefield with their positions, stats, and status effects.

### terrain
Grid terrain features affecting movement and combat.

### turnOrder
Current initiative order of units.

### currentTurn
Turn counter for the battle.

### currentUnit
ID of the unit whose turn it currently is.

### actions
Complete history of battle actions for replay and validation.

### victoryConditions
Win/loss criteria for the battle.

### status
Current battle state (setup, active, completed, etc.).

## Mechanics

### Turn-Based Resolution
Battles follow strict turn order based on unit speed stats. Each unit can move and perform one action per turn.

### Grid-Based Combat
Units occupy specific grid positions with terrain modifiers:
- **Movement**: Affected by terrain costs
- **Combat**: Line-of-sight and range calculations
- **Cover**: Terrain provides defense bonuses

### Unit Stats
Each unit has core combat statistics:
- **Health**: Hit points (damage reduces this)
- **Attack**: Damage output
- **Defense**: Damage reduction
- **Speed**: Initiative and movement

### Status Effects
Temporary modifiers from abilities:
- Buffs/debuffs
- Stuns and disables
- Damage over time
- Healing effects

## Engine Integration

### Client Implementation
- Battle grid visualization
- Unit movement animations
- Combat effect displays
- Auto-battle simulation

### Server Implementation
- Battle state validation
- Action resolution
- Anti-cheat measures
- Result persistence

### Deterministic Simulation
All combat math is predictable and reproducible for fair multiplayer battles.

## Examples

### PvE Battle Setup
```json
{
  "battleId": "pve-encounter-12345",
  "type": "pve",
  "mapId": "forest-clearing",
  "gridSize": {
    "width": 8,
    "height": 8
  },
  "participants": [
    {
      "playerId": "player-789",
      "team": 1,
      "deckId": "battle-deck-001",
      "isAI": false
    },
    {
      "playerId": "ai-opponent",
      "team": 2,
      "deckId": "ai-deck-forest",
      "isAI": true,
      "aiTacticId": "aggressive"
    }
  ],
  "units": [
    {
      "unitId": "hero-001",
      "cardId": "fire-mage",
      "playerId": "player-789",
      "position": {
        "x": 3,
        "y": 4
      },
      "stats": {
        "health": 100,
        "maxHealth": 100,
        "attack": 25,
        "defense": 10,
        "speed": 15
      },
      "status": [],
      "isAlive": true
    }
  ],
  "terrain": [
    {
      "position": {
        "x": 2,
        "y": 2
      },
      "type": "forest",
      "modifiers": {
        "defense": 1.2,
        "movement": 1.5
      }
    }
  ],
  "turnOrder": ["hero-001", "enemy-001"],
  "currentTurn": 1,
  "currentUnit": "hero-001",
  "actions": [],
  "victoryConditions": {
    "type": "elimination"
  },
  "status": "active",
  "startTime": 1640995200,
  "schemaVersion": 1
}
```

### PvP Battle Action
```json
{
  "battleId": "pvp-match-67890",
  "type": "pvp",
  "actions": [
    {
      "actionId": "action-001",
      "unitId": "hero-001",
      "type": "attack",
      "target": {
        "unitId": "enemy-hero-001"
      },
      "timestamp": 1640995210
    }
  ],
  "victoryConditions": {
    "type": "elimination"
  },
  "status": "active",
  "schemaVersion": 1
}
```

### Alliance Battle
```json
{
  "battleId": "alliance-siege-99999",
  "type": "alliance",
  "participants": [
    {
      "playerId": "alliance-member-1",
      "team": 1,
      "deckId": "siege-deck",
      "isAI": false
    }
  ],
  "victoryConditions": {
    "type": "objective",
    "objectives": [
      {
        "id": "capture-castle",
        "description": "Capture the enemy castle",
        "position": {
          "x": 7,
          "y": 7
        },
        "isCompleted": false
      }
    ]
  },
  "status": "active",
  "schemaVersion": 1
}
```

## Validation Rules
- battleId must be unique
- Grid positions must be within bounds
- Unit stats must be non-negative
- Turn order must include all living units
- Actions must reference valid units and positions

## Related Schemas
- [Tactic Schema](tactic-schema.md) - AI behavior for auto-battle
- [Card Schema](card-schema.md) - Unit source cards
- [Map Schema](map-schema.md) - Battle terrain
- [Ability Schema](ability-schema.md) - Combat abilities
