Alliance Schema — notes and governance

Purpose
- Alliances are shared social entities with treasury, events, and governance.

Key fields
- `members` array includes role and joinedAt.
- `treasury` and immutable `bankHistory` for auditing and moderation.
- `allianceTech` provides shared bonuses and levels.

Governance
- Provide role-based APIs (leader/officer/member) for invites, withdrawals, and event management.
- Consider multi-signature withdrawal rules for high-value treasury operations.

Events & wars
- `events` list scheduled alliance activities; emit events to members and record contribution tallies.
- `warDeclarations` should have time windows and replenishment costs to prevent spam.

Scaling
- Shard alliance data by `allianceId` and store histories in append-only partitions.
- Cache frequently-read alliance summaries.
