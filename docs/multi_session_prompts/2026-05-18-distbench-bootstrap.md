# Distbench bootstrap — multi-session prompt

> **Audience:** a fresh Claude Code session opened in `~/Desktop/project_seed_framework/`.
> **Authored:** 2026-05-18 (predecessor Cowork session — see "State at handoff" below).
> **Pre-reading (required before starting):** this entire document, plus
> `.claude/rules/workflow.md`, `.claude/rules/stage-contract.md`,
> `.claude/rules/layer-triage.md`, `.claude/rules/validation-loop.md`.

---

## TL;DR

Four sequential phases (~3 hours), one optional. **The framework's value compounds only if you do Phase 3** — skip it only if distbench is genuinely a sub-two-week throwaway.

| # | Phase | Time | Optional? |
|---|-------|------|-----------|
| 1 | Pre-flight: commit pending changes + cleanup | ~10 min | No |
| 2 | Rename framework (placeholder name: **Loam**) | ~30 min | Yes — skip if not renaming |
| 3 | Port high-value skills from `parbench_sam` | ~60–90 min | Yes — see decision criterion |
| 4 | Render distbench + bootstrap | ~60 min | No |

**Phase 3 decision criterion:** is distbench expected to live longer than two weeks? If yes → do it. If no → skip and accept that you'll duplicate work the framework's job is to prevent.

---

## State at handoff

The predecessor Cowork session implemented four fixes against the seed framework but **did not commit them**. As of handoff, `git status` shows:

```
M  .claude/agents/self-critic.md
M  .claude/agents/verification-lead.md
M  .claude/hooks/pre-commit-gate.sh
M  .claude/rules/validation-loop.md
M  .claude/skills/validate/SKILL.md
M  .github/workflows/test.yml
M  CLAUDE.md.jinja
M  CONTEXT.md.jinja
M  bin/verify-template.sh
?? .claude/.write-probe         (1-byte empty file, sandbox artifact)
?? .write-probe                  (1-byte empty file, sandbox artifact)
?? PROJECT-BACKGROUND.md.jinja  (new file: project-background prose, moved from CONTEXT.md.jinja)
```

The four fixes, in implementation order:

- **Fix 4** — `/validate` restructured to three waves (Deterministic / Rule-based / Probabilistic) per `layer-triage.md` 60/30/10. Sentinel now actually emits `waves_passed`; `pre-commit-gate.sh` `≥3` check is no longer fail-open. Wave 1 has zero LLM calls.
- **Fix 1** — `.github/workflows/test.yml:27` had two dead `template/...` shellcheck globs (from pre-v2.0 layout). Replaced with the three-glob list `verify-template.sh:55` already uses.
- **Fix 3** — `template-sync` skill downgraded to "experimental." `CLAUDE.md.jinja:53` description softened. `verify-template.sh:118` hard-fail downgraded to WARN. Skill itself untouched.
- **Fix 2** — `CONTEXT.md.jinja` rewritten as a six-section ICM L1 routing skeleton (matching `.claude/rules/context-md-anatomy.md` and `.claude/skills/scaffold-context/SKILL.md`). Project-background prose moved to new `PROJECT-BACKGROUND.md.jinja` at root (NOT `docs/`, because `docs/` is in `copier.yml:_exclude`). `bin/verify-template.sh` now invariant-checks both: CONTEXT.md must contain the 6 named section headers, PROJECT-BACKGROUND.md must exist.

Local `bin/verify-template.sh` runs green. No commits yet.

---

## Phase 1 — Pre-flight

**Inputs:** the 9 modified files + 1 new file listed above; the two 1-byte `.write-probe` files.

**Process:**

1. Delete the sandbox artifacts:
   ```bash
   rm .write-probe .claude/.write-probe
   ```
2. Run `bin/verify-template.sh`. Confirm `ALL OK`. If it doesn't, STOP and diagnose before going further — something diverged.
3. Run `/validate` in this session against the pending diff. This is the **bootstrap test** of the new wave structure: the first time `/validate` runs under the rewritten validation-loop is on the diff that *defines* the rewrite. If `/validate` cannot complete or the sentinel is rejected by the gate, you've found a real bug in Fix 4 — investigate before committing.
4. If `/validate` passes (sentinel written with `waves_passed=3`), commit in four atomic commits, in implementation order:

   ```bash
   # Commit 1 — Fix 4 (wave restructure)
   git add .claude/rules/validation-loop.md .claude/skills/validate/SKILL.md \
           .claude/agents/self-critic.md .claude/agents/verification-lead.md \
           .claude/hooks/pre-commit-gate.sh
   git commit -m "validate: restructure to 3 waves (Det/Rule/Prob) per layer-triage; emit waves_passed"

   # Commit 2 — Fix 1 (CI shellcheck)
   git add .github/workflows/test.yml
   git commit -m "ci: drop dead template/ globs from shellcheck; align with verify-template.sh"

   # Commit 3 — Fix 3 (template-sync downgrade)
   git add CLAUDE.md.jinja bin/verify-template.sh
   git commit -m "template-sync: downgrade to experimental (loop never run end-to-end)"

   # Commit 4 — Fix 2 (CONTEXT.md.jinja as L1 skeleton + PROJECT-BACKGROUND.md.jinja split)
   git add CONTEXT.md.jinja PROJECT-BACKGROUND.md.jinja bin/verify-template.sh
   git commit -m "templates: split CONTEXT.md (L1 skeleton) from PROJECT-BACKGROUND.md (prose)"
   ```

   Note Fix 3 and Fix 4 both touch `verify-template.sh`. Stage the file twice with different hunks — `git add --patch bin/verify-template.sh` for each commit, selecting the relevant hunks.

5. Each commit will trigger `pre-commit-gate.sh`. If the gate blocks (sentinel stale or missing `waves_passed` field), re-run `/validate` and retry.

**Output:** four commits on a clean working tree; `.write-probe` files gone.

**Must NOT include:**
- Bundling fixes into one commit (defeats `git bisect` if anything regresses).
- Pushing to remote yet — wait until Phase 4 success.
- Touching skill content in this phase (Phase 3's job).

**Done looks like:** `git status` is clean; `git log --oneline -4` shows the four commit subjects above; `bin/verify-template.sh` exits 0.

---

## Phase 2 — Rename framework *(optional)*

Predecessor session suggested four single-word candidates: **Loam** (recommended), **Sourdough**, **Trellis**, **Saga**. Pick one or invent your own. Below assumes **Loam**.

**Inputs:**
- Every reference to `project_seed_framework` or `project-seed-framework` in the repo (use `rg -l "project[-_]seed[-_]framework"` to enumerate)
- The repo's GitHub URL (will need to be renamed via `gh repo rename`)
- The repo's local directory name

**Process:**

1. Decide on capitalization conventions:
   - CLI / package name: `loam` (lowercase)
   - Display name in docs: `Loam` (titlecase)
   - GitHub repo: `loam` or `loam-template` (your call — `loam` alone is fine, lots of empty namespace)
2. Find every reference: `rg -n "project[-_]seed[-_]framework"` — expect ~10–20 hits across `CLAUDE.md.jinja`, `TEMPLATE-*.md`, `README.md.jinja`, `bin/template-sync.sh`, `docs/SYNC.md`, `docs/BOOTSTRAP.md`, `V2.0-HANDOFF-SUMMARY.md`, possibly `.claude/skills/template-sync/SKILL.md`.
3. Replace each occurrence with the chosen name, attending to case.
4. Rename the local directory: `mv ~/Desktop/project_seed_framework ~/Desktop/loam`.
5. Rename the GitHub repo: `gh repo rename loam` (run from inside the renamed directory).
6. Update `.copier-answers.yml.jinja` if it references the source repo by name.
7. Update any local Claude Code project that was rendered from this template — their `.copier-answers.yml` will still point at the old repo name. They'll need a manual edit. List them: `find ~/Desktop -name '.copier-answers.yml' -exec grep -l 'project_seed_framework' {} \;`
8. Run `bin/verify-template.sh`. Commit:
   ```bash
   git commit -am "rename: project_seed_framework → loam"
   ```

**Output:** one commit; repo renamed locally and on GitHub.

**Must NOT include:**
- Renaming `template-sync` itself (it's the workflow name, not the framework name — keep it).
- Updating skill internals beyond reference substitution.

**Done looks like:** `rg "project[-_]seed[-_]framework"` returns zero matches (or only intentional historical references in `V2.0-HANDOFF-SUMMARY.md` — your call). `bin/verify-template.sh` exits 0.

---

## Phase 3 — Port parbench skills *(the leverage phase)*

Distbench will resemble parbench (both benchmarking work, both Python+HPC-flavored). The framework's whole point is to harvest cross-project conventions; this is where it earns its keep.

**Inputs:**
- Source: `~/Desktop/parbench_sam/.claude/` (read-only — do not modify parbench).
- Target: `<framework-root>/.claude/` and `<framework-root>/_research/`.
- Reference: parbench's structure was previously enumerated via `Glob /Users/samyakjhaveri/Desktop/parbench_sam/.claude/**/*.md` — see classification below.

### Classification (do not blindly copy everything)

**CORE — port to `.claude/skills/`, `.claude/agents/`, `.claude/rules/` (default flavor, every spawned project gets these):**

| Source (parbench) | Target | Reason |
|---|---|---|
| `skills/gen-spec/SKILL.md` | `skills/gen-spec/SKILL.md` | Spec-first workflow — forces written specs before code |
| `skills/spec-check/SKILL.md` | `skills/spec-check/SKILL.md` | Validates a spec against the schema before implementation |
| `skills/spec-validator/SKILL.md` | `skills/spec-validator/SKILL.md` | Runtime spec validator |
| `agents/spec-auditor.md` | `agents/spec-auditor.md` | Paired with gen-spec — adversarial spec review |
| `rules/spec-conventions.md` | `rules/spec-conventions.md` | Naming / shape conventions for spec files |
| `skills/agent-team/` *(full dir: SKILL.md, advisor-prompt.md, teammate-prompt.md, scenarios.md)* | `skills/agent-team/` | Advisor/teammate pattern for multi-agent deliberation; stronger than /multi-review for heavy decisions |
| `skills/model-route/SKILL.md` | `skills/model-route/SKILL.md` | Deterministic model dispatch — clean Layer-2 example fitting 60/30/10 |
| `skills/session-critique/` *(full dir: SKILL.md, teammates.md)* | `skills/session-critique/` | Retrospective skill — complements `reflect` and `dream` |
| `agents/diff-reviewer.md` | `agents/diff-reviewer.md` | More targeted than plan-reviewer for /validate Wave 3 |
| `agents/consistency-checker.md` | `agents/consistency-checker.md` | Cross-file consistency check |
| `agents/regression-checker.md` | `agents/regression-checker.md` | Useful in /validate Wave 2 or 3 |
| `agents/test-synthesizer.md` | `agents/test-synthesizer.md` | Generates test cases from a spec |

**RESEARCH-FLAVOR — port to `_research/skills/`, `_research/agents/`, `_research/rules/` (only rendered when `is_research=true`):**

| Source (parbench) | Target | Reason |
|---|---|---|
| `skills/eval-run/SKILL.md` | `_research/skills/eval-run/` | Benchmark sweep runner |
| `skills/eval-grader/SKILL.md` | `_research/skills/eval-grader/` | Grades eval outputs |
| `skills/overnight-eval/SKILL.md` | `_research/skills/overnight-eval/` | Long-running eval orchestrator |
| `skills/post-eval/SKILL.md` | `_research/skills/post-eval/` | Post-processing of eval results |
| `skills/interpret-results/SKILL.md` | `_research/skills/interpret-results/` | Statistical interpretation |
| `agents/eval-batcher.md` | `_research/agents/eval-batcher.md` | Batch dispatcher for eval runs |
| `skills/hpc-code-reviewer/SKILL.md` | `_research/skills/hpc-code-reviewer/` | HPC-aware code review |
| `skills/aris-shared-references/` *(citation-discipline, assurance-contract, effort-contract, reviewer-independence, venue-checklists, writing-principles)* | `_research/skills/aris-shared-references/` | Paper-writing shared rules |
| `skills/citation-audit/SKILL.md`, `skills/cite-check/SKILL.md` | `_research/skills/` | Citation verification |
| `skills/paper-write/SKILL.md`, `skills/paper-claim-audit/SKILL.md`, `skills/paper-review-sim/SKILL.md`, `skills/rebuttal/SKILL.md` | `_research/skills/` | Paper-writing pipeline |
| `skills/grill-research/SKILL.md`, `skills/hypothesis-tree/SKILL.md`, `skills/augment-test/SKILL.md` | `_research/skills/` | Research-specific reasoning skills |

**SKIP — do not port:**

| Source (parbench) | Reason |
|---|---|
| `skills/cuda-omp-translator/`, `agents/rodinia-verifier.md`, `agents-archive/xsbench-explorer.md`, `agents/verify-app.md` | Parbench-specific hardware/benchmark suite |
| `skills/validate/`, `skills/fix-bug/`, `skills/feature-dev/`, `skills/catchup/`, `skills/dream/`, `skills/reflect/`, `skills/handoff/`, `skills/techdebt/` | Seed already has equivalents — DO NOT overwrite without comparing first |
| `agents/code-simplifier.md`, `agents/self-critic.md`, `agents/plan-reviewer.md`, `agents/explorer.md`, `agents/verification-lead.md`, `agents/security-scanner.md` | Seed already has these — compare and merge any improvements only if a clear win |
| `skills/workflow-ref/SKILL.md`, `skills/navigate/`, `skills/mentoring/` | Parbench-specific; seed has `scaffold-context` for routing |
| `skills/auto-paper-improvement-loop/SKILL.md` | Too parbench/paper-specific |
| `agents-archive/*` | Already archived in source — don't resurrect |

### Process

For each skill / agent / rule in the CORE and RESEARCH-FLAVOR tables above:

1. **Read** the source file in full. Look for parbench-specific references:
   - Hard-coded paths like `~/Desktop/parbench_sam/`, `parbench/`, `rodinia/`, `xsbench/`
   - Domain-specific assumptions (CUDA kernels, OpenMP pragmas, specific benchmark names)
   - References to files that exist in parbench but won't exist in a fresh project (e.g., `MODEL_CONFIG_REFERENCE.md`)
2. **Decide** per file: PORT AS-IS / PORT-WITH-GENERALIZATION / SKIP. If you decide SKIP for a file the table marks CORE/RESEARCH-FLAVOR, write a one-line justification in this doc's "Deviations" section at the bottom.
3. **Copy** the file (or directory) to the target path. Use `cp -r` from bash if it's a directory, or `Read` + `Write` if you need to scrub.
4. **Scrub** parbench-specific references: replace hard paths with `{{PROJECT_ROOT}}` or relative paths; replace domain-specific examples with generic ones; remove `MODEL_CONFIG_REFERENCE.md`-style references unless that file is also being ported.
5. **Verify** each ported skill's frontmatter still parses: every `SKILL.md` must have `name:` and `description:` per `bin/verify-template.sh`'s agentskills.io schema check.
6. **Update counters**: `session-start.sh` references "19 total" skills. After porting, count: `find .claude/skills -mindepth 1 -maxdepth 1 -type d | wc -l`. Update the `19 total` string in `session-start.sh` to match. Same for research-flavor if applicable.
7. **Update `verify-template.sh`** if the research-flavor invariants need to add tests for newly-rendered skills.
8. **Run `bin/verify-template.sh`** after each batch of ~5 skills. If it fails, fix before continuing.
9. **Commit** in batches of ~5 related skills per commit (e.g., "port spec workflow from parbench: gen-spec, spec-check, spec-validator, spec-auditor, spec-conventions").

### Output

~12 new skills, ~5 new agents, ~1 new rule in `.claude/`; ~15 new skills / 1 new agent in `_research/`. New commit count: ~5–8.

### Must NOT include

- Overwriting any existing seed skill without explicit decision recorded here.
- Porting a file with a domain-specific reference left unscubbed (e.g., a skill that mentions `rodinia` and applies only to CUDA kernels — that's parbench-specific cargo).
- Porting skills marked SKIP without a justification in this doc.
- Bundling unrelated skills into one commit.
- Pushing to remote until Phase 4 also passes.

### Done looks like

- `find .claude/skills -mindepth 1 -maxdepth 1 -type d | wc -l` returns ~31 (was 19).
- `find _research/skills -mindepth 1 -maxdepth 1 -type d | wc -l` returns ~15.
- `bin/verify-template.sh` exits 0 in both default and research flavors.
- `session-start.sh`'s skill count string matches actual.
- A scratch render with `is_research=true` shows the new research skills appearing.

---

## Phase 4 — Render distbench + bootstrap

**Inputs:** the upgraded framework (Phases 1–3 complete and committed).

### 4.1 Render

```bash
cd ~/Desktop
uvx copier copy --trust \
  --data project_name=distbench \
  --data is_research=true \
  --data github_repo=samyakjhaveri/distbench \
  ~/Desktop/loam ./distbench    # path is the framework, even if renamed
```

If you haven't renamed (skipped Phase 2), substitute `~/Desktop/project_seed_framework`.

If `gh` is configured, the post-render `_tasks` block in `copier.yml` will offer to create the GitHub repo. Decide at the prompt.

### 4.2 First Claude Code session in distbench

```bash
cd ~/Desktop/distbench
claude              # opens Claude Code; SessionStart hook fires
```

In-session:

1. **Read** the rendered `CLAUDE.md` and `PROJECT-BACKGROUND.md`. They're skeletons — fill them in.
2. **Fill `PROJECT-BACKGROUND.md` first** — the prose comes first because it answers "why does this project exist" and unblocks every other authoring step. Put real text in: what problem distbench solves, who the user is (likely you + future-you), constraints (hardware, deadlines, paper venue if any), prior art (parbench, MLPerf, anything you're building on), glossary.
3. **Update `CLAUDE.md` "Current State" section** with: today's date, what you intend to build first, what's NOT in scope yet.
4. **Decide on root `CONTEXT.md`**: it's a skeleton. Either fill it for the project root or `rm CONTEXT.md` and rely on `/scaffold-context` for subdirectory routing files later. Don't leave it as a stub.
5. **Author domain rules**:
   - `.claude/rules/tech-stack.md` — your Python version, key deps (likely: pytest, hypothesis, asyncio, possibly Ray/Dask), build system, run commands
   - `.claude/rules/architecture.md` — the system-level shape (workers, coordinator, message bus, persistence)
   - If distributed-specific gotchas exist (clock skew, partial-failure semantics, leader-election bugs), add a `.claude/rules/distributed-invariants.md`
6. **Skill-tiering audit** — the rendered skill set includes ~31 core + 15 research. `.claude/rules/known-issues.md` documents the convention: specialized skills should have `auto-activate: false`. Walk through the new skills and tier them.
7. **First task — author its L2 stage contract before any code.** Pick the smallest meaningful unit (e.g., "scaffold the runner loop with mocked workers"). Open `.claude/rules/stage-contract.md` and write the contract for that task. This is the framework's discipline; bypassing it on task 1 sets a bad precedent.

### 4.3 Output

A `~/Desktop/distbench/` repo with:
- Filled CLAUDE.md + PROJECT-BACKGROUND.md
- Domain rules in `.claude/rules/`
- A first L2 stage contract written (in `docs/contracts/01-runner-scaffolding.md` or similar)
- Zero code yet — the contract goes first.

### Must NOT include

- Writing any production code in this phase. Phase 4 is bootstrap only. The first code goes in Phase 5 (out of scope for this plan), and it goes through the framework's normal `implement → /validate → commit` loop.
- Skipping `PROJECT-BACKGROUND.md` because "you know the project." Future-you will not. Write it now.
- Auto-activating every ported skill. The whole tiering convention exists to prevent that.

### Done looks like

- `cat distbench/PROJECT-BACKGROUND.md` shows real content, not placeholder text.
- `cat distbench/CLAUDE.md` has a populated "Current State" section.
- `ls distbench/.claude/rules/` shows at least `tech-stack.md`, `architecture.md`, and the standard rules.
- One L2 stage contract exists, ready for the first implementation session.
- `git -C distbench log` shows at least 2 commits (initial scaffold + bootstrap).

---

## What NOT to do across this entire plan

- **Don't skip Phase 1 step 3** (running `/validate` on the pending diff). It's the bootstrap test of Fix 4. If the new wave structure has a bug, you want to find it before three more phases of work pile on top of it.
- **Don't try to do Phases 1–4 in one Claude Code session.** `/clear` between phases. Per the framework's own `workflow.md`, this is a multi-session project; let it be.
- **Don't add new skills you invent during Phase 3 — only port.** New skills authored fresh belong in Phase 5 (post-bootstrap distbench work), not here. Discipline: this plan ports parbench's existing work; novel skill design is a separate stage contract.
- **Don't push to remote until Phase 4 succeeds.** A clean local history lets you `git reset --hard` if any phase reveals a deep issue.
- **Don't trust the parbench skill catalog blindly.** Read each before porting. The classification table above was authored from a directory listing, not full reads; expect 1–2 surprises.

---

## Deviations log (fill in during execution)

> Record each time you deviate from the plan, with a one-line justification.
> Future-you reading this in three months will thank you.

- (Add entries here as you go.)

---

## Open questions for the user (resolve before starting)

1. **Distbench scope:** distributed systems benchmarking in the MLPerf-style sense, or something else? The `is_research=true` recommendation in Phase 4 assumes paper-flavored work. Adjust if not.
2. **Rename or not:** if yes, pick a name before Phase 2 starts. If no, skip Phase 2 cleanly.
3. **Phase 3 scope:** if distbench is <2 weeks, consider porting only the spec workflow (5 files) and agent-team (4 files) and skipping the research overlay. ~30 min instead of 90.

---

## References

- `.claude/rules/workflow.md` — 6-stage workflow + anti-patterns
- `.claude/rules/stage-contract.md` — L2 contract anatomy
- `.claude/rules/layer-triage.md` — 60/30/10 framework
- `.claude/rules/validation-loop.md` — 3-wave Pipeline Gate (after Fix 4)
- `bin/verify-template.sh` — the framework's structural invariants
- `~/Desktop/parbench_sam/.claude/` — source of truth for Phase 3 porting
