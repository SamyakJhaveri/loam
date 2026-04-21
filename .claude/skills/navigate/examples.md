# Intent → Tool Examples

Grounded in real ParBench usage (memory files, git log, active Phase 3 work). Loaded by `/navigate` when the user's intent doesn't match one of the 5 headline examples in SKILL.md.

## Eval pipeline

| Intent | Primary | Also consider |
|--------|---------|--------------|
| "run evals overnight on Rodinia CUDA→OMP" | `/overnight-eval rodinia cuda-to-omp` | `eval-batcher` agent |
| "run a quick eval batch interactively" | `/eval-run` | — |
| "an eval batch just finished — now what?" | `/post-eval <model>` | `/interpret-results` |
| "interpret results from the latest batch" | `/interpret-results` | `/cite-check` if paper-bound |
| "stress-test my experimental design before launch" | `/grill-research` | `superpowers:brainstorming` |
| "refresh the dashboard after new eval data" | `dashboard-refresher` agent | `/post-eval` (includes refresh) |

## Spec / oracle / benchmark

| Intent | Primary | Also consider |
|--------|---------|--------------|
| "a spec is broken — fix it" | `/fix-bug` | `/spec-check`, `rodinia-verifier` |
| "check if spec X is healthy" | `/spec-check <name>` | `spec-auditor` agent for bulk |
| "audit all specs for correctness" | `spec-auditor` agent | `/validate` wave 2 |
| "add a new kernel spec" | `/gen-spec <suite>` | `superpowers:writing-plans` first |
| "test my new AST transform" | `/augment-test` | `explorer` agent for c_augmentation |
| "verify all Rodinia specs still PASS" | `rodinia-verifier` agent | `/validate` |

## Planning / implementation

| Intent | Primary | Also consider |
|--------|---------|--------------|
| "plan a new feature" | `/feature-dev` or `/gsd-plan-phase` | `plan-reviewer` agent |
| "trivial one-line change" | `/gsd-fast` | — |
| "small atomic task with guarantees" | `/gsd-quick` | — |
| "multi-phase project work" | `/gsd-execute-phase` | `/gsd-discuss-phase` first |
| "explore an unfamiliar area of the codebase" | `explorer` agent | Glob/Grep direct (surgical) |
| "I want team-based critic loop for a plan" | `/agent-team` (advisor pattern) | `plan-reviewer` + critic |
| "build a skill for X" | `superpowers:writing-skills` | — |
| "debug systematically — where to start" | `superpowers:systematic-debugging` | `/gsd-debug` |
| "loop over N independent tasks overnight" | `/ralph-loop` | — |

## Paper / research

| Intent | Primary | Also consider |
|--------|---------|--------------|
| "draft the methodology section" | `/agent-team` scenario=paper-assembly | — |
| "simulate peer review on the draft" | `/paper-review-sim` | `/grill-research` |
| "verify every claim traces to data" | `/cite-check` | `/interpret-results` |
| "branching investigation of a failure mode" | `/hypothesis-tree` | `superpowers:systematic-debugging` |
| "teach me the HPC/SE context of X" | `/mentoring` | — |

## Session management

| Intent | Primary | Also consider |
|--------|---------|--------------|
| "resumed after a break — orient me" | `/catchup` | `/gsd-progress` if GSD active |
| "resume mid-phase GSD work" | `/gsd-resume-work` | `/catchup` |
| "write handoff for next session" | `/handoff` | `/gsd-pause-work` |
| "capture a stray idea" | `/gsd-note` or `/gsd-add-todo` | — |
| "consolidate memory before a break" | `/dream` | `/reflect` |
| "reflect on what I just learned" | `/reflect` | — |

## Validation / commit / review

| Intent | Primary | Also consider |
|--------|---------|--------------|
| "verify pipeline health before commit" | `/validate` | pre-commit hook enforces waves 1–3 |
| "4-wave validation without manual orchestration" | `verification-lead` agent | `/validate` |
| "code quality review on a change" | `/review` | `code-simplifier` agent |
| "scan for tech debt" | `/techdebt` | — |
| "adversarial self-critique on my diff" | `self-critic` agent | Wave 4 of `/validate` |

## Cross-cutting / ops

| Intent | Primary | Also consider |
|--------|---------|--------------|
| "pick the right model for this session" | `/model-route` | — |
| "what should I use for X?" (meta) | `/navigate` (this skill) | `/workflow-ref` (static table) |
| "route generic text to a GSD command" | `/gsd-do` | `/navigate` (broader scope) |
| "show me all GSD commands" | `/gsd-help` | — |
| "list pending todos and pick one" | `/gsd-check-todos` | — |
| "full git worktree isolation for a feature" | `superpowers:using-git-worktrees` | — |

## Matching rules for /navigate

1. If intent contains "overnight" or mentions >30min → prefer `/overnight-eval` over `/eval-run`.
2. If intent mentions "commit", "before push", "verify nothing broke" → `/validate`.
3. If intent mentions "resume", "coming back", "break" → `/catchup` (or `/gsd-resume-work` if `.planning/STATE.md` has paused_at).
4. If intent mentions "paper", "methodology", "reviewer", "citations" → paper-bound tool (see Paper/research table).
5. If intent mentions "parallel", "multiple agents", "2+ workers" → `/agent-team` unless explicitly independent tasks (`superpowers:dispatching-parallel-agents`).
6. If intent is a single-line/trivial change → `/gsd-fast`; small atomic → `/gsd-quick`; feature-scale → `/feature-dev` or `/gsd-plan-phase`.
