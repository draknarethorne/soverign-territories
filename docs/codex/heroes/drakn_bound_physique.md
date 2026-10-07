# Sovereign Territories — Hero Card Roster: Mythic Tier (ST-011 – ST-020)
## Male Heroes Character Architecture & Physical Specification Matrix (Schema-Aligned)

---

## 1. Master Bloodline Architecture: Shared Baseline vs. Elemental Phenotype

Aligning with the `HERO_*.json` schema structure established by the Transcendent tier, the Mythic Male Heroes represent distinct humanoid races, martial bloodlines, and combat roles. 

### The Foundational Male Core (Universal Studio Setup)
* **Master Studio Base Uniform:** Minimalist athletic compression combat-brief underlayer (`data/art/wardrobe/underlayers/briefs/athletic-compression-brief.json`), signature low-profile combat greaves/barefoot wraps (`defaultFootwear`), satin-matte/light-specular finish (`defaultSheen`).
* **Render Standards:** Master Canvas `944 × 1104` with studio cream background padding (`#F5F0E6`), scaling downstream to `1080 × 1350` (4:5) for mobile UI card frames.
* **Structural Archetypes:** Broad shoulder-to-waist V-taper, defined functional core without cartoonish distortion, clear masculine neck and jawline geometry, grounded combat-ready A-pose.

### The Elemental Glamour Phenotype (Individualized)
* Each hero possesses fully specified facial planes, eye coloration, skin undertone, hair styling, accent metals, and strict negative arrays to prevent cross-contamination in diffusion passes.

---

## 2. Master Card Registry & Phenotype Alignment

| Card ID | Hero Name | Element | Class | Race Presentation | Primary Colors & Metals | Eye / Hair Phenotype | Physical Preset Category |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **ST-011** | Draknare Thorne | Darkness | Shadow Knight | Human | Obsidian, Void Violet, Smoked Chrome | Dark Violet Irises / Obsidian-Black Hair | Heavy Armor / Imposing Commander |
| **ST-012** | Ignis Emberstride | Fire | Warrior | Human | Molten Crimson, Cinder Brass, Gold | Amber-Gold / Copper-Brown Hair | Lean Martial / Greatsword Striker |
| **ST-013** | Nizaras Featherstone | Grass | Rogue | Wood Elf | Forest Moss, Living Bronze, Bark | Leaf-Green / Deep Chestnut-Brunette | Wiry / Woodland Infiltrator |
| **ST-014** | Lyran Frostfall | Ice | Knight | High Elf | Glacial Cyan, Frosted Silver, Arctic Navy | Crystalline Frost-Blue / Silver-Platinum Hair | Statuesque / Regal Bastion |
| **ST-015** | Corin Tidewalker | Water | Beast Lord | Human | Deep Pelagic Blue, Teal, Sea-Platinum | Sea-Grey Blue / Dark Sand-Brown Hair | Taut / Pelagic Vanguard |
| **ST-016** | Hauk Hammerfell | Light | Paladin | Human | Solar Alabaster, Sun-Gold, Polished Steel | Bright Amber / Honey-Brown Hair | Heavy Armor / Unyielding Bulwark |
| **ST-017** | Torvald Stonebreaker | Earth | Berserker | Barbarian | Burnt Ochre, Granite Slate, Raw Bronze | Slate-Grey Hazel / Dark Ash-Brown Hair | Brutal / Dense Juggernaut |
| **ST-018** | Dorian Stormstrike | Lightning | Monk | Celestial | Storm Cobalt, Arc Violet, Fulgurite Silver | Luminous Azure / Pale Platinum-White Hair | Wiry / Kinetic Conduit |
| **ST-019** | Zephyr Galeheart | Wind | Warrior | High Elf | Sky Cerulean, Wind-Brass, Cloud White | Wind-Grey Cyan / Sun-Bleached Blonde Hair | Lean Martial / Aerodynamic Duelist |
| **ST-020** | Malakor Venomcaller | Poison | Assassin | Orc | Toxic Malachite, Corroded Iron, Black Steel | Acid-Yellow / Coarse Jet-Black Hair | Brutal / Coiled Stalker |

---

## 3. Individual Character JSON-Ready Specifications

### ST-011: Draknare Thorne
* **Card ID:** `HERO_DRAKNARE_THORNE`
* **Element / Class / Race:** Darkness | Shadow Knight | Human
* **Physique Profile:** Imposing athletic tank build; broad-shouldered, tall, commanding warrior posture.
* **Palette & Cosmetics:**
  * primaryColor: "Midnight Obsidian", accentColors: ["Void Violet", "Smoked Chrome"], metal: "smoked chrome"
  * eyeColor: "Intense dark violet iris with sharp black limbal ring and calculating cold specular highlight"
  * hairColor: "Obsidian-black hair, clean swept-back masculine cut"
  * skinTone: "Pale alabaster-fair complexion with cool neutral undertones, battle-hardened and unblemished"
  * eyeColorNegatives: ["blue eyes", "green eyes", "brown eyes", "amber eyes", "red eyes"]
  * skinColorNegatives: ["tanned skin", "sunburnt skin", "ruddy complexion", "warm peach skin"]
* **Physique Block:**
  * build: "Imposing athletic tank build; broad-shouldered, tall, commanding warrior posture"
  * torso: "Deep, powerful chest plate contour tapering into a disciplined waist; firm, flat athletic midsection with subtle core definition"
  * shouldersAndArms: "Broad, squared shoulders with defined deltoids; muscular forearms with prominent vascular grip definition"
  * hips: "Narrow athletic hips, disciplined masculine pelvis alignment"
  * legs: "Strong, heavily muscled legs; grounded stance capable of anchoring massive armor weight"
  * distinguishingMarks: []
  * raceAlignment: "Human patriarch presentation aligned to heavy dread-knight characteristics (imposing, tactical, unyielding authority)"

---

### ST-012: Ignis Emberstride
* **Card ID:** `HERO_IGNIS_EMBERSTRIDE`
* **Element / Class / Race:** Fire | Warrior | Human
* **Physique Profile:** Chiseled athletic striker build; functional swordsman frame with high explosive power.
* **Palette & Cosmetics:**
  * primaryColor: "Molten Crimson", accentColors: ["Cinder Brass", "Burnished Gold"], metal: "cinder brass"
  * eyeColor: "Piercing amber-gold iris with bronze limbal ring and faint incandescent flecks"
  * hairColor: "Dark copper-brown hair, textured and cropped with warm bronze undertones"
  * skinTone: "Warm bronze-tanned complexion, forge-tempered, healthy radiant warmth"
  * eyeColorNegatives: ["blue eyes", "violet eyes", "grey eyes", "green eyes"]
  * skinColorNegatives: ["pale skin", "ghostly white skin", "cold blue skin"]
* **Physique Block:**
  * build: "Chiseled athletic striker build; functional swordsman frame with high explosive power"
  * torso: "Pronounced athletic V-taper; defined pectoral plates; tight, flat core with visible upper abdominal tone and serratus cuts"
  * shouldersAndArms: "Sculpted deltoids; powerful biceps and conditioned forearms scarred from forge and fire"
  * hips: "Narrow, mobile hips built for rapid rotational torque"
  * legs: "Toned, spring-loaded thighs; athletic combat-ready forward stagger stance"
  * distinguishingMarks: []
  * raceAlignment: "Human presentation aligned to frontline vanguard warrior characteristics (forged, explosive, high stamina)"

---

### ST-013: Nizaras Featherstone
* **Card ID:** `HERO_NIZARAS_FEATHERSTONE`
* **Element / Class / Race:** Grass | Rogue | Wood Elf
* **Physique Profile:** Lithe, sinewy wood-elven scout build; ultra-lean, flexible, long-limbed silhouette.
* **Palette & Cosmetics:**
  * primaryColor: "Deep Forest Moss", accentColors: ["Living Bronze", "Weathered Bark"], metal: "living bronze"
  * eyeColor: "Sharp forest-green iris with dark umber limbal ring and gold moss specks"
  * hairColor: "Deep chestnut-brown hair, tied in a practical leather-bound scout braid"
  * skinTone: "Sun-dappled warm olive complexion, weathered by forest canopy exposure"
  * eyeColorNegatives: ["violet eyes", "blue eyes", "red eyes", "black eyes"]
  * skinColorNegatives: ["chalky white skin", "porcelain skin", "grey skin"]
* **Physique Block:**
  * build: "Lithe, sinewy wood-elven scout build; ultra-lean, flexible, long-limbed silhouette"
  * torso: "Compact, flat midriff with distinct oblique fluting; narrow waist and light, agile ribcage"
  * shouldersAndArms: "Slender, defined shoulders; corded, fibrous forearm muscles showing pronounced tendon precision"
  * hips: "Narrow, flexible hips with silent, predatory balance"
  * legs: "Long, lean runner legs with high, springy calves and agile, silent footwork"
  * distinguishingMarks: []
  * raceAlignment: "Wood elf presentation aligned to canopy tracker characteristics (whiplash agility, low body fat, corded sinew)"

---

### ST-014: Lyran Frostfall
* **Card ID:** `HERO_LYRAN_FROSTFALL`
* **Element / Class / Race:** Ice | Knight | High Elf
* **Physique Profile:** Tall, statuesque high-elven knight; aristocratic, perfectly symmetrical athletic frame.
* **Palette & Cosmetics:**
  * primaryColor: "Glacial Cyan", accentColors: ["Frosted Silver", "Deep Arctic Navy"], metal: "frosted silver"
  * eyeColor: "Crystalline frost-blue iris with deep navy limbal ring and diamond-sharp catchlights"
  * hairColor: "Lustrous silver-platinum hair, perfectly kept and straight, reaching shoulder length"
  * skinTone: "Cool alabaster-fair complexion, immaculate porcelain finish with faint frosty rim highlights"
  * eyeColorNegatives: ["brown eyes", "amber eyes", "hazel eyes", "green eyes", "red eyes"]
  * skinColorNegatives: ["tanned skin", "terracotta skin", "ruddy skin", "sunburnt skin"]
* **Physique Block:**
  * build: "Tall, statuesque high-elven knight; aristocratic, perfectly symmetrical athletic frame"
  * torso: "Firm, sculpted athletic torso with smooth contours; unblemished flat core with clean vertical line"
  * shouldersAndArms: "Square, elevated shoulders; long, powerful arms with clean, elegant muscle flow and fine wrists"
  * hips: "Narrow, elegant hips flowing into tall vertical leg lines"
  * legs: "Exceptionally long, straight, armor-ready legs with rigid, balanced posture"
  * distinguishingMarks: []
  * raceAlignment: "High elf presentation aligned to royal knight bastion characteristics (geometric balance, unyielding poise, crystalline nobility)"

---

### ST-015: Corin Tidewalker
* **Card ID:** `HERO_CORIN_TIDEWALKER`
* **Element / Class / Race:** Water | Beast Lord | Human
* **Physique Profile:** Lean, powerful swimmer build; broad back, wiry endurance frame conditioned by wind and tide.
* **Palette & Cosmetics:**
  * primaryColor: "Deep Pelagic Blue", accentColors: ["Sea-Teal", "Polished Sea-Platinum"], metal: "sea-platinum"
  * eyeColor: "Deep sea-grey blue iris with dark slate limbal ring and aqua catchlights"
  * hairColor: "Dark sand-brown hair, windblown, salt-textured, and naturally tousled"
  * skinTone: "Weathered salt-bronze tan complexion with clean, natural maritime specular highlights"
  * eyeColorNegatives: ["amber eyes", "violet eyes", "red eyes", "hazel eyes"]
  * skinColorNegatives: ["pale white skin", "ghostly pale skin", "ashen skin"]
* **Physique Block:**
  * build: "Lean, powerful swimmer build; broad back, wiry endurance frame conditioned by wind and tide"
  * torso: "Wide latissimus taper; lean, flat midriff with visible functional core definition and serratus ribs"
  * shouldersAndArms: "Mobile, rounded deltoids; strong, rope-weathered forearms with prominent grip strength"
  * hips: "Grounded athletic hips built for pitching deck balance"
  * legs: "Dense, balanced legs; grounded low stance adapted for maritime footing and beast handling"
  * distinguishingMarks: []
  * raceAlignment: "Human presentation aligned to pelagic vanguard characteristics (swimmer back, functional endurance, sea-weathered resilience)"

---

### ST-016: Hauk Hammerfell
* **Card ID:** `HERO_HAUK_HAMMERFELL`
* **Element / Class / Race:** Light | Paladin | Human
* **Physique Profile:** Massive, powerful tank physique; dense heavy-armor frame with broad structural mass.
* **Palette & Cosmetics:**
  * primaryColor: "Solar Alabaster", accentColors: ["Sun-Forged Gold", "Polished Steel"], metal: "sun-forged gold"
  * eyeColor: "Warm radiant amber iris with dark bronze limbal ring and bright golden flecks"
  * hairColor: "Warm honey-brown hair with golden-blonde streaks, short military trim"
  * skinTone: "Healthy sun-hardened cream-tan complexion, firm and clean"
  * eyeColorNegatives: ["violet eyes", "green eyes", "blue eyes", "black eyes"]
  * skinColorNegatives: ["corrupted skin", "ashen grey skin", "pale sickly skin"]
* **Physique Block:**
  * build: "Massive, powerful tank physique; dense heavy-armor frame with broad structural mass"
  * torso: "Deep barrel chest; thick, powerful abdominal wall; solid, wide waistline built for heavy plate load"
  * shouldersAndArms: "Heavily developed trapezius and deltoids; thick, hammer-wielding forearms and broad hands"
  * hips: "Wide, sturdy pelvis anchored for maximum kinetic shock absorption"
  * legs: "Heavy, pillar-like thighs and dense calves anchored in a wide, immovable stance"
  * distinguishingMarks: []
  * raceAlignment: "Human presentation aligned to holy bastion characteristics (unshakeable mass, dense muscle wall, radiant vanguard authority)"

---

### ST-017: Torvald Stonebreaker
* **Card ID:** `HERO_TORVALD_STONEBREAKER`
* **Element / Class / Race:** Earth | Berserker | Barbarian
* **Physique Profile:** Massive, raw-boned barbarian powerhouse; thick heavy frame with colossal functional mass.
* **Palette & Cosmetics:**
  * primaryColor: "Deep Burnt Ochre", accentColors: ["Granite Slate", "Raw Ancient Bronze"], metal: "raw ancient bronze"
  * eyeColor: "Hard slate-grey hazel iris with dark charcoal limbal ring and stone-brown flecks"
  * hairColor: "Coarse dark ash-brown hair, thick, unkempt, and bound with raw leather cords"
  * skinTone: "Harshly weathered ruddy-tan complexion, scarred from mountain exposure and rockfall"
  * eyeColorNegatives: ["violet eyes", "blue eyes", "bright green eyes", "golden eyes"]
  * skinColorNegatives: ["pale porcelain skin", "soft ivory skin", "unblemished smooth skin"]
* **Physique Block:**
  * build: "Massive, raw-boned barbarian powerhouse; thick heavy frame with colossal functional mass"
  * torso: "Wide, dense ribcage; thick powerlifter abdominal wall; massive oblique slabs and heavy chest"
  * shouldersAndArms: "Massive neck and bull traps merging into dense shoulders; heavy, rock-crushing forearms"
  * hips: "Broad, heavy-boned hips supporting immense physical torque"
  * legs: "Huge, tree-trunk thighs and dense calves capable of lunging through shattered bedrock"
  * distinguishingMarks: ["faint battle scars across chest and left shoulder"]
  * raceAlignment: "Barbarian presentation aligned to primal mountain juggernaut characteristics (thick skeletal density, raw kinetic power, heavy mass)"

---

### ST-018: Dorian Stormstrike
* **Card ID:** `HERO_DORIAN_STORMSTRIKE`
* **Element / Class / Race:** Lightning | Monk | Celestial
* **Physique Profile:** Hyper-conditioned celestial martial artist build; ultra-dense, razor-defined kinetic silhouette.
* **Palette & Cosmetics:**
  * primaryColor: "Storm Cobalt", accentColors: ["Arc Violet", "Fulgurite Silver"], metal: "fulgurite silver"
  * eyeColor: "Luminous electric-blue iris with glowing silver limbal ring and kinetic arc filaments"
  * hairColor: "Pale platinum-white hair with faint azure-violet highlights, cropped close"
  * skinTone: "Luminous celestial-alabaster complexion, flawless, reflecting faint arc-light sheen"
  * eyeColorNegatives: ["brown eyes", "hazel eyes", "dark eyes", "yellow eyes"]
  * skinColorNegatives: ["muddy skin", "tanned skin", "ruddy red skin"]
* **Physique Block:**
  * build: "Hyper-conditioned celestial martial artist build; ultra-dense, razor-defined kinetic silhouette"
  * torso: "Carved, tight midriff with deep serratus contours and chiseled abdominal plates; narrow waist"
  * shouldersAndArms: "Striated deltoids and triceps; calloused, energized iron fists with blue specular energy trace"
  * hips: "Tight, narrow hips aligned for instantaneous directional change"
  * legs: "Tightly coiled athletic legs; light spring-loaded feet poised on balls of the toes"
  * distinguishingMarks: []
  * raceAlignment: "Celestial presentation aligned to barehanded kinetic conduit characteristics (zero body fat, wire-taut muscle fibers, electric stillness)"

---

### ST-019: Zephyr Galeheart
* **Card ID:** `HERO_ZEPHYR_GALEHEART`
* **Element / Class / Race:** Wind | Warrior | High Elf
* **Physique Profile:** Tall, aerodynamic high-elven swordsman; lithe, graceful athletic frame with long reach.
* **Palette & Cosmetics:**
  * primaryColor: "Sky Cerulean", accentColors: ["Burnished Wind-Brass", "Cloud Ivory"], metal: "burnished wind-brass"
  * eyeColor: "Clear wind-grey cyan iris with thin platinum limbal ring and bright breezy catchlights"
  * hairColor: "Sun-bleached pale golden-blonde hair, fine-textured, flowing back in natural swept locks"
  * skinTone: "Fair ivory complexion with smooth, soft wind-brushed clarity"
  * eyeColorNegatives: ["violet eyes", "brown eyes", "black eyes", "red eyes"]
  * skinColorNegatives: ["dark brown skin", "ashen skin", "scarred rough skin"]
* **Physique Block:**
  * build: "Tall, aerodynamic high-elven swordsman; lithe, graceful athletic frame with long reach"
  * torso: "Clean, flat athletic stomach; natural narrow waist taper; smooth pectoral contours without bulk"
  * shouldersAndArms: "Broad, flexible shoulders; long slender arms with clean, rapid blade-drawing mechanics"
  * hips: "Slender, flexible hips facilitating frictionless footwork"
  * legs: "Long, elegant duelist legs; agile, open-stance footwork poised for immediate lateral steps"
  * distinguishingMarks: []
  * raceAlignment: "High elf presentation aligned to wind duelist characteristics (aerodynamic reach, parrying leverage, unforced grace)"

---

### ST-020: Malakor Venomcaller
* **Card ID:** `HERO_MALAKOR_VENOMCALLER`
* **Element / Class / Race:** Poison | Assassin | Orc
* **Physique Profile:** Dense yet agile orcish assassin build; heavy bone structure stripped down to corded predator muscle.
* **Palette & Cosmetics:**
  * primaryColor: "Toxic Malachite", accentColors: ["Corroded Dark Iron", "Blackened Steel"], metal: "corroded dark iron"
  * eyeColor: "Acidic yellow-amber iris with jagged black limbal ring and toxic green catchlights"
  * hairColor: "Coarse jet-black hair, shaved at temples with a topknot warrior crest"
  * skinTone: "Mottled slate-green orc hide, tough and leathery with a subtle oily toxic sheen"
  * eyeColorNegatives: ["blue eyes", "violet eyes", "soft brown eyes", "white eyes"]
  * skinColorNegatives: ["pale white human skin", "fair skin", "rosy skin"]
* **Physique Block:**
  * build: "Dense yet agile orcish assassin build; heavy bone structure stripped down to corded predator muscle"
  * torso: "Broad chest plate with heavy ribcage; tight, conditioned midsection held in a stalking flex"
  * shouldersAndArms: "Thick, muscular shoulders; long heavy arms with knotty forearm cords and sharp claws"
  * hips: "Heavy, low-slung hips built for powerful forward lunges"
  * legs: "Powerful, bowed stalking legs with thick calves built for explosive low-angle lunges"
  * distinguishingMarks: ["subtle ritual scarification lines along jaw and forearms"]
  * raceAlignment: "Orcish presentation aligned to predatory stalker characteristics (dense jaw/neck architecture, leathery hide, silent lethal momentum)"

---

## 4. Master Prompt Assembly Algorithm for Male Hero Studio A-Pose Plates

When the pipeline renders a master plate for any Mythic Male Hero, tokens concatenate in this strict sequence:

```text
[Master Shot & Camera]:
"Full-body master portrait, neutral studio A-pose character plate, single male hero, centered composition, front view, eye-level framing, 944x1104 resolution"

+ [Bloodline Core Physique]:
"{physique.build}, {physique.torso}, {physique.shouldersAndArms}, {physique.hips}, {physique.legs}, {physique.raceAlignment}"

+ [Elemental Phenotype & Grooming]:
"{palette.skinTone}, {palette.eyeColor}, {palette.hairColor}, sharp masculine jawline, clean groomed facial features"

+ [Underlayer Uniform & Finish]:
"wearing athletic compression combat brief in {palette.primaryColor} with {palette.metal} accents and low-profile combat wraps in {palette.primaryColor}, satin-matte finish on garments and clean specular skin highlights"

+ [Studio Environment & Lighting]:
"neutral cream studio background (#F5F0E6), directional studio key lighting with rim highlights carving muscular contours, sharp focus, 8k resolution, photorealistic masterwork creature and character design"