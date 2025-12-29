# Campaign Schema

## Overview
The Campaign Schema defines the structure for the Saga Campaign, a linear PvE story mode with progressive difficulty. Campaigns consist of sequential levels with boss battles, story elements, and increasing rewards.

## Key Fields

### campaignId
Unique identifier for the campaign.

### name
Display name for the campaign.

### theme
Visual and narrative theme (medieval, sci-fi, mythic).

### levels
Array of campaign levels:
- **levelId**: Unique level identifier
- **number**: Sequential level number
- **type**: Normal, boss, story, or challenge
- **difficulty**: Difficulty rating (1-10)
- **energyCost**: Energy required to attempt
- **battleConfig**: Enemy configuration and win conditions
- **rewards**: First-time, standard, and perfect completion rewards
- **prerequisites**: Levels that must be completed first
- **story**: Narrative elements
- **modes**: Normal and hard mode availability

### progression
Player's campaign progress:
- **currentLevel**: Furthest unlocked level
- **completedLevels**: Array of completed level IDs
- **stars**: Star ratings (0-3) per level

### unlockConditions
Requirements to unlock the campaign.

## Mechanics

### Level Progression
Players advance through levels sequentially, unlocking new stages by completing prerequisites. Boss battles occur every 10 levels with enhanced rewards.

### Difficulty Modes
- **Normal**: Standard difficulty
- **Hard**: Increased enemy stats with bonus rewards

### Star Ratings
Levels award 1-3 stars based on performance:
- 1 star: Complete the level
- 2 stars: Complete without losing units
- 3 stars: Complete within turn limit/perfect score

### Energy System
Each level costs energy to attempt, encouraging strategic resource management.

### Story Integration
Narrative elements connect levels, creating a cohesive campaign experience with character development and plot progression.

## Engine Integration

### Client Implementation
- Level selection UI
- Battle integration
- Story dialog display
- Progress tracking

### Server Implementation
- Level unlocking validation
- Battle result verification
- Reward distribution
- Progress persistence

### Anti-Cheat
- Server validates level prerequisites
- Energy deduction verification
- Battle result validation

## Examples

### Basic Campaign
```json
{
  "campaignId": "saga-medieval-01",
  "name": "The Kingdom's Trial",
  "theme": "medieval",
  "levels": [
    {
      "levelId": "level-001",
      "number": 1,
      "name": "First Steps",
      "type": "normal",
      "difficulty": 1,
      "energyCost": 5,
      "battleConfig": {
        "mapId": "forest-clearing",
        "enemies": [
          {
            "cardId": "bandit",
            "level": 1,
            "count": 3,
            "position": {
              "x": 6,
              "y": 4
            }
          }
        ],
        "aiTacticId": "defensive",
        "victoryCondition": "elimination"
      },
      "rewards": {
        "firstTime": ["starter-hero", "energy-refill"],
        "standard": ["common-card-pack"],
        "perfect": ["rare-card"]
      },
      "prerequisites": [],
      "story": {
        "intro": "Your journey begins in the forest...",
        "outro": "You've proven yourself worthy!",
        "characters": ["hero-protagonist", "mentor-guide"]
      },
      "modes": {
        "normal": true,
        "hard": false
      }
    },
    {
      "levelId": "level-010",
      "number": 10,
      "name": "The Bandit King",
      "type": "boss",
      "difficulty": 5,
      "energyCost": 10,
      "battleConfig": {
        "mapId": "bandit-fortress",
        "enemies": [
          {
            "cardId": "bandit-king",
            "level": 10,
            "count": 1,
            "position": {
              "x": 7,
              "y": 7
            }
          },
          {
            "cardId": "bandit-elite",
            "level": 8,
            "count": 4
          }
        ],
        "aiTacticId": "boss-aggressive",
        "victoryCondition": "elimination",
        "turns": 20
      },
      "rewards": {
        "firstTime": ["legendary-card", "achievement-first-boss"],
        "standard": ["rare-card-pack"],
        "perfect": ["epic-equipment"]
      },
      "prerequisites": ["level-009"],
      "story": {
        "intro": "The Bandit King awaits...",
        "outro": "The kingdom is safe once more!",
        "characters": ["bandit-king", "hero-protagonist"]
      },
      "modes": {
        "normal": true,
        "hard": true,
        "hardMultiplier": 1.5
      }
    }
  ],
  "isLocked": false,
  "unlockConditions": [],
  "schemaVersion": 1
}
```

### Player Progression
```json
{
  "campaignId": "saga-medieval-01",
  "name": "The Kingdom's Trial",
  "theme": "medieval",
  "levels": [],
  "progression": {
    "currentLevel": 5,
    "completedLevels": ["level-001", "level-002", "level-003", "level-004"],
    "stars": {
      "level-001": 3,
      "level-002": 2,
      "level-003": 3,
      "level-004": 1
    }
  },
  "isLocked": false,
  "schemaVersion": 1
}
```

## Validation Rules
- campaignId must be unique
- Level numbers must be sequential
- Prerequisites must reference valid level IDs within campaign
- Energy cost must be non-negative
- Star ratings must be 0-3

## Related Schemas
- [Battle Schema](battle-schema.md) - Level battles
- [Reward Schema](reward-schema.md) - Level rewards
- [Achievement Schema](achievement-schema.md) - Campaign achievements