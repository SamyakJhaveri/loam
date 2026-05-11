# project-template — Remediation Plan (v2, reviewer-revised)

> **Audit date:** 2026-05-11
> **Target repo:** `/Users/samyakjhaveri/Desktop/project_template`
> **For:** a fresh Claude Code session with NO prior conversation context.
> **Author note:** This plan was written by one session, adversarially reviewed by the
> `plan-reviewer` agent (verdict: REVISE), and rewritten to address every flaw. It is
> intentionally explicit — a new Claude session pasting this in should be able to
> execute sessions A → K without re-exploring the codebase to find what to do.

---

## 0. How to use this plan (READ THIS FIRST)

You are reading the *output* of a prior audit session. Your job, in this session, is **only to execute one of the remediation sessions** described below — most likely Session A (or whichever session the user names). Do not execute multiple sessions in one go. The template's own workflow rule (`.claude/rules/workflow.md` anti-pattern #4) says: *one behavior change per session.*

**Before doing anything else:**

1. Run **`/catchup`** to bootstrap your understanding of repo state. This is a skill already in `.claude/skills/catchup/SKILL.md` of the target repo.
2. Confirm with the user *which* session (A, B, C, …, K) they want you to execute.
3. **Stop** and read the "Session X" block below that matches.
4. Follow it literally. Every command, path, and verify step is spelled out.

**Skills you must have available** (verify with the user if uncertain):
- `superpowers:test-driven-development` (used in Sessions B and F)
- `superpowers:brainstorming` (only for re-planning if a session goes off-rails)
- `/handoff` (used in Session K)
- `/validate` (used at the end of every session)
- `/catchup` (used at the start of every session)
- `plan-reviewer` agent (`.claude/agents/plan-reviewer.md` — adversarial review)
- `self-critic` agent (used by `/validate` Wave 1)
- `karpathy-skills` plugin — **install in Step 0 below if not present**

---

## 1. Step 0 — Prerequisites (run ONCE before Session A)

This step installs the Karpathy skill plugin. Skip if `/plugin list` already shows `karpathy-skills`.

```bash
# Inside Claude Code, in the target repo (cwd = /Users/samyakjhaveri/Desktop/project_template):
/plugin marketplace add forrestchang/andrej-karpathy-skills
/plugin install karpathy-skills@andrej-karpathy-skills
```

**Verify:**
```bash
/plugin list | grep -i karpathy
# Expected: a line containing "karpathy-skills" with status "enabled"
```

If install fails (e.g., the repo isn't a registered marketplace), fall back to manual install:
```bash
git clone https://github.com/forrestchang/andrej-karpathy-skills.git /tmp/karpathy-skills
# Then copy /tmp/karpathy-skills/skills/* into ~/.claude/skills/ for user-level availability,
# OR into ./.claude/skills/ for project-local availability.
```

**Why Karpathy skills matter for THIS work:** Karpathy's 4 principles (Think Before Coding, Simplicity First, Surgical Changes, Goal-Driven Execution) directly mitigate the failure modes the plan-reviewer agent flagged in the v1 plan — overcomplicating remediation, touching adjacent code, making assumptions silently. Invoke whenever this plan says "Karpathy-check" — e.g., before any edit, ask: "is this the *minimum* change that fixes the finding?"

---

## 2. Glossary (for undergrad readability)

Read this once. The plan uses these terms repeatedly.

| Term | What it means |
|------|---------------|
| **CLAUDE.md** | A markdown file at the project root that Claude Code loads into context at the start of every session. Yours is at `/Users/samyakjhaveri/Desktop/project_template/CLAUDE.md` (53 lines). |
| **Pointer pattern** | A section in CLAUDE.md that lists other docs (in `.claude/rules/` or `docs/`) by their relevance condition, so Claude reads them *only when needed* rather than every session. Saves context-window tokens. |
| **Path-scoped rule** | A markdown file in `.claude/rules/` that has YAML frontmatter `paths: [...]` so Claude only loads it when working on matching files. Example: `python.md` loads only when a `*.py` file is in scope. |
| **Sentinel file** | A small file (e.g., `.validation_passed`) used to signal "this gate is open." Yours is described in `.claude/rules/validation-loop.md`. Created by `/validate`, deleted by edit hooks, checked by pre-commit hook. |
| **Hook** | A shell script in `.claude/hooks/` that runs deterministically on a Claude Code event (PreToolUse, PostToolUse, Stop, etc.). Defined in `.claude/settings.json`. Hooks block (exit 2), warn (exit 1), or pass silently (exit 0). |
| **Skill** | A markdown file under `.claude/skills/<name>/SKILL.md` (or a plugin) that defines a reusable workflow Claude can invoke via `/<name>` or auto-invocation based on its `description:` field. |
| **Agent (sub-agent)** | A markdown file in `.claude/agents/<name>.md`. Claude can delegate a task to it; the sub-agent gets its own isolated context window and reports back. |
| **Agent team** | An experimental Claude Code feature (`CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1` is already set in `.claude/settings.json`) where multiple sub-agents work in parallel, share a task list, and can talk to each other peer-to-peer. Used in Session H (skills-to-integrate triage). |
| **Flavor pack** | A directory under `flavors/<name>/` containing flavor-specific agents/skills/hooks/rules/seed-docs that `bin/init-project.sh` overlays on top of the generic `.claude/` when bootstrapping a new project. Existing flavors: `research`, `software-eng`, `ml`, `hpc`. |
| **Seed folder/doc/config** | Empty dirs (`seed-folders/`), templated docs (`seed-docs/*.tmpl`), and templated config (`seed-config/*.tmpl`) that `bin/init-project.sh` materializes into new projects at bootstrap. |
| **Bootstrap** | The act of running `bin/init-project.sh <path> --flavor <name>` to create a new project from this template. |
| **Karpathy-check** | An informal pre-edit pause to apply Karpathy's 4 principles: (a) state assumptions, (b) prefer the minimum change, (c) touch only what's necessary, (d) define how you'll verify success. |
| **Advisor pattern** | An agent-team configuration where a more-capable model (Opus) leads and less-capable models (Sonnet) work as teammates. Cheaper than all-Opus teams. |

---

## 3. Findings summary (the audit, in 1 table)

> Full details for each finding are in the v1 plan revision history. The plan-reviewer
> agent reviewed v1 and required these factual corrections, already applied here:
> (a) `audit.log` does NOT propagate to bootstrapped projects — `bin/init-project.sh:143`
> already strips it. The file is still cruft in the template's git, just not in
> bootstrapped output. (b) `init-project.sh` has no `--noninteractive` flag; it's
> non-interactive by default. (c) `bash-audit-log.sh` is a 5-line shell bug (uses
> `$CLAUDE_TOOL_INPUT` env var that's empty in Claude Code; payload comes via stdin),
> not a delete-or-fix architectural question.

| ID | Severity | One-line finding | Session |
|----|----------|------------------|---------|
| P0-1 | High | `bash-audit-log.sh` writes literal "unknown" — broken stdin parsing | B |
| P0-2 | High | `.claude/audit.log` checked into git as template cruft (does not propagate, but pollutes template repo) | A |
| P0-3 | High | Project-shaped rules (`python.md`, `architecture.md`, `tech-stack.md`, `frontend-design.md`) in template's `.claude/rules/` propagate to all bootstrapped projects | D |
| P0-4 | High | `internal_docs/claude_mastery_reference/` (large personal docx) in template repo — stripped by init-project.sh but pollutes template | C |
| P0-5 | High | `skills-to-integrate/` — 16 untracked skills staged at repo root, half-completed | H |
| P1-1 | Med | CLAUDE.md has no concrete verify commands for the template itself | F |
| P1-2 | Med | CLAUDE.md missing reference-docs pointer pattern | E |
| P1-3 | Med | `.claudeignore` too narrow — doesn't exclude internal_docs/, audit.log, skills-to-integrate/, .DS_Store | A |
| P1-4 | Med | Orphan files: `.graphifyignore` (0 bytes), committed `.DS_Store` | A |
| P1-5 | Med | No `/commit` or `/pr` skills (mastery doc §8c — most-used skills) | G |
| P1-6 | Med | `workflow.md` Opus-exclusive rule contradicts mastery doc (Haiku for transactional ops) | E |
| P1-7 | Low | `.claude/reference/Claude Code Operational Playbook.md` — unreferenced, purpose unclear | E (sub-step) |
| P2-1 | Low | 15 skill descriptions compete in the auto-invocation match space | I |
| P2-2 | Low | `dream` machinery — earning its keep? | J |
| P2-3 | Low | Validation-gate mechanism not documented in seed-docs | J |
| P2-4 | Low | `seed-config/` has only one file — possibly belongs in `software-eng` flavor | J |
| P2-5 | Low | README.md (root) not audited — may duplicate CLAUDE.md | J |

---

## 4. Per-session execution blocks

> **Universal rules for every session below:**
> 1. **First action**: run `/catchup` to refresh your understanding of repo state.
> 2. **Second action**: `cd /Users/samyakjhaveri/Desktop/project_template`. All paths below are relative to this directory unless prefixed with `/`.
> 3. **Branch**: each session works on its own branch `audit/session-<letter>`. Never on `main` directly (per CLAUDE.md line 50: "Don't push to main directly").
> 4. **Plan-review gate**: enter plan mode, write the plan, dispatch `plan-reviewer` agent on it, address feedback, then `ExitPlanMode` for user approval. Only then implement.
> 5. **Karpathy-check**: before any edit, pause and ask: minimum change? touching only what's necessary? assumptions stated?
> 6. **Verify**: every session ends by running `/validate` and the session-specific verify steps. The `.validation_passed` sentinel must exist before commit.
> 7. **Commit**: one commit per session, conventional commit format. Pre-commit gate hook (`.claude/hooks/pre-commit-gate.sh`) enforces `/validate` passed.
> 8. **Rollback**: if anything goes off-rails, `git checkout main && git branch -D audit/session-<letter>`. No work is lost — the audit doc + this plan are stable.
> 9. **Confirmation gates** (marked **STOP**): pause and ask the user before proceeding past these. The plan-reviewer agent flagged unverified assumptions that need user input.

---

### Session A — Gitignore/claudeignore hygiene + orphan file cleanup

**Goal.** Stop committing cruft (`.DS_Store`, `audit.log`, `.graphifyignore`, untriaged staging) into the template repo. Pure subtraction.

**Skills to invoke.** `/catchup`, `plan-reviewer`, `/validate`. No agent team needed.

**Effort.** S (~30 min).

**Pre-state check** (run these; you should see this exact state):
```bash
git status --short
# Expected: clean (no uncommitted changes)
git rev-parse --abbrev-ref HEAD
# Expected: main

ls -la .DS_Store .claude/.DS_Store .graphifyignore .claude/audit.log 2>&1 | grep -v "No such"
# Expected: all 4 files present
test -d skills-to-integrate && echo "EXISTS"
# Expected: EXISTS
test -d internal_docs && echo "EXISTS"
# Expected: EXISTS
```

**Branch setup:**
```bash
git checkout -b audit/session-a-gitignore-hygiene
```

**Files to edit:**

1. `/Users/samyakjhaveri/Desktop/project_template/.gitignore` — append:
```
# Audit findings 2026-05-11 (Session A)
.DS_Store
**/.DS_Store
.claude/audit.log
**/audit.log
**/*.log
.validation_passed
internal_docs/
skills-to-integrate/
```

2. `/Users/samyakjhaveri/Desktop/project_template/.claudeignore` — append:
```
# Audit findings 2026-05-11 (Session A) — exclude from Claude's context loads
.DS_Store
**/.DS_Store
.claude/audit.log
**/audit.log
internal_docs/
skills-to-integrate/
.graphifyignore
```

3. Delete orphan: `rm /Users/samyakjhaveri/Desktop/project_template/.graphifyignore` (0-byte orphan, never referenced).

**Destructive operations — backup first:**
```bash
mkdir -p ~/Backups/project-template-session-a
cp -R /Users/samyakjhaveri/Desktop/project_template/internal_docs ~/Backups/project-template-session-a/ 2>/dev/null || true
cp -R /Users/samyakjhaveri/Desktop/project_template/skills-to-integrate ~/Backups/project-template-session-a/ 2>/dev/null || true
cp /Users/samyakjhaveri/Desktop/project_template/.claude/audit.log ~/Backups/project-template-session-a/ 2>/dev/null || true
```

**Then remove from git index (files stay on disk per ignore rules but stop tracking):**
```bash
git rm --cached .claude/audit.log
git rm --cached --ignore-unmatch .DS_Store .claude/.DS_Store
# internal_docs/ and skills-to-integrate/ — only remove from index if currently tracked:
git ls-files internal_docs/ | xargs -r git rm --cached
git ls-files skills-to-integrate/ | xargs -r git rm --cached
```

**STOP — confirmation gate before commit:**
- Ask user: "Confirm `internal_docs/` and `skills-to-integrate/` should be untracked (kept on disk locally, never propagated to bootstrapped projects). Backup is at `~/Backups/project-template-session-a/`. Proceed with commit?"
- If user says no: `git restore --staged .` and re-plan.
- If user says yes: continue.

**Verify steps** (each must pass):
```bash
# 1. Ignore rules work
git check-ignore -v .DS_Store .claude/audit.log internal_docs/foo skills-to-integrate/foo
# Expected: each line matches a .gitignore rule

# 2. Tracked file list no longer contains cruft
git ls-files | grep -E "(audit\.log|DS_Store|graphifyignore|internal_docs/|skills-to-integrate/)"
# Expected: empty (no matches)

# 3. Bootstrap still works (regression check):
bin/init-project.sh /tmp/session-a-test --flavor research
test -d /tmp/session-a-test/.claude && echo "OK: .claude/ exists"
test ! -f /tmp/session-a-test/.claude/audit.log && echo "OK: audit.log stripped"
test ! -f /tmp/session-a-test/.DS_Store && echo "OK: no .DS_Store"
test -f /tmp/session-a-test/CLAUDE.md && echo "OK: CLAUDE.md rendered"
rm -rf /tmp/session-a-test
```

**Validate + commit:**
```bash
/validate
# Wait for .validation_passed to be written
git add .gitignore .claudeignore
git commit -m "chore: stop tracking template-local cruft (audit Session A)

- gitignore: .DS_Store, audit.log, internal_docs/, skills-to-integrate/
- claudeignore: same set + .graphifyignore
- Removed 0-byte orphan .graphifyignore
- Backup of removed-from-index content at ~/Backups/project-template-session-a/

Addresses audit findings P0-2, P1-3, P1-4."
```

**Rollback (if needed):** `git checkout main && git branch -D audit/session-a-gitignore-hygiene` — local backups remain in `~/Backups/`.

---

### Session B — Fix `bash-audit-log.sh` (broken stdin parsing)

**Goal.** Make the audit-log hook actually log bash commands, OR remove it. Currently it logs `<timestamp> | unknown` because it reads `$CLAUDE_TOOL_INPUT` (empty in Claude Code) instead of parsing the JSON payload on stdin.

**Skills to invoke.** `/catchup`, `superpowers:test-driven-development` (write a test that asserts the log contains a real command), `plan-reviewer`, `/validate`.

**Effort.** S (~40 min, TDD discipline).

**Pre-state check:**
```bash
git rev-parse --abbrev-ref HEAD       # Expected: main
git status --short                     # Expected: clean
cat .claude/hooks/bash-audit-log.sh    # Expected: 19 lines, reads $CLAUDE_TOOL_INPUT on line 17
test -s .claude/audit.log && tail -3 .claude/audit.log
# Expected: lines like "<timestamp> | unknown"
```

**Branch setup:** `git checkout -b audit/session-b-audit-log-fix`

**STOP — confirmation gate:**
Ask user: "The audit-log hook is currently broken (writes 'unknown'). Two options: (1) **Fix** it to log the actual bash command, or (2) **Delete** it and remove the hook wiring from `.claude/settings.json` lines 44–48. The reviewer flagged that I shouldn't assume your preference. Which?"

Branch on answer:

**Option 1 — Fix (TDD path, recommended by mastery doc §10):**

Files to edit (use `superpowers:test-driven-development` workflow — write the test first):

1. **First, write a test** at `.claude/hooks/test-bash-audit-log.sh`:
```bash
#!/usr/bin/env bash
# Test: bash-audit-log.sh logs the real command from stdin JSON
set -euo pipefail
tmpdir=$(mktemp -d)
cd "$tmpdir"
git init -q
mkdir -p .claude

# Simulate Claude Code passing JSON on stdin
INPUT='{"tool_name":"Bash","tool_input":{"command":"ls -la /tmp"}}'

echo "$INPUT" | /Users/samyakjhaveri/Desktop/project_template/.claude/hooks/bash-audit-log.sh

# Assert: audit.log contains the real command, NOT "unknown"
grep -q "ls -la /tmp" .claude/audit.log || { echo "FAIL: command not logged"; exit 1; }
! grep -q "| unknown" .claude/audit.log || { echo "FAIL: still logging 'unknown'"; exit 1; }
echo "PASS"
rm -rf "$tmpdir"
```

2. **Run the test, confirm it FAILS** (currently broken):
```bash
bash .claude/hooks/test-bash-audit-log.sh
# Expected: FAIL on first assertion
```

3. **Now fix** `.claude/hooks/bash-audit-log.sh`. Replace lines 12–17 with:
```bash
# Read stdin JSON (Claude Code passes hook payload as JSON on stdin)
PAYLOAD="$(cat)"
PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || exit 0
LOG="$PROJECT_ROOT/.claude/audit.log"
# Extract the bash command from the JSON payload. Fall back to "unparseable" if missing.
COMMAND="$(printf '%s' "$PAYLOAD" | python3 -c 'import sys, json; d=json.load(sys.stdin); print(d.get("tool_input",{}).get("command","unparseable"))' 2>/dev/null || echo "unparseable")"
echo "$(date -Iseconds) | $COMMAND" >> "$LOG"
```

4. **Re-run test, confirm it PASSES:**
```bash
bash .claude/hooks/test-bash-audit-log.sh
# Expected: PASS
```

5. **Truncate old garbage log** so future entries are clean:
```bash
> .claude/audit.log  # Truncate. (Or git rm if you completed Session A first.)
```

**Option 2 — Delete (if user prefers):**
```bash
rm .claude/hooks/bash-audit-log.sh
# Edit .claude/settings.json — remove the hook entry at lines 44-48 (the second
# command block under the "Bash" PreToolUse matcher). Keep the first block (rm -rf guard).
```

**Verify after either option:**
```bash
# Option 1 verify:
bash .claude/hooks/test-bash-audit-log.sh   # PASS
# Then trigger a real bash via Claude and confirm log entry is real:
# (After running this plan's next `git status`)
tail -1 .claude/audit.log
# Expected: "<timestamp> | git status" (not "unknown")

# Option 2 verify:
test ! -f .claude/hooks/bash-audit-log.sh && echo "OK: deleted"
grep -c "bash-audit-log" .claude/settings.json
# Expected: 0
```

**Validate + commit:**
```bash
/validate
git add .claude/hooks/ .claude/settings.json .claude/audit.log
git commit -m "fix(hooks): bash-audit-log.sh — parse JSON stdin, not empty env var

Old code read \$CLAUDE_TOOL_INPUT which is not set by Claude Code (payload
arrives via stdin as JSON). All previous entries logged 'unknown'.

Fix: pipe stdin through python3 json parser; extract .tool_input.command.
Truncated stale log. Added regression test at hooks/test-bash-audit-log.sh.

Addresses audit finding P0-1."
```

**Rollback:** `git checkout main && git branch -D audit/session-b-audit-log-fix`.

---

### Session C — Move `internal_docs/` out of repo

**Goal.** The personal mastery-reference docx is template-private content. Move it to your personal docs and stop committing it.

**Skills to invoke.** `/catchup`, `/validate`.

**Effort.** S (~15 min).

**Pre-state check:**
```bash
test -d internal_docs && du -sh internal_docs
# Expected: a directory, several MB (the docx is ~50KB but other files may exist)
git ls-files internal_docs/ | head -5
# Expected: lists internal_docs/claude_mastery_reference/-[HUMAN]_claude-code-mastery-reference.docx and any siblings
```

**Branch setup:** `git checkout -b audit/session-c-move-internal-docs`

**STOP — confirmation gate:**
Ask user: "Move `internal_docs/` to `~/Documents/claude-mastery-reference/` (or another personal-archive location of your choice)? Or keep on disk in the project but make sure it's gitignored?"

**Action (default — move out, recommended):**
```bash
mkdir -p ~/Documents/claude-mastery-reference
mv internal_docs/* ~/Documents/claude-mastery-reference/
rmdir internal_docs  # Empty after move
# If Session A already completed: internal_docs/ is already in .gitignore — that's fine.
# Otherwise the next session-A run will add it.
```

If Session A is NOT yet done, also untrack:
```bash
git rm -r --cached internal_docs/   # Will error if Session A already untracked — that's fine
```

**Verify:**
```bash
test ! -d /Users/samyakjhaveri/Desktop/project_template/internal_docs && echo "OK: dir gone"
test -d ~/Documents/claude-mastery-reference && echo "OK: archived"
ls ~/Documents/claude-mastery-reference/  # Confirm contents arrived

# Bootstrap regression check:
bin/init-project.sh /tmp/session-c-test --flavor research
test ! -d /tmp/session-c-test/internal_docs && echo "OK: not in bootstrapped project"
rm -rf /tmp/session-c-test
```

**Validate + commit:**
```bash
/validate
git add -A   # Will record the deletion of internal_docs/ from tree
git commit -m "chore: move internal_docs/ to personal archive (audit Session C)

Personal mastery reference moved to ~/Documents/claude-mastery-reference/.
Stays available locally; no longer tracked in the template repo.

Addresses audit finding P0-4."
```

**Rollback:** restore from `~/Documents/claude-mastery-reference/` back into the repo.

---

### Session D — Move project-shaped rules out of template's `.claude/`

**Goal.** Rules like `python.md`, `architecture.md`, `tech-stack.md`, `frontend-design.md` are concrete and opinionated (e.g., Python 3.12+, snake_case, "Inter font", "8pt grid"). They live in `.claude/rules/` and `init-project.sh:137` does `cp -R .claude/.` — so they leak verbatim into every bootstrapped project. Move them to either `seed-folders/.claude/rules/` (so they only seed) or to specific flavors.

**Skills to invoke.** `/catchup`, `superpowers:brainstorming` (this is non-trivial design), `plan-reviewer` agent (mandatory — touches `bin/init-project.sh`), `/validate`.

**Effort.** **L** (~2.5–4 hr). Reviewer reclassified from M to L because `bin/init-project.sh`, `docs/ASSET-LAYERS.md`, and possibly `template-manifest.schema.json` all need updates.

**Pre-state check:**
```bash
ls .claude/rules/
# Expected: architecture.md  frontend-design.md  known-issues.md  python.md  tech-stack.md  validation-loop.md  workflow.md

# Confirm which rules ARE generic (keep in template's .claude/) vs project-shaped (move):
grep -l "TBD\|<!--" .claude/rules/*.md
# Generic rules will have placeholders; project-shaped rules have concrete content.

# Inspect init-project.sh's rule-copy mechanism:
grep -n -A2 "rules" /Users/samyakjhaveri/Desktop/project_template/bin/init-project.sh
# Expected: line ~137 cp -R .claude/.  +  line ~173-178 flavor overlay loop for "rules"
```

**STOP — confirmation gate (CRITICAL):**

Read `bin/init-project.sh` lines 134–181 end-to-end. The reviewer flagged this as a hidden-scope risk: the design choice is significant.

Ask user to pick one of three approaches:

**Approach 1 — Move to `seed-folders/.claude/rules/` (cleanest separation, biggest change to init-project.sh).**
- `seed-folders/.claude/rules/python.md` etc. would need a new copy step in `init-project.sh` after the `.claude/` cp.
- Pro: rules live with seeds; clearly labelled as "for new projects only."
- Con: `init-project.sh` gains a new code path.

**Approach 2 — Move to flavor packs (most semantically honest).**
- `python.md` → `flavors/software-eng/.claude/rules/python.md` and `flavors/ml/.claude/rules/python.md`
- `architecture.md` and `tech-stack.md` (Python-shaped) → `flavors/software-eng/.claude/rules/`
- `frontend-design.md` → `flavors/software-eng/.claude/rules/` (or a future `web` flavor)
- Pro: opt-in via `--flavor`. Flavor pack overlay loop at `init-project.sh:173-178` already handles this — no script change needed.
- Con: a no-flavor bootstrap gets ZERO concrete rules (only generic ones remain). User must always pick a flavor.

**Approach 3 — Use `paths:` frontmatter to gate (simplest, reviewer-suggested simpler alternative).**
- Add `paths: ['!/Users/samyakjhaveri/Desktop/project_template/**']` (negation pattern) to each project-shaped rule.
- Pro: zero file moves, zero script changes. Rules still propagate via `cp -R` but only LOAD when the destination is a project, not when you're editing the template.
- Con: bootstrapped projects still receive Python-specific rules even if the project isn't Python. Doesn't fix the propagation, only the local-editing pollution.

**Recommended:** Approach 2 (flavor packs) is the most honest given the template's flavor design. But it's the most work. Approach 3 is fastest if the primary complaint is "rules load when I'm editing the template itself." Discuss with user, pick one, then proceed.

**After user picks an approach, write a fresh sub-plan** (use `superpowers:brainstorming` to design it, `plan-reviewer` to review), get approval, then execute. **Do NOT short-cut this** — the plan-reviewer specifically flagged this as L-effort because `bin/init-project.sh` is the load-bearing infrastructure.

**Verify (after implementation, regardless of approach):**
```bash
# 1. Test bootstrap without flavor:
bin/init-project.sh /tmp/session-d-no-flavor
ls /tmp/session-d-no-flavor/.claude/rules/
# Expected (Approach 2): only generic rules (workflow.md, known-issues.md, validation-loop.md)
# Expected (Approach 1 or 3): all rules present

# 2. Test bootstrap with software-eng flavor:
bin/init-project.sh /tmp/session-d-swe --flavor software-eng
ls /tmp/session-d-swe/.claude/rules/
# Expected: includes python.md, tech-stack.md, etc.

# 3. Cleanup:
rm -rf /tmp/session-d-no-flavor /tmp/session-d-swe

# 4. Confirm template's OWN .claude/rules/ doesn't have project-shaped rules anymore (Approaches 1 & 2):
ls .claude/rules/ | grep -E "(python|architecture|tech-stack|frontend-design)"
# Expected (Approaches 1 & 2): empty
# Expected (Approach 3): files present but with negation-glob frontmatter
```

**Validate + commit** (commit message must name the approach):
```bash
/validate
git add -A
git commit -m "refactor(rules): move project-shaped rules per Approach <N> (audit Session D)

<describe approach + what moved where>

Addresses audit finding P0-3."
```

**Update `docs/ASSET-LAYERS.md`** to reflect the new placement (this is part of the session, not a follow-up).

**Rollback:** `git checkout main && git branch -D audit/session-d-move-rules`. The rule files are still in git history.

---

### Session E — CLAUDE.md pointer pattern + workflow.md model-selection rewrite + `.claude/reference/` triage

**Goal.** Three coupled CLAUDE.md / rules edits:
1. Add a "Reference Docs (Read When Relevant)" pointer block to CLAUDE.md (mastery doc §7a pattern).
2. Rewrite `workflow.md`'s model-selection section to match mastery-doc model-routing (Haiku for transactional, Sonnet for advisor-pattern teammates, Opus for main).
3. Decide what to do with `.claude/reference/Claude Code Operational Playbook.md` (link from CLAUDE.md, integrate into rules, or delete).

**Skills to invoke.** `/catchup`, `plan-reviewer` (mandatory for the workflow.md rewrite — touches a load-bearing rule), `/validate`.

**Effort.** S (~30–45 min).

**Pre-state check:**
```bash
grep -n "Reference Docs" CLAUDE.md   # Expected: empty (no such section yet)
grep -n "Opus exclusively" .claude/rules/workflow.md
# Expected: 1 match around line 80-85
test -f .claude/reference/Claude\ Code\ Operational\ Playbook.md && echo "EXISTS"
```

**STOP — confirmation gate:**
Ask user about the Opus-exclusive rule:
"`.claude/rules/workflow.md` line ~83 says 'All modes → use Opus exclusively. Exception: user may switch to Haiku for commit/push.' The mastery doc (§9b, §8c) recommends Haiku for transactional ops, Sonnet for advisor-pattern team workers, Opus for main sessions. Did you set the Opus-exclusive rule deliberately (e.g., for cost-predictability, quality-floor) — or was it a default that should be relaxed?"

If user says deliberate → SKIP the workflow.md rewrite, do only the pointer pattern.
If user says relax → proceed with rewrite below.

**Branch setup:** `git checkout -b audit/session-e-claudemd-and-workflow`

**Files to edit:**

1. **`CLAUDE.md`** — append after line 45 (after the Layout table):
```markdown
## Reference Docs (Read When Relevant)

Path-scoped rules in `.claude/rules/` load only when matching files are touched.
Read these on demand:

- Workflow + anti-patterns: `.claude/rules/workflow.md` *(always loaded)*
- Known gotchas: `.claude/rules/known-issues.md` *(always loaded)*
- Validation protocol: `.claude/rules/validation-loop.md` *(when working on hooks/validate skill)*
- Asset layering: `docs/ASSET-LAYERS.md` *(when adding or moving template assets)*
- Bootstrap mechanics: `docs/BOOTSTRAP.md` *(when editing `bin/init-project.sh`)*
- Sync mechanics: `docs/SYNC.md` *(when promoting an asset)*
- Operational playbook: `.claude/reference/Claude Code Operational Playbook.md` *(when designing new skills/agents)*
```

2. **`.claude/rules/workflow.md`** — replace the "Model Selection" section (currently ~3 lines around L83) with:
```markdown
## Model Selection

| Workload | Model | Why |
|----------|-------|-----|
| Main interactive session | Opus | Default — best reasoning for planning + design |
| `/commit`, `/pr`, `/format`, transactional git ops | Haiku | Fast, cheap, deterministic operations |
| Agent team teammates (advisor pattern) | Sonnet | Opus lead + Sonnet workers — cost-effective parallel execution |
| Agent team teammates (deep-reasoning mode) | Opus | All-Opus override for complex investigations |
| Sub-agents (one-shot exploration) | Sonnet or Opus | Sonnet by default; Opus for tasks requiring deep reasoning |

Use the `/model-route` skill if uncertain — it advises per-task.
```

3. **`.claude/reference/Claude Code Operational Playbook.md`** — read it (you didn't in the audit). Then:
   - If it duplicates the mastery doc: delete it, replace with a 1-line stub pointing to `~/Documents/claude-mastery-reference/`.
   - If it has unique content: link from CLAUDE.md's "Reference Docs" block (already in step 1 above).
   - Either way: commit the decision.

**Verify:**
```bash
# 1. CLAUDE.md still under 200 lines
wc -l CLAUDE.md
# Expected: < 90 lines (was 53, adding ~15)

# 2. Pointer block parses
grep -c "Reference Docs (Read When Relevant)" CLAUDE.md
# Expected: 1

# 3. workflow.md model section matches new shape
grep -c "Sonnet" .claude/rules/workflow.md
# Expected: >= 2 (was 1)

# 4. /model-route skill still loadable
test -f .claude/skills/model-route/SKILL.md && echo "OK"
```

**Validate + commit:**
```bash
/validate
git add CLAUDE.md .claude/rules/workflow.md .claude/reference/
git commit -m "docs: CLAUDE.md pointer pattern + workflow.md model-selection rewrite

- CLAUDE.md: added 'Reference Docs (Read When Relevant)' section (mastery doc §7a)
- workflow.md: relaxed Opus-exclusive rule per user direction; table of model routing
- .claude/reference/: <kept|deleted|relinked> per audit Session E sub-step

Addresses audit findings P1-2, P1-6, P1-7."
```

**Rollback:** `git checkout main && git branch -D audit/session-e-claudemd-and-workflow`.

---

### Session F — Add Verify section to CLAUDE.md + a verify script for the template

**Goal.** Mastery doc §11 calls verification feedback loops "the single highest-leverage thing." The template has no concrete verify command for itself. Add one.

**Skills to invoke.** `/catchup`, `superpowers:test-driven-development` (write the verify script test-first), `plan-reviewer`, `/validate`.

**Effort.** M (~1.5 hr).

**Pre-state check:**
```bash
grep -n "Build & Verify\|## Verify" CLAUDE.md   # Expected: empty
ls bin/   # Expected: add-flavor.sh  init-project.sh  template-sync.sh
test -f bin/verify-template.sh && echo "EXISTS"   # Expected: not exists
```

**STOP — confirmation gate:**
Ask user: "What should the verify script check? Suggested: (a) bootstrap a test project with no flavor + each of the 4 flavors, (b) confirm bootstrapped projects have valid `.claude/settings.json` (jq parses), (c) shellcheck `bin/*.sh` and `.claude/hooks/*.sh`. Add/remove?"

**Branch setup:** `git checkout -b audit/session-f-verify`

**TDD path:**

1. **Write the verify script's test first** at `bin/test-verify-template.sh`:
```bash
#!/usr/bin/env bash
# Test: verify-template.sh exits 0 on a clean template, exits 1 if bootstrap is broken.
set -euo pipefail
EXPECTED_FLAVORS=(research software-eng ml hpc)

# Run the verify script
bash bin/verify-template.sh > /tmp/verify-out.log 2>&1 || { cat /tmp/verify-out.log; exit 1; }

# Assert: every flavor was checked
for f in "${EXPECTED_FLAVORS[@]}"; do
  grep -q "OK: flavor $f" /tmp/verify-out.log || { echo "FAIL: flavor $f not verified"; exit 1; }
done
echo "PASS"
```

2. **Run the test, confirm FAIL** (script doesn't exist yet).

3. **Implement** `bin/verify-template.sh`:
```bash
#!/usr/bin/env bash
# verify-template.sh — sanity-check that bootstrapping produces valid projects.
set -euo pipefail
TMP=$(mktemp -d); trap "rm -rf $TMP" EXIT

# (a) Shellcheck if available
if command -v shellcheck >/dev/null; then
  shellcheck bin/*.sh .claude/hooks/*.sh || { echo "FAIL: shellcheck"; exit 1; }
  echo "OK: shellcheck"
fi

# (b) Bootstrap with no flavor
bin/init-project.sh "$TMP/no-flavor" >/dev/null
test -f "$TMP/no-flavor/CLAUDE.md"           || { echo "FAIL: no CLAUDE.md"; exit 1; }
test -f "$TMP/no-flavor/.claude/settings.json" || { echo "FAIL: no settings.json"; exit 1; }
python3 -m json.tool "$TMP/no-flavor/.claude/settings.json" >/dev/null || { echo "FAIL: invalid settings.json"; exit 1; }
test ! -f "$TMP/no-flavor/.claude/audit.log" || { echo "FAIL: audit.log propagated"; exit 1; }
echo "OK: flavor (none)"

# (c) Bootstrap with each flavor
for flavor in research software-eng ml hpc; do
  bin/init-project.sh "$TMP/$flavor" --flavor "$flavor" >/dev/null
  test -f "$TMP/$flavor/.claude/settings.json" || { echo "FAIL: $flavor missing settings.json"; exit 1; }
  echo "OK: flavor $flavor"
done

echo "ALL OK"
```

4. **Make executable:** `chmod +x bin/verify-template.sh`

5. **Run test, confirm PASS:** `bash bin/test-verify-template.sh`

6. **Add a `## Verify` section to CLAUDE.md** (after the "Reference Docs" block from Session E):
```markdown
## Verify

```bash
# Sanity-check the template end-to-end (bootstraps all 4 flavors, parses JSON):
bin/verify-template.sh
# Expected: ALL OK on the last line.

# Run before any PR that touches bin/, .claude/, flavors/, or seed-*/.
```
```

**Verify:**
```bash
bash bin/test-verify-template.sh   # Expected: PASS
bin/verify-template.sh             # Expected: ALL OK
grep -c "## Verify" CLAUDE.md      # Expected: 1
wc -l CLAUDE.md                    # Expected: < 110 lines
```

**Validate + commit:**
```bash
/validate
git add bin/verify-template.sh bin/test-verify-template.sh CLAUDE.md
git commit -m "feat(verify): add bin/verify-template.sh + test + CLAUDE.md Verify section

Bootstraps each flavor end-to-end, validates settings.json with python json.tool,
shellchecks scripts. Test-driven (test written first).

Addresses audit finding P1-1."
```

**Rollback:** `git checkout main && git branch -D audit/session-f-verify`.

---

### Session G — Add `/commit` and `/pr` skills

**Goal.** Add the two highest-frequency skills from mastery doc §8c. Haiku-modeled, with inline-bash pre-computed git context.

**Skills to invoke.** `/catchup`, `plan-reviewer`, `/validate`.

**Effort.** S (~45 min).

**STOP — confirmation gate:**
Ask user: "Mastery doc recommends `/commit` and `/pr` skills as Haiku-modeled fire-and-forget. Want both, or just one, or neither? Also: should they be project-local (`.claude/skills/`) or user-level (`~/.claude/skills/`)?"

Skip session if user says neither.

**Branch setup:** `git checkout -b audit/session-g-commit-pr-skills`

**Files to create:**

1. `.claude/skills/commit/SKILL.md`:
```markdown
---
name: commit
description: Create a conventional commit. Use when user says "commit", "make a commit", or "save changes".
model: haiku
allowed-tools:
  - Bash(git add:*)
  - Bash(git commit:*)
  - Bash(git status:*)
  - Bash(git diff:*)
argument-hint: "[optional commit message override]"
---

<git_status>
!`git status --short`
</git_status>

<staged_diff>
!`git diff --cached`
</staged_diff>

1. Review the staged diff above.
2. Write a Conventional Commit message: feat: / fix: / chore: / docs: / refactor: / test: / perf:
3. If `$ARGUMENTS` is provided, use it as the commit subject.
4. Format: `<type>(<optional-scope>): <subject>` — subject under 72 chars.
5. Run: `git commit -m "<message>"`
6. Run: `git status` to confirm clean state.
7. Output the commit hash and message.
```

2. `.claude/skills/pr/SKILL.md`:
```markdown
---
name: pr
description: Push and open a GitHub PR. Use when user says "open a PR", "create a pull request", or "push and PR".
model: haiku
allowed-tools:
  - Bash(git push:*)
  - Bash(git log:*)
  - Bash(gh pr create:*)
  - Bash(gh pr view:*)
---

<recent_commits>
!`git log --oneline -10 --no-merges`
</recent_commits>

<branch>
!`git branch --show-current`
</branch>

1. Push: `git push -u origin HEAD`.
2. Write PR title: type + concise description (under 72 chars).
3. Write PR body: what changed, why, how to test, risks.
4. Run: `gh pr create --title "<title>" --body "<body>"`.
5. Output PR URL.

If push fails: stop and report the exact error. Do NOT force push.
```

**Karpathy-check:** Both skills above are *minimum* — they don't include speculative features (no auto-tagging, no auto-changelog, no auto-reviewers). That matches "Simplicity First."

**Verify:**
```bash
test -f .claude/skills/commit/SKILL.md && echo "OK: commit"
test -f .claude/skills/pr/SKILL.md     && echo "OK: pr"
# After Claude reloads skills (may need a /clear or new session):
/commit help   # Expected: skill triggers, asks for staged diff
```

**Validate + commit:**
```bash
/validate
git add .claude/skills/commit/ .claude/skills/pr/
git commit -m "feat(skills): add /commit and /pr (Haiku-modeled, mastery doc §8c)

Pre-computed git status/diff via inline-bash. Conventional Commit format.
PR skill uses gh CLI. Both restrict allowed-tools to relevant bash patterns.

Addresses audit finding P1-5."
```

**Rollback:** `git checkout main && git branch -D audit/session-g-commit-pr-skills`.

---

### Session H — Triage `skills-to-integrate/` (USE AGENT TEAM)

**Goal.** 16 candidate skills are staged at `skills-to-integrate/`. Decide each: integrate into `.claude/skills/`, move to a flavor, or delete.

**Skills to invoke.** `/catchup`, **`agent-team`** (parallelizes 16 independent decisions), `plan-reviewer` (for any decision that promotes a skill), `/validate`.

**Effort.** L (multi-session, ~4–6 hr total — even with agent team).

**Pre-state check:**
```bash
ls skills-to-integrate/
# Expected: council create-skill decision-matrix frontend-design know-me process-optimizer
#           prompt-improver researcher scalability security self-healing skill-builder
#           sop-writer weekly-review workflow-mapper

# Verify agent teams are enabled:
grep CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS .claude/settings.json
# Expected: "1"
```

**STOP — confirmation gate:**
Ask user: "16 skills to triage. Approach options:
(1) **One agent team, all 16 in parallel** — Opus lead + Sonnet teammates (advisor pattern). Each teammate gets 4 skills to decide on. Lead synthesizes.
(2) **Sequential, one skill per micro-session** — slower but each decision is reviewable.
(3) **Bulk-delete unfamiliar, keep only ones you recognize** — fastest, lossy.
Which?"

**Approach 1 (recommended):** spawn agent team.

**Backup first (mandatory before any deletion):**
```bash
cp -R skills-to-integrate ~/Backups/skills-to-integrate-$(date +%Y%m%d)/
echo "Backup at: ~/Backups/skills-to-integrate-$(date +%Y%m%d)/"
```

**Spawn agent team** (the `agent-team` skill at `.claude/skills/agent-team/SKILL.md` defines the protocol; read it first). Use this team-spawn prompt verbatim:

> Spawn an agent team of 4 teammates (Opus lead + 3 Sonnet workers, advisor pattern) to triage the 16 directories in `/Users/samyakjhaveri/Desktop/project_template/skills-to-integrate/`. Distribute 4 skills per teammate. Each teammate produces, for its assigned skills:
> 1. Read `SKILL.md` if it exists; report the `description:` field.
> 2. Grep `.claude/skills/` for any existing skill that overlaps (search the description field + name).
> 3. Verdict (one of): `KEEP-GENERIC` (move into `.claude/skills/`), `KEEP-FLAVOR-<name>` (move into `flavors/<name>/skills/`), `DELETE-DUPLICATE` (overlaps with existing X), `DELETE-EMPTY` (no SKILL.md or empty body), `ESCALATE` (cannot decide without user input).
> 4. One-sentence justification.
>
> Lead synthesizes a single decision table. Each row = one skill. Lead does NOT execute moves/deletes — only proposes the table. User reviews and approves before any file action.

**STOP after team returns:** review the decision table with the user. For each `ESCALATE`, ask. For each `DELETE-*`, confirm.

**Execute the approved actions** in micro-batches (commit one batch per ~4 skills):
```bash
# KEEP-GENERIC moves:
git mv skills-to-integrate/<skill> .claude/skills/<skill>

# KEEP-FLAVOR moves:
mkdir -p flavors/<flavor>/skills/
git mv skills-to-integrate/<skill> flavors/<flavor>/skills/<skill>

# DELETE actions (only after user confirmation):
git rm -r skills-to-integrate/<skill>
```

**Verify per batch:**
```bash
# 1. Backup is intact:
ls ~/Backups/skills-to-integrate-*/ | wc -l   # Expected: 16

# 2. Bootstrap regression:
bin/verify-template.sh   # (after Session F is done) — expected ALL OK
# OR:
bin/init-project.sh /tmp/session-h-test --flavor research --flavor software-eng
ls /tmp/session-h-test/.claude/skills/   # Inspect — does the bootstrapped project get expected skills?
rm -rf /tmp/session-h-test
```

**Validate + commit** (one commit per batch — see workflow.md anti-pattern #4):
```bash
/validate
git add -A
git commit -m "refactor(skills): triage batch <N> of skills-to-integrate/ (audit Session H)

<list of decisions: moved, deleted, escalated>
Backup retained at ~/Backups/skills-to-integrate-<date>/.

Addresses audit finding P0-5."
```

**Rollback any batch:** `git checkout main -- .` then restore from `~/Backups/skills-to-integrate-<date>/`.

---

### Session I — Skill description-budget audit

**Goal.** 15 active skills compete in the auto-invocation match space. Some may overlap. Narrow descriptions or fold duplicates.

**Skills to invoke.** `/catchup`, `plan-reviewer` for any narrowing/deletion, `/validate`.

**Effort.** M (~1.5 hr).

**Pre-state check:**
```bash
ls .claude/skills/
# Expected: 15 directories (or whatever Session H left)
for f in .claude/skills/*/SKILL.md; do
  echo "=== $f ==="; head -5 "$f"
done | head -100
```

**STOP — confirmation gate:** review each skill's `description:` with the user. Re-examine:
- `grill-research` vs `plan-reviewer` agent — overlap?
- `reflect` vs CLAUDE.md self-update loop — overlap?
- `session-critique` vs `review` + `validate` — overlap?
- `dream` vs `reflect` — overlap?

For each overlap candidate, ask user: "Keep both (narrow descriptions), fold A into B, or delete A?"

**Action:** edit each affected `SKILL.md` to narrow the `description:` field (more conditional language: "Use ONLY when X and not Y"). Or `git rm -r` if user chose deletion.

**Verify:**
```bash
ls .claude/skills/ | wc -l   # New count
# For each surviving skill, confirm description is conditional:
for f in .claude/skills/*/SKILL.md; do
  grep -A2 "description:" "$f" | head -3
done
```

**Validate + commit:** standard pattern. Commit msg: "refactor(skills): narrow descriptions / fold duplicates (audit Session I)".

---

### Session J — P2 judgment calls (small batch)

**Goal.** Address P2-2 (dream machinery), P2-3 (document validation-gate in seed-docs), P2-4 (`seed-config/` → flavor?), P2-5 (read README.md, fold or prune).

**Skills to invoke.** `/catchup`, `plan-reviewer` for any deletion, `/validate`.

**Effort.** M (~1.5 hr if done together, S each if split).

**STOP — confirmation gate per item:**
- P2-2: "Is `dream` skill earning its keep? Run `grep -r dream-hook .claude/` — how often does it fire? Keep, move to user-level (`~/.claude/`), or delete?"
- P2-3: "Add a 1-paragraph mention of `.validation_passed` and the pre-commit gate to `seed-docs/CLAUDE.md.tmpl` so new projects discover it?"
- P2-4: "Should `seed-config/pyproject.toml.tmpl` move to `flavors/software-eng/seed-config/`? It's Python-specific."
- P2-5: "I haven't read README.md. May overlap with CLAUDE.md. Read together?"

**Action:** per user direction. Each item is its own commit.

**Verify:** `/validate` + standard verify pattern. No new scripts.

---

### Session K — Final handoff

**Goal.** Use the `/handoff` skill to write a completion doc that another future session (or you, in 3 months re-running this audit) can pick up.

**Skills to invoke.** `/catchup`, **`/handoff`**, `/validate`.

**Effort.** S (~15 min).

**Pre-state check:**
```bash
# Are sessions A–J done?
git log --oneline | grep -E "audit Session [A-J]"
# Expected: a line per completed session
```

**Action — invoke `/handoff` with this directive:**

> Use the `/handoff` skill to write a handoff document at `docs/audits/2026-05-11-template-health-handoff.md`. The document should include:
> 1. **Summary**: which audit findings were addressed (P0-X, P1-X, P2-X) — list completed sessions.
> 2. **Outstanding**: which findings were skipped or deferred and why.
> 3. **Verification status**: confirm `bin/verify-template.sh` passes (run it and paste the output).
> 4. **Decision log**: for each `STOP` confirmation gate, what the user decided and why.
> 5. **Next audit**: suggest a re-audit date 3–6 months out and what to watch for.
> 6. **Refer back to**: `/Users/samyakjhaveri/.claude/plans/ultrathink-brainstorming-read-quiet-willow.md` (this plan) as the source artifact.

**Verify:**
```bash
test -f docs/audits/2026-05-11-template-health-handoff.md && echo "OK"
bin/verify-template.sh && echo "OK: template still green"
```

**Validate + commit:**
```bash
/validate
git add docs/audits/
git commit -m "docs(audit): completion handoff for 2026-05-11 template-health audit

Summary of all completed remediation sessions, outstanding items, decision log,
and next-audit guidance.

Addresses audit Session K."
```

**Push (optional, ask user):**
Per CLAUDE.md line 50 ("Don't push to main directly"), open a PR instead:
```bash
gh pr create --title "Audit remediation 2026-05-11" --body "$(cat docs/audits/2026-05-11-template-health-handoff.md)"
```

---

## 5. Suggested execution order (with dependencies)

```
A ──┐
    ├── E (depends on A only loosely)
B   │
    │
C ──┘
        ├── D (Approach 2 also depends on no flavor breakages → run after F is ideal)
        │
F ──────┤
        │
G ──────┤
        │
H ──────┤   (uses agent-team; can run after A/B/C done)
        │
I ──────┘
        │
J        (any time)
        │
K        (final, requires everything else done)
```

**Quickest first wave** (P0/P1 in ~6–8 hr total of focused sessions): **A → B → C → E → F → G**. Defer D (L-effort, design decision needed) and H (multi-session) to a second wave.

---

## 6. Things the v1 audit got WRONG (corrections applied here)

The plan-reviewer agent and a re-read of source files caught these errors in the original audit. Calling them out for transparency:

1. **`audit.log` does NOT propagate to bootstrapped projects.** `bin/init-project.sh:143` strips it explicitly. The file is still cruft in the *template's git* but doesn't leak into new projects. The v1 plan claimed propagation. Fixed.
2. **`bin/init-project.sh` has no `--noninteractive` flag.** The v1 plan invented one for the Verify section. The script is non-interactive by default. Fixed (Session F's verify script doesn't use the flag).
3. **`bash-audit-log.sh` is a 5-line shell bug** — uses empty `$CLAUDE_TOOL_INPUT` env var instead of parsing stdin JSON. The v1 plan called it "broken, fix or delete" without reading the file. Now Session B has the exact replacement code + TDD test.

---

## 7. Appendix — skill+agent inventory used by this plan

| Asset | What it does in this plan |
|-------|---------------------------|
| `/catchup` | First action every session; refreshes state |
| `/handoff` | Final action (Session K) — writes completion doc |
| `/validate` | End-of-session gate; writes `.validation_passed` sentinel |
| `superpowers:test-driven-development` | Sessions B & F — write test first |
| `superpowers:brainstorming` | Session D — when user needs to design the approach |
| `plan-reviewer` agent | Before every implementation — adversarial review |
| `self-critic` agent | Used by `/validate` Wave 1 |
| `agent-team` skill | Session H — parallel triage of 16 skills |
| `karpathy-skills` plugin | Always loaded; informs "minimum change" discipline |
| `/model-route` skill | Session E reference — model-selection advisor |

---

## 8. Where this plan should live after approval

Recommended destination: `/Users/samyakjhaveri/Desktop/project_template/docs/audits/2026-05-11-template-health.md`.

- `docs/` is already the canonical template-documentation location (CLAUDE.md line 33).
- `audits/` dated subdirectory lets future audits diff against this one.
- After the file is in place, Session K's handoff doc lives alongside as `2026-05-11-template-health-handoff.md`.
- Do NOT keep this plan only in `~/.claude/plans/` — that's a transient runtime location. Promote it.

The very first session (probably Session A) should start by `cp /Users/samyakjhaveri/.claude/plans/ultrathink-brainstorming-read-quiet-willow.md docs/audits/2026-05-11-template-health.md && git add docs/audits/ && git commit -m "docs(audit): import 2026-05-11 template-health audit plan"` as a prelude, so the plan is durable in the repo before any remediation commits land.
