# Unity & Nakama Framework Reference

## Overview

This document provides an overview of how the Unity game engine and Nakama multiplayer server framework support the Sovereign Territories game design. It highlights out-of-the-box features that align with our specs and provides guidance for kick-starting development.

## Nakama Server Framework

Nakama is an open-source server designed for multiplayer games, providing backend services for authentication, matchmaking, persistence, and real-time communication. It's built with Go and uses CockroachDB for persistence and Redis for caching.

### Official Resources
- **Documentation**: [https://heroiclabs.com/docs/nakama/](https://heroiclabs.com/docs/nakama/)
- **GitHub Repository**: [https://github.com/heroiclabs/nakama](https://github.com/heroiclabs/nakama)
- **Getting Started Guide**: [https://heroiclabs.com/docs/nakama/getting-started/](https://heroiclabs.com/docs/nakama/getting-started/)
- **API Reference**: [https://heroiclabs.com/docs/nakama/server-framework/](https://heroiclabs.com/docs/nakama/server-framework/)

### Out-of-the-Box Features Matching Our Specs

#### 1. Player Management (Player Schema)
**Nakama Feature**: Built-in user accounts with authentication
- **Supported Auth Methods**: Email/password, social login (Google, Facebook, Apple), custom authentication
- **User Profiles**: Custom metadata storage for player stats, preferences
- **Friends System**: Built-in friend relationships

**Example Implementation**:
```lua
-- Server-side Lua script
local nk = require("nakama")

function authenticate_user(context, payload)
    local user_id = nk.authenticate_email(payload.email, payload.password)
    return { user_id = user_id }
end
```

**Integration with Our Specs**:
- Maps directly to [player-schema.json](specs/player-schema.json)
- User metadata can store XP, level, tutorial progress
- Friends system supports alliance member management

#### 2. Matchmaking (Matchmaking Schema)
**Nakama Feature**: Advanced matchmaking system with Elo support
- **Ticket-based Matching**: Players create match tickets with criteria
- **Filters**: Custom properties for balanced matchmaking
- **Elo Rating**: Built-in ranking system

**Example Implementation**:
```lua
function make_match(context, payload)
    local ticket = nk.match_create(payload.match_type, {
        min_players = 2,
        max_players = 4,
        mode = payload.mode
    })
    return { ticket = ticket }
end
```

**Integration with Our Specs**:
- Directly implements [matchmaking-schema.json](specs/matchmaking-schema.json)
- Supports Elo-based ranking for PvP balance
- Custom properties for game mode filtering

#### 3. Alliances/Diplomacy (Diplomacy Schema)
**Nakama Feature**: Groups system for social structures
- **Group Creation**: Players can create and manage groups
- **Membership Management**: Roles, invitations, join requests
- **Group Metadata**: Custom data storage for alliance policies

**Example Implementation**:
```lua
function create_alliance(context, payload)
    local group = nk.group_create(context.user_id, payload.name, {
        description = payload.description,
        open = payload.open_membership
    })
    return { alliance_id = group.id }
end
```

**Integration with Our Specs**:
- Groups map to alliances in [diplomacy-schema.json](specs/diplomacy-schema.json)
- Supports voting through custom RPC calls
- Metadata stores reputation and treaty information

#### 4. Notifications (Notification Schema)
**Nakama Feature**: Built-in notification system
- **Push Notifications**: Send to individual users or groups
- **Persistent Storage**: Notifications stored server-side
- **Real-time Delivery**: WebSocket-based delivery

**Example Implementation**:
```lua
function send_trade_notification(context, payload)
    nk.notification_send(context.user_id, payload.recipient_id, {
        subject = "Trade Offer",
        content = payload.message,
        code = 1, -- Custom notification type
        persistent = true
    })
end
```

**Integration with Our Specs**:
- Implements [notification-schema.json](specs/notification-schema.json)
- Supports all notification types (trade, diplomacy, achievements)
- Persistent notifications survive client disconnects

#### 5. Data Persistence (All Schemas)
**Nakama Feature**: Storage engine for game data
- **Collections**: Key-value storage with user or global scope
- **Versioning**: Automatic conflict resolution
- **Queries**: Advanced querying capabilities

**Example Implementation**:
```lua
function save_player_deck(context, payload)
    nk.storage_write({
        {
            collection = "decks",
            key = payload.deck_id,
            user_id = context.user_id,
            value = payload.deck_data,
            version = payload.version
        }
    })
end
```

**Integration with Our Specs**:
- Stores all game entities (cards, maps, trades, etc.)
- Versioning prevents data corruption
- Global collections for shared game data

#### 6. Chat & Communication
**Nakama Feature**: Real-time chat system
- **Channels**: Global, group, direct messaging
- **Moderation**: Built-in message filtering
- **Persistence**: Chat history storage

**Integration with Our Specs**:
- Supports diplomacy negotiations
- Group chat for alliances
- Direct messaging for trades

#### 7. Leaderboards & Tournaments
**Nakama Feature**: Competitive features
- **Leaderboards**: Global and social rankings
- **Tournaments**: Time-limited competitions

**Integration with Our Specs**:
- Progression system rankings
- Seasonal tournaments

## Unity Game Engine

Unity is a cross-platform game engine that provides the client-side framework for Sovereign Territories.

### Official Resources
- **Documentation**: [https://docs.unity3d.com/Manual/index.html](https://docs.unity3d.com/Manual/index.html)
- **Scripting API**: [https://docs.unity3d.com/ScriptReference/](https://docs.unity3d.com/ScriptReference/)
- **Learn Platform**: [https://learn.unity.com/](https://learn.unity.com/)
- **Asset Store**: [https://assetstore.unity.com/](https://assetstore.unity.com/)

### Out-of-the-Box Features Matching Our Specs

#### 1. JSON Serialization (All Schemas)
**Unity Feature**: Built-in JSON utilities
- **JsonUtility**: Simple JSON serialization/deserialization
- **Newtonsoft.Json**: Advanced JSON handling via package

**Example Implementation**:
```csharp
using UnityEngine;

[System.Serializable]
public class PlayerData
{
    public string playerId;
    public int level;
    public int xp;
}

public class DataManager : MonoBehaviour
{
    public void SavePlayer(PlayerData player)
    {
        string json = JsonUtility.ToJson(player);
        // Send to Nakama storage
    }

    public PlayerData LoadPlayer(string json)
    {
        return JsonUtility.FromJson<PlayerData>(json);
    }
}
```

**Integration with Our Specs**:
- Serializes all schema objects for network transmission
- Generated TypeScript types from CI can be mirrored in C#

#### 2. UI System (UI Schema)
**Unity Feature**: Unity UI (UGUI)
- **Canvas-based UI**: Flexible UI construction
- **Event System**: Input handling and interactions
- **Layout Components**: Automatic UI arrangement

**Example Implementation**:
```csharp
using UnityEngine.UI;

public class NotificationPanel : MonoBehaviour
{
    public Text titleText;
    public Text messageText;
    public Button acceptButton;

    public void ShowNotification(NotificationData data)
    {
        titleText.text = data.title;
        messageText.text = data.message;
        acceptButton.onClick.AddListener(() => AcceptNotification(data));
    }
}
```

**Integration with Our Specs**:
- Implements notification display from [notification-schema.json](specs/notification-schema.json)
- Tutorial overlays and UI highlighting

#### 3. Networking (Multiplayer Features)
**Unity Feature**: Unity Transport Package
- **Low-level Networking**: Socket-based communication
- **Integration Ready**: Works alongside Nakama

**Integration with Our Specs**:
- Real-time communication for matchmaking and game state
- Nakama handles high-level multiplayer logic

#### 4. Asset Management
**Unity Feature**: Addressables system
- **Dynamic Loading**: Load assets on demand
- **Content Delivery**: Over-the-air updates
- **Memory Management**: Efficient asset unloading

**Integration with Our Specs**:
- Dynamic card loading from [card-schema.json](specs/card-schema.json)
- Map asset management

#### 5. Input System
**Unity Feature**: New Input System
- **Cross-platform Input**: Keyboard, mouse, touch, gamepad
- **Input Actions**: Configurable control schemes

**Integration with Our Specs**:
- Touch-optimized controls for mobile deployment
- Accessibility features

## Getting Started Workflow

### 1. Nakama Setup
1. **Install Nakama**: Use Docker or binary installation
2. **Configure Database**: Set up CockroachDB/Redis
3. **Create Project**: Initialize with nakama-cli
4. **Implement RPCs**: Write Lua scripts for game logic

### 2. Unity Setup
1. **Install Unity**: Use Unity Hub with 2021+ LTS version
2. **Create Project**: 2D/3D template with mobile support
3. **Install Packages**: Add Newtonsoft.Json, Addressables
4. **Setup Nakama Client**: Use Nakama Unity SDK

### 3. Integration Example
```csharp
using Nakama;

public class GameManager : MonoBehaviour
{
    private IClient client;
    private ISession session;

    async void Start()
    {
        client = new Client("defaultkey", "127.0.0.1", 7350, false);
        session = await client.AuthenticateEmailAsync("email@example.com", "password");
    }

    public async void CreateAlliance(string name)
    {
        var result = await client.RpcAsync(session, "create_alliance", JsonUtility.ToJson(new { name = name }));
        Debug.Log("Alliance created: " + result.Payload);
    }
}
```

## Examples in Action

### Nakama Examples
- **Spacewar**: [https://github.com/heroiclabs/nakama/tree/master/examples](https://github.com/heroiclabs/nakama/tree/master/examples)
- **Unity Integration**: [https://github.com/heroiclabs/nakama-unity](https://github.com/heroiclabs/nakama-unity)

### Unity Examples
- **Multiplayer Samples**: [https://github.com/Unity-Technologies/multiplayer](https://github.com/Unity-Technologies/multiplayer)
- **UI Examples**: Built-in templates in Unity Editor

### Sovereign Territories Specific
- **Matchmaking Flow**: Use Nakama's ticket system for [matchmaking-schema.json](specs/matchmaking-schema.json)
- **Data Sync**: Combine Unity's JsonUtility with Nakama storage for all schemas
- **Real-time Updates**: WebSocket connections for live game state

## Best Practices

### Nakama
- Use RPCs for complex game logic
- Leverage storage versioning for data integrity
- Implement proper error handling for network operations

### Unity
- Use ScriptableObjects for game configuration
- Implement proper state management for offline/online modes
- Optimize for mobile performance from the start

This framework combination provides a solid foundation for Sovereign Territories, handling most backend concerns while allowing creative freedom in game design and client implementation.