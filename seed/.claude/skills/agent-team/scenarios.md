# Pre-Built Scenario Templates

Use with `/agent-team --scenario <name>`. Skips Phase 2 (team design) and provides
a pre-filled team configuration. Still requires user approval before launching.

---

## `feature-implementation`

**Purpose:** General implementation with Opus advisor providing strategic oversight
to Sonnet workers. Good default for multi-file feature work.

**Usage:** `/agent-team --scenario feature-implementation "implement X"`

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

**Usage:** `/agent-team --scenario failure-investigation "<component> <failure-type>"`

**Recommended: `--all-opus`** — deep debugging requires strong reasoning from all workers.

| Teammate | Model | Role | Scope |
|----------|-------|------|-------|
| input-investigator | **opus** | Input/setup analyst | Config, input data, initialization code |
| logic-investigator | **opus** | Core logic analyst | Main processing code, algorithms |
| output-investigator | **opus** | Output/validation analyst | Output formatting, assertions, expected vs actual |

Each investigator: Grep for relevant functions first, read only their stage,
share findings to identify the failing stage.

**Cost:** ~3x (all-Opus)

---

## `documentation-assembly`

**Purpose:** Parallel data gathering and documentation drafting across multiple
sources. Useful for README assembly, architecture docs, or onboarding guides.

| Teammate | Model | Role | Scope |
|----------|-------|------|-------|
| advisor | opus | Strategic reviewer | All areas (read-only) |
| codebase-reader | sonnet | Code structure documenter | `src/`, tests, configs |
| doc-drafter | sonnet | Documentation writer | `docs/`, README, guides |
| critic | sonnet | Accuracy reviewer | All teammate outputs (read-only) |

**codebase-reader:** Explores code structure, extracts key patterns, public APIs,
and architecture decisions. Delegates bulk reads to Explore subagents.

**doc-drafter:** Drafts documentation sections from codebase-reader's findings.

**critic:** Verifies all claims in docs match actual code. Flags stale references.

**Cost:** ~35-45% of all-Opus equivalent

---

## `multi-system-analysis`

**Purpose:** Deep-dive comparison across multiple subsystems, data sources, or
configurations. Each analyst specializes in one area; a comparator synthesizes.

| Teammate | Model | Role | Scope |
|----------|-------|------|-------|
| advisor | opus | Strategic reviewer | All areas (read-only) |
| analyst-1 | sonnet | System A analyst | `<system-a-path>/` |
| analyst-2 | sonnet | System B analyst | `<system-b-path>/` |
| comparator | sonnet | Cross-system comparator | Analyst summaries only (no raw file reads) |

**Per-analyst:** Delegate reads to Explore subagent. Extract key metrics, patterns,
configurations. Summarize findings in structured format.

**Comparator:** Compute deltas, identify anomalies, rank differences by significance.
Works ONLY from analyst summaries — never reads raw files directly.

**Cost:** ~35-45% of all-Opus equivalent

---

## `advisor-guided-implementation`

Alias for `feature-implementation`. Identical team structure.

---

## Creating Custom Scenarios

Not every task fits a pre-built template. Use Phase 2 (team design) for custom teams.
The templates above are starting points — adapt teammate count, scope, and roles to
match the actual task.
