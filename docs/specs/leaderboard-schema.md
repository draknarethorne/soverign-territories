# Leaderboard Schema

## Overview
The Leaderboard Schema defines the structure for competitive rankings across various game modes and metrics. Leaderboards drive competition, provide goals, and distribute rewards based on performance.

## Key Fields

### leaderboardId
Unique identifier for the leaderboard.

### name
Display name shown in the UI.

### type
Leaderboard scope:
- **global**: All players worldwide
- **alliance**: Within an alliance
- **friends**: Friend list only
- **regional**: Geographic region

### category
Ranking metric:
- **pvp_elo**: PvP rating
- **conquest**: Territories conquered
- **deck_power**: Total deck strength
- **donations**: Alliance contributions
- **achievements**: Achievement points
- **expedition**: Weekly expedition scores

### period
Time period for rankings:
- **all_time**: Permanent rankings
- **season**: Seasonal competition
- **weekly**: Weekly reset
- **daily**: Daily reset

### entries
Ranked player list with scores and metadata.

### rewards
Tier-based rewards for rank placement.

### pagination
Settings for displaying large leaderboards.

### updateFrequency
How often rankings are recalculated.

## Mechanics

### Ranking System
Players are ranked based on their score in the specified category. Ties are broken by timestamp (earlier achiever ranks higher).

### Reward Tiers
Rewards are distributed in tiers:
- Top 1: Premium rewards
- Top 10: Rare rewards
- Top 100: Uncommon rewards
- All participants: Participation rewards

### Real-time Updates
Leaderboards update at specified intervals to reflect current standings.

### Seasonal Competition
Seasonal leaderboards reset periodically, allowing fresh competition and maintaining engagement.

## Engine Integration

### Client Implementation
- Leaderboard UI with scrolling
- Player rank highlighting
- Reward preview display
- Rank change indicators

### Server Implementation
- Score calculation and sorting
- Reward distribution
- Anti-cheat validation
- Pagination handling

### Performance Optimization
- Caching for frequently accessed leaderboards
- Incremental updates
- Efficient sorting algorithms

## Examples

### PvP Elo Leaderboard
```json
{
  "leaderboardId": "pvp-elo-global",
  "name": "Global PvP Rankings",
  "type": "global",
  "category": "pvp_elo",
  "period": {
    "type": "season",
    "startTime": 1640995200,
    "endTime": 1643673600,
    "seasonId": "season-2025-q1"
  },
  "entries": [
    {
      "rank": 1,
      "playerId": "player-champion",
      "displayName": "DragonSlayer99",
      "allianceId": "alliance-elite",
      "score": 2450,
      "metadata": {
        "level": 50,
        "wins": 150,
        "losses": 25,
        "winRate": 85.7,
        "streak": 12
      },
      "previousRank": 2,
      "rankChange": 1,
      "lastUpdated": 1641000000
    },
    {
      "rank": 2,
      "playerId": "player-veteran",
      "displayName": "StrategyMaster",
      "allianceId": "alliance-elite",
      "score": 2435,
      "metadata": {
        "level": 48,
        "wins": 140,
        "losses": 30,
        "winRate": 82.4,
        "streak": 5
      },
      "previousRank": 1,
      "rankChange": -1,
      "lastUpdated": 1640999500
    }
  ],
  "rewards": {
    "tiers": [
      {
        "minRank": 1,
        "maxRank": 1,
        "rewardIds": ["legendary-card-pack", "exclusive-title-champion"],
        "tierName": "Champion"
      },
      {
        "minRank": 2,
        "maxRank": 10,
        "rewardIds": ["epic-card-pack", "rare-cosmetic"],
        "tierName": "Master"
      },
      {
        "minRank": 11,
        "maxRank": 100,
        "rewardIds": ["rare-card-pack"],
        "tierName": "Expert"
      }
    ],
    "distributionTime": 1643673600
  },
  "pagination": {
    "pageSize": 50,
    "currentPage": 1,
    "totalEntries": 10000
  },
  "updateFrequency": 300,
  "isActive": true,
  "schemaVersion": 1
}
```

### Alliance Leaderboard
```json
{
  "leaderboardId": "alliance-donations",
  "name": "Top Contributors",
  "type": "alliance",
  "category": "donations",
  "period": {
    "type": "weekly",
    "startTime": 1640995200,
    "endTime": 1641600000
  },
  "entries": [
    {
      "rank": 1,
      "playerId": "player-generous",
      "displayName": "BountifulKing",
      "score": 50000,
      "metadata": {
        "level": 35
      },
      "lastUpdated": 1641000000
    }
  ],
  "rewards": {
    "tiers": [
      {
        "minRank": 1,
        "maxRank": 3,
        "rewardIds": ["alliance-bonus-pack"],
        "tierName": "Top Donor"
      }
    ],
    "distributionTime": 1641600000
  },
  "updateFrequency": 600,
  "isActive": true,
  "schemaVersion": 1
}
```

## Validation Rules
- leaderboardId must be unique
- Entries must be sorted by score (descending) and rank (ascending)
- Reward tiers must not overlap
- Update frequency must be positive
- Pagination page size must be reasonable (1-100)

## Related Schemas
- [Matchmaking Schema](matchmaking-schema.md) - PvP Elo rankings
- [Achievement Schema](achievement-schema.md) - Achievement points
- [Reward Schema](reward-schema.md) - Leaderboard rewards
- [Alliance Schema](alliance-schema.md) - Alliance leaderboards