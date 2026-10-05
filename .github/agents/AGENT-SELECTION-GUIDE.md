# Agent Selection Guide

Quick reference for choosing the right specialized agent for Sovereign Territories tasks.

---

## 🎯 Quick Decision Tree

```
Is it about game design/systems/documentation?
├─ YES → @Sovereign-Beast-Mode (Claude Sonnet 4.5)
└─ NO
   ├─ Is it math/balance/economy calculations?
   │  └─ YES → @Sovereign-Balance-Master (o1-preview)
   │
   ├─ Does it involve images/UI/visual assets?
   │  └─ YES → @Sovereign-Visual-Analyst (Gemini Pro)
   │
   ├─ Is it Unity code/scenes/prefabs?
   │  └─ YES → @Sovereign-Unity-Builder (GPT-4o)
   │
   ├─ Is it bulk data (50+ cards/buildings)?
   │  └─ YES → @Sovereign-Data-Factory (Claude Haiku)
   │
   ├─ Is it Nakama/multiplayer/backend?
   │  └─ YES → @Sovereign-Network-Ninja (GPT-5.1-Codex)
   │
   └─ Is it algorithm/pathfinding/complex logic?
      └─ YES → @Sovereign-Code-Mode (GPT-5.1-Codex)
```

---

## 📋 Agent Matrix

| Agent | Model | Best For | Don't Use For |
|-------|-------|----------|---------------|
| **@Sovereign-Beast-Mode** | Claude Sonnet 4.5 | Game design, documentation, system architecture, balance discussions | Code implementation, visual analysis |
| **@Sovereign-Balance-Master** | GPT-5.2 | Damage formulas, XP curves, gacha math, economy optimization | Simple calculations, Unity code |
| **@Sovereign-Visual-Analyst** | Gemini 3 Pro (Preview) | Card art critique, UI/UX analysis, battle map terrain design | Code implementation, design docs |
| **@Sovereign-Unity-Builder** | GPT-4o | MonoBehaviours, ScriptableObjects, UI, scenes, general Unity code | Complex algorithms, backend logic |
| **@Sovereign-Data-Factory** | Claude Haiku 4.5 | Bulk card generation (50+), JSON validation, batch file operations | Single card design, complex balance |
| **@Sovereign-Network-Ninja** | GPT-5.1-Codex | Nakama server logic, authentication, matchmaking, real-time battles | Unity client code (use Unity-Builder) |
| **@Sovereign-Code-Mode** | GPT-5.1-Codex | Complex algorithms, pathfinding, procedural generation, battle AI | Simple Unity scripts (use Unity-Builder) |

---

## 🎮 By Project Phase

### **Phase 1: Design (Current)**
**Primary**: @Sovereign-Beast-Mode  
**Secondary**: @Sovereign-Balance-Master (for formulas), @Sovereign-Visual-Analyst (for mockups)

**Typical Tasks**:
- Update game-bible.md with new systems
- Design card rarity tiers
- Plan progression curves
- Review UI mockups

---

### **Phase 2: Data Creation**
**Primary**: @Sovereign-Data-Factory  
**Secondary**: @Sovereign-Beast-Mode (for design specs)

**Typical Tasks**:
- Generate 100 card entries from schemas
- Create building/tactic data
- Validate JSON schemas
- Batch rename asset files

---

### **Phase 3: Unity Implementation**
**Primary**: @Sovereign-Unity-Builder  
**Secondary**: @Sovereign-Code-Mode (for complex logic), @Sovereign-Visual-Analyst (for UI polish)

**Typical Tasks**:
- Create CardManager, BattleManager scripts
- Build deck builder UI
- Implement battle map grid system
- Create ScriptableObject templates

---

### **Phase 4: Backend Integration**
**Primary**: @Sovereign-Network-Ninja  
**Secondary**: @Sovereign-Unity-Builder (for client-side network code)

**Typical Tasks**:
- Implement Nakama authentication
- Create matchmaking system
- Build real-time battle sync
- Set up leaderboards

---

### **Phase 5: Balance & Polish**
**Primary**: @Sovereign-Balance-Master  
**Secondary**: @Sovereign-Beast-Mode (for design iteration), @Sovereign-Visual-Analyst (for UI polish)

**Typical Tasks**:
- Tune damage formulas
- Optimize economy curves
- Fix gacha probabilities
- Adjust XP progression

---

## 🔍 By Task Type

### **Documentation**
- Game design docs → **@Sovereign-Beast-Mode**
- Code documentation → **@Sovereign-Unity-Builder** or **@Sovereign-Code-Mode**
- Visual style guide → **@Sovereign-Visual-Analyst**

### **Analysis**
- System design → **@Sovereign-Beast-Mode**
- Math/balance → **@Sovereign-Balance-Master**
- Visual critique → **@Sovereign-Visual-Analyst**

### **Creation**
- Game systems → **@Sovereign-Beast-Mode**
- Unity code → **@Sovereign-Unity-Builder**
- Bulk data → **@Sovereign-Data-Factory**
- Nakama server → **@Sovereign-Network-Ninja**

### **Optimization**
- Economy tuning → **@Sovereign-Balance-Master**
- Code performance → **@Sovereign-Code-Mode**
- UI/UX clarity → **@Sovereign-Visual-Analyst**

---

## 💡 Example Scenarios

### Scenario 1: "Design a new pack system with 3 tiers"
**Agent**: @Sovereign-Beast-Mode  
**Why**: System design, game-bible.md updates, cross-system impact analysis

---

### Scenario 2: "Calculate optimal gold production rates for 5 building tiers"
**Agent**: @Sovereign-Balance-Master (GPT-5.2)  
**Why**: Math-heavy, requires formula derivation and curve optimization

---

### Scenario 3: "Review main-menu.jpg and suggest UI improvements"
**Agent**: @Sovereign-Visual-Analyst  
**Why**: Visual analysis, UI/UX critique, requires image understanding

---

### Scenario 4: "Create CardManager.cs to handle deck building"
**Agent**: @Sovereign-Unity-Builder  
**Why**: Unity MonoBehaviour, general C# coding

---

### Scenario 5: "Generate 100 Fire element units (Common to Legendary)"
**Agent**: @Sovereign-Data-Factory  
**Why**: Bulk data generation, repetitive task, needs speed

---

### Scenario 6: "Implement Nakama matchmaking with ELO brackets"
**Agent**: @Sovereign-Network-Ninja  
**Why**: Nakama server logic, multiplayer systems

---

### Scenario 7: "Write A* pathfinding for 8x8 tactical grid"
**Agent**: @Sovereign-Code-Mode  
**Why**: Complex algorithm, requires deep reasoning

---

## 🚫 Common Mistakes

### ❌ Using Unity-Builder for complex algorithms
**Problem**: GPT-4o is fast but less rigorous than GPT-5.1-Codex for algorithms  
**Fix**: Use @Sovereign-Code-Mode for pathfinding, AI, procedural generation

### ❌ Using Beast-Mode for bulk data creation
**Problem**: Sonnet 4.5 is thorough but slower than Haiku for repetitive tasks  
**Fix**: Use @Sovereign-Data-Factory for 50+ entries

### ❌ Using Balance-Master for simple questions
**Problem**: GPT-5.2's deep reasoning wastes time on "What's 2+2?"  
**Fix**: Use @Sovereign-Unity-Builder or Haiku 4.5 for quick tasks

### ❌ Using Visual-Analyst without images
**Problem**: Gemini 3 Pro's superpower is multimodal vision  
**Fix**: Only use for tasks involving JPEGs/PNGs in assets/examples/

---

## 📁 Agent Files Location

All agents are in `.github/agents/`:

- `Sovereign-Beast-Mode.agent.md` (Claude Sonnet 4.5)
- `Sovereign-Balance-Master.agent.md` (GPT-5.2)
- `Sovereign-Visual-Analyst.agent.md` (Gemini 3 Pro Preview)
- `Sovereign-Unity-Builder.agent.md` (GPT-4o)
- `Sovereign-Data-Factory.agent.md` (Claude Haiku 4.5)
- `Sovereign-Network-Ninja.agent.md` (GPT-5.1-Codex)
- `Sovereign-Code-Mode.agent.md` (GPT-5.1-Codex)

---

## 🔄 Switching Agents Mid-Task

**Example Workflow**: Designing a new battle mechanic

1. **@Sovereign-Beast-Mode**: Design the mechanic, update game-bible.md
2. **@Sovereign-Balance-Master**: Calculate damage formulas, stat curves
3. **@Sovereign-Unity-Builder**: Implement BattleManager.cs, CombatResolver.cs
4. **@Sovereign-Visual-Analyst**: Review battle UI mockup for clarity
5. **@Sovereign-Balance-Master**: Tune values based on playtesting

**Key Point**: Each agent specializes in one step. Don't ask Unity-Builder to do balance math or Beast-Mode to write Unity code.

---

## 🎯 Current Active Agent

**You are currently talking to**: @Sovereign-Beast-Mode (Claude Sonnet 4.5)

**Specialized for**:
- Game design & system architecture
- Documentation (game-bible.md, README.md)
- Design iteration & balance discussions
- Cross-system impact analysis

**To switch**: Mention the agent in chat (e.g., "@Sovereign-Balance-Master, calculate XP curve for levels 1-50")

---

**Last Updated**: December 30, 2024  
**Total Agents**: 7 (each optimized for specific tasks)
