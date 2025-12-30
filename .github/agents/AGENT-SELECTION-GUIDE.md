# Agent Selection Guide

Quick reference for choosing the right specialized agent for Sovereign Territories tasks.

---

## 🎯 Quick Decision Tree

```
Is it about game design/systems/documentation?
├─ YES → @Soverign-Beast-Mode (Claude Sonnet 4.5)
└─ NO
   ├─ Is it math/balance/economy calculations?
   │  └─ YES → @Soverign-Balance-Master (o1-preview)
   │
   ├─ Does it involve images/UI/visual assets?
   │  └─ YES → @Soverign-Visual-Analyst (Gemini Pro)
   │
   ├─ Is it Unity code/scenes/prefabs?
   │  └─ YES → @Soverign-Unity-Builder (GPT-4o)
   │
   ├─ Is it bulk data (50+ cards/buildings)?
   │  └─ YES → @Soverign-Data-Factory (Claude Haiku)
   │
   ├─ Is it Nakama/multiplayer/backend?
   │  └─ YES → @Soverign-Network-Ninja (GPT-5.1-Codex)
   │
   └─ Is it algorithm/pathfinding/complex logic?
      └─ YES → @Soverign-Code-Mode (GPT-5.1-Codex)
```

---

## 📋 Agent Matrix

| Agent | Model | Best For | Don't Use For |
|-------|-------|----------|---------------|
| **@Soverign-Beast-Mode** | Claude Sonnet 4.5 | Game design, documentation, system architecture, balance discussions | Code implementation, visual analysis |
| **@Soverign-Balance-Master** | GPT-5.2 | Damage formulas, XP curves, gacha math, economy optimization | Simple calculations, Unity code |
| **@Soverign-Visual-Analyst** | Gemini 3 Pro (Preview) | Card art critique, UI/UX analysis, battle map terrain design | Code implementation, design docs |
| **@Soverign-Unity-Builder** | GPT-4o | MonoBehaviours, ScriptableObjects, UI, scenes, general Unity code | Complex algorithms, backend logic |
| **@Soverign-Data-Factory** | Claude Haiku 4.5 | Bulk card generation (50+), JSON validation, batch file operations | Single card design, complex balance |
| **@Soverign-Network-Ninja** | GPT-5.1-Codex | Nakama server logic, authentication, matchmaking, real-time battles | Unity client code (use Unity-Builder) |
| **@Soverign-Code-Mode** | GPT-5.1-Codex | Complex algorithms, pathfinding, procedural generation, battle AI | Simple Unity scripts (use Unity-Builder) |

---

## 🎮 By Project Phase

### **Phase 1: Design (Current)**
**Primary**: @Soverign-Beast-Mode  
**Secondary**: @Soverign-Balance-Master (for formulas), @Soverign-Visual-Analyst (for mockups)

**Typical Tasks**:
- Update game-bible.md with new systems
- Design card rarity tiers
- Plan progression curves
- Review UI mockups

---

### **Phase 2: Data Creation**
**Primary**: @Soverign-Data-Factory  
**Secondary**: @Soverign-Beast-Mode (for design specs)

**Typical Tasks**:
- Generate 100 card entries from schemas
- Create building/tactic data
- Validate JSON schemas
- Batch rename asset files

---

### **Phase 3: Unity Implementation**
**Primary**: @Soverign-Unity-Builder  
**Secondary**: @Soverign-Code-Mode (for complex logic), @Soverign-Visual-Analyst (for UI polish)

**Typical Tasks**:
- Create CardManager, BattleManager scripts
- Build deck builder UI
- Implement battle map grid system
- Create ScriptableObject templates

---

### **Phase 4: Backend Integration**
**Primary**: @Soverign-Network-Ninja  
**Secondary**: @Soverign-Unity-Builder (for client-side network code)

**Typical Tasks**:
- Implement Nakama authentication
- Create matchmaking system
- Build real-time battle sync
- Set up leaderboards

---

### **Phase 5: Balance & Polish**
**Primary**: @Soverign-Balance-Master  
**Secondary**: @Soverign-Beast-Mode (for design iteration), @Soverign-Visual-Analyst (for UI polish)

**Typical Tasks**:
- Tune damage formulas
- Optimize economy curves
- Fix gacha probabilities
- Adjust XP progression

---

## 🔍 By Task Type

### **Documentation**
- Game design docs → **@Soverign-Beast-Mode**
- Code documentation → **@Soverign-Unity-Builder** or **@Soverign-Code-Mode**
- Visual style guide → **@Soverign-Visual-Analyst**

### **Analysis**
- System design → **@Soverign-Beast-Mode**
- Math/balance → **@Soverign-Balance-Master**
- Visual critique → **@Soverign-Visual-Analyst**

### **Creation**
- Game systems → **@Soverign-Beast-Mode**
- Unity code → **@Soverign-Unity-Builder**
- Bulk data → **@Soverign-Data-Factory**
- Nakama server → **@Soverign-Network-Ninja**

### **Optimization**
- Economy tuning → **@Soverign-Balance-Master**
- Code performance → **@Soverign-Code-Mode**
- UI/UX clarity → **@Soverign-Visual-Analyst**

---

## 💡 Example Scenarios

### Scenario 1: "Design a new pack system with 3 tiers"
**Agent**: @Soverign-Beast-Mode  
**Why**: System design, game-bible.md updates, cross-system impact analysis

---

### Scenario 2: "Calculate optimal gold production rates for 5 building tiers"
**Agent**: @Soverign-Balance-Master (GPT-5.2)  
**Why**: Math-heavy, requires formula derivation and curve optimization

---

### Scenario 3: "Review main-menu.jpg and suggest UI improvements"
**Agent**: @Soverign-Visual-Analyst  
**Why**: Visual analysis, UI/UX critique, requires image understanding

---

### Scenario 4: "Create CardManager.cs to handle deck building"
**Agent**: @Soverign-Unity-Builder  
**Why**: Unity MonoBehaviour, general C# coding

---

### Scenario 5: "Generate 100 Fire element units (Common to Legendary)"
**Agent**: @Soverign-Data-Factory  
**Why**: Bulk data generation, repetitive task, needs speed

---

### Scenario 6: "Implement Nakama matchmaking with ELO brackets"
**Agent**: @Soverign-Network-Ninja  
**Why**: Nakama server logic, multiplayer systems

---

### Scenario 7: "Write A* pathfinding for 8x8 tactical grid"
**Agent**: @Soverign-Code-Mode  
**Why**: Complex algorithm, requires deep reasoning

---

## 🚫 Common Mistakes

### ❌ Using Unity-Builder for complex algorithms
**Problem**: GPT-4o is fast but less rigorous than GPT-5.1-Codex for algorithms  
**Fix**: Use @Soverign-Code-Mode for pathfinding, AI, procedural generation

### ❌ Using Beast-Mode for bulk data creation
**Problem**: Sonnet 4.5 is thorough but slower than Haiku for repetitive tasks  
**Fix**: Use @Soverign-Data-Factory for 50+ entries

### ❌ Using Balance-Master for simple questions
**Problem**: GPT-5.2's deep reasoning wastes time on "What's 2+2?"  
**Fix**: Use @Soverign-Unity-Builder or Haiku 4.5 for quick tasks

### ❌ Using Visual-Analyst without images
**Problem**: Gemini 3 Pro's superpower is multimodal vision  
**Fix**: Only use for tasks involving JPEGs/PNGs in assets/examples/

---

## 📁 Agent Files Location

All agents are in `.github/agents/`:

- `Soverign-Beast-Mode.agent.md` (Claude Sonnet 4.5)
- `Soverign-Balance-Master.agent.md` (GPT-5.2)
- `Soverign-Visual-Analyst.agent.md` (Gemini 3 Pro Preview)
- `Soverign-Unity-Builder.agent.md` (GPT-4o)
- `Soverign-Data-Factory.agent.md` (Claude Haiku 4.5)
- `Soverign-Network-Ninja.agent.md` (GPT-5.1-Codex)
- `Soverign-Code-Mode.agent.md` (GPT-5.1-Codex)

---

## 🔄 Switching Agents Mid-Task

**Example Workflow**: Designing a new battle mechanic

1. **@Soverign-Beast-Mode**: Design the mechanic, update game-bible.md
2. **@Soverign-Balance-Master**: Calculate damage formulas, stat curves
3. **@Soverign-Unity-Builder**: Implement BattleManager.cs, CombatResolver.cs
4. **@Soverign-Visual-Analyst**: Review battle UI mockup for clarity
5. **@Soverign-Balance-Master**: Tune values based on playtesting

**Key Point**: Each agent specializes in one step. Don't ask Unity-Builder to do balance math or Beast-Mode to write Unity code.

---

## 🎯 Current Active Agent

**You are currently talking to**: @Soverign-Beast-Mode (Claude Sonnet 4.5)

**Specialized for**:
- Game design & system architecture
- Documentation (game-bible.md, README.md)
- Design iteration & balance discussions
- Cross-system impact analysis

**To switch**: Mention the agent in chat (e.g., "@Soverign-Balance-Master, calculate XP curve for levels 1-50")

---

**Last Updated**: December 30, 2024  
**Total Agents**: 7 (each optimized for specific tasks)
