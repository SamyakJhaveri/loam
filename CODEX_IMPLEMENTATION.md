# Codex CLI Integration — Implementation Handoff

> **What this document is:** A step-by-step implementation plan for a fresh Claude Code session.
> Every file path is absolute, every command is copy-pasteable, every step has inline verification.
> Written for an undergraduate software engineering student — no assumed prior context.

---

## Background: What Are We Doing and Why?

**ParBench** is a benchmark for evaluating how well Large Language Models translate parallel code between CUDA, OpenMP, and OpenCL. It's targeting NeurIPS 2026 (deadline: May 1, 2026). All development so far has been done by Claude (Anthropic's AI). The problem: if the same AI that writes the code also reviews it, blind spots and errors can go undetected. This is called **sycophancy** — where the reviewer agrees with the author because they share the same reasoning patterns.

**The solution:** Use a second AI from a different company — OpenAI's **Codex CLI** (powered by GPT-5.4) — to independently review Claude's work. Think of it like getting a code review from a colleague who has a completely different perspective.

**What's already installed:**
- Codex CLI v0.122.0 at `/home/samyak/.npm-global/bin/codex` (verified working)
- Codex plugin for Claude Code v1.0.4 (provides `/codex:review`, `/codex:rescue`, etc.)
- A pre-commit hook that reminds you to run Codex review before committing

**What's missing (your job to create):**
1. An `AGENTS.md` file — gives Codex project context (like CLAUDE.md but for Codex)
2. A `.codex/config.toml` file — configures Codex with review profiles
3. Verification that the existing hook works correctly

---

## Skills and Guidelines to Load

Before starting implementation, load these skills for guidance:

```
/andrej-karpathy-skills:karpathy-guidelines
```

**Why these skills matter:**
- **Karpathy guidelines** — "Think Before Coding / Simplicity First / Surgical Changes." These config files are simple — resist the urge to over-engineer them. The karpathy skill reminds you to verify assumptions and keep changes surgical.

**TDD note:** This task creates configuration files (TOML + Markdown), not application code. TDD (test-driven development) does not apply — there's no red-green-refactor cycle for static config. Instead, each step has **inline verification commands** that serve the same purpose: write the file, run a check, confirm it works.

---

## Pre-Flight Check (Step 0)

**Goal:** Verify Codex CLI actually works before creating any files. If this fails, stop — there's no point writing config files for a broken tool.

```bash
# Check Codex is installed and accessible
/home/samyak/.npm-global/bin/codex --version
# Expected output: codex-cli 0.122.0

# Check Codex can execute (smoke test)
cd /home/samyak/Desktop/parbench_sam
/home/samyak/.npm-global/bin/codex exec -s read-only --ephemeral "Say hello and state the current working directory"
# Expected: Codex responds with the project path. If this errors, check API key with `codex login`.
```

**If this fails:** Run `codex login` to re-authenticate. If that also fails, the OpenAI API key may be expired — ask the user.

---

## Step 1: Create `.codex/config.toml`

**What this does:** Tells Codex CLI which model to use, how hard to think, and defines 3 named "profiles" for different review scenarios. A profile is like a preset — instead of typing `--model gpt-5.4 -c model_reasoning_effort="high"` every time, you type `--profile results-audit`.

**File to create:** `/home/samyak/Desktop/parbench_sam/.codex/config.toml`

First create the directory:
```bash
mkdir -p /home/samyak/Desktop/parbench_sam/.codex
```

**File content (verified against official Codex config schema):**

```toml
# ParBench project-level Codex configuration
# Loaded automatically when running `codex` from this directory.
# Docs: https://developers.openai.com/codex/config-reference

# Default model for all Codex operations in this project
model = "gpt-5.4"

# Default reasoning effort (how deeply the model thinks)
# Values: none, minimal, low, medium, high, xhigh
model_reasoning_effort = "high"

# --- Review Profiles ---
# Use with: codex --profile <name> OR codex exec -p <name>
# Each profile overrides the defaults above for its specific use case.

[profiles.code-review]
# Standard code review of uncommitted changes.
# Medium effort is sufficient for typical diff review.
model = "gpt-5.4"
model_reasoning_effort = "medium"
sandbox_mode = "read-only"

[profiles.results-audit]
# Audit eval result JSONs for consistency, KNOWN_FAIL contamination,
# and pass-rate accuracy. Higher effort for data integrity checks.
model = "gpt-5.4"
model_reasoning_effort = "high"
sandbox_mode = "read-only"

[profiles.deep-review]
# Adversarial review — challenges design decisions, finds blind spots,
# questions assumptions. Maximum reasoning effort.
model = "gpt-5.4"
model_reasoning_effort = "xhigh"
sandbox_mode = "read-only"
```

**Key decisions explained:**
- `sandbox_mode = "read-only"` on all profiles — reviews should NEVER modify files. Codex can read the entire repo but cannot write.
- Three effort tiers: medium (quick review), high (thorough audit), xhigh (adversarial deep dive).
- `model = "gpt-5.4"` is the default model available on the Azure-backed OpenAI API. If you want to try GPT-5.5 later, change this value.

**Verification:**
```bash
# Verify TOML parses correctly
python3 -c "
import tomllib
with open('/home/samyak/Desktop/parbench_sam/.codex/config.toml', 'rb') as f:
    config = tomllib.load(f)
print('Profiles:', list(config.get('profiles', {}).keys()))
print('Default model:', config.get('model'))
assert 'code-review' in config['profiles'], 'Missing code-review profile'
assert 'results-audit' in config['profiles'], 'Missing results-audit profile'
assert 'deep-review' in config['profiles'], 'Missing deep-review profile'
print('PASS: config.toml is valid')
"
# Expected: Profiles: ['code-review', 'results-audit', 'deep-review']

# Verify Codex loads the profile without error
cd /home/samyak/Desktop/parbench_sam
/home/samyak/.npm-global/bin/codex exec -p code-review -s read-only --ephemeral "echo profile loaded successfully"
# Expected: Codex runs without config errors
```

---

## Step 2: Create `AGENTS.md`

**What this does:** `AGENTS.md` is Codex's equivalent of `CLAUDE.md`. When Codex starts in a directory, it automatically discovers and reads any `AGENTS.md` file in that directory or parent directories. This file tells Codex what the project is, what the rules are, and what to look for during reviews.

**File to create:** `/home/samyak/Desktop/parbench_sam/AGENTS.md`

**Important design decisions:**
- The `## Review Guidelines` section is **automatically loaded** by Codex during `/review` commands.
- We include a canary token (`PARBENCH_AGENTS_CANARY_2026`) so we can verify Codex actually reads this file.
- The file references `CLAUDE.md` for full details — this avoids duplication and prevents the two files from drifting apart over time.
- Target: under 120 lines, under 32 KiB (Codex's `project_doc_max_bytes` default).

**File content:**

```markdown
# AGENTS.md — ParBench

<!-- PARBENCH_AGENTS_CANARY_2026 — used to verify Codex reads this file -->

ParBench is a kernel-centric benchmark for evaluating LLM-based parallel code
translation across CUDA, OpenMP, and OpenCL. Targeting NeurIPS 2026 Datasets &
Benchmarks track (deadline: May 1, 2026).

For full project rules, read `CLAUDE.md` in this same directory. The invariants
and architecture described there are authoritative. This file provides
Codex-specific review guidance.

## Architecture

| Path | Purpose |
|------|---------|
| `specs/` | Kernel spec JSONs (`{suite}-{slug}-{api}.json`) — 206 total |
| `manifest.jsonl` | Append-only kernel registry — never modify existing entries |
| `harness/` | Build → Run → Verify pipeline. Invoke: `python3 -m harness` |
| `scripts/evaluation/` | LLM eval pipeline (`run_eval_batch.py`, `llm_evaluate.py`) |
| `scripts/analysis/` | Result analysis and paper data generation |
| `results/` | Immutable eval + augmentation result JSONs |
| `c_augmentation/` | AST transforms (libclang). Tests: `pytest c_augmentation/test_transforms.py` |
| `schema/` | JSON schema for spec validation |
| `docs/paper/` | NeurIPS paper source and figures |

## Key Invariants

These rules are non-negotiable. Flag any violation during review:

1. **`manifest.jsonl` is append-only** — never modify or delete existing entries
2. **Result JSONs are immutable** — files in `results/` must never be modified after creation
3. **Never change spec run args** without verifying the source code's `argc` check
4. **9 KNOWN_FAIL specs** must be excluded from eval batches and pass-rate denominators
5. **~15 schema validation errors are expected** (from 5 deleted phantom specs) — do not fix

## KNOWN_FAIL Specs (9 total — exclude from all evaluations)

- `rodinia-kmeans-cuda` — texture<> removed in CUDA 12
- `rodinia-mummergpu-cuda` — texture<> removed in CUDA 12
- `rodinia-mummergpu-omp` — texture<> + cuMemGetInfo_v2 signature
- `rodinia-hybridsort-cuda` — GL/glew.h not found
- `rodinia-nn-opencl` — TIMEOUT / SIGSEGV
- `rodinia-kmeans-opencl` — SIGSEGV in OpenCL runtime
- `rodinia-backprop-opencl` — clEnqueueReadBuffer error
- `hecbench-stencil1d-omp_target` — BUILD_FAIL
- `hecbench-scan-omp_target` — VERIFY_FAIL

The canonical exclusion list is in `harness/constants.py` → `EXCLUDED_SPECS`.

## Build & Test Commands

```bash
source env_parbench/bin/activate                          # activate venv
python3 -m harness verify specs/rodinia-bfs-cuda.json     # verify single spec
python3 scripts/spec_tools/validate_schema.py --all       # schema check (~15 errors expected)
pytest c_augmentation/test_transforms.py                  # augmentation tests
pytest tests/                                             # unit tests
```

## Review Guidelines

When reviewing code in this repository, focus on these areas:

**Critical (must flag):**
- Modifications to existing entries in `manifest.jsonl`
- Modifications to existing result JSONs in `results/evaluation/`
- Spec `run_args` that don't match the source code's `argc` check
- KNOWN_FAIL specs included in eval batch configurations
- Pass-rate denominators that don't exclude KNOWN_FAIL specs
- API keys, secrets, or credentials in code

**Important (should flag):**
- Data races, memory model violations, or synchronization bugs in CUDA/OpenMP/OpenCL code
- Inconsistencies between `CLAUDE.md` / `known-issues.md` and actual code behavior
- Stale line numbers or function names in documentation
- Missing `--resume` flag on evaluation commands (risks overwriting results)
- Schema validation errors beyond the expected ~15 (indicates a real problem)

**Style (optional):**
- Python: must use `python3`, never `python`
- Prefer `source env_parbench/bin/activate` before running any Python commands

## What NOT to Do

- Do NOT modify any files during review — reviews are read-only
- Do NOT attempt to fix KNOWN_FAIL specs — they are deferred intentionally
- Do NOT trust documentation over source code — the code is authoritative
```

**Verification:**
```bash
# Check line count (must be under 120)
wc -l /home/samyak/Desktop/parbench_sam/AGENTS.md
# Expected: ~95 lines

# Check byte size (must be under 32768 = 32 KiB)
wc -c /home/samyak/Desktop/parbench_sam/AGENTS.md
# Expected: ~3500 bytes (well under limit)

# Verify Codex discovers and reads the file (canary test)
cd /home/samyak/Desktop/parbench_sam
/home/samyak/.npm-global/bin/codex exec -s read-only --ephemeral "What is the canary token in your project instructions? Reply with ONLY the token value."
# Expected output should contain: PARBENCH_AGENTS_CANARY_2026
# If Codex does NOT return the canary, AGENTS.md is not being discovered.
# Fallback: pass context via -c model_instructions_file="AGENTS.md"
```

**If the canary test fails:** Codex may not auto-discover `AGENTS.md` in this version. Two fallback options:
1. Add `model_instructions_file = "AGENTS.md"` to `.codex/config.toml` (instructs Codex to read it explicitly)
2. Or rename to `CODEX.md` and set `project_doc_fallback_filenames = ["CODEX.md"]` in config.toml

---

## Step 3: Verify the Existing Hook

**What this does:** The file `.claude/hooks/codex-review-reminder.sh` is a pre-commit hook that reminds you to run a Codex review before committing. It checks for a `.codex_review_done` sentinel file. We need to verify it actually works.

**File location:** `/home/samyak/Desktop/parbench_sam/.claude/hooks/codex-review-reminder.sh`
**Wired in:** `/home/samyak/Desktop/parbench_sam/.claude/settings.json` (line 58-61, PreToolUse → Bash hooks)

**Important context you should know:**
- The sentinel cleanup hook at `/home/samyak/Desktop/parbench_sam/.claude/hooks/sentinel-cleanup.sh` (lines 30-34) **already deletes** `.codex_review_done` whenever any file is edited. This is correct behavior — do not modify it.
- Writing the AGENTS.md and config.toml files in steps 1-2 will trigger sentinel cleanup. This is expected.

**Test scenarios (run from project root):**

```bash
cd /home/samyak/Desktop/parbench_sam

# --- Test 1: Non-commit command should produce no output ---
echo '{"tool_input":{"command":"ls -la"}}' | bash .claude/hooks/codex-review-reminder.sh
echo "Exit code: $?"
# Expected: No output, exit code 0

# --- Test 2: git commit without sentinel should show reminder ---
rm -f .codex_review_done
echo '{"tool_input":{"command":"git commit -m test"}}' | bash .claude/hooks/codex-review-reminder.sh
echo "Exit code: $?"
# Expected: JSON with "Codex review reminder" in hookSpecificOutput, exit code 0

# --- Test 3: git commit with fresh sentinel should be silent ---
touch .codex_review_done
echo '{"tool_input":{"command":"git commit -m test"}}' | bash .claude/hooks/codex-review-reminder.sh
echo "Exit code: $?"
# Expected: No output, exit code 0

# --- Test 4: git commit with stale sentinel (>30 min) should show reminder ---
touch -d "35 minutes ago" .codex_review_done
echo '{"tool_input":{"command":"git commit -m test"}}' | bash .claude/hooks/codex-review-reminder.sh
echo "Exit code: $?"
# Expected: JSON with "Codex review reminder", exit code 0

# --- Test 5: Malformed JSON should not crash (trap catches it) ---
echo 'THIS IS NOT JSON' | bash .claude/hooks/codex-review-reminder.sh
echo "Exit code: $?"
# Expected: No output, exit code 0

# --- Test 6: Empty stdin should not crash ---
echo '' | bash .claude/hooks/codex-review-reminder.sh
echo "Exit code: $?"
# Expected: No output, exit code 0

# Clean up
rm -f .codex_review_done
```

**If any test fails:** Read the hook at `/home/samyak/Desktop/parbench_sam/.claude/hooks/codex-review-reminder.sh` and debug. The hook has a `trap 'exit 0' ERR` on line 12 that should catch all errors. If it's still crashing, the `python3` JSON parser on lines 15-23 is the most likely culprit.

---

## Step 4: Update `.gitignore` for `.codex/`

**What this does:** We want to track `.codex/config.toml` in git (it's shared project config, like `.claude/settings.json`), but we do NOT want to accidentally commit other files Codex might create in `.codex/` (session state, cache, credentials).

**File to edit:** `/home/samyak/Desktop/parbench_sam/.gitignore`

**Add these lines** (after the existing `.claude/` entries around line 58):

```
# Codex CLI local state (only config.toml is tracked)
.codex/*
!.codex/config.toml
```

**Verification:**
```bash
cd /home/samyak/Desktop/parbench_sam
# Check that config.toml would be tracked
git check-ignore .codex/config.toml
# Expected: NO output (empty = not ignored = will be tracked)

# Check that other .codex files would be ignored
git check-ignore .codex/sessions.json .codex/cache/ .codex/some-random-file
# Expected: All three paths printed (= they are ignored)
```

---

## Step 5: Final Verification

Run all checks together to confirm everything works:

```bash
cd /home/samyak/Desktop/parbench_sam

echo "=== 1. Config.toml validation ==="
python3 -c "
import tomllib
with open('.codex/config.toml', 'rb') as f:
    config = tomllib.load(f)
profiles = list(config.get('profiles', {}).keys())
assert profiles == ['code-review', 'results-audit', 'deep-review'], f'Wrong profiles: {profiles}'
print(f'PASS: {len(profiles)} profiles configured')
"

echo "=== 2. AGENTS.md size check ==="
LINES=$(wc -l < AGENTS.md)
BYTES=$(wc -c < AGENTS.md)
echo "Lines: $LINES (limit: 120), Bytes: $BYTES (limit: 32768)"
[ "$LINES" -le 120 ] && [ "$BYTES" -le 32768 ] && echo "PASS" || echo "FAIL"

echo "=== 3. Canary test ==="
/home/samyak/.npm-global/bin/codex exec -s read-only --ephemeral "What is the canary token in your project instructions? Reply with ONLY the token string." 2>&1 | grep -q "PARBENCH_AGENTS_CANARY_2026" && echo "PASS: Codex reads AGENTS.md" || echo "WARN: Canary not found — check AGENTS.md discovery"

echo "=== 4. Profile test ==="
/home/samyak/.npm-global/bin/codex exec -p code-review -s read-only --ephemeral "Reply with only: profile loaded" 2>&1 | grep -qi "profile\|loaded" && echo "PASS: code-review profile works" || echo "FAIL: profile not loading"

echo "=== 5. Hook test ==="
rm -f .codex_review_done
HOOK_OUT=$(echo '{"tool_input":{"command":"git commit -m test"}}' | bash .claude/hooks/codex-review-reminder.sh 2>/dev/null)
echo "$HOOK_OUT" | grep -q "Codex review reminder" && echo "PASS: Hook fires reminder" || echo "FAIL: Hook silent when it should remind"
rm -f .codex_review_done

echo "=== 6. Gitignore test ==="
git check-ignore .codex/config.toml 2>/dev/null && echo "FAIL: config.toml is gitignored (should be tracked)" || echo "PASS: config.toml will be tracked"
```

---

## Step 6: Run `/validate` and Commit

After all 6 checks pass:

```bash
# Run the full validation loop (required before every commit)
/validate

# After validation passes, stage and commit
git add AGENTS.md .codex/config.toml .gitignore
git commit -m "feat: add AGENTS.md and Codex config for cross-model review

- AGENTS.md gives Codex project context (architecture, invariants, review guidelines)
- .codex/config.toml configures 3 review profiles (code-review, results-audit, deep-review)
- .gitignore updated to track config.toml but ignore other .codex/ files
- Existing codex-review-reminder.sh hook verified working (6 test scenarios passed)"
```

---

## Rollback Plan

If Codex behaves incorrectly after these changes (e.g., wrong invariants lead to bad review advice):

```bash
git rm AGENTS.md .codex/config.toml
git commit -m "revert: remove codex config (caused incorrect review behavior)"
```

Codex will fall back to default behavior with no project context. No other project files are modified by this plan, so rollback is clean.

---

## Usage Cheat Sheet (Post-Implementation Reference)

Once everything is set up, here's how to use Codex for reviews:

### From Within Claude Code (via plugin)

| What you want | Command |
|---------------|---------|
| Review uncommitted changes | `/codex:rescue review the uncommitted changes for correctness and regressions` |
| Adversarial design review | `/codex:adversarial-review` |
| Standard code review | `/codex:review` |
| Check Codex job status | `/codex:status` |
| Mark review done | `touch .codex_review_done` |

### Direct Codex CLI Commands (from terminal)

| What you want | Command |
|---------------|---------|
| Quick code review | `codex review --uncommitted` |
| Review against main | `codex review --base main` |
| Review specific commit | `codex review --commit <sha>` |
| Audit eval results | `codex exec -p results-audit -s read-only "Audit results/evaluation/ for schema consistency and KNOWN_FAIL contamination"` |
| Deep adversarial review | `codex exec -p deep-review -s read-only "Find the strongest reasons these changes should NOT ship"` |
| Review analysis scripts | `codex exec -p code-review -s read-only "Review scripts/analysis/ for correctness, especially pass-rate denominators and KNOWN_FAIL exclusion logic"` |

### Typical Workflow

1. Claude implements a feature or fix
2. Before committing, run `/codex:rescue review the uncommitted changes` (or `codex review --uncommitted`)
3. Read Codex's findings — decide which to act on (Codex may flag things Claude missed)
4. Fix any real issues Claude found
5. Run `touch .codex_review_done` to mark the review complete
6. Run `/validate` then commit

---

## What Codex CAN and CANNOT Do

### Capabilities
- Read your entire repo (all code, specs, results, docs)
- Review code diffs with structured feedback
- Adversarial review that challenges design decisions
- Use GPT-5.4 (default), GPT-5.5, or gpt-5.3-codex
- Run in read-only sandbox (safe — cannot modify your files)

### Limitations
- **Tool output truncated to 256 lines or 10 KiB per file** — very large files get cut off
- **Context window ~258K usable tokens** — auto-compacts at ~95% capacity
- **No network by default** — cannot access external APIs during sandboxed review
- **No memory across sessions** — each `codex exec` starts fresh (unless using `codex resume`)
- **Cannot run your build/test pipeline** in read-only mode — it can only read code and reason about it

### Key Differences from Claude

| Aspect | Claude Code | Codex CLI |
|--------|-------------|-----------|
| Project context | CLAUDE.md (auto-loaded) | AGENTS.md (auto-loaded) |
| Config | .claude/settings.json | .codex/config.toml |
| Review command | /review (multi-agent) | codex review (single model) |
| Sandbox | Not sandboxed by default | Sandboxed by default |
| Hooks | .claude/hooks/*.sh | .codex/hooks.toml |
| Persistent memory | Yes (.claude/memory/) | Experimental (feature flag) |

---

## Files Created/Modified by This Plan

| File | Action | Purpose |
|------|--------|---------|
| `/home/samyak/Desktop/parbench_sam/AGENTS.md` | CREATE | Project context for Codex (~95 lines) |
| `/home/samyak/Desktop/parbench_sam/.codex/config.toml` | CREATE | Codex config with 3 review profiles |
| `/home/samyak/Desktop/parbench_sam/.gitignore` | EDIT (2 lines added) | Track config.toml, ignore other .codex/ files |
| `/home/samyak/Desktop/parbench_sam/.claude/hooks/codex-review-reminder.sh` | VERIFY ONLY | Existing hook — no changes needed |
| `/home/samyak/Desktop/parbench_sam/.claude/hooks/sentinel-cleanup.sh` | DO NOT TOUCH | Already handles .codex_review_done cleanup |
