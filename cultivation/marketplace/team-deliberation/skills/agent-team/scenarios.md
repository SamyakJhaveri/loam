# Pre-Built Scenario Templates

Use with `/agent-team --scenario <name>`. Skips Phase 2 (team design) and provides
a pre-filled team configuration. Still requires user approval before launching.

---

## `advisor-guided-implementation`

**Purpose:** General implementation with Opus advisor providing strategic oversight
to Sonnet workers. Good default for multi-file feature work.

**Usage:** `/agent-team --scenario advisor-guided-implementation "implement X"`

| Teammate | Model | Role | Scope |
|----------|-------|------|-------|
| advisor | opus | Strategic reviewer | All areas (read-only) |
| planner | sonnet | Plan and coordinate | Target files + dependencies |
| implementer | sonnet | Code changes | Target files only |
| critic | sonnet | Quality gate | All teammate outputs (read-only) |

**planner:** Consults advisor on approach, produces implementation plan, gets
user approval before implementer starts.

**implementer:** Follows plan, consults advisor at decision points and when stuck.
Reports milestones to lead with "consulted advisor: yes/no".

**critic:** Reviews all changes, escalates ambiguous findings to advisor.

**Cost:** ~35-45% of all-Opus equivalent

---

## `failure-investigation`

**Purpose:** Multi-stage pipeline debugging for a specific failure.

**Usage:** `/agent-team --scenario failure-investigation "module-X VERIFY_FAIL"`

**Recommended: `--all-opus`** — deep debugging requires strong reasoning from all workers.

| Teammate | Model | Role | Scope |
|----------|-------|------|-------|
| input-investigator | **opus** | Input/config analyst | Config files, input data, entry points |
| logic-investigator | **opus** | Core logic analyst | Main processing code, algorithms |
| output-investigator | **opus** | Output/validation analyst | Output generation, validation, assertions |

Each investigator: Grep for relevant functions first, read only their stage,
share findings to identify the failing stage.

**Cost:** ~3x (all-Opus)

---

## `research-analysis`

**Purpose:** Parallel analysis across multiple data sources or result directories.

**Usage:** `/agent-team --scenario research-analysis "compare results across X, Y, Z"`

| Teammate | Model | Role | Scope |
|----------|-------|------|-------|
| advisor | opus | Strategic reviewer | All areas (read-only) |
| analyst-1 | sonnet | Data analyst | First data source/directory |
| analyst-2 | sonnet | Data analyst | Second data source/directory |
| synthesizer | sonnet | Cross-source comparator | Analyst summaries only (no raw file reads) |

**Per-analyst:** Extract key metrics, compute summary statistics, identify anomalies.
Delegate file reads to Explore subagent for large directories.

**Synthesizer:** Compute deltas, identify cross-source patterns, rank findings.
Works ONLY from analyst summaries — never reads data files directly.

**Cost:** ~35-45% of all-Opus equivalent

---

## `codebase-migration`

**Purpose:** Parallel codebase migration or large-scale refactoring.

**Usage:** `/agent-team --scenario codebase-migration "migrate from X to Y"`

| Teammate | Model | Role | Scope |
|----------|-------|------|-------|
| advisor | opus | Strategic reviewer | All areas (read-only) |
| planner | sonnet | Migration planner | Dependency analysis, ordering |
| migrator-core | sonnet | Core module migrator | Core/library code |
| migrator-tests | sonnet | Test updater | Test files only |
| critic | sonnet | Regression checker | All changes (read-only) |

**planner:** Maps dependencies, determines migration order, identifies breaking changes.

**migrator-core:** Applies migration to production code following the plan.

**migrator-tests:** Updates tests to match migrated code, adds new tests for edge cases.

**Cost:** ~30-40% of all-Opus equivalent

---

## Creating Custom Scenarios

Not every task fits a pre-built template. Use Phase 2 (team design) for custom teams.
The templates above are starting points — adapt teammate count, scope, and roles to
match the actual task.
