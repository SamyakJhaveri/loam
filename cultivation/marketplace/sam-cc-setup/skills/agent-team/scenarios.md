# Pre-built scenario templates

Use with `/agent-team --scenario <name>`.
A scenario skips Phase 2 (team design) and supplies a pre-filled team configuration.
It still requires user approval before launching.

Every teammate below runs Opus; the Effort column is the dial.

---

## `feature-implementation`

**Purpose:** multi-file feature work with a planning pass, an implementation pass, and a quality gate.

**Usage:** `/agent-team --scenario feature-implementation "implement X"`

| Teammate    | Effort | Role | Scope |
|-------------|--------|------|-------|
| planner     | xhigh  | Plan and coordinate | Target files plus their dependencies |
| implementer | high   | Code changes | Target files only |
| critic      | xhigh  | Quality gate | All teammate outputs (read-only) |

**planner:** produces the implementation plan and gets user approval before the implementer starts.

**implementer:** follows the plan and reports milestones to the lead.

**critic:** reviews all changes against the plan and the repo's conventions.

Add `--advisor` when the architecture is genuinely uncertain and you want a read-only peer challenging the plan as it forms.

---

## `failure-investigation`

**Purpose:** multi-stage debugging of a specific failure, run as an adversarial cross-challenging team.
Each investigator owns one stage hypothesis and tries to disprove the others'.

**Usage:** `/agent-team --scenario failure-investigation "<component> <failure-type>"`

| Teammate            | Effort | Role | Scope |
|---------------------|--------|------|-------|
| input-investigator  | xhigh  | Input and setup analyst | Config, input data, initialization code |
| logic-investigator  | xhigh  | Core logic analyst | Main processing code, algorithms |
| output-investigator | xhigh  | Output and validation analyst | Output formatting, assertions, expected vs actual |

Each investigator greps for the relevant functions first, reads only its own stage, then debates adversarially: it owns a hypothesis for its stage and actively tries to disprove the others' hypotheses by message, not merely share findings.
The hypothesis that survives the cross-challenge is the likely root cause; the lead synthesizes the surviving theory.

This is the scenario to escalate to for genuinely ambiguous bugs, after a single-session diagnosis has already failed.

---

## `documentation-assembly`

**Purpose:** parallel gathering and drafting across multiple sources. Useful for README assembly, architecture docs, or onboarding guides.

| Teammate        | Effort | Role | Scope |
|-----------------|--------|------|-------|
| codebase-reader | high   | Code structure documenter | Source tree, tests, configs |
| doc-drafter     | high   | Documentation writer | Docs directory, README, guides |
| critic          | xhigh  | Accuracy reviewer | All teammate outputs (read-only) |

**codebase-reader:** explores the code structure and extracts key patterns, public APIs, and architecture decisions. Delegates bulk reads to mechanical Explore subagents.

**doc-drafter:** drafts the documentation sections from codebase-reader's findings.

**critic:** verifies every claim in the docs against the actual code and flags stale references.

---

## `multi-system-analysis`

**Purpose:** deep-dive comparison across multiple subsystems, data sources, or configurations.
Each analyst specializes in one area; a comparator synthesizes.

| Teammate   | Effort | Role | Scope |
|------------|--------|------|-------|
| analyst-1  | high   | System A analyst | `<system-a-path>/` |
| analyst-2  | high   | System B analyst | `<system-b-path>/` |
| comparator | xhigh  | Cross-system comparator | Analyst summaries only, no raw file reads |

**Per analyst:** delegate bulk reads to a mechanical Explore subagent. Extract the key metrics, patterns, and configurations, and summarize in a structured format.

**Comparator:** computes deltas, identifies anomalies, and ranks differences by significance. Works only from the analyst summaries and never reads raw files directly.

---

## Creating custom scenarios

Not every task fits a template. Use Phase 2 (team design) for custom teams.
The templates above are starting points: adapt the teammate count, scope, and roles to the actual task.
