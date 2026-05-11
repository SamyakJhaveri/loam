# Handoff — project-template Health Audit (2026-05-11)

> **Read this if:** You are a Claude Code session that has been pasted this file
> as your starting context, and asked to continue the project-template remediation
> work. You have no prior memory of this codebase. This document is written for
> a software-engineering undergrad — every term is defined, every path is absolute,
> every assumption is surfaced.

---

## 1. The single most important thing to know

There are **two** durable artifacts from the prior planning session:

1. **The plan** — `/Users/samyakjhaveri/.claude/plans/ultrathink-brainstorming-read-quiet-willow.md`
   This is the detailed, executable remediation plan. It has 11 sessions (A through K) — each one is a single bounded change to the repo. The plan was adversarially reviewed by the `plan-reviewer` agent and rewritten to be **self-contained**: every command, file path, and verify step is spelled out. You should not need to re-explore the codebase to know what to do.

2. **This handoff doc** — you're reading it. It exists at
   `/Users/samyakjhaveri/Desktop/project_template/docs/audits/2026-05-11-template-health-handoff.md`.
   It's the orientation layer. It tells you the *why*, the *what's done so far*, and the *what's pending*. The plan tells you the *how*.

**Your first action**: open the plan file in your context (`Read` tool on the path above), then come back here for the user-facing summary.

---

## 2. Goal — what we're trying to accomplish

`/Users/samyakjhaveri/Desktop/project_template/` is the user's Claude Code
**template repository**. Its job is to bootstrap new projects via
`bin/init-project.sh <new-project-path> --flavor <name>`. Over time it
accumulated cruft (stale audit logs, personal docs, half-finished skills,
project-specific rules that wrongly propagated to every bootstrapped project).
The plan is a prioritized remediation: P0 (broken or actively wrong) → P1
(drift from the rules the repo set for itself) → P2 (judgment calls).

The **success criterion** for the audit overall: running
`bin/verify-template.sh` (which Session F creates) prints `ALL OK` after every
remaining session has been executed, with no project-specific content leaking
into bootstrapped projects.

---

## 3. Current progress

**Phase 1 — Audit (DONE).** The prior session:
- Read the user's mastery-reference doc (Anthropic Claude Code playbook v4, March 2026).
- Read all of `CLAUDE.md`, every file in `.claude/rules/`, the hooks in `.claude/hooks/`, `bin/init-project.sh`, `.claude/settings.json`.
- Produced a 17-finding prioritized punch list (5 P0, 7 P1, 5 P2).
- Wrote a v1 plan, dispatched the `plan-reviewer` agent for adversarial review (verdict: **REVISE** with 5 critical flaws).
- Rewrote into v2 — the plan file you should now read.

**Phase 2 — Remediation (NOT STARTED).** No code or asset changes have been made to the repo. The plan defines 11 sessions; you (or the user) will execute one at a time, in suggested order: A → B → C → E → F → G first wave; D and H second wave; I, J, K last.

**Phase 3 — Handoff (this file).** This document exists so a fresh session can pick up Phase 2 cleanly.

---

## 4. Prerequisites — what to set up before Session A

These are one-time prerequisites. Run them once, in this order:

### 4.1 Verify the plan file is readable

```bash
test -f /Users/samyakjhaveri/.claude/plans/ultrathink-brainstorming-read-quiet-willow.md && wc -l /Users/samyakjhaveri/.claude/plans/ultrathink-brainstorming-read-quiet-willow.md
# Expected: an integer > 400 (the plan is ~600 lines)
```

If the file is missing, regenerate it from the conversation history — but it should be there.

### 4.2 Install the Karpathy skills plugin

The plan references "Karpathy-check" — a discipline of "minimum change, surgical edits, no overcomplication" — derived from Andrej Karpathy's observations on LLM coding pitfalls. Install:

```bash
# From within Claude Code, in the target repo:
cd /Users/samyakjhaveri/Desktop/project_template
/plugin marketplace add forrestchang/andrej-karpathy-skills
/plugin install karpathy-skills@andrej-karpathy-skills
/plugin list | grep -i karpathy
# Expected: a line containing "karpathy-skills" with status "enabled"
```

Source: `https://github.com/forrestchang/andrej-karpathy-skills` — the repo provides 4 principles:
1. **Think Before Coding** — state assumptions, don't pick interpretations silently
2. **Simplicity First** — minimum code, no speculative abstractions
3. **Surgical Changes** — touch only what the user asked for
4. **Goal-Driven Execution** — define success criteria, loop until verified

### 4.3 Confirm the other required skills are loaded

```bash
ls /Users/samyakjhaveri/Desktop/project_template/.claude/skills/
# Expected: includes catchup, validate, handoff, agent-team, model-route, plus others
ls /Users/samyakjhaveri/Desktop/project_template/.claude/agents/
# Expected: code-simplifier.md, plan-reviewer.md, self-critic.md, verification-lead.md
```

`superpowers:test-driven-development` and `superpowers:brainstorming` are user-level plugin skills — they should already be available. Verify by trying:
```bash
/test-driven-development help   # If installed: shows skill content. If not: tells you to install.
```

### 4.4 Confirm agent teams are enabled

```bash
grep CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS /Users/samyakjhaveri/Desktop/project_template/.claude/settings.json
# Expected: "1"
```

Required for Session H (skills-to-integrate triage).

---

## 5. How to run a session (the universal protocol)

Every session in the plan follows the same protocol. Do not deviate.

### Step 1: Catchup
```bash
/catchup
```
This is a skill at `.claude/skills/catchup/SKILL.md`. It gives you 30s of orientation: git status, recent commits, env state, pending tasks. **Always run this first**, even if you think you know the state.

### Step 2: Confirm the session
Ask the user: *"Which session do you want to execute now? (A-K)"*
Then **read the corresponding section** of the plan literally. Do not skip steps.

### Step 3: Branch
Each session works on its own branch named `audit/session-<letter>-<short-description>`. Never on `main` directly (CLAUDE.md line 50: "Don't push to main directly").

```bash
cd /Users/samyakjhaveri/Desktop/project_template
git checkout -b audit/session-X-<descriptor>
```

### Step 4: Enter Plan mode for the implementation
Before making any file changes, enter Plan mode (Shift+Tab×2 in interactive use, or by stating "Let me plan this before implementing"). Even though the high-level plan exists, each session benefits from a session-scoped plan that gets reviewed.

### Step 5: Dispatch plan-reviewer
```
Use the plan-reviewer agent to adversarially critique the session-X plan.
```
Read the verdict, address any flaws, only then `ExitPlanMode`.

### Step 6: Karpathy-check before each edit
Before any file write, ask yourself:
- What's the **minimum** change that fixes this finding?
- Am I touching code adjacent to the change that I shouldn't?
- Have I stated my assumptions?
- How will I **verify** this worked?

If you can't answer all four, pause.

### Step 7: Execute the session's "Files to edit" + "Verify steps"
The plan spells out exact paths and exact bash commands. Follow them.

### Step 8: STOP gates
Several sessions have **STOP — confirmation gate** blocks. These mark decisions where the user must speak. **Do not infer the answer.** Pause, ask, and wait.

The STOP gates and the questions they raise are:

| Session | What you must ask the user |
|---------|----------------------------|
| A | "Confirm `internal_docs/` and `skills-to-integrate/` should be untracked. Backup is at `~/Backups/project-template-session-a/`. Proceed?" |
| B | "Audit-log hook is broken. **Fix** (TDD path with stdin JSON parsing) or **delete** (remove from settings.json)?" |
| C | "Move `internal_docs/` to `~/Documents/claude-mastery-reference/` (recommended) or just gitignore in place?" |
| D | "Three approaches for moving project-shaped rules: (1) seed-folders, (2) flavor packs, (3) `paths:` negation glob. Which?" |
| E | "Opus-exclusive rule in workflow.md — deliberate (skip rewrite) or relax-to-mastery-doc (proceed with rewrite)?" |
| F | "Verify-script scope — bootstrap all flavors, validate JSON, shellcheck. Add/remove?" |
| G | "Add `/commit` and `/pr` skills — both, one, or neither? Project-local or user-level?" |
| H | "16 skills to triage. Agent team (parallel), sequential (slow), or bulk-delete (fast/lossy)?" |
| I | "For each skill-overlap candidate, keep both / fold / delete?" |
| J (×4 items) | "P2-2 dream: keep/move/delete? P2-3 docs: yes/no? P2-4 seed-config: move? P2-5 README: read together?" |

### Step 9: /validate
```bash
/validate
```
This writes `.validation_passed` (a sentinel file) on success. The pre-commit hook at `.claude/hooks/pre-commit-gate.sh` requires that sentinel.

### Step 10: Commit
Conventional Commit format, single commit per session. The plan provides the exact commit message template for each session.

### Step 11: Update this handoff doc
After every completed session, append a one-line entry to the **"Sessions completed"** table below. This is how a *future* fresh session knows where to pick up.

---

## 6. Sessions completed (append as you finish)

| Date | Session | Branch | Verdict | Commit |
|------|---------|--------|---------|--------|
| (none yet) | — | — | — | — |

---

## 7. What worked (lessons from the audit phase that should carry forward)

1. **Surgical exploration over agent sweeps.** The audit followed `.claude/rules/workflow.md` §2 ("no upfront sweeps") and read files directly with `Read` / `Bash` rather than dispatching Explore agents. Result: full picture of the repo built up in ~10 tool calls without burning Explore-agent tokens. Apply this discipline in remediation sessions too.
2. **plan-reviewer agent caught real bugs in v1.** The reviewer's REVISE verdict surfaced 5 critical flaws — and crucially, two **factual errors** the audit had made (claimed `audit.log` propagates to bootstrapped projects; invented a `--noninteractive` flag for `init-project.sh`). Always dispatch plan-reviewer before implementing.
3. **STOP gates beat assumed answers.** When the reviewer flagged "unverified assumptions about user intent," the fix was *not* to write better assumptions — it was to surface each one as an explicit user-question pause. This pattern is durable; reuse it.
4. **Karpathy's 4 principles map directly onto the failure modes.** Every reviewer flaw — "L disguised as M effort", "overcomplicated rewrite when paths-glob would do", "adjacent file edits unrequested" — is a violation of one of Karpathy's principles. Keep them in mind during edits.

---

## 8. What didn't work (so future sessions don't repeat it)

1. **Audit-without-reading-source.** The v1 audit asserted `bash-audit-log.sh` was "broken — fix or delete" without reading the script. It also assumed `bin/init-project.sh` had a `--noninteractive` flag (it doesn't). **Lesson:** for any finding that includes a recommendation, you must have read the relevant source before recommending.
2. **Effort underestimation.** v1 marked Session D as M effort. The reviewer correctly flagged it as L because moving rules touches `bin/init-project.sh` (load-bearing) and `docs/ASSET-LAYERS.md`. **Lesson:** any finding that touches a script that other things depend on is L by default.
3. **Skipping the Karpathy install discussion.** v1 didn't surface what the Karpathy skill is or how to install it. **Lesson:** prerequisites get their own §, not a footnote.

---

## 9. Next steps — clear action items in priority order

### Immediate (first wave, ~6–8 hr total)
1. **Session A** — gitignore/claudeignore hygiene. ~30 min. Pure subtraction. Low risk. Good first session to verify the protocol works.
2. **Session B** — fix `bash-audit-log.sh`. ~40 min. TDD discipline (writes test first). Validates that `superpowers:test-driven-development` is loaded.
3. **Session C** — move `internal_docs/` out. ~15 min.
4. **Session E** — CLAUDE.md pointer pattern + workflow.md model rewrite. ~30–45 min. Couples two coupled edits.
5. **Session F** — Verify section + `bin/verify-template.sh`. ~1.5 hr. TDD. Creates the success-criterion infrastructure for the whole audit.
6. **Session G** — `/commit` and `/pr` skills (user-confirmed). ~45 min.

### Second wave (design-heavy, ~4–6 hr)
7. **Session D** — move project-shaped rules. **L effort.** Requires user decision among 3 approaches. Touches `bin/init-project.sh`. Use `superpowers:brainstorming` to design first.
8. **Session H** — triage 16 skills-to-integrate. **L effort, multi-session.** Use agent team (4 teammates, 4 skills each, advisor pattern). Each batch = its own commit.

### Third wave (cleanup)
9. **Session I** — skill description-budget audit. ~1.5 hr.
10. **Session J** — P2 judgment calls. ~1.5 hr (or split).
11. **Session K** — final handoff. ~15 min. Updates this file's "Sessions completed" table and writes a closing summary.

### After Session K (post-remediation)
- Run `bin/verify-template.sh` to confirm green.
- Open a PR with the cumulative remediation (`gh pr create` — see plan §K).
- Schedule a re-audit in 3–6 months.

---

## 10. Reference map — where to find things

| What | Where |
|------|-------|
| The plan (executable) | `/Users/samyakjhaveri/.claude/plans/ultrathink-brainstorming-read-quiet-willow.md` |
| This handoff doc | `/Users/samyakjhaveri/Desktop/project_template/docs/audits/2026-05-11-template-health-handoff.md` |
| Target repo root | `/Users/samyakjhaveri/Desktop/project_template/` |
| Target repo's CLAUDE.md | `/Users/samyakjhaveri/Desktop/project_template/CLAUDE.md` (53 lines) |
| Always-loaded rules | `/Users/samyakjhaveri/Desktop/project_template/.claude/rules/workflow.md`, `known-issues.md` |
| Path-scoped rules | `/Users/samyakjhaveri/Desktop/project_template/.claude/rules/*.md` (each has `paths:` frontmatter) |
| Hooks (wired in settings.json) | `/Users/samyakjhaveri/Desktop/project_template/.claude/hooks/` |
| Mastery reference | `~/Documents/claude-mastery-reference/` after Session C; was at `internal_docs/` before |
| Skill stage area | `/Users/samyakjhaveri/Desktop/project_template/skills-to-integrate/` (16 dirs awaiting triage in Session H) |
| Backups during remediation | `~/Backups/project-template-session-<letter>/` |

---

## 11. Glossary (definitions repeated from the plan for self-containment)

| Term | Definition |
|------|-----------|
| CLAUDE.md | Markdown file at repo root, loaded by Claude Code every session. The "project constitution." |
| Path-scoped rule | `.claude/rules/<name>.md` with `paths: [...]` frontmatter — loads only when matching files are in scope. |
| Pointer pattern | A "Reference Docs (Read When Relevant)" section in CLAUDE.md listing other docs by condition, so Claude reads them on demand. |
| Sentinel file | `.validation_passed` — written by `/validate`, checked by pre-commit hook, deleted by edit hooks. Gates `git commit`. |
| Hook | Shell script in `.claude/hooks/` triggered by Claude Code events (PreToolUse, PostToolUse, Stop). Exit 0 = pass, 1 = warn, 2 = block. |
| Skill | `.claude/skills/<name>/SKILL.md` or plugin — reusable workflow invokable via `/<name>`. |
| Sub-agent | `.claude/agents/<name>.md` — isolated context window, custom system prompt, restricted tools. Reports back to caller. |
| Agent team | Experimental multi-agent feature (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1`). Multiple sub-agents in parallel, peer-to-peer + lead-synthesis. Used in Session H. |
| Flavor pack | `flavors/<name>/` directory overlaid by `init-project.sh` on bootstrap. Flavors: research, software-eng, ml, hpc. |
| Bootstrap | Running `bin/init-project.sh` to create a new project from this template. |
| Karpathy-check | A pre-edit pause applying the 4 Karpathy principles: state assumptions, prefer minimum change, touch only what's necessary, define verification. |

---

## 12. If you get stuck

- **Source-of-truth disagreement?** Per `workflow.md` anti-pattern #8: "the source code and test outputs are authoritative. If documentation contradicts source, verify against the source and update the documentation, never the reverse."
- **Validation fails?** Per `validation-loop.md`: "Fix loop: enter plan mode → user approval → implement → re-validate. Max 3 iterations. After 3 fails → escalate to user."
- **Session went off-rails?** STOP. Re-enter plan mode. Re-plan. Do NOT push forward (`workflow.md` anti-pattern #3).
- **Lost context after compaction?** Re-read this file + the plan file. They are designed to bootstrap a fresh session.
