# Quick Start - Finding Your Files

## Where Are My Cards?

```
docs/codex/base-set/cards/
```

**30 complete card JSON files** (BS-001 to BS-030):
- `hero-aria-flame-knight.json` - Epic Fire Hero (80 HP, 45 ATK, Blazing Strike ability)
- `unit-fire-soldier.json` - Common Fire Unit (30 HP, 20 ATK)
- `tactic-fireball.json` - Rare Fire Tactic (50 damage, range 5)

**110 remaining** to be generated from `COMPLETE-CARD-LIST.md`

---

## Where Are My Packs?

```
docs/products/packs/
```

**16 pack JSON files** (all complete):
- `standard-pack.json` - Main pack (1,000 Gold, 5 cards, all elements)
- `element-booster-fire.json` - Fire only (1,500 Gold, 5 cards)
- `hero-pack.json` - Hero guaranteed (3,500 Gold)
- `daily-reward-pack.json` - Daily login reward (low hero rate)
- `weekly-reward-pack.json` - Weekly milestone (guaranteed hero)
- `monthly-reward-pack.json` - Monthly grand prize (Epic+ hero + Legendary)

---

## Key Principle: No Duplication

### ✅ CORRECT (What We Have)
```
Card File (hero-aria-flame-knight.json):
{
  "cardId": "HERO_ARIA_FLAME_KNIGHT",
  "stats": {"health": 80, "attack": 45},  ← Defined ONCE here
  "abilities": [...]
}

Pack File (standard-pack.json):
{
  "cardPool": "base-set-all",  ← References pool, NOT individual cards
  "rarityDistribution": {...}  ← How to pick from pool
}
```

### ❌ WRONG (What We're Avoiding)
```
Pack File (BAD EXAMPLE):
{
  "cards": [
    {"cardId": "HERO_ARIA_FLAME_KNIGHT", "hp": 80, "attack": 45},  ← Duplication!
    {"cardId": "UNIT_FIRE_SOLDIER", "hp": 30, "attack": 20}
  ]
}
```

---

## File Counts

| Type | Location | Count | Status |
|------|----------|-------|--------|
| Cards | `codex/base-set/cards/` | 30/140 | ⚠️ In progress |
| Packs | `products/packs/` | 16/16 | ✅ Complete |
| Boxes | `products/boxes/` | 3/3 | ✅ Complete |
| Rewards | `products/rewards/` | 1/1 | ✅ Complete |

---

## View a Card

**Open**: `docs/codex/base-set/cards/hero-aria-flame-knight.json`

You'll see:
- Full stats (HP, mana, attack, defense, movement, range)
- All abilities with descriptions
- Rarity tier and points
- Lore text
- Which packs can drop this card

**Browse all cards**: `docs/codex/base-set/cards/` folder

---

## View a Pack

**Open**: `docs/products/packs/standard-pack.json`

You'll see:
- Price (1,000 Gold / 100 Gems / $0.99)
- Card pool reference (`"cardPool": "base-set-all"`)
- Rarity odds (65% Common, 25% Uncommon, etc.)
- Guarantees (slot 5 = Uncommon+)
- Pity system (Epic every 10 packs)

**Browse all packs**: `docs/products/packs/` folder

---

## Complete Documentation

- **FILE-LOCATIONS.md** - This file (quick navigation)
- **ARCHITECTURE.md** - Full system architecture (how cards/packs interact)
- **COMPLETE-CARD-LIST.md** - All 140 cards in readable tables

---

**Next Step**: Generate remaining 110 card JSON files from `COMPLETE-CARD-LIST.md`
