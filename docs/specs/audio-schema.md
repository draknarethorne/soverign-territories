# Audio Schema

## Overview
The Audio Schema defines all audio assets in Sovereign Territories, including music tracks, sound effects, ambient sounds, voiceovers, and UI feedback. It supports adaptive music, localization, accessibility features, and premium audio monetization.

## Key Fields

### audioId
Unique identifier for the audio asset.

### name
Display name shown in settings or audio galleries.

### type
Audio asset category:
- **music**: Background music tracks
- **sfx**: Sound effects for actions
- **ambient**: Environmental sounds
- **voiceover**: Tutorial and character dialogue
- **ui**: UI interaction feedback

### category
Contextual category for playback:
- **battle**: Combat music and SFX
- **menu**: Main menu and navigation
- **map**: Territory exploration
- **expedition**: Board game mode
- **campaign**: Story mode
- **victory/defeat**: Match end screens
- **card**: Card play and collection
- **building**: Construction and placement
- **notification**: Alert sounds

### assetPath
Unity Addressables reference for dynamic loading.

### duration
Audio length in seconds (for timing and transitions).

### loopable
Whether audio should loop seamlessly (music, ambient).

### loopPoints
Precise loop start/end times for gapless music loops.

### volume
Default volume (0.0 to 1.0), overridden by user settings.

### priority
Unity audio priority (0 = highest, 256 = lowest) for voice limit management.

### fadeIn/fadeOut
Smooth transitions between audio states.

### triggers
Events that activate audio playback:
- `battle_start`: Combat music begins
- `card_play`: Card placement SFX
- `victory`: Victory fanfare
- `building_destroyed`: Siege audio

### mixerGroup
Unity Audio Mixer group for volume control:
- **master**: Overall volume
- **music**: Background tracks
- **sfx**: Sound effects
- **ambient**: Environmental audio
- **ui**: Interface sounds
- **voiceover**: Tutorial and dialogue

### adaptive
Adaptive music configuration for dynamic intensity:
- Battle music layers: Calm → Tense → Intense based on HP
- Map music: Exploration → Conflict based on territory state
- Example: Add percussion layer when combat starts, string layer at low HP

### localization
Voiceover variants per region:
- `en-US`: English voiceover
- `es-ES`: Spanish voiceover
- `ja-JP`: Japanese voiceover

### accessibility
Features for inclusive audio:
- **hasSubtitles**: Display text for voiceovers
- **transcriptId**: Screen reader descriptions
- **hapticPattern**: Vibration for deaf/hard-of-hearing players
- **visualCue**: On-screen indicators (e.g., sword icon for attack SFX)

### monetization
Premium audio for pay-for-look-and-feel:
- **isPremium**: Locked behind purchase or VIP
- **unlockMethod**: VIP, gem purchase, achievement, event reward
- **price**: Gem cost for premium soundtracks

### themeId
Association with game themes (medieval, sci-fi, norse) for expansion packs.

## Mechanics

### Audio Playback
- **One-Shot**: SFX plays once (card placement, attack hit)
- **Looping**: Music and ambient loop seamlessly
- **Crossfade**: Smooth transitions between tracks (menu → battle)

### Adaptive Music
Dynamic intensity based on game state:
- **Battle**: Low intensity at full HP → High intensity at critical HP
- **Map**: Peaceful exploration → Tense conflict
- **Boss Fights**: Unique tracks with phase-based layers

### Audio Mixing
Unity Audio Mixer with separate volume sliders:
- Players control music, SFX, ambient, voiceover independently
- Master volume for overall control
- Ducking: Lower music when voiceover plays

### Accessibility
- **Subtitles**: Display voiceover text
- **Visual Cues**: On-screen icons when audio plays
- **Haptic Feedback**: Vibration patterns for critical audio (battle hits, notifications)
- **Audio Descriptions**: Screen reader narration for blind players

## Engine Integration

### Unity Implementation
- **Audio Source**: Unity components for playback
- **Audio Mixer**: Volume control and effects
- **Addressables**: Dynamic loading/unloading for memory optimization
- **Audio Settings**: Player preferences persistence

### Asset Pipeline
- **Compression**: OGG Vorbis for music, WAV for short SFX
- **Streaming**: Large music files stream from disk
- **Preload**: Critical SFX preloaded for responsiveness
- **Memory Budget**: 50MB max for loaded audio

### Performance
- **Voice Limit**: 32 simultaneous sounds (Unity default)
- **Priority System**: Important audio (voiceover, victory) overrides background
- **Distance Attenuation**: Ambient sounds fade with distance on maps

### Localization
- **Voice-Over**: Tutorial and character dialogue in 10+ languages
- **Regional Music**: Optional cultural music packs (Asian themes, European orchestral)

## Examples

### Battle Music (Adaptive)
```json
{
  "audioId": "music-battle-medieval",
  "name": "Epic Battle Theme",
  "type": "music",
  "category": "battle",
  "assetPath": "audio/music/battle_medieval_base.ogg",
  "duration": 180,
  "loopable": true,
  "loopPoints": {
    "start": 10.0,
    "end": 170.0
  },
  "volume": 0.7,
  "priority": 64,
  "fadeIn": 2.0,
  "fadeOut": 3.0,
  "mixerGroup": "music",
  "adaptive": {
    "enabled": true,
    "layers": [
      {
        "layerId": "percussion",
        "assetPath": "audio/music/battle_medieval_percussion.ogg",
        "condition": "battleState == 'active'"
      },
      {
        "layerId": "strings",
        "assetPath": "audio/music/battle_medieval_strings.ogg",
        "condition": "playerHP < 30"
      }
    ]
  },
  "themeId": "medieval",
  "schemaVersion": 1
}
```

### Card Play SFX
```json
{
  "audioId": "sfx-card-play",
  "name": "Card Play Sound",
  "type": "sfx",
  "category": "card",
  "assetPath": "audio/sfx/card_play.wav",
  "duration": 0.5,
  "loopable": false,
  "volume": 0.8,
  "priority": 128,
  "triggers": [
    {
      "event": "card_deployed",
      "delay": 0.0
    }
  ],
  "mixerGroup": "sfx",
  "accessibility": {
    "hasSubtitles": false,
    "hapticPattern": "light_tap",
    "visualCue": "card_glow"
  },
  "schemaVersion": 1
}
```

### Premium Soundtrack
```json
{
  "audioId": "music-campaign-norse-premium",
  "name": "Valhalla Symphony",
  "type": "music",
  "category": "campaign",
  "assetPath": "audio/music/valhalla_symphony.ogg",
  "duration": 240,
  "loopable": true,
  "volume": 0.75,
  "mixerGroup": "music",
  "monetization": {
    "isPremium": true,
    "unlockMethod": "purchase",
    "price": {
      "currency": "gems",
      "amount": 500
    }
  },
  "themeId": "norse",
  "tags": ["premium", "orchestral", "expansion"],
  "schemaVersion": 1
}
```

### Localized Voiceover
```json
{
  "audioId": "vo-tutorial-welcome",
  "name": "Welcome Tutorial",
  "type": "voiceover",
  "category": "menu",
  "assetPath": "audio/vo/tutorial_welcome_en.ogg",
  "duration": 5.0,
  "loopable": false,
  "volume": 1.0,
  "priority": 32,
  "mixerGroup": "voiceover",
  "localization": {
    "isLocalized": true,
    "variants": {
      "en-US": "audio/vo/tutorial_welcome_en.ogg",
      "es-ES": "audio/vo/tutorial_welcome_es.ogg",
      "ja-JP": "audio/vo/tutorial_welcome_jp.ogg"
    }
  },
  "accessibility": {
    "hasSubtitles": true,
    "transcriptId": "tutorial_welcome_transcript"
  },
  "schemaVersion": 1
}
```

## Best Practices

### Music Composition
- **Seamless Loops**: Use loop points to avoid gaps
- **Adaptive Layers**: Record separate stems for dynamic mixing
- **Theme Consistency**: Match music to visual theme (medieval = orchestral, sci-fi = synth)

### SFX Design
- **Feedback**: Every action needs audio confirmation
- **Variation**: Use 3-5 variants to avoid repetition
- **Spatial Audio**: Position SFX at source (card placement at tile position)

### Performance
- **Streaming**: Stream music > 1MB
- **Compression**: OGG Vorbis for music (quality 7), WAV for SFX < 100KB
- **Pooling**: Reuse AudioSource components

### Accessibility
- **Subtitles**: Always provide for voiceovers
- **Visual Cues**: Icon + color flash when audio plays
- **Volume Control**: Independent sliders for all mixer groups

## Validation Rules
- audioId must be unique
- assetPath must reference valid Addressables asset
- volume must be 0.0 to 1.0
- priority must be 0 to 256
- Adaptive layers must reference valid audio files
- Localized variants must cover all supported languages

## Related Schemas
- [UI Schema](ui-schema.md) - UI audio feedback
- [Battle Schema](battle-schema.md) - Combat audio triggers
- [Tutorial Schema](tutorial-schema.md) - Tutorial voiceovers
- [Notification Schema](notification-schema.md) - Alert sounds
