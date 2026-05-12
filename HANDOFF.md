# HANDOFF: Research Experiment Pipeline (Stage 13)

> **For the next Claude Code session.** This document is self-contained — you don't
> need any prior conversation context. Read this, then implement.

## Goal

Add experiment orchestration to the project-template's **research flavor** so that
every new research project bootstraps with a structured way to:

1. Design experiments (with forced hypothesis validation)
2. Run experiments (with reproducibility enforcement)
3. Track how experiments evolve over time (the key innovation)
4. Connect to existing research skills that already handle analysis

**Think of it like this:** The research flavor already has a brain (analysis tools).
We're adding the hands (execution + tracking).

---

## Background (What You Need to Know)

### What is this project?

`project-template` is a reusable template that bootstraps new Claude Code projects.
It has **flavors** — stackable packs of skills, hooks, rules, and seed docs. The
`research` flavor adds tools for research workflows.

Key paths:
- `flavors/research/skills/` — research-specific skills (copied to `.claude/skills/` at bootstrap)
- `flavors/research/hooks/` — research-specific hooks (copied to `.claude/hooks/`)
- `flavors/research/rules/` — research-specific rules (copied to `.claude/rules/`)
- `flavors/research/seed-docs/` — template docs rendered at project root during bootstrap
- `flavors/research/README.md` — inventory of everything the flavor adds
- `bin/init-project.sh` — the bootstrap script (DO NOT modify)

### What the research flavor already has

These skills **already exist** — DO NOT rebuild or duplicate them:

| Skill | What it does | Path |
|-------|-------------|------|
| `/grill-research` | Forces you to state hypothesis + null hypothesis before running anything | `.claude/skills/grill-research/SKILL.md` |
| `/interpret-results` | Hypothesis-first analysis of experiment results | `flavors/research/skills/interpret-results/SKILL.md` |
| `/hypothesis-tree` | Tracks hypotheses with evidence for/against | `flavors/research/skills/hypothesis-tree/SKILL.md` |
| `protect-results.sh` | Hook that blocks deletion/overwriting of files in `results/` | `flavors/research/hooks/protect-results.sh` |

These seed docs **already exist** — the experiment skill should reference them:
- `EXPERIMENTS.md.tmpl` — running ledger of experiments (append-only)
- `FINDINGS.md.tmpl` — distilled insights from experiments
- `RESULTS.md.tmpl` — index of result artifacts

### The core insight driving this work

An experiment is just three things:

1. **A spec** — what you're testing, with what parameters and metrics
2. **Runs** — immutable snapshots of executing that spec
3. **A changelog** — why the spec changed between versions

Most experiment trackers capture what ran. This system also captures **why the
experiment changed** — so six months from now you can read the version history
and understand the research narrative, not just data points.

### What was explicitly ruled out (don't build these)

| Thing | Why not |
|-------|---------|
| SLURM/HPC job submission skill | User decided to skip it |
| Separate metrics registry file | Metrics tracked per-spec; a global registry drifts |
| `/experiment compare` subcommand | Just diff two reports manually |
| `/experiment status` subcommand | Just read registry.md |
| `/experiment list` subcommand | Just `ls experiments/specs/` |
| Separate `config-schema.md` file | Inline in SKILL.md instead |
| Separate `spec-template.md` file | Inline in SKILL.md instead |

---

## What Was Done So Far

- [x] Read Stage 13 from the reference doc (`[HUMAN]_claude-code-deep-reference.md`)
- [x] Audited all existing research flavor assets (12 skills, 2 agents, 1 hook, 6 seed docs)
- [x] Identified gaps: experiment execution layer + reproducibility enforcement + evolution tracking
- [x] Researched best practices from MLflow, DVC, and electronic lab notebook literature
- [x] Designed architecture: pipeline hub pattern (experiment skill connects existing skills)
- [x] Trimmed over-engineering: 8 deliverables → 5, 7 subcommands → 4
- [x] Wrote detailed implementation plan (see plan file below)
- [ ] **Implementation not started** — that's your job

### What worked during design

- **Pipeline hub pattern**: Instead of building everything from scratch, the experiment
  skill acts as a connector between existing skills. grill-research does pre-flight,
  interpret-results does post-analysis, hypothesis-tree tracks evidence. The experiment
  skill just orchestrates the flow between them.
- **Inline everything**: Putting the config schema and spec template directly in the
  SKILL.md instead of separate files reduces cognitive load. One file to read, not three.
- **Modeling the hook after protect-results.sh**: Same structure, same conventions,
  same exit codes. Consistency matters.

### What didn't work / was rejected

- **Original 8-deliverable plan**: Too many files, too many subcommands. Three of the
  seven subcommands were just "read a file" wrapped in a skill. Separate schema and
  template files split one concept across three files.
- **METRICS-REGISTRY.md.tmpl**: A global registry of metrics that must be kept in sync
  with per-spec metric definitions. Two sources of truth = drift. Eliminated.
- **Per-run evolution.md**: Each run would have a file explaining what changed from
  the previous version. But the spec's Version History section already captures this.
  Duplication eliminated.

---

## Next Steps — The 5 Deliverables to Build

Build these **in this order** (dependencies noted):

### Step 1: `flavors/research/skills/experiment/SKILL.md` (the big one)

A single self-contained skill file with 4 subcommands: `init`, `plan`, `run`, `evolve`.

**Key design details:**

The skill creates the directory structure on first `/experiment init` (not at bootstrap):
```
experiments/
├── registry.md      ← master index of all experiments
├── specs/           ← versioned experiment specs
├── runs/            ← timestamped, immutable run directories
└── eval-scripts/    ← user-written deterministic eval scripts
```

**Experiment spec format** (embed this as a template in the skill):
```markdown
# Experiment: <name>

## Current Version: v1 (<date>)

**Hypothesis:** <what you expect and why>
**Null hypothesis:** <what result would disprove your expectation>
**Parameters:**
  - <param>: <value>
**Metrics:** [<metric1>, <metric2>]
**Eval Script:** experiments/eval-scripts/<script>.py (or "manual")
**Parent Version:** none

## Version History

### v1 (<date>) — Initial design
- Created after /grill-research pre-flight
```

**Reproducibility config schema** (embed in skill, enforced by hook):
```json
{
  "schema_version": 1,
  "experiment_name": "...",
  "spec_version": "v1",
  "timestamp": "ISO-8601",
  "git_commit": "<HEAD SHA>",
  "config_hash": "<SHA-256 of spec file>",
  "seed": 42,
  "parameters": {},
  "metrics": [],
  "eval_script": "path or null",
  "environment": { "python_version": "...", "os": "..." }
}
```

**Subcommand details:**

| Subcommand | Phases | Integrates with | Hard gates |
|------------|--------|-----------------|------------|
| `init <name>` | Create dirs + spec from template | — | — |
| `plan <name>` | 1) Mandatory `/grill-research` pre-flight, 2) ultrathink batch planning | grill-research | Cannot skip pre-flight; stops for user approval |
| `run <name>` | Execute plan, write config.json + results, aggregate, write report | agent teams, eval scripts | Hook validates config.json; protect-results guards results/ |
| `evolve <name>` | Ask what changed + why, bump version, update changelog | — | Must state rationale; suggests /experiment plan next |

**Anti-rationalization rules to embed:**
- Cannot skip pre-flight ("just run it quick")
- Cannot overwrite existing run results (append-only)
- Cannot claim results without citing actual file paths
- Cannot evolve without stating what changed and why
- Cannot run without user-approved plan

**YAML frontmatter gotcha:** Descriptions with colons must use folded scalar (`>`).
See `.claude/rules/known-issues.md` for details.

**Reference skills for style/structure:**
- `flavors/research/skills/interpret-results/SKILL.md` — similar complexity, good model
- `flavors/research/skills/hypothesis-tree/SKILL.md` — subcommand pattern to follow

---

### Step 2: `flavors/research/hooks/validate-experiment-config.sh` (parallel with 3, 4)

A PreToolUse hook on Write that blocks writes to `experiments/runs/*/config.json`
unless the JSON contains all required reproducibility fields.

**Model it directly after** `flavors/research/hooks/protect-results.sh` — same
structure, same exit code convention (0 = allow, 2 = BLOCK), same python3 JSON
parsing pattern.

**What to validate:**
- Required fields present: `experiment_name`, `spec_version`, `timestamp`, `git_commit`, `config_hash`, `seed`
- `timestamp` matches ISO 8601 pattern
- `git_commit` is hex, 7+ characters
- `schema_version` is a positive integer
- Target file doesn't already exist (append-only enforcement)

**Scope:** Only fires on paths matching `experiments/runs/*/config.json`. Don't
interfere with other writes.

---

### Step 3: `flavors/research/seed-docs/EXPERIMENT-PROTOCOL.md.tmpl` (parallel with 2, 4)

A template doc rendered at bootstrap. Contains:

1. The research ↔ Claude Code mapping table:

| Research Activity | Claude Code Primitive |
|---|---|
| Form hypothesis | `/hypothesis-tree add` |
| Validate hypothesis | `/grill-research` |
| Design experiment | `/experiment init` + `/experiment plan` |
| Run experiment | `/experiment run` |
| Analyze results | `/interpret-results` |
| Track evidence | `/hypothesis-tree update` |
| Evolve experiment | `/experiment evolve` |
| Record learnings | MEMORY.md with `[LEARN:tag]` |

2. Directory structure explanation (what goes where)
3. Quick-start: the 5 commands to run your first experiment
4. Uses `{{PROJECT_NAME}}` and `{{DATE}}` template variables (see other .tmpl files for pattern)

---

### Step 4: `flavors/research/rules/research-memory.md` (parallel with 2, 3)

A rule file documenting the `[LEARN:tag]` convention for cross-session memory:

```
[LEARN:method]     — methodological corrections
[LEARN:data]       — data handling surprises
[LEARN:tool]       — tool/environment gotchas
[LEARN:claim]      — claims that turned out wrong
[LEARN:metric]     — metric definition changes
[LEARN:experiment] — experiment design evolution decisions
```

Also document conventions for "Key Facts" and "Active Experiments" sections in MEMORY.md.

**Note:** This is a `.claude/rules/` file, which means it auto-loads. Keep it concise —
rules are loaded into every conversation.

---

### Step 5: Update `flavors/research/README.md` (after 1-4)

Add new assets to the existing inventory. Read the current README first
(`flavors/research/README.md`) — it has clear sections for Skills, Hooks, Seeds,
and Rules. Add one entry per new asset in the appropriate section.

---

## The Pipeline (How Everything Connects)

```
  /hypothesis-tree add ──── "I have a hypothesis"
          │
          ▼
  /grill-research ───────── "Is it testable?"
          │
          ▼
  /experiment init ──────── "Set up the experiment"
          │
          ▼
  /experiment plan ──────── "Plan the batches" (ultrathink)
          │                    ↓ user approves plan
          ▼
  /experiment run ───────── "Run it" (agent teams)
          │                    ↓ validate-experiment-config.sh (GATE)
          │                    ↓ protect-results.sh (GATE)
          ▼
  /interpret-results ────── "Analyze results"
          │
          ▼
  /hypothesis-tree update ── "Update evidence"
          │
          ├──→ EXPERIMENTS.md ─── ledger entry
          ├──→ FINDINGS.md ────── distilled insight
          └──→ MEMORY.md ─────── [LEARN:tag] corrections

  ── When understanding changes: ──

  /experiment evolve ────── "Update spec + rationale"
          │
          └──→ back to /experiment plan
```

Skills on the LEFT already exist. The `/experiment` skill (center) is what you're
building. It's the hub that connects the existing tools into a coherent workflow.

---

## Verification Checklist

After implementation, run these checks:

- [ ] SKILL.md YAML frontmatter parses without error (test: no unquoted colons)
- [ ] Hook exits 0 for valid config.json, 2 for missing required fields
- [ ] Hook blocks overwrites of existing config.json files
- [ ] Seed doc renders correctly: `{{PROJECT_NAME}}` and `{{DATE}}` get substituted
- [ ] Bootstrap test passes:
  ```bash
  bin/init-project.sh /tmp/test-experiment --flavor research
  # Then verify these exist in the test project:
  # - EXPERIMENT-PROTOCOL.md (at project root)
  # - .claude/skills/experiment/SKILL.md
  # - .claude/hooks/validate-experiment-config.sh
  # - .claude/rules/research-memory.md
  ```
- [ ] `bin/verify-template.sh` outputs ALL OK

---

## Detailed Plan File

The full implementation plan with schemas, formats, and anti-patterns is at:
`~/.claude/plans/ultrathink-brainstorming-16-stage-tingly-piglet.md`

Read it before starting implementation — it has details this handoff summarizes.
