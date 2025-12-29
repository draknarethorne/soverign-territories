# Player Schema — notes and privacy

Purpose

- The player schema captures identity, progression, inventory, and aggregated stats for leaderboards.

Privacy & security

- Sensitive fields (email, payment receipts) must be server-only and encrypted.
- PII should never be sent to other players; use public profiles with sanitized views.

Important fields

- `playerId`, `username`, `createdAt` — canonical identifiers.
- `level`, `xp`, `vipLevel`, `vipExpiry` — progression and monetization state.
- `resources`, `cards`, `decks` — inventory; avoid sending full inventories to other players.
- `stats` — denormalized aggregates for quick leaderboard access; update via event logs for auditability.

Session management

- Maintain `sessions` for device listing and remote logout capabilities.
- Consent flags included for telemetry and marketing.

Examples

- Use `player-schema.json` for validation. Example public view (sanitized):

```json
{
  "playerId": "player-77",
  "displayName": "Red Banner",
  "level": 12,
  "elo": 1320,
  "seasonRank": 4521,
  "allianceId": "all-222"
}
```

Indexing & performance

- Index by `region`, `elo`, and `allianceId` for matchmaking and leaderboards.
- Keep heavy time-series (match logs) in append-only stores separate from main profile records.

Data Lifecycle and Retention

- **Creation**: Player profiles created on first login; initial resources allocated.
- **Updates**: Stats updated post-match; inventory via purchases/trades.
- **Deletion**: Soft delete for GDPR; retain anonymized data for analytics.
- **Retention**: Player data retained indefinitely unless requested deletion; match logs for 2 years.
- Engine: Nakama handles persistence; backups daily; encryption at rest.
