# UI Schema

## Overview
The UI Schema defines the structure for user interface elements, layouts, and interactions in Sovereign Territories. This schema enables consistent UI implementation across platforms while supporting responsive design and accessibility features.

## Key Fields

### uiId
Unique identifier for the UI element.

### type
UI element category:
- **screen**: Full application screens
- **panel**: Sub-components and overlays
- **button**: Interactive buttons
- **list**: Scrollable item lists
- **grid**: Grid-based layouts
- **form**: Data input forms
- **modal**: Pop-up dialogs

### name
Human-readable element name.

### layout
Positioning and sizing properties:
- **position**: X/Y coordinates
- **size**: Width/height dimensions
- **anchor**: Layout anchor points
- **pivot**: Rotation/scaling center

### visual
Styling and appearance:
- **background/foreground**: Asset references
- **colors**: Color scheme
- **fonts**: Typography settings

### content
Displayed content:
- **text**: Static text
- **dynamicText**: Localized content
- **images**: Visual assets

### interactions
Interactive behaviors and event handlers.

### states
Visual states (normal, hover, pressed, etc.).

### animations
UI animations and transitions.

### accessibility
Screen reader support and navigation.

### responsive
Cross-platform layout adaptations.

## Mechanics

### Layout System
Flexible positioning system supporting:
- **Absolute positioning**: Fixed coordinates
- **Relative positioning**: Parent-relative placement
- **Anchored layouts**: Screen-edge alignment
- **Responsive scaling**: Device-adaptive sizing

### State Management
Multi-state UI elements with smooth transitions:
- Normal, hover, pressed states
- Disabled and selected states
- Custom state definitions

### Interaction Model
Event-driven interactions:
- Click, hover, drag gestures
- Conditional interactions
- Action parameter passing

## Engine Integration

### Unity Implementation
- **Canvas-based**: Unity UI Canvas system
- **Component-driven**: Modular UI components
- **Event system**: Unity's event handling
- **Layout groups**: Automatic responsive layouts

### Cross-Platform Support
- **Mobile optimization**: Touch-friendly interactions
- **Desktop support**: Mouse/keyboard inputs
- **Tablet adaptation**: Hybrid interaction models

### Accessibility Features
- **Screen readers**: Text-to-speech support
- **Keyboard navigation**: Full keyboard accessibility
- **High contrast**: Visual accessibility options

## Examples

### Main Menu Button
```json
{
  "uiId": "main-menu-play-button",
  "type": "button",
  "name": "Play Button",
  "layout": {
    "position": {
      "x": 0.5,
      "y": 0.4
    },
    "size": {
      "width": 200,
      "height": 60
    },
    "anchor": "middle-center",
    "pivot": {
      "x": 0.5,
      "y": 0.5
    }
  },
  "visual": {
    "background": "ui/button_normal",
    "colors": {
      "primary": "#4A90E2",
      "accent": "#FFFFFF"
    },
    "fonts": {
      "family": "Arial",
      "size": 24,
      "style": "bold"
    }
  },
  "content": {
    "dynamicText": {
      "key": "ui.play_button",
      "variables": {}
    }
  },
  "interactions": [
    {
      "event": "click",
      "action": "navigate",
      "parameters": {
        "screen": "game-mode-selection"
      }
    }
  ],
  "states": {
    "normal": {
      "background": "ui/button_normal"
    },
    "hover": {
      "background": "ui/button_hover"
    },
    "pressed": {
      "background": "ui/button_pressed"
    }
  },
  "animations": [
    {
      "trigger": "onShow",
      "type": "fade",
      "duration": 0.5,
      "easing": "ease-out"
    }
  ],
  "accessibility": {
    "label": "Start playing Sovereign Territories",
    "hint": "Tap to begin your adventure",
    "order": 1
  },
  "schemaVersion": 1
}
```

### Codex Grid View
```json
{
  "uiId": "codex-card-grid",
  "type": "grid",
  "name": "Card Collection Grid",
  "layout": {
    "position": {
      "x": 0.1,
      "y": 0.1
    },
    "size": {
      "width": 0.8,
      "height": 0.8
    },
    "anchor": "top-left"
  },
  "visual": {
    "background": "ui/panel_background",
    "colors": {
      "primary": "#2C3E50",
      "secondary": "#34495E"
    }
  },
  "interactions": [
    {
      "event": "click",
      "action": "select_card",
      "parameters": {
        "grid_position": true
      }
    }
  ],
  "responsive": {
    "breakpoints": {
      "mobile": {
        "layout": {
          "size": {
            "width": 0.9,
            "height": 0.7
          }
        }
      }
    }
  },
  "schemaVersion": 1
}
```

### Battle HUD Panel
```json
{
  "uiId": "battle-hud",
  "type": "panel",
  "name": "Battle Heads-Up Display",
  "layout": {
    "position": {
      "x": 0,
      "y": 0
    },
    "size": {
      "width": 1.0,
      "height": 0.2
    },
    "anchor": "bottom-left"
  },
  "content": {
    "images": [
      {
        "asset": "ui/health_bar",
        "position": {
          "x": 0.1,
          "y": 0.1
        }
      }
    ]
  },
  "states": {
    "normal": {
      "visual": {
        "colors": {
          "primary": "#27AE60"
        }
      }
    },
    "low_health": {
      "visual": {
        "colors": {
          "primary": "#E74C3C"
        }
      }
    }
  },
  "animations": [
    {
      "trigger": "onStateChange",
      "type": "shake",
      "duration": 0.3
    }
  ],
  "schemaVersion": 1
}
```

## Validation Rules
- uiId must be unique
- Layout positions must be valid numbers
- Font sizes must be reasonable (8-72pt)
- Animation durations must be positive
- Accessibility labels required for interactive elements

## Related Schemas
- [Tutorial Schema](tutorial-schema.md) - Tutorial UI overlays
- [Notification Schema](notification-schema.md) - Notification displays
- [Battle Schema](battle-schema.md) - Combat UI elements