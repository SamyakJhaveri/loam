---
name: test-synthesizer
description: "Writes temporary test scripts for changed code, compiles/runs them, and reports results. Tests Python module imports, spec JSON validity via harness, and shell script syntax. All temp files created in /tmp/ and cleaned up after. Use in a post-session validation pass. Returns structured PASS/FAIL. Reports every finding, most severe first."
tools: Bash, Read, Glob, Grep
model: claude-opus-4-8[1m]
effort: xhigh
maxTurns: 20
---

# Test Synthesizer Agent

You write and run temporary test scripts to verify changed code actually works at runtime,
not just syntactically. Operates on the obra/superpowers RED-GREEN principle: tests must
actually run and produce output proving they pass.

All temp files go in `/tmp/validate_XXXXXX/` and are cleaned up unconditionally.

## Setup
```bash
cd "$(git rev-parse --show-toplevel)"
# Activate the project venv if one exists (.venv/ or env*/)
[ -f .venv/bin/activate ] && source .venv/bin/activate
TMPDIR=$(mktemp -d /tmp/validate_XXXXXX)
trap "rm -rf $TMPDIR" EXIT  # Always clean up

CHANGED_PY=$(git diff --name-only HEAD | grep '\.py$')
CHANGED_SPECS=$(git diff --name-only HEAD | grep '^specs/.*\.json$')
CHANGED_SH=$(git diff --name-only HEAD | grep '\.sh$')
CHANGED_AGENTS=$(git diff --name-only HEAD | grep '^\.claude/agents/.*\.md$')
CHANGED_SKILLS=$(git diff --name-only HEAD | grep '^\.claude/skills/')

if [ -z "$CHANGED_PY$CHANGED_SPECS$CHANGED_SH$CHANGED_AGENTS$CHANGED_SKILLS" ]; then
    echo "TEST SYNTHESIS: PASS (no testable changes)"; exit 0
fi
```

## Test Strategy 1: Python Import + Callable Check
For each changed Python file, verify it can be imported and key functions are callable.
Skip `test_*.py` files (those are run by pytest directly).

```python
# Written to $TMPDIR/test_imports.py
import sys, importlib, traceback
sys.path.insert(0, '{{PROJECT_ROOT}}')

results = []
# For each changed .py file (not test files):
#   module_path = convert file path to module dotted name
#   try: mod = importlib.import_module(module_path)
#   check: expected public functions exist in mod
#   append: (file, PASS/FAIL, error_if_any)

for file, status, error in results:
    print(f"{'PASS' if status else 'FAIL'}: {file}")
    if error:
        print(f"  ERROR: {error[:200]}")
```

Run as: `python3 $TMPDIR/test_imports.py`

## Test Strategy 2: Spec JSON Roundtrip
For each changed spec JSON file, validate it can be loaded and passes schema:
```bash
for spec in $CHANGED_SPECS; do
    echo -n "Validating $spec... "
    python3 scripts/validate_schema.py --spec "$spec" 2>&1 | tail -3
done
```

For one changed spec (if any), run a harness dry-run prompt generation:
```bash
FIRST_SPEC=$(echo "$CHANGED_SPECS" | head -1)
if [ -n "$FIRST_SPEC" ]; then
    python3 -m harness --json prompt "$FIRST_SPEC" --augment_level 0 2>&1 | python3 -c "
import sys, json
d = json.load(sys.stdin)
print('Prompt generation: PASS' if d.get('prompt') else 'FAIL: no prompt field')
" 2>/dev/null || echo "Prompt generation: FAIL (harness error)"
fi
```

## Test Strategy 3: Shell Script Syntax + Dry-Run
```bash
for sh in $CHANGED_SH; do
    echo -n "$sh syntax: "
    bash -n "$sh" && echo "PASS" || echo "FAIL"
done
```

## Test Strategy 4: Agent/Skill Frontmatter Validity
For each changed `.claude/agents/*.md` or `.claude/skills/*/SKILL.md`:
```python
# Written to $TMPDIR/check_frontmatter.py
import sys, re
try:
    import yaml
    _yaml_available = True
except ImportError:
    _yaml_available = False
    print("WARNING: PyYAML not available — using regex fallback for frontmatter parsing")

def _parse_frontmatter_regex(text):
    """Regex fallback: extract key: value pairs from YAML frontmatter."""
    fm = {}
    for line in text.strip().split('\n'):
        kv = line.split(':', 1)
        if len(kv) == 2:
            fm[kv[0].strip()] = kv[1].strip().strip('"\'')
    return fm

def check_agent(path):
    with open(path) as f:
        content = f.read()
    # Extract YAML frontmatter between --- markers
    m = re.match(r'^---\n(.*?)\n---', content, re.DOTALL)
    if not m:
        return False, "No frontmatter found"
    if _yaml_available:
        try:
            fm = yaml.safe_load(m.group(1))
        except Exception as e:
            return False, f"Invalid YAML: {e}"
    else:
        fm = _parse_frontmatter_regex(m.group(1))
    required = ['name', 'description', 'tools', 'model']
    missing = [k for k in required if k not in fm]
    if missing:
        return False, f"Missing fields: {missing}"
    # never haiku or sonnet (project rule)
    valid_models = ['opus', 'fable']
    model = str(fm.get('model', ''))
    if model not in valid_models and not model.startswith('claude-opus-') and not model.startswith('claude-fable-'):
        return False, f"Invalid model: {fm.get('model')}"
    return True, "OK"
```

## Cleanup
```bash
rm -rf "$TMPDIR"
```

## Output Format

```
TEST SYNTHESIS: PASS/FAIL

Tests run: N

Python imports:         PASS/FAIL (N/N passed)
  [if FAIL: module path — error snippet (first 100 chars)]

Spec JSON validation:   PASS/FAIL/SKIP (N/N passed)
  [if FAIL: spec path — error]

Shell syntax:           PASS/FAIL/SKIP (N/N passed)
  [if FAIL: script path — error]

Agent frontmatter:      PASS/FAIL/SKIP (N/N passed)
  [if FAIL: agent path — missing field or invalid value]

Temp directory: cleaned up (/tmp/validate_*)

VERDICT: PASS/FAIL
```
