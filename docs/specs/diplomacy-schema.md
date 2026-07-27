# Diplomacy Schema

## Overview
The Diplomacy Schema defines the structure for alliances, treaties, and political relationships between players and factions. Diplomacy adds strategic depth through cooperation, trade agreements, and political maneuvering.

## Key Fields

### allianceId
Unique identifier for the alliance.

### name
Display name chosen by the alliance leader.

### leaderId
Player ID of the alliance leader who has administrative privileges.

### members
Array of alliance members, each with:
- **playerId**: Member's player identifier
- **role**: Leadership hierarchy (leader, officer, member)
- **joinedAt**: When the player joined the alliance

### treaties
Formal agreements with other alliances:
- **treatyId**: Unique treaty identifier
- **type**: Agreement category (trade, defense, non-aggression, research)
- **partnerAllianceId**: The other alliance involved
- **terms**: Specific treaty conditions
- **signedAt**: When the treaty was established
- **expiresAt**: Optional expiration date
- **status**: Current treaty state

### reputation
Numerical reputation scores (-100 to 100) with other alliances, affecting diplomacy options and trade costs.

### policies
Alliance governance settings:
- **openMembership**: Whether new players can join freely
- **taxRate**: Percentage of member resources collected as alliance tax
- **votingThreshold**: Majority required for votes to pass

### votes
Active democratic processes within the alliance:
- **voteId**: Unique vote identifier
- **proposal**: Description of what's being voted on
- **type**: Vote category (policy changes, treaties, expulsions, declarations)
- **initiatorId**: Player who started the vote
- **options**: Available voting choices
- **votes**: Current votes cast by members
- **deadline**: When voting period ends
- **status**: Vote progress state

### createdAt
When the alliance was founded.

## Mechanics

### Alliance Formation
Players can create alliances with founding members, establishing initial policies and leadership structure.

### Treaty Negotiation
Alliances can propose treaties to other alliances, requiring mutual agreement and potentially alliance votes.

### Reputation System
Actions like honoring treaties, successful trades, or betrayals affect reputation scores, influencing future diplomatic options.

### Voting System
Major alliance decisions require member votes, with configurable thresholds for different action types.

### Leadership Roles
- **Leader**: Full administrative control, can dissolve alliance
- **Officer**: Can initiate votes and manage members
- **Member**: Standard participation rights

## Engine Integration

### Client Implementation
- Alliance management UI for policies and member management
- Voting interfaces with real-time updates
- Treaty negotiation dialogs
- Reputation displays in diplomacy screens

### Server Implementation
- Alliance state persistence and synchronization
- Vote timing and resolution logic
- Treaty enforcement and expiration handling
- Reputation calculation and decay

### Anti-Cheat
- Server validates all diplomatic actions
- Prevents vote manipulation or treaty spoofing
- Tracks reputation changes for audit trails

## Examples

### New Alliance
```json
{
  "allianceId": "alliance-terran-empire",
  "name": "Terran Empire",
  "leaderId": "player-123",
  "members": [
    {
      "playerId": "player-123",
      "role": "leader",
      "joinedAt": 1640995200
    },
    {
      "playerId": "player-456",
      "role": "member",
      "joinedAt": 1640995300
    }
  ],
  "treaties": [],
  "reputation": {},
  "policies": {
    "openMembership": true,
    "taxRate": 0.1,
    "votingThreshold": 0.6
  },
  "votes": [],
  "createdAt": 1640995200,
  "schemaVersion": 1
}
```

### Treaty Negotiation
```json
{
  "allianceId": "alliance-terran-empire",
  "name": "Terran Empire",
  "leaderId": "player-123",
  "members": [
    {
      "playerId": "player-123",
      "role": "leader",
      "joinedAt": 1640995200
    }
  ],
  "treaties": [
    {
      "treatyId": "treaty-trade-001",
      "type": "trade",
      "partnerAllianceId": "alliance-zorgons",
      "terms": {
        "tradeBonus": 0.2,
        "sharedResearch": true
      },
      "signedAt": 1640995400,
      "status": "active"
    }
  ],
  "reputation": {
    "alliance-zorgons": 75
  },
  "policies": {
    "openMembership": true,
    "taxRate": 0.1,
    "votingThreshold": 0.6
  },
  "votes": [],
  "createdAt": 1640995200,
  "schemaVersion": 1
}
```

### Alliance Vote
```json
{
  "allianceId": "alliance-terran-empire",
  "name": "Terran Empire",
  "leaderId": "player-123",
  "members": [
    {
      "playerId": "player-123",
      "role": "leader",
      "joinedAt": 1640995200
    },
    {
      "playerId": "player-456",
      "role": "officer",
      "joinedAt": 1640995300
    },
    {
      "playerId": "player-789",
      "role": "member",
      "joinedAt": 1640995350
    }
  ],
  "treaties": [],
  "reputation": {},
  "policies": {
    "openMembership": true,
    "taxRate": 0.1,
    "votingThreshold": 0.6
  },
  "votes": [
    {
      "voteId": "vote-policy-tax",
      "proposal": "Increase alliance tax rate to 15% for expansion",
      "type": "policy",
      "initiatorId": "player-456",
      "options": ["Yes", "No"],
      "votes": {
        "player-123": "Yes",
        "player-456": "Yes"
      },
      "deadline": 1641081800,
      "status": "active"
    }
  ],
  "createdAt": 1640995200,
  "schemaVersion": 1
}
```

## Validation Rules
- allianceId must be unique across all alliances
- leaderId must be a valid member with "leader" role
- treaties must reference valid allianceIds
- reputation scores must be within -100 to 100 range
- votingThreshold must be between 0.5 and 1.0
- vote deadlines must be in the future for active votes

## Related Schemas
- [Player Schema](player-schema.md) - Player alliance membership
- [Trade Schema](trade-schema.md) - Alliance trade bonuses
- [Notification Schema](notification-schema.md) - Diplomacy notifications
