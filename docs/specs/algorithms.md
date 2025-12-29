# Algorithms

This document outlines the core algorithms used in Sovereign Territories for pathfinding, area-of-effect calculations, combat resolution, and other game mechanics. These algorithms ensure deterministic, performant gameplay across client and server.

## Pathfinding (A*)

The game uses A* pathfinding for unit movement on tile-based maps. This algorithm finds the shortest path while considering tile costs, obstacles, and unit capabilities.

### Pseudocode

```python
def a_star(start, goal, graph):
    frontier = PriorityQueue()
    frontier.put(start, 0)
    came_from = {}
    cost_so_far = {}
    came_from[start] = None
    cost_so_far[start] = 0

    while not frontier.empty():
        current = frontier.get()

        if current == goal:
            break

        for next in graph.neighbors(current):
            new_cost = cost_so_far[current] + graph.cost(current, next)
            if next not in cost_so_far or new_cost < cost_so_far[next]:
                cost_so_far[next] = new_cost
                priority = new_cost + heuristic(goal, next)
                frontier.put(next, priority)
                came_from[next] = current

    return reconstruct_path(came_from, start, goal)

def heuristic(a, b):
    # Manhattan distance for square grids
    return abs(a.x - b.x) + abs(a.y - b.y)
```

### Tile Costs

- Base cost: 1 per tile
- Terrain modifiers: Forest (+1), Mountain (+2), Road (-0.5)
- Unit modifiers: Heavy units pay double cost on difficult terrain

### Engine Integration

- Server-side: Nakama handles pathfinding to prevent cheating
- Client-side: Unity visualizes paths but validates against server
- Performance: Precompute paths for common scenarios; cache results

## Area-of-Effect (AoE) Shapes

Abilities and effects can target areas using various shapes. All calculations use tile coordinates.

### Circle (Radius)

Enumerate all tiles within Manhattan distance ≤ radius.

```python
def circle_tiles(center, radius):
    tiles = []
    for dx in range(-radius, radius + 1):
        for dy in range(-radius, radius + 1):
            if abs(dx) + abs(dy) <= radius:
                tiles.append((center.x + dx, center.y + dy))
    return tiles
```

### Cone

From origin in direction, expanding at angle.

```python
def cone_tiles(origin, direction, angle, length):
    tiles = []
    for dist in range(1, length + 1):
        for offset in range(-dist, dist + 1):
            # Calculate position based on direction and offset
            # Simplified: assume direction vectors
            tiles.append(calculate_position(origin, direction, dist, offset))
    return tiles
```

### Line

Straight line from origin to target.

```python
def line_tiles(start, end):
    tiles = []
    dx = end.x - start.x
    dy = end.y - start.y
    steps = max(abs(dx), abs(dy))
    for i in range(steps + 1):
        x = start.x + round(dx * i / steps)
        y = start.y + round(dy * i / steps)
        tiles.append((x, y))
    return tiles
```

### Engine Integration

- Server validates AoE targets before applying effects
- Client previews AoE shapes using these enumerations
- Optimization: Use lookup tables for common radii/directions

## Combat Resolution

Combat uses deterministic math with elemental interactions.

### Base Formula

Damage = (Attacker_Power * Multiplier) - Defender_Defense

Where Multiplier = Elemental_Matrix[Attacker_Element][Defender_Element]

### Elemental Matrix

| Attacker \ Defender | Fire | Water | Earth | Air |
|---------------------|------|-------|-------|-----|
| Fire                | 1.0  | 2.0   | 0.5   | 1.0 |
| Water               | 0.5  | 1.0   | 2.0   | 1.0 |
| Earth               | 2.0  | 0.5   | 1.0   | 1.0 |
| Air                 | 1.0  | 2.0   | 0.5   | 1.0 |

### Stack Math

Units in formation share damage: Damage per unit = Total_Damage / Stack_Size

### Combat Engine Integration

- Server computes all combat to ensure fairness
- Client simulates for UI but defers to server
- Events: Combat results trigger ability procs and status effects

## Other Algorithms

- Matchmaking: Elo-based rating system
- Fog-of-War: Raycasting from unit positions
- Alliance Contributions: Weighted voting based on resource input