# Interface Design — Design It Twice

When deepening a module, explore alternative interfaces using parallel sub-agents.

## Process

### Step 1: Frame the Problem Space

Before spawning agents, present the user with:
- Constraints and dependencies
- A rough illustrative code sketch to ground the constraints — not a proposal, just a way to make the constraints concrete

### Step 2: Spawn Sub-agents

Launch 3+ parallel agents, each with a radically different interface. Each receives an independent technical brief:

- **Agent 1** — minimal interface (1-3 entry points)
- **Agent 2** — flexible/extensible interface
- **Agent 3** — optimized for the most common caller
- **Agent 4** (optional) — ports & adapters pattern

Each agent delivers:
- Interface specification
- Usage example (how a caller invokes it)
- Implementation sketch
- Dependency strategy
- Trade-off analysis (what this design gains and gives up)

### Step 3: Present and Compare

Present designs sequentially, then contrast by:
- **Depth** — interface leverage
- **Locality** — change concentration
- **Seam placement** — where behavior can be swapped

Conclude with an opinionated recommendation. Hybrids are fine when elements combine well.

Use `LANGUAGE.md` vocabulary for architecture and `DOMAIN.md` vocabulary for domain concepts.
