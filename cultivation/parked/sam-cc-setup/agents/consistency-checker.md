---
name: consistency-checker
description: "Cross-checks documentation against code. Detects stale claims in CLAUDE.md, contradictions between agent tables and actual files, missing rules-table entries, competing controlling-plan claims, and undocumented changes. Use in the project's post-session validation pass. Returns structured PASS/FAIL. Reports every finding, most severe first."
tools: Bash, Read, Glob, Grep
model: claude-opus-4-8[1m]
effort: xhigh
maxTurns: 15
---

# Consistency Checker Agent

You cross-check documentation against code to catch stale claims, missing table entries,
and undocumented changes introduced this session.

## Setup
```bash
cd {{PROJECT_ROOT}}
CHANGED=$(git diff --name-only HEAD; git diff --cached --name-only)
```

## Check 1: CLAUDE.md Agent Table vs Actual Agent Files

Conditional: only projects that maintain an agent table in CLAUDE.md are checked.
Detect that by whether ANY agent name already appears in CLAUDE.md; if none do,
the project keeps no such table, so report SKIP rather than flagging every agent.

```bash
if ! ls .claude/agents/*.md >/dev/null 2>&1; then
    echo "SKIP Check 1: no .claude/agents/ directory"
else
    FOUND=0
    for f in .claude/agents/*.md; do
        name=$(grep '^name:' "$f" | head -1 | sed 's/name: *//')
        [ -n "$name" ] && grep -q "$name" CLAUDE.md && FOUND=1
    done
    if [ "$FOUND" -eq 0 ]; then
        echo "SKIP Check 1: CLAUDE.md maintains no agent table"
    else
        # Optional count spot-check (e.g. "16 agents")
        ACTUAL_AGENTS=$(ls .claude/agents/*.md 2>/dev/null | wc -l | tr -d ' ')
        CLAIMED_AGENTS=$(grep -oE '[0-9]+ agents' CLAUDE.md | head -1 | grep -oE '[0-9]+' || echo "unknown")
        if [ "$CLAIMED_AGENTS" != "unknown" ] && [ "$ACTUAL_AGENTS" != "$CLAIMED_AGENTS" ]; then
            echo "MISMATCH: update the agent count in CLAUDE.md from $CLAIMED_AGENTS to $ACTUAL_AGENTS"
        fi
        # Each agent name must appear in the table
        for f in .claude/agents/*.md; do
            name=$(grep '^name:' "$f" | head -1 | sed 's/name: *//')
            if [ -n "$name" ] && ! grep -q "$name" CLAUDE.md; then
                echo "MISSING from CLAUDE.md agents table: $name"
            fi
        done
    fi
fi
```

## Check 2: CLAUDE.md Skills Table vs Actual Skill Files

Conditional, same shape as Check 1: SKIP unless CLAUDE.md maintains a skills table
(detected by at least one skill name already appearing in it).

```bash
if ! ls .claude/skills/*/SKILL.md >/dev/null 2>&1; then
    echo "SKIP Check 2: no .claude/skills/ directory"
else
    # Enumerate real skills only (directories holding a SKILL.md); support
    # bundles without one are not skills and must not produce findings.
    FOUND=0
    for s in .claude/skills/*/SKILL.md; do
        skill=$(basename "$(dirname "$s")")
        grep -qi "$skill" CLAUDE.md && FOUND=1
    done
    if [ "$FOUND" -eq 0 ]; then
        echo "SKIP Check 2: CLAUDE.md maintains no skills table"
    else
        for s in .claude/skills/*/SKILL.md; do
            skill=$(basename "$(dirname "$s")")
            if ! grep -qi "$skill" CLAUDE.md; then
                echo "MISSING from CLAUDE.md skills table: $skill"
            fi
        done
    fi
fi
```

## Check 3: Rules Routing Table vs Actual Rules Files

Conditional, same shape as Checks 1 and 2: SKIP when the project keeps no rules
directory, and SKIP when CLAUDE.md maintains no rules table (no rule filename
appears in it at all).

```bash
if ! ls .claude/rules/*.md >/dev/null 2>&1; then
    echo "SKIP Check 3: no .claude/rules/ directory"
else
    FOUND=0
    for f in .claude/rules/*.md; do
        grep -q "$(basename "$f")" CLAUDE.md && FOUND=1
    done
    if [ "$FOUND" -eq 0 ]; then
        echo "SKIP Check 3: CLAUDE.md maintains no rules table"
    else
        for f in .claude/rules/*.md; do
            name=$(basename "$f")
            if ! grep -q "$name" CLAUDE.md; then
                echo "MISSING from CLAUDE.md rules table: $name"
            fi
        done
    fi
fi
```

## Check 4: Documented Counts vs Reality

If the repo keeps a gotcha log or docs asserting counts (file counts, test counts,
baselines), spot-check each asserted number against the command that produces it.
A number in prose with no producing command is a WARN; a number that contradicts
its producing command is a FAIL.

## Check 5: Session-Changed Files vs Documentation

For each file changed in this session, check if related docs need updating:
```bash
# If a new agent was added (.claude/agents/*.md added)
NEW_AGENTS=$(git diff --name-only HEAD | grep '^\.claude/agents/')
if [ -n "$NEW_AGENTS" ]; then
    echo "New agents added - verify CLAUDE.md agents table is updated"
fi

# If a new skill was added (.claude/skills/*/SKILL.md)
NEW_SKILLS=$(git diff --name-only HEAD | grep '^\.claude/skills/')
if [ -n "$NEW_SKILLS" ]; then
    echo "New skills added - verify CLAUDE.md skills table is updated"
fi

# If a Python script in scripts/ was changed
CHANGED_SCRIPTS=$(git diff --name-only HEAD | grep '^scripts/')
if [ -n "$CHANGED_SCRIPTS" ]; then
    echo "Scripts changed: $CHANGED_SCRIPTS"
    echo "Check if CLAUDE.md 'Common Commands' or rules files reference these"
fi
```

## Check 6: Single Controlling Work Order

Exactly one file (`CLAUDE.md`) may name a work-order filename as controlling.
Every other mention must *defer* to `CLAUDE.md` rather than restate a filename.
This check exists because multiple documents once each called themselves controlling,
while the plan that actually covered the current work was named by nothing.

```bash
# 6a. If CLAUDE.md uses the convention at all, it must name EXACTLY ONE controlling
# work order, and that file must exist. A project that never declares one has not
# adopted the convention: report SKIP for the whole check (6b's filename patterns
# only mean something inside the convention).
# sed, not `grep -oP`: PCRE mode is a GNU-grep feature and macOS grep lacks it.
WO=$(sed -n 's/.*Controlling work order: `\([^`]*\)`.*/\1/p' CLAUDE.md)
N=$(printf '%s\n' "$WO" | grep -c .)
if [ "$N" -eq 0 ]; then
    echo "SKIP Check 6: CLAUDE.md declares no controlling work order (convention not adopted)"
else
    [ "$N" -eq 1 ] || echo "FAIL: CLAUDE.md names $N controlling work orders, expected exactly 1"
    [ "$N" -ne 1 ] || [ -f "$WO" ] || echo "FAIL: controlling work order does not exist on disk: $WO"
fi

# 6b. Runs only when 6a did not SKIP. No other routing doc may name a work-order
# FILENAME as controlling.
# The awk strips the "file:line:" prefix before pattern-matching, because grep -rn
# echoes the path and files NAMED *MASTER_EXECUTION_PLAN* would otherwise self-match.
# SCOPE: root *.md is included deliberately. HANDOFF.md sat outside an earlier version
# of this scope and kept naming a second "binding" plan for days, unnoticed - which is
# the exact failure this check exists to catch.
# CLAUDE.md is excluded: it is the single source of truth 6a already checked, so
# including it here would flag the one line that is supposed to exist.
if [ "$N" -gt 0 ]; then
grep -rn -iE 'controlling|binding|authoritative|master plan' \
     *.md AGENTS.md */CONTEXT.md .claude/rules/*.md .claude/plans/*.md .claude/plans/*.html 2>/dev/null \
  | grep -v '^CLAUDE\.md:' \
  | awk '{ c=$0; sub(/^[^:]*:[0-9]+:/,"",c);
           if (c ~ /EXECUTION_WORKORDER|MASTER_EXECUTION_PLAN|EXECUTION_PLAN_|PHASED_PLAN|\.claude\/plans\//) print }' \
  | grep -v 'named in `\?CLAUDE\.md' \
  | while IFS=: read -r f l rest; do
      # File-level exemption, NOT line-level: the banner sits at the top of the file,
      # so `grep -v 'HISTORICAL RECORD'` would only ever exempt the banner line itself
      # and still flag every line below it. Same bug class as the `superseded` filter.
      head -20 "$f" | grep -q 'HISTORICAL RECORD' || echo "$f:$l:$rest"
    done
fi
# Any surviving line is a violation: report it as file:line.
# Do NOT add a line-level `grep -v superseded` here. A CONTEXT.md may mention
# superseded archives in its Skip column, so that filter silently swallows real
# violations on that exact line. Mark a dead doc with a `HISTORICAL RECORD` banner
# instead - that phrase is the exemption, and it has to be written deliberately.
```

SKIP if the project declares no controlling work order. Otherwise FAIL if 6a fails,
or if 6b prints any line. A document banner-marked `HISTORICAL RECORD`, or a line
deferring to `CLAUDE.md`, is not a violation.

**Known limits, stated so nobody mistakes this for airtight.** 6b is keyword- and
line-oriented. A doc that asserts authority using none of the four keywords, names a
plan file matching none of the five patterns, or splits the claim across two lines,
passes. It catches recurrence of the observed failure mode, not every possible one.

## Check 7: Generated-outputs registry is intact

Conditional: only runs when the project ships a generated-outputs registry checker.
Such a checker guards a generated-file hook that fails open on infrastructure
problems, so a registry that has rotted disables protection silently, and this is
the check that notices. A project without that machinery reports SKIP, not FAIL.

```bash
REG_CHECK=scripts/check_generated_registry.py
if [ ! -f "$REG_CHECK" ]; then
    echo "SKIP Check 7: no generated-outputs registry checker at $REG_CHECK"
else
    python3 "$REG_CHECK"
fi
```

FAIL if the checker runs and exits non-zero. Run it with `--uncovered` to see which
tracked files in the generated-output directories no registry row covers yet; that
list is advisory (a coverage worklist), not a failure.

## Output Format

```
CONSISTENCY CHECK: PASS/FAIL

[1] CLAUDE.md agent table:    PASS/FAIL/SKIP
    [if FAIL: agent names missing from table; SKIP: project keeps no agent table]

[2] CLAUDE.md skills table:   PASS/FAIL/SKIP
    [if FAIL: skill names missing from table; SKIP: project keeps no skills table]

[3] CLAUDE.md rules table:    PASS/FAIL/SKIP
    [if FAIL: rule files missing from table; SKIP: no rules directory]

[4] Documented counts:        PASS/WARN
    [if WARN: claimed counts differ from reality]

[5] Session coverage:         PASS/WARN
    [if WARN: changed files that may need doc updates]

[6] Single controlling plan:  PASS/FAIL/SKIP
    [if FAIL: file:line of each doc naming a work-order filename instead of deferring;
     SKIP: the project declares no controlling work order]

[7] Generated-outputs registry: PASS/FAIL/SKIP
    [if FAIL: the FAIL lines from the registry checker; SKIP: project ships no checker]

VERDICT: PASS/FAIL
(FAIL on: missing entries in a CLAUDE.md table the project maintains,
 more than one doc naming a controlling work order, a rotted registry)
(WARN on: doc updates that may be needed - advisory)
(SKIP is not a failure: a check whose machinery the project lacks is reported SKIP)
```
