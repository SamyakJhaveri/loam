# HANDOFF: Create Gated TDD Skill for Claude Code

**Date:** 2026-04-23
**Author:** Claude Code session (brainstorming + adversarial plan review + infrastructure exploration)
**Status:** Ready to implement — complete SKILL.md content provided, all design decisions finalized
**Audience:** Written for undergraduate software engineering clarity. Follow every step in order. Do not skip ahead.

---

## What Is This? (Plain English)

Claude Code has a **TDD skill** (from the "superpowers" plugin) that guides test-driven development. The problem: it lets Claude run through the entire red-green-refactor cycle **autonomously** — writing tests, running them, implementing fixes — without ever stopping to ask "is this actually what the user wants?"

This led to a **real incident**: during ParBench ablation studies, Claude used `temperature=0.0` instead of the approved `temperature=0.7`. The tests all passed internally because Claude was testing *its own assumptions*, not the user's intent. The wrong data was committed and had to be deleted.

### What You're Building

A **"Gated TDD" skill** — an augmented version of the superpowers TDD that adds 3 mandatory human checkpoints ("gates") to every TDD cycle:

1. **Gate 1: INTENT** — Before writing any test, Claude stops and asks: "Here's what I plan to test. Is this right?"
2. **Gate 2: RED** — After the test fails, Claude stops and shows: "Here's why it failed. Is this the correct failure?"
3. **Gate 3: GREEN** — After the test passes, Claude stops and shows: "Here's what I implemented. Is this correct?"

At each gate, Claude presents a **structured report** (summary table + code blocks) and uses **AskUserQuestion** (interactive multiple-choice) so the user must make an explicit choice before Claude proceeds.

### Why This Matters

Without gates, Claude is essentially a student who does homework, checks their own answers, and turns it in without showing the teacher. Gates force Claude to show its work at every step — the teacher (you) can catch mistakes like `temperature=0.0` before they become committed code.

---

## What's Already Done

| Item | Status | Details |
|------|--------|---------|
| Design brainstorming | DONE | 8 rounds of user feedback on gate format, checkpoint granularity, and options |
| Gate report format | FINALIZED | Summary table + code blocks outside table + AskUserQuestion with rich descriptions |
| Adversarial plan review | DONE | `plan-reviewer` agent found 8 issues — all addressed in the plan below |
| Infrastructure exploration | DONE | Confirmed: custom skills shadow plugin skills; hook input format is JSON via stdin; settings.json backup required |
| Complete SKILL.md content | WRITTEN | Full 580-line file ready to write — no "copy and weave" ambiguity |
| Superpowers plugin update | SKIPPED | Pinned to v5.0.7 cache — update independently later |

### What Worked

- **Iterative gate format design**: Started verbose, user asked for tables, then for code outside tables, then for compact format. Final format is clean and scannable.
- **Real incident grounding**: Using the temp=0.0 incident as a concrete example made design decisions crisp — every feature exists to prevent that specific class of error.
- **Adversarial review**: The plan-reviewer caught that "copy and weave" was not an executable instruction. The final plan now includes the complete file content.

### What Didn't Work

- **Referencing superpowers TDD instead of copying**: User explicitly rejected the "thin wrapper" approach. The skill must be self-contained with the full content, not a reference to `superpowers:test-driven-development`.
- **Verbose per-gate report formats**: User found 3 different report templates (one per gate) too heavy. Settled on one compact table template used for all 3 gates.
- **Plugin update step**: The command `claude plugins update superpowers` is unverified — no documentation confirms it exists. Removed from plan; pinned to current cached version.

---

## Skills to Load at Session Start

Before doing ANY implementation work, invoke these skills. They guide HOW you work:

```
Skill("andrej-karpathy-skills:karpathy-guidelines")  — think before coding, surgical changes, verify before claiming done
Skill("superpowers:verification-before-completion")   — verify each step before moving on
```

**After Step 2 (creating SKILL.md)**, invoke the new skill to test it:
```
Skill("test-driven-development")  — should load the gated version you just created
```

---

## Working Directory

**All commands assume:**
```bash
cd /home/samyak/Desktop/parbench_sam
source env_parbench/bin/activate
```

Run these two lines FIRST, before any other command. (The venv isn't strictly required for this task, but it's the project convention.)

---

## Step-by-Step Implementation

### Step 1: Create Skill Directory

**What:** Create the directory where the new global skill will live.

**Why:** Claude Code auto-discovers skills from `~/.claude/skills/{name}/`. A directory named `test-driven-development` with a `SKILL.md` file will automatically register as a skill and shadow the plugin version (`superpowers:test-driven-development`).

```bash
mkdir -p /home/samyak/.claude/skills/test-driven-development
```

**Verification:**
```bash
ls -la /home/samyak/.claude/skills/test-driven-development/
# Expected: empty directory exists, no errors
```

**GATE:** Directory must exist before proceeding.

---

### Step 2: Write SKILL.md (Complete Content)

**What:** Write the full Gated TDD skill file. This is the COMPLETE, FINAL content — do NOT modify it, do NOT "improve" it, do NOT add anything. Write exactly what is provided.

**Why:** This file IS the skill. When Claude invokes `test-driven-development`, this file's content is loaded as instructions.

**Action:** Write the following content to `/home/samyak/.claude/skills/test-driven-development/SKILL.md`:

<details>
<summary>The complete SKILL.md content is in the plan file. Read it from there.</summary>

**Plan file location:** `/home/samyak/.claude/plans/show-me-the-test-driven-development-vast-popcorn.md`

The complete SKILL.md content is between the ```` ```markdown ```` fence starting at approximately line 48 and ending at approximately line 582. Read the plan file and extract that content exactly.

</details>

**The content starts with this frontmatter:**
```yaml
---
name: test-driven-development
description: Gated TDD with mandatory human checkpoints at every cycle step. Use when implementing any feature or bugfix, before writing implementation code. Supersedes superpowers:test-driven-development.
---
```

**Key sections in the file (in order):**
1. Overview — adds "Gated principle" to the standard TDD overview
2. When to Use — same as superpowers, adds gate-skipping warning
3. The Iron Law — adds "NO TEST WITHOUT USER-APPROVED INTENT FIRST"
4. The 3-Gate Protocol — NEW: detailed gate report formats and AskUserQuestion options
5. Red-Green-Refactor (Gated) — modified flow diagram with gates, STOP callouts at each step
6. Good Tests — same as superpowers
7. Why Order Matters — same as superpowers
8. Common Rationalizations — superpowers table + 4 new gate-skipping rows
9. Red Flags — superpowers list + 4 new gate-specific red flags
10. Example: Bug Fix (Gated) — full worked example showing all 3 gates
11. Verification Checklist — superpowers checklist + 3 gate-specific items
12. When Stuck, Debugging Integration, Anti-Patterns, Final Rule — same as superpowers

**Verification:**
```bash
# File exists and has correct frontmatter
head -5 /home/samyak/.claude/skills/test-driven-development/SKILL.md
# Expected:
# ---
# name: test-driven-development
# description: Gated TDD with mandatory human checkpoints...
# ---

# File has gate sections
grep -c "Gate 1\|Gate 2\|Gate 3" /home/samyak/.claude/skills/test-driven-development/SKILL.md
# Expected: 9 or more matches

# File has AskUserQuestion references
grep -c "AskUserQuestion" /home/samyak/.claude/skills/test-driven-development/SKILL.md
# Expected: 6 or more matches

# File is not suspiciously short (should be ~500+ lines)
wc -l /home/samyak/.claude/skills/test-driven-development/SKILL.md
# Expected: 500+ lines
```

**GATE:** All 4 checks must pass before proceeding.

---

### Step 3: Copy Testing Anti-Patterns Companion File

**What:** Copy the testing anti-patterns reference file from the superpowers plugin to your skill directory.

**Why:** The SKILL.md references `@testing-anti-patterns.md` (a sibling-file reference). The file must exist in the same directory for the reference to resolve. We copy it verbatim rather than writing a new one — the superpowers version is comprehensive and well-maintained.

**Source file (READ ONLY):** `/home/samyak/.claude/plugins/cache/claude-plugins-official/superpowers/5.0.7/skills/test-driven-development/testing-anti-patterns.md`

**Destination:** `/home/samyak/.claude/skills/test-driven-development/testing-anti-patterns.md`

```bash
cp /home/samyak/.claude/plugins/cache/claude-plugins-official/superpowers/5.0.7/skills/test-driven-development/testing-anti-patterns.md \
   /home/samyak/.claude/skills/test-driven-development/testing-anti-patterns.md
```

**Verification:**
```bash
# Files are identical
diff /home/samyak/.claude/plugins/cache/claude-plugins-official/superpowers/5.0.7/skills/test-driven-development/testing-anti-patterns.md \
     /home/samyak/.claude/skills/test-driven-development/testing-anti-patterns.md
# Expected: no output (empty diff = files match)

# File exists and is not empty
wc -l /home/samyak/.claude/skills/test-driven-development/testing-anti-patterns.md
# Expected: ~200+ lines
```

**GATE:** Diff must be empty before proceeding.

---

### Step 4: Add PreToolUse Hook to Block Superpowers TDD

**What:** Add a hook to `~/.claude/settings.json` that blocks direct invocation of `superpowers:test-driven-development` and tells Claude to use the gated version instead.

**Why:** Even though custom skills shadow plugin skills by name, someone could explicitly invoke `superpowers:test-driven-development` (the namespaced version). This hook catches that and redirects. It's a safety net, not the primary mechanism.

**How hooks work (background for the implementer):**
- Claude Code hooks are shell commands that run before/after tool invocations
- `PreToolUse` hooks run BEFORE a tool executes
- The `matcher` field matches **tool names** (like `"Bash"`, `"Write"`, `"Skill"`), NOT skill names
- Hook input comes via **stdin** as JSON: `{"tool_name": "Skill", "tool_input": {"skill": "superpowers:test-driven-development", "args": "..."}}`
- Hook exit codes: `0` = allow, `2` = block (with stderr message shown to Claude)

**IMPORTANT — Back up settings.json first:**
```bash
cp /home/samyak/.claude/settings.json /home/samyak/.claude/settings.json.bak
```

**Hook to add:** Append this object to the existing `PreToolUse` array in `/home/samyak/.claude/settings.json`:

```json
{
  "matcher": "Skill",
  "hooks": [
    {
      "type": "command",
      "command": "INPUT=$(cat); if echo \"$INPUT\" | python3 -c \"import sys,json; d=json.load(sys.stdin); exit(0 if 'superpowers:test-driven-development' in d.get('tool_input',{}).get('skill','') else 1)\" 2>/dev/null; then echo 'BLOCKED: Use test-driven-development (gated version) instead of superpowers:test-driven-development. Invoke with skill: test-driven-development' >&2; exit 2; fi",
      "timeout": 5
    }
  ]
}
```

**Step-by-step explanation of the hook command:**
1. `INPUT=$(cat)` — reads the JSON from stdin into a variable
2. `echo "$INPUT" | python3 -c "..."` — pipes the JSON to Python for parsing
3. Python extracts `tool_input.skill` and checks if it contains `superpowers:test-driven-development`
4. If match: Python exits 0 → the `if` is true → hook prints BLOCKED message to stderr → exits 2 (block)
5. If no match: Python exits 1 → the `if` is false → hook exits normally (allow)

**Where to add it:** The `PreToolUse` key in `/home/samyak/.claude/settings.json` already has entries for `Write|Edit` and `Bash` matchers. Add this `Skill` matcher as a new entry in the same array.

**Verification:**
```bash
# Settings.json is still valid JSON
python3 -c "import json; json.load(open('/home/samyak/.claude/settings.json')); print('JSON OK')"
# Expected: JSON OK

# Hook was added correctly
python3 -c "
import json
d = json.load(open('/home/samyak/.claude/settings.json'))
hooks = d.get('hooks', {}).get('PreToolUse', [])
skill_hooks = [h for h in hooks if h.get('matcher') == 'Skill']
print(f'Skill hooks found: {len(skill_hooks)}')
if skill_hooks:
    cmd = skill_hooks[0]['hooks'][0]['command']
    print(f'Hook command starts with: {cmd[:50]}...')
    print(f'Contains superpowers check: {\"superpowers:test-driven-development\" in cmd}')
"
# Expected:
#   Skill hooks found: 1
#   Hook command starts with: INPUT=$(cat); if echo "$INPUT" | python3...
#   Contains superpowers check: True
```

**GATE:** JSON must be valid AND hook must be found before proceeding.

**Rollback if settings.json is broken:**
```bash
cp /home/samyak/.claude/settings.json.bak /home/samyak/.claude/settings.json
```

---

### Step 5: End-to-End Verification

**What:** Verify the complete integration works — skill loads, gates fire, hook blocks.

**5a. Confirm skill directory is complete:**
```bash
ls -la /home/samyak/.claude/skills/test-driven-development/
# Expected: SKILL.md and testing-anti-patterns.md, both non-empty
```

**5b. Invoke the gated skill (requires fresh Claude Code session or /clear):**
After `/clear`, the skill list should include `test-driven-development` (unprefixed). Invoke it:
```
Skill("test-driven-development")
```
The skill content should load and include "Gated TDD", "3-Gate Protocol", and "AskUserQuestion" references.

**5c. Test the hook (try invoking the superpowers version):**
```
Skill("superpowers:test-driven-development")
```
Expected: Hook blocks with message "BLOCKED: Use test-driven-development (gated version)..."

**5d. Test a real TDD cycle:**
Ask Claude to implement a trivial change (e.g., "add a function that returns 42") using TDD. Verify:
- Gate 1 fires with summary table before test is written
- Gate 2 fires with failure output after test runs
- Gate 3 fires with implementation code after test passes
- Each gate uses AskUserQuestion (not plain text "proceed?")

**If any verification step fails:** Stop and diagnose. Do NOT proceed to claim the task is done.

---

## Files Summary

| File | Action | Absolute Path |
|------|--------|---|
| Skill directory | Create | `/home/samyak/.claude/skills/test-driven-development/` |
| SKILL.md | Create (content in plan file) | `/home/samyak/.claude/skills/test-driven-development/SKILL.md` |
| Anti-patterns companion | Copy from superpowers | `/home/samyak/.claude/skills/test-driven-development/testing-anti-patterns.md` |
| Settings backup | Create before editing | `/home/samyak/.claude/settings.json.bak` |
| Settings (hooks) | Edit — add PreToolUse entry | `/home/samyak/.claude/settings.json` |

## Source Files (Read Only — Do NOT Modify)

| File | Why You Need It |
|------|----------------|
| `/home/samyak/.claude/plans/show-me-the-test-driven-development-vast-popcorn.md` | **THE PLAN** — contains the complete SKILL.md content between markdown fences (lines ~48-582) |
| `/home/samyak/.claude/plugins/cache/claude-plugins-official/superpowers/5.0.7/skills/test-driven-development/SKILL.md` | Original superpowers TDD (reference only — do NOT copy this, use the plan file content) |
| `/home/samyak/.claude/plugins/cache/claude-plugins-official/superpowers/5.0.7/skills/test-driven-development/testing-anti-patterns.md` | Source for Step 3 copy |
| `/home/samyak/.claude/plugins/cache/karpathy-skills/andrej-karpathy-skills/1.0.0/skills/karpathy-guidelines/SKILL.md` | Karpathy behavioral guidelines skill (load for implementation discipline) |
| `/home/samyak/.claude/settings.json` | Global Claude Code settings — edit carefully (has existing hooks) |

---

## What NOT To Do

| Don't | Why | Instead |
|-------|-----|---------|
| Modify the superpowers plugin files | They're in a cache directory and will be overwritten on update | Create in `~/.claude/skills/` |
| Write a "thin wrapper" that references superpowers TDD | User explicitly rejected this approach — must be self-contained | Use the complete content from the plan file |
| Skip the settings.json backup | A malformed JSON breaks ALL hooks globally | `cp settings.json settings.json.bak` first |
| "Improve" or "enhance" the SKILL.md content | The content was iteratively designed with the user over 8 rounds | Write it exactly as provided |
| Run `claude plugins update superpowers` | This command is unverified — may not exist | Plugin stays at v5.0.7, update independently later |
| Skip end-to-end verification (Step 5) | The hook mechanism is novel and untested on this machine | Must verify all 4 checks |

---

## Glossary (For Quick Reference)

| Term | Meaning |
|------|---------|
| **Gate** | A mandatory human checkpoint in the TDD cycle where Claude stops and asks for approval |
| **AskUserQuestion** | A Claude Code tool that presents interactive multiple-choice options to the user |
| **PreToolUse hook** | A shell command that runs BEFORE a Claude Code tool executes — can block the tool |
| **Custom skill** | A skill in `~/.claude/skills/` that auto-registers and takes precedence over plugin skills |
| **Plugin skill** | A skill bundled with a plugin (like superpowers) — has a namespace prefix (e.g., `superpowers:`) |
| **Shadow** | When a custom skill has the same name as a plugin skill, it "shadows" (overrides) the plugin version |
| **superpowers** | A Claude Code plugin (v5.0.7) that provides TDD, brainstorming, and other development skills |
| **Iron Law** | The TDD rule that no production code should exist without a failing test first |

---

## Design Decisions (Why Things Are The Way They Are)

These decisions were made during the brainstorming session. If you're tempted to change something, read the rationale first.

**Q: Why 3 gates and not 4 (no gate for refactor)?**
A: Refactoring is behavior-preserving cleanup. If the implementation was approved at Gate 3, refactoring doesn't introduce new assumptions. Adding a 4th gate would slow the cycle without catching a new class of error.

**Q: Why always full checkpoints, no escape hatch?**
A: The temp=0.0 incident "looked trivial" at the time. Any escape hatch would have been used to skip the exact gate that would have caught it. No exceptions means no judgment calls about when to skip.

**Q: Why AskUserQuestion instead of plain text "proceed?"?**
A: Plain text prompts can be rubber-stamped (user types "yes" without reading). AskUserQuestion forces the user to choose from structured options, each with a description of what happens next. Harder to approve without reading.

**Q: Why copy the full superpowers content instead of referencing it?**
A: The user wants a self-contained skill that works even if the superpowers plugin is updated or removed. References create a dependency; copies are independent.

**Q: Why a hook AND a custom skill (isn't shadowing enough)?**
A: Shadowing means `test-driven-development` (unprefixed) loads the gated version. But someone could explicitly invoke `superpowers:test-driven-development` (the namespaced version). The hook catches that edge case.
