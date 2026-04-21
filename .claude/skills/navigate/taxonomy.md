# Tool Taxonomy — ParBench Claude Code Setup

Grounded reference for `/navigate`. ~100 tools across 4 ecosystems. Each row includes trigger conditions (when to use) so the matcher can route by intent.

---

## Table A: ParBench Skills (25)

All at `/home/samyak/Desktop/parbench_sam/.claude/skills/<name>/SKILL.md`.

| Slash command | Phase | When to use |
|---------------|-------|------------|
| `/creating-agent-teams` (`/agent-team`) | plan/implement | 2+ workers needing cross-talk + shared task list. NOT for independent parallel tasks |
| `/augment-test` | verify | Testing an AST transform, diagnosing transform failures |
| `/catchup` | orient | Any time you resume work after a break or start fresh |
| `/cite-check` | verify/paper | Before paper submission; after major eval runs that change numbers |
| `/dream` | ops | Memory consolidation; after 5+ sessions without it, or when stale |
| `/eval-run` | eval | Interactive eval batch, short/foreground. Use overnight-eval for >30min |
| `/feature-dev` | implement | Adding a new non-trivial feature to harness/scripts/visualizations |
| `/fix-bug` | implement | Test fails, spec breaks, unexpected eval result — reproduce-first |
| `/gen-spec` | implement | Add new benchmark suite or kernel spec |
| `/grill-research` | research | Before /overnight-eval or publishing a claim — adversarial stress-test |
| `/handoff` | ops | Write handoff doc for next session or next agent |
| `/hypothesis-tree` | research | Multi-step "why X fails" investigation with branching hypotheses |
| `/interpret-results` | eval/paper | After eval batch or /post-eval — hypothesis-first interpretation |
| `/mentoring` | research | HPC/SE/research teaching grounded in ParBench context |
| `/model-route` | ops | Selecting Opus/Sonnet/Haiku for a specific task |
| `/overnight-eval` | eval | Long eval campaigns (>30min), canonical + ablation runs |
| `/paper-review-sim` | paper | Simulate peer review of paper draft with 5 personas |
| `/post-eval` | eval | After eval batch — analyze → classify → dashboard refresh |
| `/ralph-loop` | implement | Stateless loop over N independent tasks, commit after each |
| `/reflect` | ops | Post-task reflection; record patterns to CLAUDE.md or rules |
| `/review` | verify | Multi-agent code review (style/correctness/security/perf) |
| `/spec-check` | verify | Single-spec health check — verify source + args + harness |
| `/techdebt` | verify | Scan for duplication, dead code, magic numbers (advisory) |
| `/validate` | verify | Pre-commit gate — 4-wave validation loop |
| `/workflow-ref` | orient | Static reference table for skill/agent decisions |

---

## Table B: ParBench Agents (14)

All at `/home/samyak/Desktop/parbench_sam/.claude/agents/<name>.md`. Spawn with `Agent` tool, `subagent_type=<name>`.

| Agent | Phase | When to use |
|-------|-------|------------|
| `code-simplifier` | verify/cleanup | Post-implementation: duplication, dead code, unclear names |
| `consistency-checker` | verify | Cross-check CLAUDE.md vs code; Wave 3 of /validate |
| `diff-reviewer` | verify | Review git diff for regressions and partial work; Wave 1 |
| `eval-batcher` | eval | Run eval batches with kernel eligibility rules baked in |
| `explorer` | explore | Map files, trace call chains, check coverage in ParBench |
| `plan-reviewer` | plan | Adversarial plan review — find missing assumptions/edge cases |
| `regression-checker` | verify | Compare metrics against baselines (60 Rodinia, 15 tests); Wave 2 |
| `rodinia-verifier` | verify | Run harness verify on Rodinia specs — PASS/FAIL counts |
| `security-scanner` | verify | Scan for secrets, command injection, path traversal; Wave 1 |
| `self-critic` | verify | Opus adversarial self-review of diff; Wave 4 (optional) |
| `spec-auditor` | verify | Audit spec JSONs for correctness; Wave 2 conditional |
| `test-synthesizer` | verify | Write temp test scripts for changed files; Wave 2 |
| `verification-lead` | verify | Hierarchical coordinator — spawns all 4 validation waves |
| `verify-app` | verify | Project health: schema + unit tests + spec integrity; Wave 1 |

---

## Table C: Top GSD Commands (20 of 73)

Global, at `~/.claude/skills/gsd-<name>/SKILL.md`.

| Command | When to use |
|---------|------------|
| `/gsd-do` | Freeform intent that should route to a GSD command |
| `/gsd-next` | Auto-advance to next logical step in active GSD project |
| `/gsd-progress` | Status report + route to next action (richer than gsd-next) |
| `/gsd-quick` | Small atomic task with GSD guarantees (commits, state tracking) |
| `/gsd-fast` | Trivial inline task — no subagents, no planning overhead |
| `/gsd-debug` | Systematic debugging with persistent state across context resets |
| `/gsd-plan-phase` | Create detailed PLAN.md for a phase — with verification loop |
| `/gsd-execute-phase` | Execute all plans in a phase with wave-based parallelization |
| `/gsd-discuss-phase` | Gather phase context before planning |
| `/gsd-add-todo` | Capture idea as todo from conversation context |
| `/gsd-check-todos` | List pending todos and pick one |
| `/gsd-resume-work` | Full context restoration for picking up previous session |
| `/gsd-pause-work` | Write HANDOFF.json when pausing mid-phase |
| `/gsd-review-backlog` | Review backlog parking lot, promote items to active |
| `/gsd-code-review` | Review source files changed during a phase |
| `/gsd-verify-work` | Conversational UAT on built features |
| `/gsd-ship` | Create PR, run review, prepare for merge |
| `/gsd-note` | Zero-friction idea capture |
| `/gsd-handoff` | Pause-work alias that writes context handoff |
| `/gsd-help` | List all GSD commands |

---

## Table D: Superpowers Skills (14)

Global, at `~/.claude/plugins/cache/claude-plugins-official/superpowers/`.

| Skill | When to use |
|-------|------------|
| `superpowers:using-superpowers` | Auto-fires at SessionStart; foundational skill dispatcher |
| `superpowers:brainstorming` | ANY creative work: new feature, component, behavior change |
| `superpowers:writing-plans` | Have spec/requirements for multi-step task, before code |
| `superpowers:executing-plans` | Have a written plan to execute in a session with checkpoints |
| `superpowers:subagent-driven-development` | Execute plan with independent tasks in current session |
| `superpowers:dispatching-parallel-agents` | 2+ independent tasks without shared state. NOT for team work |
| `superpowers:using-git-worktrees` | Feature work needing isolation from current workspace |
| `superpowers:test-driven-development` | Implementing any feature/bugfix before writing impl code |
| `superpowers:systematic-debugging` | Any bug/test failure/unexpected behavior — before proposing fix |
| `superpowers:verification-before-completion` | Before claiming work complete, fixed, or passing |
| `superpowers:finishing-a-development-branch` | Implementation complete, tests pass, deciding merge approach |
| `superpowers:requesting-code-review` | Completing task, implementing major feature, before merge |
| `superpowers:receiving-code-review` | Receiving feedback before implementing suggestions |
| `superpowers:writing-skills` | Creating, editing, or verifying skills |

---

## Cross-ecosystem patterns (key for /navigate matching)

**Eval pipeline governance:** `/overnight-eval` (long) or `/eval-run` (short) → `/post-eval` → `/interpret-results` → `/cite-check` (if paper-bound) + `eval-batcher` agent inside any of these.

**Spec/oracle health:** `/spec-check` (single) or `spec-auditor` agent (bulk) + `rodinia-verifier` for Rodinia-specific + `/fix-bug` when diagnosis needed.

**Session continuity:** `/catchup` (fresh/break) or `/gsd-resume-work` (active GSD phase) + `/handoff` or `/gsd-pause-work` on exit + `/dream` periodic memory consolidation.

**Parallel team work:** `/agent-team` (cross-talk needed) vs `superpowers:dispatching-parallel-agents` (independent tasks). TeamCreate is mandatory for the former per project convention.

**Pre-commit:** `/validate` waves 1–3 (required by pre-commit hook) + optionally `/review` for code quality + `/techdebt` for cleanup scan.

**Paper work:** `/agent-team` scenario=paper-assembly + `/cite-check` + `/paper-review-sim` + `/grill-research` (before claims) + `/interpret-results` (source of claims).

**Planning:** `/gsd-plan-phase` (GSD active) or `superpowers:writing-plans` (general) + `plan-reviewer` agent (adversarial) + `/gsd-discuss-phase` (context gathering first).
