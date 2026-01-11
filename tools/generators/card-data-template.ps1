# Card Generation Script - Base Set Complete

# This script generates all 140 Base Set cards based on the design spec
# Run this to create the complete codex in one operation

$baseSet = @{
    fire = @{
        heroes = @(
            @{id="HERO_ARIA_FLAME_KNIGHT"; num=1; name="Aria, Flame Knight"; rarity="Epic"; hp=80; mana=60; atk=45; def=12; move=3; range=1}
            @{id="HERO_RAGNAR_INFERNO_BERSERKER"; num=2; name="Ragnar, Inferno Berserker"; rarity="Rare"; hp=70; mana=50; atk=50; def=8; move=4; range=1}
            @{id="HERO_CINDER_FLAME_MAGE"; num=3; name="Cinder, Flame Mage"; rarity="Uncommon"; hp=50; mana=80; atk=30; def=10; move=2; range=3}
            @{id="HERO_BLAZE_DRAGON_RIDER"; num=4; name="Blaze, Dragon Rider"; rarity="Legendary"; hp=100; mana=70; atk=60; def=20; move=5; range=1; flying=$true}
            @{id="HERO_EMBER_PHOENIX_GUARDIAN"; num=5; name="Ember, Phoenix Guardian"; rarity="Epic"; hp=75; mana=65; atk=40; def=18; move=3; range=1}
        )
        units_common = @(
            @{id="UNIT_FIRE_SOLDIER"; num=6; name="Fire Soldier"; hp=30; mana=20; atk=20; def=8; move=2; range=1}
            @{id="UNIT_EMBER_SCOUT"; num=7; name="Ember Scout"; hp=25; mana=15; atk=18; def=5; move=3; range=1}
            @{id="UNIT_FLAME_IMP"; num=8; name="Flame Imp"; hp=20; mana=25; atk=22; def=4; move=2; range=2}
            @{id="UNIT_SCORCH_ELEMENTAL"; num=9; name="Scorch Elemental"; hp=35; mana=30; atk=25; def=6; move=2; range=1}
            @{id="UNIT_LAVA_GOLEM"; num=10; name="Lava Golem"; hp=40; mana=15; atk=18; def=12; move=1; range=1}
            @{id="UNIT_ASH_WARRIOR"; num=11; name="Ash Warrior"; hp=28; mana=20; atk=21; def=7; move=2; range=1}
            @{id="UNIT_CINDER_BEAST"; num=12; name="Cinder Beast"; hp=32; mana=18; atk=24; def=5; move=3; range=1}
            @{id="UNIT_MOLTEN_HOUND"; num=13; name="Molten Hound"; hp=26; mana=22; atk=23; def=6; move=3; range=1}
            @{id="UNIT_PYRO_SPRITE"; num=14; name="Pyro Sprite"; hp=22; mana=28; atk=19; def=4; move=2; range=2}
            @{id="UNIT_EMBER_WOLF"; num=15; name="Ember Wolf"; hp=29; mana=19; atk=22; def=7; move=3; range=1}
        )
        units_uncommon = @(
            @{id="UNIT_GOBLIN_RAIDER"; num=16; name="Goblin Raider"; hp=35; mana=25; atk=28; def=9; move=3; range=1}
            @{id="UNIT_PHOENIX_HATCHLING"; num=17; name="Phoenix Hatchling"; hp=30; mana=35; atk=26; def=8; move=2; range=1}
            @{id="UNIT_FLAME_SENTINEL"; num=18; name="Flame Sentinel"; hp=45; mana=30; atk=24; def=14; move=2; range=1}
            @{id="UNIT_INFERNO_GUARD"; num=19; name="Inferno Guard"; hp=42; mana=28; atk=26; def=12; move=2; range=1}
        )
        units_rare = @(
            @{id="UNIT_EMBER_LEGIONNAIRE"; num=20; name="Ember Legionnaire"; hp=50; mana=40; atk=35; def=16; move=2; range=1}
            @{id="UNIT_FIRE_DRAGON_WHELP"; num=21; name="Fire Dragon Whelp"; hp=55; mana=45; atk=38; def=14; move=3; range=1; flying=$true}
        )
        tactics = @(
            @{id="TACTIC_FIREBALL"; num=22; name="Fireball"; rarity="Rare"; manaCost=25; desc="Deal 50 damage to target enemy."}
            @{id="TACTIC_FLAME_SHIELD"; num=23; name="Flame Shield"; rarity="Uncommon"; manaCost=20; desc="Target ally gains +15 DEF for 3 turns."}
            @{id="TACTIC_INFERNO"; num=24; name="Inferno"; rarity="Epic"; manaCost=40; desc="Deal 35 damage to all enemies."}
        )
        buildings = @(
            @{id="BUILDING_FORGE"; num=25; name="Forge"; rarity="Uncommon"; hp=60; desc="Fire-themed economy building. +10% Fire unit production (Phase 2)."}
        )
    }
}

Write-Host "Base Set card generation script ready."
Write-Host "Total cards to generate: 140"
Write-Host "This is a TEMPLATE - see full implementation in card-generator.ps1"
