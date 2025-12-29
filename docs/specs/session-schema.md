# Session Schema

## Overview
The Session Schema tracks player sessions for analytics, telemetry, engagement metrics, and retention analysis. It ensures GDPR compliance while providing actionable data for live ops, balance adjustments, and feature development.

## Key Fields

### sessionId
Unique identifier for the session (UUID).

### playerId
Player who owns this session (linked to player-schema).

### deviceId
Anonymized device identifier for multi-device tracking.

### platform
Platform type: iOS, Android, Windows, macOS, Web.

### clientVersion
Client version (e.g., '1.2.3') for correlating issues and feature rollouts.

### schemaVersion
Schema version for migrations and backwards compatibility.

### region
Geographic region (US, EU, APAC) for latency analysis and regional content.

### startTime / endTime / duration
Session lifecycle timestamps (Unix) and total duration in seconds.

### status
Current state:
- **active**: Session in progress
- **paused**: Backgrounded or minimized
- **ended**: Normal termination
- **crashed**: Abnormal termination

### metrics
Session-level aggregates:
- **battlesPlayed**: Combat engagement
- **cardsCollected**: Collection progression
- **goldEarned / gemsSpent**: Economy tracking
- **screensVisited**: UI navigation patterns
- **actionsPerformed**: Total interactions (clicks, drags, swipes)
- **errorCount**: Quality metrics

### events
Detailed event log for replay and analysis:
- **battle_start, battle_end**: Combat tracking
- **card_combined, card_split**: Collection management
- **purchase**: Monetization events
- **auction_listing**: Economy activity
- **match_found, match_result**: Matchmaking performance
- **resource_produced**: AFK economy validation
- **building_destroyed**: Combat outcomes

### performance
Technical metrics:
- **avgFPS / minFPS / maxFPS**: Frame rate tracking
- **loadTimes**: Screen load duration (target < 2 seconds)
- **memoryUsage**: Peak RAM usage (mobile optimization)
- **networkLatency**: Server response time (target < 100ms)

### engagement
Behavioral metrics:
- **tutorialProgress**: FTUE completion (0.0 to 1.0)
- **dailyQuestsCompleted**: Daily engagement
- **socialInteractions**: Community activity
- **timeInBattle / timeInMenu**: Activity distribution
- **afkTime**: Background activity detection

### monetization
Revenue tracking:
- **purchasesMade**: IAP count
- **totalRevenue**: USD generated (server-side validation)
- **adsViewed**: Rewarded ad engagement (if applicable)
- **vipLevel**: Monetization tier

### funnel
Key conversion milestones:
- **ftueCompleted**: Tutorial completion
- **firstBattle**: First combat engagement
- **firstPurchase**: Monetization conversion
- **pvpUnlocked**: Reached Level 10
- **allianceJoined**: Social integration

### consent
GDPR compliance flags:
- **telemetryConsent**: Analytics opt-in
- **marketingConsent**: Promotional emails opt-in
- **crashReportingConsent**: Error reporting opt-in
- **consentTimestamp**: When consent was granted
- **gdprCompliant**: Session adheres to regulations

### errors
Error tracking:
- **errorType**: crash, exception, network, validation, timeout
- **message**: Error description (sanitized PII)
- **stackTrace**: Debug information (server-only)
- **severity**: low, medium, high, critical

### abTests
Active A/B test variants (e.g., `balance_v2: variant_a`).

### retention
Player lifecycle metrics:
- **daysSinceInstall**: Cohort analysis
- **daysSinceLastSession**: Re-engagement tracking
- **totalSessions**: Engagement frequency
- **isChurned**: Inactivity flag (>7 days)

## Mechanics

### Session Lifecycle
1. **Start**: Create session record on app launch
2. **Active**: Log events, track metrics
3. **Pause**: Background/minimize (save state)
4. **Resume**: Restore from pause
5. **End**: Normal termination, flush data to server
6. **Crash**: Abnormal termination, retry upload on next launch

### Event Logging
Minimum events (from Section 12.5):
- `battle_start`, `battle_end`, `battle_action`
- `card_combined`, `card_split`
- `purchase`, `auction_listing`
- `match_found`, `match_result`
- `resource_produced`, `building_destroyed`
- `vip_purchase`

### Performance Monitoring
- **FPS Tracking**: Sample every second, alert if < 30 FPS for > 5 seconds
- **Load Time Tracking**: Measure scene transitions, target < 2 seconds
- **Memory Profiling**: Alert if > 1GB on mobile devices
- **Network Monitoring**: Track latency, retry failed requests

### GDPR Compliance
- **Opt-In**: Explicit consent before tracking
- **Opt-Out**: Stop telemetry if consent revoked
- **Data Deletion**: Remove sessions on player account deletion
- **Anonymization**: No PII in logs (device ID hashed, no email/name)

## Engine Integration

### Unity Implementation
- **Unity Analytics**: Basic telemetry (install, retention, revenue)
- **Custom Events**: Game-specific tracking via Nakama RPCs
- **Performance Profiler**: FPS, memory, load time tracking
- **Crash Reporting**: Unity Cloud Diagnostics or Sentry

### Nakama Integration
- **Session Storage**: Store sessions in `sessions` collection
- **RPC Endpoints**: Custom event logging (e.g., `log_battle_event`)
- **Real-Time Updates**: WebSocket for live session monitoring
- **Server-Side Validation**: Verify event integrity, prevent spoofing

### Data Pipeline
1. **Client**: Log events locally (offline support)
2. **Upload**: Batch send events every 30 seconds or on session end
3. **Server**: Validate, enrich (server timestamp, region), store
4. **Analytics**: Export to BigQuery/Redshift for dashboards
5. **Dashboards**: Grafana/Tableau for live ops

### A/B Testing
- **Feature Flags**: Server-side flags for variants (e.g., `balance_v2: variant_a`)
- **Randomization**: Hash player ID for consistent assignment
- **Metrics**: Track win rates, retention, revenue by variant
- **Rollout**: Gradual rollout (10% → 50% → 100%)

## Examples

### Basic Session
```json
{
  "sessionId": "session-abc123",
  "playerId": "player-456",
  "deviceId": "device-hashed-789",
  "platform": "ios",
  "clientVersion": "1.2.3",
  "schemaVersion": 1,
  "region": "US",
  "startTime": 1640995200,
  "endTime": 1640998800,
  "duration": 3600,
  "status": "ended",
  "metrics": {
    "battlesPlayed": 5,
    "cardsCollected": 3,
    "goldEarned": 500,
    "gemsSpent": 0,
    "screensVisited": ["menu", "codex", "battle", "map"],
    "actionsPerformed": 120,
    "errorCount": 0
  },
  "consent": {
    "telemetryConsent": true,
    "marketingConsent": false,
    "crashReportingConsent": true,
    "consentTimestamp": 1640990000,
    "gdprCompliant": true
  }
}
```

### Session with Events
```json
{
  "sessionId": "session-def456",
  "playerId": "player-789",
  "platform": "android",
  "clientVersion": "1.2.3",
  "schemaVersion": 1,
  "startTime": 1641000000,
  "status": "active",
  "events": [
    {
      "eventId": "event-001",
      "eventType": "battle_start",
      "timestamp": 1641000100,
      "metadata": {
        "battleId": "battle-123",
        "type": "pvp"
      }
    },
    {
      "eventId": "event-002",
      "eventType": "purchase",
      "timestamp": 1641000500,
      "metadata": {
        "productId": "gems-pack-500",
        "amount": 4.99,
        "currency": "USD"
      }
    }
  ],
  "consent": {
    "telemetryConsent": true,
    "marketingConsent": true,
    "crashReportingConsent": true,
    "gdprCompliant": true
  }
}
```

### Session with Crash
```json
{
  "sessionId": "session-ghi789",
  "playerId": "player-101",
  "platform": "windows",
  "clientVersion": "1.2.2",
  "schemaVersion": 1,
  "startTime": 1641005000,
  "endTime": 1641006000,
  "duration": 1000,
  "status": "crashed",
  "errors": [
    {
      "errorId": "error-crash-001",
      "errorType": "crash",
      "message": "NullReferenceException in BattleController",
      "stackTrace": "at BattleController.Update() line 45",
      "timestamp": 1641006000,
      "severity": "critical"
    }
  ],
  "consent": {
    "telemetryConsent": true,
    "crashReportingConsent": true,
    "gdprCompliant": true
  }
}
```

## Best Practices

### Data Privacy
- **No PII**: Never log email, username, real name
- **Anonymize**: Hash device IDs, sanitize stack traces
- **Consent**: Always check consent flags before logging
- **Retention**: Delete sessions after 2 years (or GDPR request)

### Performance
- **Batch Uploads**: Send events in batches, not individually
- **Compression**: GZIP event payloads before upload
- **Offline Support**: Queue events locally, upload when online
- **Sampling**: Sample events for high-volume players (>1000 events/session)

### Analytics
- **Dashboards**: Real-time dashboards for DAU, retention, revenue
- **Alerts**: Alert on critical errors (crash rate > 1%, FPS < 30)
- **Cohorts**: Track Day 1, Day 7, Day 30 retention
- **Funnels**: FTUE → First Battle → First Purchase → PvP Unlock

### A/B Testing
- **Hypothesis**: Clear hypothesis (e.g., "Reducing card costs increases retention")
- **Metrics**: Pre-define success metrics (e.g., Day 7 retention +5%)
- **Sample Size**: Run until statistical significance (p < 0.05)
- **Rollback**: Revert if metrics degrade

## Validation Rules
- sessionId must be unique
- playerId must reference valid player
- startTime < endTime (if session ended)
- consent flags required for GDPR compliance
- events must have unique eventIds within session
- errors must have severity level

## Related Schemas
- [Player Schema](player-schema.md) - Player identity
- [Battle Schema](battle-schema.md) - Battle event details
- [Resource Schema](resource-schema.md) - Economy events
- [Achievement Schema](achievement-schema.md) - Milestone tracking
