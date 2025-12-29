# Notification Schema

## Overview
The Notification Schema defines the structure for in-game notifications, alerts, and messages that inform players about game events, achievements, and interactions. Notifications are essential for asynchronous communication in multiplayer games.

## Key Fields

### notificationId
Unique identifier for tracking and referencing notifications.

### type
Category of notification:
- **info**: General information
- **warning**: Important alerts
- **error**: Critical issues
- **achievement**: Player accomplishments
- **trade**: Trade-related events
- **diplomacy**: Alliance/political events
- **combat**: Battle-related notifications

### title
Short, attention-grabbing headline.

### message
Detailed notification content.

### recipientId
Target player who receives the notification.

### senderId
Source of the notification (player ID or "system").

### timestamp
When the notification was created (Unix timestamp).

### expiresAt
Optional expiration time for time-sensitive notifications.

### isRead
Tracks whether the player has viewed the notification.

### actions
Array of interactive buttons, each with:
- **actionId**: Unique action identifier
- **label**: Display text
- **type**: Action category (accept, decline, view, dismiss)
- **data**: Additional context data

### metadata
Flexible object for notification-specific data.

## Mechanics

### Notification Types
Different types trigger different UI behaviors:
- Achievements show with celebration effects
- Trade notifications include accept/decline buttons
- Combat alerts highlight urgent information

### Action Handling
Actions can trigger various responses:
- Accept/decline for proposals
- View to navigate to relevant screens
- Dismiss to remove the notification

### Expiration
Notifications can auto-expire for time-sensitive information, preventing clutter.

## Engine Integration

### Client Implementation
- Notification panel displays unread notifications
- Toast popups for urgent alerts
- Action buttons trigger appropriate handlers

### Server Implementation
- Notifications queued and delivered via WebSocket
- Persistence for unread notifications
- Batch operations for cleanup

### Anti-Cheat
- Server validates notification actions
- Prevents spoofing sender information
- Tracks notification delivery

## Examples

### Trade Offer Notification
```json
{
  "notificationId": "trade-12345",
  "type": "trade",
  "title": "Trade Offer Received",
  "message": "Player AllianceX offers 50 Gold for your Iron resource",
  "recipientId": "player-789",
  "senderId": "player-456",
  "timestamp": 1640995200,
  "isRead": false,
  "actions": [
    {
      "actionId": "accept-trade",
      "label": "Accept",
      "type": "accept",
      "data": {
        "tradeId": "trade-12345"
      }
    },
    {
      "actionId": "decline-trade",
      "label": "Decline",
      "type": "decline",
      "data": {
        "tradeId": "trade-12345"
      }
    }
  ],
  "schemaVersion": 1
}
```

### Achievement Notification
```json
{
  "notificationId": "achievement-67890",
  "type": "achievement",
  "title": "First Victory!",
  "message": "Congratulations on your first battle victory! You've earned 100 XP.",
  "recipientId": "player-789",
  "senderId": "system",
  "timestamp": 1640995300,
  "isRead": false,
  "actions": [
    {
      "actionId": "view-achievement",
      "label": "View Details",
      "type": "view",
      "data": {
        "achievementId": "first-victory"
      }
    }
  ],
  "metadata": {
    "xpGained": 100,
    "achievementId": "first-victory"
  },
  "schemaVersion": 1
}
```

### Diplomacy Notification
```json
{
  "notificationId": "diplomacy-11111",
  "type": "diplomacy",
  "title": "Alliance Invitation",
  "message": "The Terran Empire invites you to join their alliance",
  "recipientId": "player-789",
  "senderId": "alliance-terran-empire",
  "timestamp": 1640995400,
  "expiresAt": 1641081800,
  "isRead": false,
  "actions": [
    {
      "actionId": "join-alliance",
      "label": "Join",
      "type": "accept",
      "data": {
        "allianceId": "terran-empire"
      }
    },
    {
      "actionId": "decline-invitation",
      "label": "Decline",
      "type": "decline",
      "data": {
        "allianceId": "terran-empire"
      }
    }
  ],
  "schemaVersion": 1
}
```

## Validation Rules
- notificationId must be unique
- type must be from the defined enum
- timestamp must be valid Unix timestamp
- expiresAt must be after timestamp if present
- actions must have valid types

## Related Schemas
- [Trade Schema](trade-schema.md) - Trade notifications
- [Diplomacy Schema](diplomacy-schema.md) - Alliance notifications
- [Achievement Schema](achievement-schema.md) - Achievement notifications