# Expedition Schema

## Overview
The Expedition Schema defines the structure for the weekly board game mode, a Mario Party-style mini-game where players roll dice, navigate a procedurally generated board, and compete for rewards. This casual mode provides variety and encourages weekly re-engagement.

## Key Fields

### expeditionId
Unique identifier for the expedition instance.

### season
Week/season identifier for tracking and rewards.

### theme
Visual theme applied to the board (Medieval, Sci-Fi, etc.).

### board
Board configuration:
- **boardId**: Layout template identifier
- **spaces**: Array of board spaces with types and content
- **length**: Total number of spaces on the board

### participants
Players in the expedition with their current state:
- **position**: Current space on the board
- **moves**: Remaining moves
- **items**: Collected rewards
- **bonuses**: Active gameplay bonuses
- **isFinished**: Completion status

### dice
Dice rolling configuration:
- **minRoll/maxRoll**: Dice range
- **rerollsAvailable**: Whether rerolls are allowed
- **rerollCost**: Cost to reroll dice

### rewards
Placement-based rewards for finishing positions.

### mode
Realtime (live) or async (turn-based) play.

## Mechanics

### Board Navigation
Players roll dice to move along a linear or branching path, landing on spaces that trigger various events:
- **Reward spaces**: Grant cards, currency, or resources
- **Penalty spaces**: Move backward or lose items
- **Event spaces**: Trigger mini-games or challenges
- **Shop spaces**: Purchase items or bonuses

### Dice Rolling
Randomized movement with VIP bonuses. Players can purchase rerolls for critical decisions.

### Competitive Gameplay
Race to the end with placement-based rewards. First player to reach the end gets the grand prize.

### Weekly Reset
Expeditions reset weekly, providing fresh boards and encouraging return engagement.

## Engine Integration

### Client Implementation
- Board visualization with animated movement
- Dice rolling animations
- Event dialogs and mini-games
- Leaderboard display

### Server Implementation
- Board generation and validation
- Dice roll verification
- Event resolution
- Reward distribution

### Anti-Cheat
- Server validates all dice rolls
- Movement verification
- Prevents position manipulation

## Examples

### Weekly Expedition
```json
{
  "expeditionId": "expedition-2025-w52",
  "season": "week-2025-52",
  "theme": "Medieval Fantasy",
  "board": {
    "boardId": "medieval-path-01",
    "spaces": [
      {
        "spaceId": 0,
        "type": "start",
        "content": {}
      },
      {
        "spaceId": 1,
        "type": "reward",
        "content": {
          "rewardId": "common-card-pack"
        }
      },
      {
        "spaceId": 2,
        "type": "event",
        "content": {
          "eventId": "mini-battle"
        }
      },
      {
        "spaceId": 15,
        "type": "end",
        "content": {
          "rewardId": "legendary-card"
        }
      }
    ],
    "length": 16
  },
  "participants": [
    {
      "playerId": "player-123",
      "position": 0,
      "moves": 3,
      "items": [],
      "bonuses": {
        "diceBonus": 0,
        "doubleMove": false
      },
      "isFinished": false
    }
  ],
  "dice": {
    "minRoll": 1,
    "maxRoll": 6,
    "rerollsAvailable": true,
    "rerollCost": {
      "type": "gems",
      "amount": 10
    }
  },
  "rewards": {
    "firstPlace": ["legendary-card-pack"],
    "secondPlace": ["rare-card-pack"],
    "thirdPlace": ["uncommon-card-pack"],
    "participation": ["energy-refill"]
  },
  "startTime": 1640995200,
  "endTime": 1641600000,
  "status": "active",
  "mode": "async",
  "schemaVersion": 1
}
```

## Validation Rules
- expeditionId must be unique per season
- Board length must match number of spaces
- Participant positions must be within board bounds
- Dice max must be greater than min
- Reward IDs must reference valid rewards

## Related Schemas
- [Reward Schema](reward-schema.md) - Expedition rewards
- [Event Schema](event-schema.md) - Event spaces
- [Player Schema](player-schema.md) - Participant tracking