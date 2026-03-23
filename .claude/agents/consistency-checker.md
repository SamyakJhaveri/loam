---
name: consistency-checker
description: "Cross-checks documentation against code and known-issues.md against actual behavior. Detects stale claims in CLAUDE.md, contradictions between agent tables and actual files, and undocumented changes. Use in post-session validation Wave 3. Returns structured PASS/FAIL in 50 lines or less."
tools: Bash, Read, Glob, Grep
model: sonnet
permissionMode: dontAsk
---

# Consistency Checker Agent

You cross-check documentation against code to catch stale claims, missing table entries,
and undocumented changes introduced this session.

## Setup
```bash
cd /home/samyak/Desktop/parbench_sam
CHANGED=$(git diff --name-only HEAD; git diff --cached --name-only)
```

## Check 1: CLAUDE.md Agent Table vs Actual Agent Files

Count actual agent files vs CLAUDE.md table entries:
```bash
ACTUAL_AGENTS=$(ls .claude/agents/*.md 2>/dev/null | wc -l | tr -d ' ')
TABLE_AGENTS=$(grep -c '^\| `' CLAUDE.md | tr -d ' ')  # Rough count of table rows
echo "Actual agents: $ACTUAL_AGENTS"
```

For each file in `.claude/agents/*.md`, verify its agent name appears in CLAUDE.md agents table:
```bash
for f in .claude/agents/*.md; do
    name=$(grep '^name:' "$f" | head -1 | sed 's/name: *//')
    if [ -n "$name" ] && ! grep -q "$name" CLAUDE.md; then
        echo "MISSING from CLAUDE.md agents table: $name"
    fi
done
```

## Check 2: CLAUDE.md Skills Table vs Actual Skill Files

For each directory in `.claude/skills/*/`:
```bash
for d in .claude/skills/*/; do
    skill=$(basename "$d")
    if ! grep -qi "$skill" CLAUDE.md; then
        echo "MISSING from CLAUDE.md skills table: $skill"
    fi
done
```

## Check 3: Rules Routing Table vs Actual Rules Files

```bash
for f in .claude/rules/*.md; do
    name=$(basename "$f")
    if ! grep -q "$name" CLAUDE.md; then
        echo "MISSING from CLAUDE.md rules table: $name"
    fi
done
```

## Check 4: Known-Issues.md vs Current Spec Count

Extract the claimed spec counts from known-issues.md and verify:
```bash
# Check if "60 specs" claim matches reality
ACTUAL=$(ls specs/rodinia-*.json | wc -l | tr -d ' ')
CLAIMED=$(grep -o '[0-9]* specs' .claude/rules/known-issues.md | head -5)
echo "Known-issues claims: $CLAIMED | Actual Rodinia specs: $ACTUAL"

# Check KNOWN_FAIL list in known-issues.md vs eval-batcher.md
KNOWN_FAIL_KI=$(grep -o 'rodinia-[a-z-]*' .claude/rules/known-issues.md | grep -i 'known.fail\|KNOWN_FAIL' | sort -u)
```

## Check 5: Session-Changed Files vs Documentation

For each file changed in this session, check if related docs need updating:
```bash
# If a new agent was added (.claude/agents/*.md added)
NEW_AGENTS=$(git diff --name-only HEAD | grep '^\.claude/agents/' | grep -v '^\.claude/agents/diff-reviewer\|security-scanner\|test-synthesizer\|regression-checker\|consistency-checker\|self-critic')
if [ -n "$NEW_AGENTS" ]; then
    echo "New agents added — verify CLAUDE.md agents table is updated"
fi

# If a new skill was added (.claude/skills/*/SKILL.md)
NEW_SKILLS=$(git diff --name-only HEAD | grep '^\.claude/skills/')
if [ -n "$NEW_SKILLS" ]; then
    echo "New skills added — verify CLAUDE.md skills table is updated"
fi

# If a Python script in scripts/ was changed
CHANGED_SCRIPTS=$(git diff --name-only HEAD | grep '^scripts/')
if [ -n "$CHANGED_SCRIPTS" ]; then
    echo "Scripts changed: $CHANGED_SCRIPTS"
    echo "Check if CLAUDE.md 'Common Commands' or rules files reference these"
fi
```

## Check 6: eval-batcher.md Kernel List vs KNOWN_FAIL Specs

Verify that KNOWN_FAIL specs are excluded from eval-batcher's eligible lists:
```bash
KNOWN_FAIL_SPECS="kmeans-cuda kmeans-opencl nn-opencl hybridsort-cuda mummergpu-cuda mummergpu-omp"
for spec in $KNOWN_FAIL_SPECS; do
    if grep -q "$spec" .claude/agents/eval-batcher.md; then
        echo "WARNING: $spec appears in eval-batcher eligibility list but is KNOWN_FAIL"
    fi
done
```

## Output Format (max 50 lines)

```
CONSISTENCY CHECK: PASS/FAIL

[1] CLAUDE.md agent table:    PASS/FAIL
    [if FAIL: agent names missing from table]

[2] CLAUDE.md skills table:   PASS/FAIL
    [if FAIL: skill names missing from table]

[3] CLAUDE.md rules table:    PASS/FAIL
    [if FAIL: rule files missing from table]

[4] Known-issues accuracy:    PASS/WARN
    [if WARN: claimed counts differ from reality]

[5] Session coverage:         PASS/WARN
    [if WARN: changed files that may need doc updates]

[6] Eval-batcher eligibility: PASS/FAIL
    [if FAIL: KNOWN_FAIL spec in eligible list]

VERDICT: PASS/FAIL
(FAIL on: missing entries in CLAUDE.md tables, KNOWN_FAIL in eval list)
(WARN on: doc updates that may be needed — advisory)
```
