# Tactics System Clarification - Dual-Purpose Design

**Document Purpose**: Clarify that tactics serve TWO distinct but complementary roles  
**Status**: Critical MVP design refinement  
**Date**: December 31, 2025  
**Priority**: ⭐⭐⭐⭐⭐ **CRITICAL** - Lost in iterations, essential for auto-battle (MVP core feature)

---

## Executive Summary

**Problem Identified**:
During design iterations, **tactics system lost its dual-purpose nature**:
1. ✅ **Stat buffs/abilities** still documented (Section 2.9: "Ice Armor" +20 HP, "Charge" move+attack)
2. ❌ **AI control instructions** mentioned (Section 1: "Focus Healers", "Aggressive Push") but NOT integrated with Section 2.9

**Original Vision** (From User):
> "Tactics are intended to inform the AI on how to execute the tactic, like a tactic to heal hero, instead of heal lowest player (or whatever default heal is). Like cast magic tactic could target the boss and the fireball tactic is the spell."

**Translation**:
- **Tactic = AI Instruction + Ability**
- Example 1: **"Heal Hero" Tactic** = AI instruction (target hero instead of lowest HP) + Heal spell (restore 50 HP)
- Example 2: **"Boss Slayer" Tactic** = AI instruction (prioritize boss target) + Fireball spell (200 damage)
- Example 3: **"Guardian" Tactic** = AI instruction (move to frontline) + Taunt ability (draw aggro)

**Why This Matters for MVP**:
- **Auto-Battle** (Week 5-6) relies on AI making smart decisions
- **Without AI instructions**, all healers just heal lowest HP unit (predictable, boring)
- **With AI instructions**, same Healer card can be:
  - **Tank Healer**: "Heal Hero" tactic (keep primary hero alive)
  - **AOE Healer**: "Heal All" tactic (mass sustain)
  - **Emergency Healer**: "Heal Lowest" tactic (default, reactive)
  - **Offensive Healer**: "Attack Boss" tactic + "Heal Self" (hybrid role)

---

## Tactics System Architecture (Revised)

### Core Design Principle

**Every Tactic = AI Behavior + Gameplay Effect**

**3 Components per Tactic**:
1. **AI Instruction** (Who/what to target, when to act, movement pattern)
2. **Gameplay Effect** (Stat buff, ability, spell, status effect)
3. **Visual Feedback** (Icon, animation, tooltip showing AI logic + effect)

---

### Tactic Categories (Revised Taxonomy)

#### **Category 1: Combat AI Tactics** (Control How Units Fight)

**"Aggressive Assault"**:
- **AI Instruction**: Move toward nearest enemy, attack immediately (no defensive positioning)
- **Gameplay Effect**: +10% damage on first attack (reward aggression)
- **Use Case**: Frontline berserkers, rush strategies, glass cannon builds

**"Defensive Stance"**:
- **AI Instruction**: Stay in back row, only attack if enemy in range (don't chase)
- **Gameplay Effect**: +20% block chance while stationary
- **Use Case**: Archers, healers, protect-the-VIP strategies

**"Boss Slayer"**:
- **AI Instruction**: Prioritize highest-HP enemy (ignore weak units)
- **Gameplay Effect**: +50% damage vs enemies with 200+ HP
- **Use Case**: Tank-busting, PvE boss fights, whale-stomping in PvP

**"Swarm Tactics"**:
- **AI Instruction**: Target weakest enemy (finish kills, snowball advantage)
- **Gameplay Effect**: Gain +5% attack per kill (stacking buff, reset each battle)
- **Use Case**: AOE teams, cleanup crews, momentum strategies

---

#### **Category 2: Healing AI Tactics** (Control Who Gets Healed)

**"Heal Hero"** (USER EXAMPLE):
- **AI Instruction**: Prioritize hero with lowest HP% (not just lowest HP)
- **Gameplay Effect**: Restore 50 HP to target hero
- **Use Case**: Keep primary Epic/Legendary hero alive (they're expensive to revive)

**"Heal Lowest HP"** (Default):
- **AI Instruction**: Target any ally with lowest HP (units or heroes)
- **Gameplay Effect**: Restore 50 HP to target ally
- **Use Case**: General sustain, no preference

**"Heal All Allies"** (AOE):
- **AI Instruction**: Activate when 3+ allies below 50% HP
- **Gameplay Effect**: Restore 30 HP to ALL allies (weaker per target, but AOE)
- **Use Case**: Group sustain, prevent wipes, tank teams

**"Heal Self"** (Selfish):
- **AI Instruction**: Only heal self when below 30% HP (ignore allies)
- **Gameplay Effect**: Restore 80 HP to self (stronger single-target)
- **Use Case**: Solo tank builds, hybrid damage/healer roles

---

#### **Category 3: Movement AI Tactics** (Control Positioning)

**"Flanking Maneuver"**:
- **AI Instruction**: Move around enemy (target back row, avoid front tanks)
- **Gameplay Effect**: +2 movement range (reach back row faster)
- **Use Case**: Assassins, archers, snipe enemy healers

**"Hold the Line"**:
- **AI Instruction**: Stay in starting position (don't advance, defend tile)
- **Gameplay Effect**: +30% defense while stationary (immovable object)
- **Use Case**: Defense objectives, protect flags, tower defense

**"Kite & Shoot"**:
- **AI Instruction**: Maintain 3-tile distance from enemy (attack → retreat)
- **Gameplay Effect**: +1 attack range (shoot farther)
- **Use Case**: Archers, mobile ranged units, harass strategies

**"Charge Forward"**:
- **AI Instruction**: Move maximum distance toward enemy each turn
- **Gameplay Effect**: First attack deals +50% damage (reward aggression)
- **Use Case**: Cavalry, rush strategies, overwhelm slow enemies

---

#### **Category 4: Spell Targeting Tactics** (Control Ability Usage)

**"Fireball Barrage"** (USER EXAMPLE):
- **AI Instruction**: Cast Fireball on highest-HP enemy (boss priority)
- **Gameplay Effect**: 200 fire damage to target + 50 AOE splash (1-tile radius)
- **Mana Cost**: 25 mana (limit 2-3 casts per battle)
- **Use Case**: Boss fights, nuke high-value targets

**"Frost Nova"**:
- **AI Instruction**: Cast when 3+ enemies within 2 tiles (crowd control trigger)
- **Gameplay Effect**: 100 ice damage + slow (-1 movement for 2 turns, AOE 2-tile radius)
- **Mana Cost**: 30 mana (limit 2 casts per battle)
- **Use Case**: Crowd control, kite strategies, delay enemy advance

**"Lightning Strike"**:
- **AI Instruction**: Cast on enemy with highest attack (neutralize threats)
- **Gameplay Effect**: 150 lightning damage + 10% stun chance (skip turn)
- **Mana Cost**: 20 mana (limit 3 casts per battle)
- **Use Case**: Assassinate damage dealers, protect squishies

**"Holy Light"**:
- **AI Instruction**: Cast when ally hero below 30% HP (emergency heal)
- **Gameplay Effect**: 100 HP heal + remove 1 debuff (cleanse poison, slow, stun)
- **Mana Cost**: 20 mana (limit 3 casts per battle)
- **Use Case**: Save critical hero from death, counter debuffs

---

#### **Category 5: Status Effect Tactics** (Control Debuff Application)

**"Poison Strike"**:
- **AI Instruction**: Apply poison on first attack (no targeting preference)
- **Gameplay Effect**: 10 damage/turn for 3 turns (30 total damage over time)
- **Use Case**: Chip damage, wear down tanks, stack with other DoTs

**"Stun Bash"**:
- **AI Instruction**: Prioritize stunning highest-attack enemy (neutralize threats)
- **Gameplay Effect**: 20% chance to stun on attack (skip 1 turn)
- **Use Case**: RNG disruption (optional Arena Mode mechanic), counter DPS

**"Armor Break"**:
- **AI Instruction**: Apply debuff on tankiest enemy (reduce defense)
- **Gameplay Effect**: -30% defense for 3 turns (team benefits from debuff)
- **Use Case**: Tank-busting, coordinate with high-damage allies

---

### Tactic Attachment Rules (Integration with Star System)

**Tactic Slots = Star Rank** (No Change):
- 1★ = 1 tactic slot
- 2★ = 2 tactic slots
- 3★ = 3 tactic slots
- ... up to 8★ = 8 tactic slots

**Multi-Tactic Synergies** (NEW INSIGHT):
- **Example 1**: Healer with "Heal Hero" + "Defensive Stance"
  - AI logic: Stay in back row (Defensive Stance), heal heroes when low (Heal Hero)
  - Result: Backline support that protects VIPs
  
- **Example 2**: Mage with "Boss Slayer" + "Fireball Barrage" + "Kite & Shoot"
  - AI logic: Target boss (Boss Slayer), cast Fireball on boss (Fireball Barrage), maintain distance (Kite & Shoot)
  - Result: Anti-boss sniper mage

- **Example 3**: Knight with "Hold the Line" + "Guardian" (taunt) + "Armor Break"
  - AI logic: Stay in place (Hold the Line), draw aggro (Guardian), debuff attackers (Armor Break)
  - Result: Immovable defensive anchor

**Tactic Conflict Resolution** (Edge Cases):
- **Conflicting Movement**: "Charge Forward" + "Hold the Line" = ERROR, can't attach both (grayed out in UI)
- **Conflicting Targeting**: "Heal Hero" + "Heal Lowest HP" = "Heal Hero" takes priority (first slot = higher priority)
- **Mana Starvation**: If unit has 3 spell tactics (Fireball + Lightning + Frost), AI prioritizes based on situation (boss = Fireball, crowd = Frost, DPS = Lightning)

---

### Auto-Battle AI Decision Tree (MVP Implementation)

**Turn Flow** (With AI Tactics):
1. **Scan Battlefield** (AI checks all units, positions, HP%, mana)
2. **Check Tactic Instructions** (read attached tactics for movement/targeting priority)
3. **Evaluate Conditions** (is hero low HP? Are 3+ enemies clustered? Is boss present?)
4. **Choose Action** (move, attack, cast spell, heal)
5. **Execute** (apply gameplay effect, deduct mana, trigger animation)
6. **Repeat** for next unit

**Example Auto-Battle Turn** (3-Tactic Mage):
- **Unit**: Water Mage 4★ (80 HP, 60 Mana)
- **Tactics Attached**:
  1. "Boss Slayer" (prioritize highest-HP enemy)
  2. "Fireball Barrage" (200 damage, 25 mana)
  3. "Kite & Shoot" (maintain 3-tile distance, +1 range)
- **Battlefield State**: Boss (500 HP) at Row 3, Goblins (50 HP each) at Row 4
- **AI Decision Process**:
  1. **Check "Boss Slayer"**: Boss present? YES → Target boss
  2. **Check "Fireball Barrage"**: Mana available (60/60)? YES → Cast Fireball
  3. **Check "Kite & Shoot"**: Boss within 3 tiles? YES → Move back 1 tile after casting
  4. **Execute**: Move to Row 7 → Cast Fireball on Boss (500→300 HP) → Deduct 25 mana (60→35)
- **Result**: Mage nuked boss and repositioned safely

**Without AI Tactics** (Default Behavior):
- Same mage would just attack nearest enemy (random Goblin)
- Waste Fireball on 50 HP Goblin (overkill)
- Stand still, get swarmed by other Goblins
- **User frustration**: "Why is my mage so dumb?!"

---

### Tactic Schema Updates (JSON)

**Current Schema** (tactic-schema.json):
```json
{
  "tacticId": "heal-hero",
  "name": "Heal Hero",
  "description": "Heals the hero with the lowest HP percentage",
  "targetType": "hero",
  "priorityRules": [
    {
      "condition": "healthLow",
      "action": "heal",
      "weight": 1.0
    }
  ],
  "movementBehavior": "defensive",
  "targetingPreferences": ["weakest"],
  "cooldown": 0,
  "unlocksAtLevel": 1
}
```

**Proposed Schema Enhancement** (Add Gameplay Effect):
```json
{
  "tacticId": "heal-hero",
  "name": "Heal Hero",
  "description": "Heals the hero with the lowest HP percentage",
  "targetType": "hero",
  
  "aiInstruction": {
    "targetingLogic": "prioritize hero units with lowest HP% (not just lowest HP value)",
    "activationCondition": "hero HP < 70%",
    "movementPattern": "stay within 3 tiles of heroes (maintain support range)"
  },
  
  "gameplayEffect": {
    "effectType": "heal",
    "healAmount": 50,
    "targetCount": 1,
    "animation": "holy-light-beam",
    "soundEffect": "heal-chime.mp3"
  },
  
  "manaCost": 0,
  "cooldown": 0,
  "unlocksAtLevel": 1,
  
  "priorityRules": [
    {
      "condition": "heroHealthLow",
      "action": "heal",
      "targetType": "hero",
      "weight": 1.0
    }
  ],
  "movementBehavior": "defensive",
  "targetingPreferences": ["hero-lowest-hp-percent"],
  "schemaVersion": 2
}
```

**New Fields**:
- `aiInstruction`: Object containing targeting logic, activation conditions, movement patterns
- `gameplayEffect`: Object containing effect type, magnitude, target count, visuals
- `manaCost`: Mana required to activate (0 for passive tactics, 5-50 for active spells)

---

### Tactic Rarity & Power Scaling (Revised)

**Common Tactics** (Simple AI + Weak Effect):
- **"Heal Lowest HP"**: Basic heal, 50 HP, targets any ally (no smart targeting)
- **"Attack Nearest"**: Move toward + attack closest enemy (default melee behavior)
- **"Defensive Stance"**: Stay in back row, +10% defense (passive)

**Uncommon Tactics** (Conditional AI + Moderate Effect):
- **"Heal Hero"**: Smart targeting (hero priority), 50 HP (same healing, better logic)
- **"Boss Slayer"**: Smart targeting (high-HP priority), +30% damage vs bosses
- **"Flanking Maneuver"**: Smart movement (target back row), +1 movement

**Rare Tactics** (Complex AI + Strong Effect):
- **"Fireball Barrage"**: Boss priority + AOE spell, 200 damage + 50 splash, 25 mana
- **"Heal All Allies"**: Conditional activation (3+ low HP), 30 HP AOE heal, 20 mana
- **"Kite & Shoot"**: Distance maintenance + range boost, +1 range, auto-retreat

**Epic Tactics** (Multi-Condition AI + Very Strong Effect):
- **"Frost Nova"**: Crowd detection (3+ enemies) + AOE slow, 100 damage + slow 2 turns, 30 mana
- **"Guardian Angel"**: Emergency heal (hero <30% HP) + cleanse debuffs, 100 HP + remove poison/stun, 25 mana
- **"Armor Shatter"**: Tank detection (highest defense) + team debuff, -50% defense for 3 turns, 0 mana (passive)

**Legendary Tactics** (Advanced AI + Ultimate Effect):
- **"Phoenix Rebirth"**: Auto-resurrect (activate on death), restore 50% HP once per battle, 50 mana (pre-cast)
- **"Time Warp"**: Turn manipulation (rewind 1 turn), restore positions + HP, 60 mana (once per battle)
- **"Annihilation"**: Boss execution (activate when boss <20% HP), 500 damage nuke, 50 mana (finish move)

---

### F2P vs Whale Balance (MVP Considerations)

**F2P Players** (Common/Uncommon Tactics):
- Access to basic AI tactics ("Heal Lowest", "Attack Nearest", "Defensive Stance")
- Auto-battle works, but not optimized (predictable, reactive)
- **80% effectiveness** compared to whales (can still win with skill)

**Mid-Tier Players** (Rare/Epic Tactics):
- Access to smart AI tactics ("Heal Hero", "Boss Slayer", "Fireball Barrage")
- Auto-battle is strategic (targets bosses, saves heroes, uses AOE efficiently)
- **95% effectiveness** compared to whales (minor optimization gap)

**Whale Players** (Legendary Tactics):
- Access to ultimate AI tactics ("Phoenix Rebirth", "Time Warp", "Annihilation")
- Auto-battle is near-perfect (resurrects, executes bosses, manipulates turns)
- **100% effectiveness** (ceiling reached, skill still matters in manual PvP)

**Why This Works**:
- ✅ **F2P can compete** - Common tactics are functional, not broken
- ✅ **Whales get advantage** - Legendary tactics save time (auto-battle faster), not pure power
- ✅ **Manual PvP equalizes** - In live PvP, player skill > AI tactics (control overrides AI)
- ✅ **Monetization path** - Tactic Booster Packs ($4.99 for 5 Rare/Epic tactics)

---

### MVP Implementation Checklist (Week 3-4: Deck Building)

**Week 3: Tactic Attachment UI** (3 days)
- [ ] **Day 1**: Deck builder screen (6 slots, tactic attachment drag-and-drop)
- [ ] **Day 2**: Tactic library UI (filter by rarity, category, search by name)
- [ ] **Day 3**: Tactic tooltip (show AI instruction + gameplay effect + mana cost)

**Week 4: AI Behavior Integration** (2 days)
- [ ] **Day 1**: AI decision tree (check tactics → evaluate conditions → choose action)
- [ ] **Day 2**: Tactic activation logic (mana costs, cooldowns, conflict resolution)

**Total Time**: 5 days (fits Week 3-4 schedule) = **Within 8-week MVP timeline** ✅

---

### Tutorial Integration (Discovery-Based System)

**Achievement: "First Tactic Attachment"** (Level 3):
- **Trigger**: Player drags first tactic onto a card in deck builder
- **Reward**: +50 Gold, +1 Uncommon Tactic ("Heal Hero"), Codex entry (Tactics tab)
- **Tooltip**: "Tactics teach your AI how to fight! Try 'Heal Hero' to protect your Epic Water Mage."

**Codex Tab: "Battle Tactics"**:
- **Section 1**: What are tactics? (AI instructions + gameplay effects)
- **Section 2**: How to attach tactics (drag-and-drop, star slots)
- **Section 3**: Tactic categories (Combat, Healing, Movement, Spells, Status)
- **Section 4**: Auto-battle tips (use "Boss Slayer" for PvE, "Heal Hero" for survival)

**Contextual Tooltip** (First Auto-Battle):
```
[Tooltip appears when player taps "Auto-Battle"]:
"Auto-Battle uses your attached tactics!"
"Your Healer has 'Heal Hero' - it will prioritize keeping your Water Mage alive."
"Try different tactics to change AI behavior!"
[Dismiss]
```

---

### Competitive Analysis Update (Post-Tactics Clarification)

**Before** (Original Rating):
- **Auto-Battle Feature**: ⭐⭐⭐⭐ (4/5) - "Exists but basic AI (no customization)"

**After** (With AI Tactic System):
- **Auto-Battle Feature**: ⭐⭐⭐⭐⭐ (5/5) - "Revolutionary: Players program AI via tactic attachment, unmatched in TCG space"

**Comparison**:
- **Hearthstone**: No auto-battle (manual play only)
- **Clash of Clans**: Auto-battle exists but zero AI customization (watch replay, can't change behavior)
- **AFK Arena**: Auto-battle exists, NO tactics system (AI is fixed, players can't modify)
- **Sovereign Territories**: Auto-battle + AI tactic programming = **BEST IN CLASS**

---

## Summary

**Problem**: Tactics system lost AI control instructions during iterations  
**Solution**: Clarify that **every tactic = AI instruction + gameplay effect**  
**Examples**:
- "Heal Hero" = AI targets heroes + 50 HP heal
- "Boss Slayer" = AI targets bosses + bonus damage
- "Fireball Barrage" = AI casts on boss + 200 AOE damage

**Impact**:
- ✅ **Auto-battle becomes strategic** (not just mindless grinding)
- ✅ **Same cards, different roles** (attach "Heal Hero" vs "Heal All" = different healer strategies)
- ✅ **F2P viable** (Common tactics work, Legendary tactics optimize)
- ✅ **Competitive advantage** (best auto-battle system in TCG market)

**Next Steps**:
1. Update [game-bible.md](game-bible.md) Section 2.9 with AI instruction examples
2. Update [tactic-schema.json](../specs/tactic-schema.json) with `aiInstruction` and `gameplayEffect` fields
3. Update [tutorial-flow.md](../mvp/tutorial-flow.md) with tactic attachment teaching (achievement-based)
4. Update [mvp-scope-final.md](../mvp/mvp-scope-final.md) with Week 3-4 tactic UI + AI integration
5. Commit all changes with message: "Restore dual-purpose tactics system (AI control + effects)"

**Version**: 1.0  
**Status**: Ready for implementation  
**Date**: December 31, 2025
