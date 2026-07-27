# Achievement Schema

## Overview
The Achievement Schema defines the structure for player achievements and milestones that track progress and provide rewards. Achievements encourage exploration of different gameplay systems and provide long-term goals.

## Key Fields

### achievementId
Unique identifier for the achievement.

### name
Display name shown in the UI.

### description
Detailed description of what the achievement requires.

### category
Achievement category:
- **combat**: Battle-related achievements
- **collection**: Card collecting achievements
- **social**: Alliance and multiplayer achievements
- **progression**: Leveling and advancement achievements
- **exploration**: Map and territory achievements

### rarity
Achievement rarity affecting visual styling and prestige.

### requirements
Achievement unlock conditions:
- **type**: Requirement category (stat, action, collection, time, social)
- **target**: Specific target (e.g., "battles_won", "cards_collected")
- **value**: Required threshold
- **conditions**: Additional filters

### rewards
List of rewards granted upon completion.

### isHidden
Whether the achievement is revealed only after unlocking.

### prerequisites
Other achievements that must be completed first.

## Mechanics

### Progress Tracking
Server-side tracking ensures achievements can't be cheated. Progress is stored in player profiles and updated in real-time.

### Categories
Different achievement types encourage diverse gameplay:
- Combat achievements for PvP/PvE engagement
- Collection achievements for card hunting
- Social achievements for alliance participation
- Progression achievements for long-term goals

### Rewards
Achievements provide meaningful rewards:
- XP for leveling
- Rare cards for collection
- Resources for economy
- Cosmetics for personalization
- Titles for prestige

## Engine Integration

### Client Implementation
- Achievement UI showing progress bars
- Notifications for unlocks
- Visual indicators for hidden achievements

### Server Implementation
- Progress calculation and validation
- Reward distribution
- Anti-cheat measures

## Examples

### Combat Achievement
```json
{
  "achievementId": "first-victory",
  "name": "First Victory",
  "description": "Win your first battle",
  "category": "combat",
  "rarity": "common",
  "requirements": {
    "type": "stat",
    "target": "battles_won",
    "value": 1
  },
  "rewards": [
    {
      "type": "xp",
      "amount": 100
    }
  ],
  "isHidden": false,
  "prerequisites": [],
  "schemaVersion": 1
}
```

### Collection Achievement
```json
{
  "achievementId": "card-collector",
  "name": "Card Collector",
  "description": "Collect 100 different cards",
  "category": "collection",
  "rarity": "rare",
  "requirements": {
    "type": "collection",
    "target": "unique_cards",
    "value": 100
  },
  "rewards": [
    {
      "type": "card",
      "id": "rare-pack",
      "amount": 1
    }
  ],
  "isHidden": false,
  "prerequisites": ["first-victory"],
  "schemaVersion": 1
}
```

### Social Achievement
```json
{
  "achievementId": "alliance-founder",
  "name": "Alliance Founder",
  "description": "Create your own alliance",
  "category": "social",
  "rarity": "epic",
  "requirements": {
    "type": "action",
    "target": "alliance_created",
    "value": 1
  },
  "rewards": [
    {
      "type": "title",
      "id": "founder",
      "amount": 1
    }
  ],
  "isHidden": true,
  "prerequisites": ["card-collector"],
  "schemaVersion": 1
}
```

## Validation Rules
- achievementId must be unique
- Prerequisites must reference valid achievementIds
- Requirements must have valid types and positive values
- Rewards must use supported types

## Related Schemas
- [Player Schema](player-schema.md) - Achievement progress tracking
- [Notification Schema](notification-schema.md) - Achievement unlock notifications
- [Reward Schema](reward-schema.md) - Achievement rewards
