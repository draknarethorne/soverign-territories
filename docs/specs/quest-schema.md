# Quest Schema

## Overview
The Quest Schema defines the structure for daily quests, weekly challenges, and special event quests that provide goals and rewards. Quests drive player engagement and guide exploration of different gameplay systems.

## Key Fields

### questId
Unique identifier for the quest.

### title
Display title shown in the quest UI.

### description
Detailed description of the quest objectives.

### type
Quest type:
- **daily**: Resets daily
- **weekly**: Resets weekly
- **event**: Special event quests
- **story**: Narrative-driven quests

### category
Quest category for organization and filtering.

### objectives
Array of quest objectives, each with:
- **objectiveId**: Unique objective identifier
- **description**: Human-readable description
- **type**: Objective type (stat, action, collect, reach, interact)
- **target**: Specific target to track
- **required**: Required amount to complete
- **current**: Current progress (tracked server-side)
- **isCompleted**: Completion status

### rewards
Rewards granted upon quest completion.

### timeLimit
Optional time limit for completion.

### cooldown
Time before quest can be repeated.

### prerequisites
Required quests or conditions before this quest unlocks.

### isRepeatable
Whether the quest can be completed multiple times.

### maxCompletions
Maximum number of times the quest can be completed.

## Mechanics

### Quest Types
- **Daily Quests**: Simple, achievable goals that reset daily
- **Weekly Quests**: More challenging objectives with better rewards
- **Event Quests**: Special quests tied to events or seasons
- **Story Quests**: Narrative progression quests

### Progress Tracking
Server-side tracking ensures quest progress can't be manipulated. Objectives update in real-time as players complete actions.

### Categories
Different quest categories encourage diverse gameplay:
- Combat quests for battle engagement
- Collection quests for card hunting
- Economy quests for resource management
- Social quests for alliance participation
- Exploration quests for map discovery

## Engine Integration

### Client Implementation
- Quest log UI showing active quests
- Progress bars and completion indicators
- Reward preview and claiming

### Server Implementation
- Objective validation and progress updates
- Quest state persistence
- Reward distribution

### Anti-Cheat
- Server validates all quest progress
- Prevents progress manipulation
- Tracks completion timestamps

## Examples

### Daily Combat Quest
```json
{
  "questId": "daily-battles",
  "title": "Battle Ready",
  "description": "Win 3 battles today",
  "type": "daily",
  "category": "combat",
  "objectives": [
    {
      "objectiveId": "win-battles",
      "description": "Win battles",
      "type": "stat",
      "target": "battles_won",
      "required": 3,
      "current": 0,
      "isCompleted": false
    }
  ],
  "rewards": [
    {
      "type": "xp",
      "amount": 500
    },
    {
      "type": "stamina",
      "amount": 50
    }
  ],
  "isRepeatable": true,
  "schemaVersion": 1
}
```

### Weekly Collection Quest
```json
{
  "questId": "weekly-collector",
  "title": "Card Hunter",
  "description": "Collect 10 new cards this week",
  "type": "weekly",
  "category": "collection",
  "objectives": [
    {
      "objectiveId": "collect-cards",
      "description": "Acquire new cards",
      "type": "collect",
      "target": "new_cards",
      "required": 10,
      "current": 0,
      "isCompleted": false
    }
  ],
  "rewards": [
    {
      "type": "card",
      "id": "rare-pack",
      "amount": 1
    }
  ],
  "isRepeatable": true,
  "schemaVersion": 1
}
```

### Story Quest
```json
{
  "questId": "tutorial-combat",
  "title": "First Steps",
  "description": "Learn the basics of combat",
  "type": "story",
  "category": "combat",
  "objectives": [
    {
      "objectiveId": "complete-tutorial",
      "description": "Complete the combat tutorial",
      "type": "action",
      "target": "tutorial_completed",
      "required": 1,
      "current": 0,
      "isCompleted": false
    },
    {
      "objectiveId": "win-first-battle",
      "description": "Win your first battle",
      "type": "stat",
      "target": "battles_won",
      "required": 1,
      "current": 0,
      "isCompleted": false
    }
  ],
  "rewards": [
    {
      "type": "card",
      "id": "starter-hero",
      "amount": 1
    }
  ],
  "prerequisites": [],
  "isRepeatable": false,
  "schemaVersion": 1
}
```

## Validation Rules
- questId must be unique
- Objectives must have valid types and positive required values
- Rewards must use supported types
- Prerequisites must reference valid quest IDs

## Related Schemas
- [Achievement Schema](achievement-schema.md) - Similar reward structures
- [Event Schema](event-schema.md) - Event-based quests
- [Reward Schema](reward-schema.md) - Quest rewards
