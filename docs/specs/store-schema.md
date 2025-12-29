# Store Schema

## Overview
The Store Schema defines all in-app purchase (IAP) products, bundles, subscriptions, and monetization offerings in Sovereign Territories. It supports regional pricing, promotional offers, A/B testing, and receipt validation for fraud prevention.

## Key Fields

### productId
Unique product identifier matching platform IDs (App Store, Google Play).

### name
Display name shown in the store UI.

### description
Product description highlighting value proposition.

### type
Product category:
- **consumable**: One-time use (gems, energy refills)
- **subscription**: Recurring purchase (VIP membership)
- **bundle**: Multiple items (starter pack, limited-time offer)
- **cosmetic**: Visual items (skins, themes, soundtracks)
- **currency**: Hard currency (gems)
- **starter_pack**: New player bundle

### category
Store organization:
- **currency**: Gem packs
- **energy**: Energy refills
- **cards**: Card packs
- **vip**: VIP subscriptions
- **cosmetics**: Skins, themes, soundtracks
- **boosters**: XP boosters, production multipliers
- **limited_time**: Seasonal offers

### price
Pricing structure:
- **usd**: Base price in USD
- **regional**: Regional pricing (EUR, JPY, GBP, etc.)

### contents
Bundle items:
- **itemType**: gems, energy, cards, cosmetics
- **itemId**: Specific item (e.g., 'legendary-card-pack')
- **quantity**: Amount included

### bonus
First-time buyer or promotional bonuses:
- **percentage**: Extra percentage (e.g., 50 = +50% gems)
- **description**: Bonus text ('+50% gems on first purchase!')

### availability
Purchase constraints:
- **isAvailable**: Currently purchasable
- **startTime/endTime**: Limited-time offers
- **purchaseLimit**: Max purchases per player
- **levelRequirement**: Minimum level to unlock

### subscription
Recurring purchase settings:
- **duration**: weekly, monthly, quarterly, yearly
- **renewalPrice**: Price for subsequent renewals
- **benefits**: VIP perks, daily gems, exclusive access

### visual
Store presentation:
- **icon**: Product icon asset
- **banner**: Featured banner
- **badge**: new, popular, best_value, limited_time, vip_exclusive

### platformIds
Platform-specific identifiers:
- **ios**: com.sovereign.gems.500
- **android**: com.sovereign.gems.500
- **steam**: 123456 (if applicable)

### analytics
Tracking and A/B testing:
- **trackingId**: Analytics identifier
- **cohort**: Player segment
- **abTestVariant**: Pricing test variant

### promotion
Discount and promotional settings:
- **discountPercentage**: Discount amount (0-100%)
- **originalPrice**: Pre-discount price
- **promoText**: Promotional message

### receiptValidation
Anti-fraud measures:
- **requiresValidation**: Server-side validation required
- **validationEndpoint**: Server API for receipt verification

## Mechanics

### Purchase Flow
1. **Client**: Display product in store UI
2. **Player**: Initiate purchase
3. **Platform**: Process payment (Apple/Google)
4. **Receipt**: Platform returns receipt
5. **Validation**: Server validates receipt
6. **Fulfillment**: Grant items to player
7. **Analytics**: Log purchase event

### Regional Pricing
- **Auto-Conversion**: Base USD price converted to local currency
- **Manual Pricing**: Custom pricing per region for optimization
- **Price Tiers**: Apple (Tier 1-87), Google (micro-transactions)

### First-Time Buyer Bonus
- **+100% Value**: Double gems on first purchase (e.g., 500 → 1000 gems)
- **One-Time Flag**: Track in player-schema to prevent abuse
- **UI Highlight**: Show 'First Purchase Bonus!' badge

### Limited-Time Offers
- **Countdown Timer**: Display time remaining
- **Push Notifications**: Alert when offer is ending
- **Purchase Limit**: Max 1-3 purchases per player

### Subscription Management
- **Auto-Renewal**: Platform handles renewal
- **Grace Period**: 3-day grace period for failed payments
- **Cancellation**: Player can cancel anytime
- **Benefits**: VIP perks persist until expiration

## Engine Integration

### Unity IAP
- **Unity Purchasing**: Cross-platform IAP library
- **Product Catalog**: Define products in Unity Editor
- **Receipt Validation**: Unity receipt validation service

### Platform Integration
- **iOS**: StoreKit for App Store purchases
- **Android**: Google Play Billing Library
- **Steam**: Steamworks SDK (if PC release)

### Server-Side Validation
- **Apple**: POST receipt to Apple's verifyReceipt endpoint
- **Google**: Use Google Play Developer API
- **Signed Receipts**: Verify signature to prevent spoofing

### Analytics
- **Purchase Events**: Log to session-schema
- **Revenue Tracking**: Track LTV (lifetime value)
- **Cohort Analysis**: Day 1, Day 7, Day 30 revenue
- **A/B Testing**: Test price points (e.g., $4.99 vs $5.99)

## Examples

### Gem Pack (Consumable)
```json
{
  "productId": "com.sovereign.gems.500",
  "name": "500 Gems",
  "description": "Purchase 500 gems for faster progression",
  "type": "consumable",
  "category": "currency",
  "price": {
    "usd": 4.99,
    "regional": {
      "EUR": 4.49,
      "JPY": 500,
      "GBP": 3.99
    }
  },
  "contents": [
    {
      "itemType": "gems",
      "quantity": 500
    }
  ],
  "bonus": {
    "enabled": true,
    "percentage": 100,
    "description": "+100% gems on first purchase!"
  },
  "availability": {
    "isAvailable": true,
    "purchaseLimit": null,
    "levelRequirement": 1
  },
  "visual": {
    "icon": "ui/store/gems_500",
    "badge": "popular"
  },
  "platformIds": {
    "ios": "com.sovereign.gems.500",
    "android": "com.sovereign.gems.500"
  },
  "receiptValidation": {
    "requiresValidation": true,
    "validationEndpoint": "/api/validate_receipt"
  },
  "schemaVersion": 1
}
```

### VIP Subscription
```json
{
  "productId": "com.sovereign.vip.monthly",
  "name": "VIP Membership",
  "description": "Unlock VIP benefits: daily gems, energy refills, exclusive content",
  "type": "subscription",
  "category": "vip",
  "price": {
    "usd": 9.99,
    "regional": {
      "EUR": 8.99,
      "JPY": 1000
    }
  },
  "subscription": {
    "duration": "monthly",
    "renewalPrice": 9.99,
    "benefits": [
      "100 daily gems",
      "2x energy refill speed",
      "VIP Level 3 perks",
      "Exclusive chat badges",
      "Alliance bonuses"
    ]
  },
  "availability": {
    "isAvailable": true,
    "levelRequirement": 5
  },
  "visual": {
    "icon": "ui/store/vip_crown",
    "banner": "ui/store/vip_banner",
    "badge": "best_value"
  },
  "platformIds": {
    "ios": "com.sovereign.vip.monthly",
    "android": "com.sovereign.vip.monthly"
  },
  "schemaVersion": 1
}
```

### Starter Pack (Bundle)
```json
{
  "productId": "com.sovereign.starter.pack",
  "name": "Beginner's Blessing",
  "description": "Kickstart your journey with gems, cards, and energy!",
  "type": "bundle",
  "category": "limited_time",
  "price": {
    "usd": 1.99
  },
  "contents": [
    {
      "itemType": "gems",
      "quantity": 500
    },
    {
      "itemType": "energy",
      "quantity": 200
    },
    {
      "itemType": "cards",
      "itemId": "rare-card-pack",
      "quantity": 3
    },
    {
      "itemType": "cosmetics",
      "itemId": "starter-banner",
      "quantity": 1
    }
  ],
  "availability": {
    "isAvailable": true,
    "purchaseLimit": 1,
    "levelRequirement": 1
  },
  "visual": {
    "icon": "ui/store/starter_pack",
    "badge": "new"
  },
  "promotion": {
    "isPromoted": true,
    "discountPercentage": 80,
    "originalPrice": 9.99,
    "promoText": "80% OFF - New Players Only!"
  },
  "schemaVersion": 1
}
```

### Limited-Time Seasonal Offer
```json
{
  "productId": "com.sovereign.holiday.2025",
  "name": "Holiday Mega Bundle",
  "description": "Celebrate with exclusive holiday items!",
  "type": "bundle",
  "category": "limited_time",
  "price": {
    "usd": 19.99
  },
  "contents": [
    {
      "itemType": "gems",
      "quantity": 2000
    },
    {
      "itemType": "cards",
      "itemId": "legendary-card",
      "quantity": 1
    },
    {
      "itemType": "cosmetics",
      "itemId": "holiday-theme-2025",
      "quantity": 1
    }
  ],
  "availability": {
    "isAvailable": true,
    "startTime": 1640995200,
    "endTime": 1641600000,
    "purchaseLimit": 3
  },
  "visual": {
    "icon": "ui/store/holiday_bundle",
    "banner": "ui/store/holiday_banner",
    "badge": "limited_time"
  },
  "promotion": {
    "isPromoted": true,
    "promoText": "Limited Time - Holiday Sale!"
  },
  "schemaVersion": 1
}
```

## Best Practices

### Pricing Strategy
- **Tiered Pricing**: Offer 3-5 price points ($0.99, $4.99, $9.99, $19.99, $49.99)
- **Value Scaling**: Higher tiers offer better $/gem ratio (encourage larger purchases)
- **Regional Optimization**: Adjust prices for purchasing power (lower in emerging markets)
- **A/B Testing**: Test price points, measure conversion and revenue

### Promotional Offers
- **First-Time Buyer**: 2x value on first purchase (high conversion)
- **Limited-Time**: Weekly sales to create urgency
- **Seasonal**: Holiday bundles with exclusive content
- **Level-Gated**: Unlock better offers at higher levels

### Subscription Benefits
- **Daily Rewards**: Daily gems, energy to encourage logins
- **Passive Bonuses**: 2x production speed, 1.5x XP gain
- **Exclusive Content**: VIP-only cards, skins, themes
- **Social Perks**: Alliance bonuses, chat badges

### Anti-Fraud
- **Receipt Validation**: Always validate on server
- **Purchase Tracking**: Detect duplicate receipts
- **Refund Monitoring**: Alert on high refund rates
- **Rate Limiting**: Prevent rapid-fire purchases (bots)

### Analytics
- **Conversion Funnel**: Store view → Product click → Purchase → Fulfillment
- **ARPU/ARPPU**: Average revenue per user/paying user
- **Whale Tracking**: Top 1% spenders, personalized offers
- **Cohort LTV**: Lifetime value by install date

## Validation Rules
- productId must match platform IDs exactly
- price.usd must be positive
- Subscription duration must be valid enum
- availability.startTime < endTime (if limited-time)
- purchaseLimit must be positive integer or null
- Regional prices must use valid ISO currency codes

## Related Schemas
- [Resource Schema](resource-schema.md) - Currency and items granted
- [Player Schema](player-schema.md) - Purchase history tracking
- [Session Schema](session-schema.md) - Purchase event logging
- [Progression Schema](progression-schema.md) - VIP level unlocks
