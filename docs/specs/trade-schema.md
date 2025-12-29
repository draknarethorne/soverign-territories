# Trade Schema — auctions and marketplace

This document explains the trade schema for player-driven economy, including direct sales and auctions.

## Key Fields

- `tradeId`, `sellerId`, `buyerId` — Identifiers for trade participants.
- `itemType`, `itemId`, `quantity` — What is being traded.
- `price` — Currency and amount.
- `tradeType` — Direct or auction.
- `auctionData` — For auctions: bids, end time.
- `status` — Active, completed, cancelled.

## Mechanics

- Tax: 10% house cut on completion.
- Escrow: Funds held until delivery.
- Restrictions: Starter cards unsellable.

## Engine Integration

- Server manages listings; escrow prevents fraud.
- Client displays market; real-time bid updates.
- Events: Auction end triggers notifications.