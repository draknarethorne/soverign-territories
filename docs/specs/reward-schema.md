# Reward Schema

## Overview
The Reward Schema defines the structure for all rewards distributed throughout the game, from quest completions to battle victories. Rewards provide motivation and progression incentives across all gameplay systems.

## Key Fields

### rewardId
Unique identifier for the reward.

### type
Reward category:
- **xp**: Experience points for leveling
- **card**: Card rewards (packs or specific cards)
- **resource**: Game resources (gold, food, etc.)
- **energy**: Energy/stamina refills
- **cosmetic**: Visual customizations
- **title**: Achievement titles
- **currency**: Special currencies (gems, tokens)

### subtype
Specific subtype within the type (e.g., "gold" for resource type).

### amount
Quantity or amount of the reward.

### itemId
Specific item identifier for unique rewards.

### rarity
Rarity level for valuable rewards.

### isGuaranteed
Whether this reward is always given or part of a random pool.

### weight
Probability weight for random reward selection.

### conditions
Eligibility requirements for the reward.

### presentation
Visual and audio presentation settings for reward delivery.

## Mechanics

### Reward Types
Comprehensive reward system covering all player motivations:
- **XP**: Core progression currency
- **Cards**: Collection incentives
- **Resources**: Economic gameplay
- **Energy**: Action economy
- **Cosmetics**: Personalization
- **Titles**: Social status
- **Currency**: Premium purchases

### Distribution Methods
Rewards are granted through various systems:
- Battle victories
- Quest completions
- Achievement unlocks
- Daily/weekly rewards
- Event participation
- Level progression

### Random Rewards
For non-guaranteed rewards, weight determines probability in random pools.

## Engine Integration

### Client Implementation
- Reward notification system
- Visual reward animations
- Inventory updates
- Progress tracking

### Server Implementation
- Reward validation and distribution
- Anti-cheat measures
- Inventory management
- Analytics tracking

### Presentation
Rich reward experiences:
- Celebration animations
- Sound effects
- Special text messages
- Particle effects

## Examples

### XP Reward
```json
{
  "rewardId": "battle-victory-xp",
  "type": "xp",
  "amount": 100,
  "isGuaranteed": true,
  "presentation": {
    "animation": "xp_burst",
    "sound": "level_up"
  },
  "schemaVersion": 1
}
```

### Card Reward
```json
{
  "rewardId": "quest-card-reward",
  "type": "card",
  "subtype": "pack",
  "itemId": "common-pack",
  "amount": 1,
  "rarity": "common",
  "isGuaranteed": true,
  "presentation": {
    "animation": "card_flip",
    "text": "New card acquired!"
  },
  "schemaVersion": 1
}
```

### Resource Reward
```json
{
  "rewardId": "mine-production",
  "type": "resource",
  "subtype": "gold",
  "amount": 50,
  "isGuaranteed": true,
  "presentation": {
    "animation": "coin_rain",
    "sound": "coins"
  },
  "schemaVersion": 1
}
```

### Random Reward Pool
```json
{
  "rewardId": "event-reward-1",
  "type": "card",
  "subtype": "specific",
  "itemId": "fire-elemental",
  "amount": 1,
  "rarity": "rare",
  "isGuaranteed": false,
  "weight": 10,
  "conditions": [
    {
      "type": "level",
      "value": "10",
      "operator": "greater"
    }
  ],
  "presentation": {
    "animation": "rare_card_glow",
    "sound": "rare_drop"
  },
  "schemaVersion": 1
}
```

## Validation Rules
- rewardId must be unique
- Amount must be positive
- ItemId required for card and cosmetic types
- Weight only applicable for non-guaranteed rewards
- Conditions must use valid types and operators

## Related Schemas
- [Quest Schema](quest-schema.md) - Quest rewards
- [Achievement Schema](achievement-schema.md) - Achievement rewards
- [Event Schema](event-schema.md) - Event rewards
- [Tutorial Schema](tutorial-schema.md) - Tutorial rewards