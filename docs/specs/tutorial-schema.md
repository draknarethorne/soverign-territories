# Tutorial Schema

## Overview
The Tutorial Schema defines the structure for onboarding tutorials and quests that guide new players through game mechanics, UI elements, and strategic concepts. Tutorials are critical for player retention and understanding complex systems like deck building, combat, and diplomacy.

## Key Fields

### tutorialId
Unique identifier for the tutorial, used for tracking completion and prerequisites.

### title
Display name shown in the tutorial UI.

### description
Brief overview of what the tutorial covers.

### steps
Array of sequential tutorial steps, each containing:
- **stepId**: Unique step identifier
- **instruction**: Text shown to guide the player
- **trigger**: How the step completes (action, completion, time)
- **target**: Specific UI element or action to highlight
- **reward**: Optional reward for completing the step

### prerequisites
List of tutorialIds that must be completed before this tutorial unlocks.

### isMandatory
Boolean flag indicating if the tutorial blocks further progression until completed.

## Mechanics

### Tutorial Flow
Tutorials use a step-by-step progression system with visual cues and blocking interactions to ensure players understand each mechanic before advancing.

### Trigger Types
- **action**: Player performs a specific action (e.g., "Deploy a unit")
- **completion**: Automatic trigger when a condition is met
- **time**: Step completes after a delay for reading

### Rewards
Steps can grant XP, cards, or resources to encourage completion and teach reward systems.

## Engine Integration

### Client Implementation
- Tutorial manager tracks progress and displays overlays
- UI highlights target elements with arrows/tooltips
- Progress saved to player profile

### Server Validation
- Tutorial completion verified server-side to prevent cheating
- Prerequisites checked before unlocking new tutorials
- Rewards distributed through standard reward system

### Anti-Cheat
- Server validates tutorial step completion
- Prevents skipping mandatory tutorials
- Tracks completion timestamps for analytics

## Examples

### Basic Movement Tutorial
```json
{
  "tutorialId": "movement-basics",
  "title": "Moving Units",
  "description": "Learn how to move your units around the map",
  "steps": [
    {
      "stepId": "select-unit",
      "instruction": "Click on one of your units to select it",
      "trigger": "action",
      "target": "unit-selection"
    },
    {
      "stepId": "move-unit",
      "instruction": "Click on an adjacent tile to move your unit",
      "trigger": "action",
      "target": "tile-movement",
      "reward": {
        "type": "xp",
        "amount": 10
      }
    }
  ],
  "prerequisites": [],
  "isMandatory": true,
  "schemaVersion": 1
}
```

### Advanced Combat Tutorial
```json
{
  "tutorialId": "combat-mechanics",
  "title": "Combat System",
  "description": "Master the art of battle",
  "steps": [
    {
      "stepId": "attack-setup",
      "instruction": "Position your units for attack",
      "trigger": "completion",
      "target": "combat-preview"
    },
    {
      "stepId": "execute-attack",
      "instruction": "Click attack to engage",
      "trigger": "action",
      "target": "attack-button",
      "reward": {
        "type": "card",
        "amount": 1
      }
    }
  ],
  "prerequisites": ["movement-basics"],
  "isMandatory": false,
  "schemaVersion": 1
}
```

## Validation Rules
- All tutorialIds must be unique across the game
- Prerequisites must reference valid tutorialIds
- Steps must have valid trigger types
- Rewards must use supported types and positive amounts

## Related Schemas
- [Player Schema](player-schema.md) - Tracks tutorial progress
- [Reward Schema](reward-schema.md) - Handles tutorial rewards
- [UI Schema](ui-schema.md) - Tutorial overlay rendering