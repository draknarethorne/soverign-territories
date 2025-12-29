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

Contribution Algorithms
- Contributions weighted by resource type: Gold (1x), Cards (2x), Time (0.5x).
- Leaderboard: Top contributors get bonuses (e.g., extra treasury share).
- Example: Player contributes 100 gold → +100 points; 5 rare cards → +200 points.
- Engine: Server calculates weekly; updates member stats.
