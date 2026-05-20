# Loam v3.0 Architecture Redesign — Implementation Spec

> **Status:** Ready for implementation
> **Owner:** Samyak Jhaveri
> **Breaking change:** Yes — existing v2.0 projects must re-bootstrap (see §11)
> **Releases:** v3.0 = structural migration + skill consolidation; v3.1 = JVC deepening (separate)

---

## Context

Loam is a Copier template (`copier.yml` at repo root) that bootstraps Claude Code projects. v2.0 uses a single-tree design where `.claude/` at the repo root serves both as the template's own config AND the deliverable shipped to projects. This requires 36 `_exclude` patterns in `copier.yml` to prevent template machinery (docs, scripts, course files) from leaking into rendered projects.

**Why v3.0:** The leak-by-default architecture is fragile — every new file needs an exclusion rule. Skills compete for auto-invocation with unclear value (user reports uncertainty about which skills help). AGENTS.md is underutilized despite Vercel research showing persistent context achieves 100% task success vs 79% for on-demand skills.

**Target audience:** Author + small technical team.

---

## 1. Repository Structure

### Core Change
Set Copier's `_subdirectory: seed`. Everything outside `seed/` is invisible to Copier. Safe-by-default: new files never leak unless explicitly placed in `seed/`.

### Proposed Directory Tree

```
loam/
├── .claude → seed/.claude           # SYMLINK for dev experience
├── CLAUDE.md                        # Template repo's own L0 (replaces TEMPLATE-CLAUDE.md)
│
├── seed/                            # === Copier _subdirectory — ALL deliverables ===
│   ├── .claude/
│   │   ├── skills/ (17)             # Curated callable skills
│   │   │   ├── catchup/
│   │   │   ├── commit/
│   │   │   ├── pr/
│   │   │   ├── handoff/
│   │   │   ├── feature-dev/
│   │   │   ├── fix-bug/
│   │   │   ├── gen-spec/            # absorbs spec-check
│   │   │   ├── validate/
│   │   │   ├── multi-review/
│   │   │   ├── session-critique/
│   │   │   ├── techdebt/
│   │   │   ├── researcher/
│   │   │   ├── dream/               # absorbs reflect + know-me
│   │   │   ├── agent-team/
│   │   │   ├── create-skill/
│   │   │   ├── template-sync/
│   │   │   └── scaffold-context/
│   │   ├── agents/ (6)
│   │   │   ├── verification-lead.md  # absorbs consistency-checker, regression-checker, test-synthesizer
│   │   │   ├── plan-reviewer.md      # absorbs spec-auditor
│   │   │   ├── self-critic.md        # absorbs code-simplifier
│   │   │   ├── diff-reviewer.md
│   │   │   ├── explorer.md
│   │   │   └── security-scanner.md
│   │   ├── rules/ (12)
│   │   │   ├── workflow.md           # always loaded
│   │   │   ├── known-issues.md       # always loaded
│   │   │   ├── L0-budget.md
│   │   │   ├── context-md-anatomy.md
│   │   │   ├── stage-contract.md
│   │   │   ├── layer-triage.md
│   │   │   ├── validation-loop.md
│   │   │   ├── spec-conventions.md
│   │   │   ├── python.md             # path-scoped: .py files
│   │   │   ├── frontend-design.md    # path-scoped: frontend files
│   │   │   ├── architecture.md       # path-scoped: arch docs
│   │   │   └── tech-stack.md         # path-scoped: build/config
│   │   ├── hooks/ (8)
│   │   │   ├── pre-commit-gate.sh
│   │   │   ├── sentinel-cleanup.sh
│   │   │   ├── result-immutability.sh
│   │   │   ├── session-start.sh      # updated for 17-skill count
│   │   │   ├── dream-hook.sh         # absorbs should-dream.sh logic
│   │   │   ├── post-compact-recovery.sh
│   │   │   ├── bash-audit-log.sh
│   │   │   └── post-edit-test.sh
│   │   ├── reference/
│   │   │   └── Claude Code Operational Playbook.md
│   │   └── settings.json             # updated hook registrations
│   │
│   ├── _research/                    # Research overlay — INSIDE seed/ for Copier access
│   │   ├── skills/ (19)
│   │   ├── agents/
│   │   ├── hooks/
│   │   ├── rules/
│   │   ├── seed-docs/
│   │   └── settings-hooks.json
│   │
│   ├── _copier_merge_hooks.py        # Inside seed/ — rendered then deleted by _tasks
│   ├── CLAUDE.md.jinja               # L0 map (~800 tokens)
│   ├── AGENTS.md.jinja               # Persistent context (~6KB, see §3 for token budget)
│   ├── README.md.jinja
│   ├── .gitignore.jinja
│   ├── .mcp.json.jinja
│   ├── .copier-answers.yml.jinja
│   └── pyproject.toml.jinja
│
├── cultivation/                      # Skill development & staging
│   ├── wip/                          # Skills under active development
│   ├── marketplace/                  # Was seed-skills/ — cut skills for future plugin
│   └── retired/                      # Skills removed from seed
│
├── soil/                             # Knowledge base & learning materials
│   ├── jvc/                          # Was claude_code_course_files/jvc_vault/
│   │   ├── constraints/              # 8 core constraint documents
│   │   ├── architectures/
│   │   ├── examples/
│   │   └── toolkit/
│   ├── foundation/                   # Was claude_code_course_files/jvc_foundation/
│   ├── playbooks/                    # Operational playbooks
│   └── reference/                    # Was internal_docs/ + human mastery guide
│
├── bin/                              # Template maintenance scripts
│   ├── verify-template.sh            # REWRITTEN for seed/ paths
│   ├── release.sh
│   ├── lint-skill-descriptions.sh    # Updated for seed/ paths
│   └── template-sync.sh             # Updated: resolve_template_claude_root → seed/
│
├── docs/
│   ├── BOOTSTRAP.md
│   ├── SYNC.md
│   ├── FLAVORS.md
│   ├── ASSET-LAYERS.md
│   ├── MEMORY.md
│   └── MIGRATION-v3.md              # NEW: migration guide for v2.0 projects
│
├── copier.yml                        # _subdirectory: seed + reduced _exclude
├── VERSION                           # 3.0.0
└── LICENSE
```

### Critical Design Decisions

**Symlink `.claude/ → seed/.claude/`**: Claude Code reads `.claude/` from the project root. The symlink lets the template repo use its own delivered config. On macOS/Linux this works transparently. On Windows (symlinks require elevation), work directly in `seed/.claude/`. After `git clone`, recreate with: `ln -s seed/.claude .claude`.

**Research overlay at `seed/_research/`**: Must be inside `seed/` because Copier with `_subdirectory: seed` only renders files from `seed/`. With `_research/` inside `seed/`, Copier copies it into the project as `_research/`, then `_tasks` process and delete it — identical to v2.0 behavior. The existing `_tasks` commands (`cp -R _research/skills/* .claude/skills/`) work unchanged.

**`_copier_merge_hooks.py` at `seed/_copier_merge_hooks.py`**: Same reasoning — must be inside `seed/` for Copier to copy it into the project for `_tasks` to use.

**CLAUDE.md split**: Root `CLAUDE.md` describes the template repo (what TEMPLATE-CLAUDE.md did). `seed/CLAUDE.md.jinja` is the project template. No more TEMPLATE-CLAUDE.md confusion.

**Not "zero exclusions"**: Copier still needs ~8 generic exclusions inside `seed/` (`.DS_Store`, `*.pyc`, `__pycache__`, `.git`, runtime state files). But all 28 template-machinery exclusions (`bin/`, `docs/`, `seed-skills/`, `claude_code_course_files/`, `TEMPLATE-*.md`, etc.) are eliminated because those files are now outside `seed/`.

---

## 2. Skill Consolidation

### Principle
If a skill is mostly guidance (rules, patterns, checklists), fold it into AGENTS.md persistent context. If it's a procedure (multi-step execution with file I/O and state), keep it as a callable skill.

### 17 Callable Skills (from 24)

| Group | Skills | Count |
|---|---|---|
| Session lifecycle | `/catchup`, `/commit`, `/pr`, `/handoff` | 4 |
| Development flow | `/feature-dev`, `/fix-bug`, `/gen-spec` (absorbs spec-check) | 3 |
| Quality gate | `/validate`, `/multi-review`, `/session-critique`, `/techdebt` | 4 |
| Knowledge | `/researcher`, `/dream` (absorbs reflect + know-me) | 2 |
| Orchestration | `/agent-team` | 1 |
| Context | `/scaffold-context` (kept — has 7-step procedure with file I/O) | 1 |
| Meta | `/create-skill`, `/template-sync` | 2 |

### 7 Skills Removed

**4 dissolved into AGENTS.md** (guidance → persistent context):

| Skill | AGENTS.md Section | Rationale |
|---|---|---|
| karpathy-guidelines | §1 Engineering Principles | Behavioral guidelines, no file I/O |
| model-route | §2 Model Selection | Decision table, no execution steps |
| security | §2 Security Practices | OWASP checklist, no multi-step procedure |
| scalability | §2 Scalability Practices | Pattern catalog, no procedure |

**3 merged into existing skills** (overlapping scope):

| Skill | Absorbed By | Rationale |
|---|---|---|
| reflect | `/dream` | Both do post-session reflection; dream is more comprehensive |
| know-me | Native Claude auto-memory | Claude's built-in auto-memory handles user preference capture |
| spec-check | `/gen-spec` | Spec validation becomes a sub-step (e.g., `/gen-spec validate <path>`) |

### 6 Agents (from 11)

**Keep (6):** verification-lead (absorbs consistency-checker + regression-checker + test-synthesizer), plan-reviewer (absorbs spec-auditor), self-critic (absorbs code-simplifier), diff-reviewer, explorer, security-scanner.

**Remove (5):** code-simplifier, consistency-checker, regression-checker, test-synthesizer, spec-auditor — content merged into the 6 remaining agents.

### 8 Hooks (from 12)

**Keep (8):** pre-commit-gate.sh, sentinel-cleanup.sh, result-immutability.sh, session-start.sh (updated), dream-hook.sh (absorbs should-dream.sh), post-compact-recovery.sh, bash-audit-log.sh, post-edit-test.sh.

**Remove (4):** should-dream.sh (merged into dream-hook.sh), codex-review-reminder.sh (→ AGENTS.md), context-budget.sh (Claude Code native), test-bash-audit-log.sh (test fixture).

### 7 Templates (from 14)

**Keep (7):** CLAUDE.md.jinja, AGENTS.md.jinja, README.md.jinja, .gitignore.jinja, .mcp.json.jinja, .copier-answers.yml.jinja, pyproject.toml.jinja.

**Remove (7):** HANDOFF.md.jinja, MEMORY.md.jinja, CONTEXT.md.jinja, ARCHITECTURE.md.jinja, DESIGN.md.jinja, PROJECT-BACKGROUND.md.jinja, SCRIPTS_DIRECTORY.md.jinja — all generated on demand by skills when actually needed.

---

## 3. Content Architecture

Three-layer content stack. JVC's voice architecture (Constraint 05) adapted for engineering.

### CLAUDE.md — L0 (~800 tokens) — "Where am I?"

Always loaded. Map, not manual. Claude-specific features (permissions, hooks, session rules).

### AGENTS.md — Persistent Guidance (~6KB) — "How do we work?"

Always loaded. Universal (works in Claude Code, Cursor, Copilot, Codex).

**Token budget acknowledgment:** AGENTS.md adds ~4,500 tokens to every session's always-loaded context (alongside CLAUDE.md's ~800). Total always-loaded: ~5,300 tokens (~2.5% of a 200K context window). This is an intentional trade-off: Vercel's research showed persistent context at this scale achieves near-perfect task success. The cost is paid once per session; the guidance compounds across every tool call.

**Three-section structure (JVC voice architecture adapted):**

**§1 Engineering Principles** (direction — changes rarely)
- Source: karpathy-guidelines content
- Surgical changes, YAGNI, verify before claiming done, prefer existing patterns, make assumptions explicit

**§2 Output Patterns** (structure — grows slowly)
- Security Practices (from security skill — OWASP awareness, input validation)
- Scalability Practices (from scalability skill — DB patterns, caching, async)
- Model Selection (from model-route — Opus vs Sonnet decision table)
- Project Conventions (blank section — each project fills this in)

**§3 Hard Constraints** (never-do — highest impact-per-token)
- Source: JVC Common Mistakes (Example 04) adapted for engineering
- Specific prohibitions: no giant CLAUDE.md, no skills without triggers, no undocumented handoffs, test deterministically before LLM validation

### .claude/rules/ — L1/L2 (~300 tokens each) — "What do I do here?"

On-demand. 2 always-loaded (workflow.md, known-issues.md). 5 JVC rules loaded by task. 4 path-scoped rules loaded by file type.

---

## 4. Delivery & Sync

### Bootstrap (New Project)
```bash
uvx copier copy gh:samyakjhaveri/loam ./my-project
```
Copier renders `seed/` → project root. `_tasks` conditionally merge research overlay, create seed dirs, init git.

### Update (Pull Template Changes)
```bash
cd my-project && uvx copier update
```
**IMPORTANT:** v3.0 is a breaking release. The `_subdirectory` change from `"."` to `"seed"` means `copier update` from a v2.0-bootstrapped project will NOT merge cleanly — Copier will see all old-root files as deleted and all seed/ files as new. Existing v2.0 projects must re-bootstrap (see §11 Migration Guide).

Future updates (v3.0 → v3.1, v3.1 → v3.2) will work normally via `copier update`.

### Promote (Push Innovation Back)
```bash
/template-sync promote --layer generic .claude/skills/my-skill/
```
Target: `seed/.claude/skills/` (updated from `.claude/skills/`).

---

## 5. Reduction Summary

| Component | v2.0 | v3.0 | Change |
|---|---|---|---|
| Core Skills | 24 | 17 | -29% (4 dissolved + 3 merged) |
| Agents | 11 | 6 | -45% (5 merged) |
| Hooks | 12 | 8 | -33% (4 removed/merged) |
| Templates | 14 | 7 | -50% (7 generated on-demand) |
| Copier Exclusions | 36 | ~8 | -78% (only generic noise exclusions remain) |
| Rules | 12 | 12 | Unchanged |
| Research Skills | 19 | 19 | Unchanged (moved to seed/_research/) |

---

## 6. Scripts That Need Updating

These scripts contain hardcoded paths that will break with the restructure. **All must be updated in Phase 1** to ensure each phase produces a working state.

### `copier.yml`

| Change | Detail |
|---|---|
| `_subdirectory` | `"."` → `"seed"` |
| `_exclude` | Remove 28 template-machinery patterns. Keep ~8 generic patterns (`.DS_Store`, `*.pyc`, `__pycache__`, `*.bak`, `.git`, `.claude/audit.log`, `.claude/.local-paths`, `.claude/settings.local.json`, `.claude/worktrees`) |
| `_tasks` | **No changes needed** — `_tasks` run in the rendered project dir where `_research/` appears at root (copied from `seed/_research/`). All `cp -R _research/...` commands work unchanged. |

### `bin/verify-template.sh` — COMPLETE REWRITE

| Current path | New path |
|---|---|
| `find .claude/skills` (line 36) | `find seed/.claude/skills` (or follows via symlink) |
| `_research/hooks/*.sh` (line 55) | `seed/_research/hooks/*.sh` |
| `find .claude/skills _research/skills seed-skills` (line 78) | `find seed/.claude/skills seed/_research/skills cultivation/marketplace` |
| `test ! -d "$TMP/default/seed-skills"` (line 121) | `test ! -d "$TMP/default/cultivation"` (cultivation should not leak) |
| Check for `TEMPLATE-CLAUDE.md` (line 30) | Remove — replaced by root `CLAUDE.md` |
| Skill count in session-start.sh (line 36-39) | Update expected count: 24 → 17 |
| Assert HANDOFF.md, CONTEXT.md, etc. rendered | Remove assertions for deleted templates |

### `bin/lint-skill-descriptions.sh`

| Current path | New path |
|---|---|
| `find "$ROOT/.claude/skills" "$ROOT/_research/skills" "$ROOT/seed-skills"` (line 70) | `find "$ROOT/seed/.claude/skills" "$ROOT/seed/_research/skills" "$ROOT/cultivation/marketplace"` |

### `bin/template-sync.sh`

| Current logic | New logic |
|---|---|
| `resolve_template_claude_root()` returns `$tpl` | Returns `$tpl/seed` |
| `template_path_for()` generic → `.claude/` | generic → `seed/.claude/` |
| `template_path_for()` flavor → `_<FLAVOR>/` | flavor → `seed/_<FLAVOR>/` |
| Comment on line 75 referencing `_<FLAVOR>/` | Update to `seed/_<FLAVOR>/` |

### `seed/.claude/hooks/session-start.sh`

| Current | New |
|---|---|
| "CORE SKILLS (.claude/skills/ — 24 total)" | "CORE SKILLS (.claude/skills/ — 17 total)" |
| Skill category listing (lines 16-20) | Updated to reflect consolidated skill set |

### `seed/.claude/hooks/dream-hook.sh`

| Current | New |
|---|---|
| Calls `should-dream.sh` externally (line ~64) | Inline the should-dream logic (24h check) |

---

## 7. Verification Plan

### Phase 1 Verification (after restructure)

| # | Check | Command | Expected |
|---|---|---|---|
| V1 | Symlink resolves | `ls -la .claude && test -d .claude/skills` | `.claude -> seed/.claude`, skills dir exists |
| V2 | Copier default render | `uvx copier copy --defaults -d project_name=test-default . /tmp/v3-test-default` | Project has `.claude/skills/`, `CLAUDE.md`, no `cultivation/`, no `soil/` |
| V3 | Copier research render | `uvx copier copy --defaults -d project_name=test-research -d is_research=true . /tmp/v3-test-research` | Has research skills (paper-write, citation-audit), `_research/` cleaned up |
| V4 | No template leaks | `test ! -d /tmp/v3-test-default/cultivation && test ! -d /tmp/v3-test-default/soil && test ! -d /tmp/v3-test-default/bin` | All pass |
| V5 | verify-template.sh | `bin/verify-template.sh` | ALL OK |
| V6 | lint-skill-descriptions | `bin/lint-skill-descriptions.sh` | No errors |
| V7 | Session-start skill count | `grep -c "CORE SKILLS" seed/.claude/hooks/session-start.sh` and compare to actual `find seed/.claude/skills -mindepth 1 -maxdepth 1 -type d \| wc -l` | Counts match (17) |
| V8 | Hook paths resolve | For each hook in `seed/.claude/settings.json`: `test -f "seed/$hook_path"` | All exist |

### Phase 2 Verification (after skill consolidation)

| # | Check | Command | Expected |
|---|---|---|---|
| V9 | Removed skills gone | `test ! -d seed/.claude/skills/karpathy-guidelines && test ! -d seed/.claude/skills/model-route && test ! -d seed/.claude/skills/security && test ! -d seed/.claude/skills/scalability` | All pass |
| V10 | Merged skills gone | `test ! -d seed/.claude/skills/reflect && test ! -d seed/.claude/skills/know-me && test ! -d seed/.claude/skills/spec-check` | All pass |
| V11 | Remaining skill count | `find seed/.claude/skills -mindepth 1 -maxdepth 1 -type d \| wc -l` | 17 |
| V12 | Removed agents gone | `test ! -f seed/.claude/agents/code-simplifier.md && test ! -f seed/.claude/agents/consistency-checker.md && test ! -f seed/.claude/agents/regression-checker.md && test ! -f seed/.claude/agents/test-synthesizer.md && test ! -f seed/.claude/agents/spec-auditor.md` | All pass |
| V13 | Remaining agent count | `find seed/.claude/agents -name "*.md" \| wc -l` | 6 |
| V14 | Removed hooks gone | `test ! -f seed/.claude/hooks/should-dream.sh && test ! -f seed/.claude/hooks/codex-review-reminder.sh && test ! -f seed/.claude/hooks/context-budget.sh && test ! -f seed/.claude/hooks/test-bash-audit-log.sh` | All pass |
| V15 | Remaining hook count | `find seed/.claude/hooks -name "*.sh" \| wc -l` | 8 |
| V16 | Removed templates gone | `test ! -f seed/HANDOFF.md.jinja && test ! -f seed/MEMORY.md.jinja && test ! -f seed/CONTEXT.md.jinja && test ! -f seed/ARCHITECTURE.md.jinja && test ! -f seed/DESIGN.md.jinja && test ! -f seed/PROJECT-BACKGROUND.md.jinja && test ! -f seed/SCRIPTS_DIRECTORY.md.jinja` | All pass |
| V17 | Remaining template count | `find seed -maxdepth 1 -name "*.jinja" \| wc -l` | 7 |
| V18 | AGENTS.md has 3 sections | `grep -c "^## " seed/AGENTS.md.jinja` | At least 3 |
| V19 | settings.json valid JSON | `python3 -m json.tool seed/.claude/settings.json > /dev/null` | Success |
| V20 | settings.json has 8 hooks | Count unique hook commands in settings.json | 8 |
| V21 | Full render test | `uvx copier copy --defaults -d project_name=v3-full . /tmp/v3-full-test` | Clean render, all 17 skills present |

### End-to-End Verification (Phase 3)

| # | Check | Expected |
|---|---|---|
| V22 | Bootstrap project → run /catchup | Session brief shows 17 skills, correct framework version |
| V23 | Bootstrap research project | 19 research skills present, REFERENCES.md rendered |
| V24 | Template-sync status in bootstrapped project | Reports correct template path and asset counts |
| V25 | Root CLAUDE.md describes template (not project) | Contains "Copier template", not "{{ project_name }}" |

---

## 8. Rollback Strategy

Each phase is implemented on a feature branch. Rollback = abandon the branch.

| Phase | Branch | Rollback |
|---|---|---|
| Phase 1 | `rework/v3-restructure` | `git checkout main` — v2.0 still works |
| Phase 2 | `rework/v3-consolidation` (from Phase 1) | `git reset --hard` to Phase 1 commit — structure intact, old skills restored |
| Phase 3 | `rework/v3-release` (from Phase 2) | `git reset --hard` to Phase 2 commit |

**Stop condition:** If verify-template.sh fails after 3 fix attempts in any phase, the issue is likely a design flaw. Stop, re-evaluate, and update this spec before retrying.

---

## 9. Implementation Plan

### Pre-Implementation
- Read this spec fully
- Run `/catchup` to understand current state
- Create branch: `git checkout -b rework/v3-restructure`

### Phase 1: Repository Restructure

**Goal:** Move all files to their new locations. Update all scripts. Verify renders work.

**Step 1.1 — Create directory structure:**
```bash
mkdir -p seed cultivation/wip cultivation/marketplace cultivation/retired
mkdir -p soil/jvc soil/foundation soil/playbooks soil/reference
```

**Step 1.2 — Move deliverables into seed/:**
```bash
# Move .claude/ directory (the main deliverable)
mv .claude seed/.claude

# Move .jinja template files (keep only 7)
mv CLAUDE.md.jinja AGENTS.md.jinja README.md.jinja .gitignore.jinja .mcp.json.jinja .copier-answers.yml.jinja pyproject.toml.jinja seed/

# Move research overlay INTO seed (critical — must be inside seed for Copier)
mv _research seed/_research

# Move merge script into seed
mv _copier_merge_hooks.py seed/_copier_merge_hooks.py
```

**Step 1.3 — Move non-deliverables to new locations:**
```bash
# Course files → soil
mv claude_code_course_files/jvc_vault/jvc_vault_files/the_full_toolkit/vault-toolkit/constraints soil/jvc/constraints
mv claude_code_course_files/jvc_vault/jvc_vault_files/the_full_toolkit/vault-toolkit/architectures soil/jvc/architectures
mv claude_code_course_files/jvc_vault/jvc_vault_files/workspace-blueprint/_examples soil/jvc/examples
mv claude_code_course_files/jvc_foundation soil/foundation
mv internal_docs/* soil/reference/ 2>/dev/null || true
# Keep claude_code_course_files around until confirmed all content migrated, then delete

# Marketplace skills → cultivation
mv seed-skills/* cultivation/marketplace/ 2>/dev/null || true

# Remove obsolete files
rm -f TEMPLATE-CLAUDE.md TEMPLATE-README.md TEMPLATE-HANDOFF.md V2.0-HANDOFF-SUMMARY.md
rm -f seed/HANDOFF.md.jinja seed/MEMORY.md.jinja seed/CONTEXT.md.jinja
rm -f seed/ARCHITECTURE.md.jinja seed/DESIGN.md.jinja seed/PROJECT-BACKGROUND.md.jinja seed/SCRIPTS_DIRECTORY.md.jinja
```

**Step 1.4 — Create symlink:**
```bash
ln -s seed/.claude .claude
```

**Step 1.5 — Write root CLAUDE.md (template's own config):**
Write a new `CLAUDE.md` at repo root that describes the template repo itself. Content: what Loam is, the seed/cultivation/soil layout, pointer to docs/, workflow for template development. Keep under 100 lines (~800 tokens).

**Step 1.6 — Update copier.yml:**
- Change `_subdirectory: "."` → `_subdirectory: "seed"`
- Replace 36 `_exclude` patterns with ~8 generic ones:
  ```yaml
  _exclude:
    - ".DS_Store"
    - "*.pyc"
    - "__pycache__"
    - "*.bak"
    - ".git"
    - ".claude/audit.log"
    - ".claude/.local-paths"
    - ".claude/settings.local.json"
    - ".claude/worktrees"
  ```
- `_tasks` section: **no changes needed** (paths are relative to rendered project, not template)

**Step 1.7 — Update bin scripts:**

Update `bin/verify-template.sh` — **this is a rewrite, not a patch**. See §6 for the full path mapping table. Key changes:
- All `.claude/` references → `seed/.claude/` (or resolve via symlink)
- All `_research/` references → `seed/_research/`
- All `seed-skills/` references → `cultivation/marketplace/`
- Remove TEMPLATE-CLAUDE.md check
- Update skill count assertion: 24 → 17
- Update render assertions: remove deleted template checks (HANDOFF.md, CONTEXT.md, etc.)

Update `bin/lint-skill-descriptions.sh`:
- Line 70: `_research/skills` → `seed/_research/skills`, `seed-skills` → `cultivation/marketplace`

Update `bin/template-sync.sh`:
- `resolve_template_claude_root()` → return `$tpl/seed`
- `template_path_for()` generic → `seed/.claude/`, flavor → `seed/_<FLAVOR>/`

**Step 1.8 — Verify Phase 1:**
Run verification checks V1–V8 (see §7). All must pass before proceeding.

**Step 1.9 — Commit Phase 1:**
```bash
git add -A && git commit -m "restructure: move deliverables into seed/ subdirectory (v3.0-alpha)"
```

---

### Phase 2: Skill & Agent Consolidation

**Goal:** Remove dissolved/merged skills, agents, hooks, templates. Write AGENTS.md. Update settings.json.

**Step 2.1 — Write AGENTS.md.jinja:**
Rewrite `seed/AGENTS.md.jinja` with three-section structure:
- §1 Engineering Principles ← content from `seed/.claude/skills/karpathy-guidelines/SKILL.md`
- §2 Output Patterns ← content from security, scalability, model-route SKILL.md files
- §3 Hard Constraints ← JVC common mistakes adapted for engineering
- Include `{{ project_name }}` template variable
- Target size: ~6KB (4,500 tokens)

Read each dissolved skill's SKILL.md BEFORE removing it to extract the guidance content.

**Step 2.2 — Merge skill content before removal:**

For `/dream` absorbing reflect + know-me:
- Read `seed/.claude/skills/reflect/SKILL.md` — extract any unique reflection prompts not already in dream
- Read `seed/.claude/skills/know-me/SKILL.md` — verify auto-memory covers all functionality
- Add any unique content to `seed/.claude/skills/dream/SKILL.md`

For `/gen-spec` absorbing spec-check:
- Read `seed/.claude/skills/spec-check/SKILL.md` — extract validation checklist
- Add as a validation sub-step in `seed/.claude/skills/gen-spec/SKILL.md`
- Ensure `/gen-spec validate <path>` mode is documented

**Step 2.3 — Remove dissolved/merged skills:**
```bash
rm -rf seed/.claude/skills/karpathy-guidelines
rm -rf seed/.claude/skills/model-route
rm -rf seed/.claude/skills/security
rm -rf seed/.claude/skills/scalability
rm -rf seed/.claude/skills/reflect
rm -rf seed/.claude/skills/know-me
rm -rf seed/.claude/skills/spec-check
```

**Step 2.4 — Merge agent content:**

For verification-lead absorbing 3 agents:
- Read consistency-checker.md, regression-checker.md, test-synthesizer.md
- Merge their check capabilities into verification-lead.md
- Update verification-lead to orchestrate the combined checks

For plan-reviewer absorbing spec-auditor:
- Read spec-auditor.md, merge spec validation into plan-reviewer.md

For self-critic absorbing code-simplifier:
- Read code-simplifier.md, merge simplification lens into self-critic.md

**Step 2.5 — Remove merged agents:**
```bash
rm -f seed/.claude/agents/code-simplifier.md
rm -f seed/.claude/agents/consistency-checker.md
rm -f seed/.claude/agents/regression-checker.md
rm -f seed/.claude/agents/test-synthesizer.md
rm -f seed/.claude/agents/spec-auditor.md
```

**Step 2.6 — Merge dream-hook.sh with should-dream.sh:**
- Read `seed/.claude/hooks/should-dream.sh` — extract the 24h staleness check
- Inline that logic into `seed/.claude/hooks/dream-hook.sh`
- Remove: `rm -f seed/.claude/hooks/should-dream.sh`

**Step 2.7 — Remove other hooks:**
```bash
rm -f seed/.claude/hooks/codex-review-reminder.sh
rm -f seed/.claude/hooks/context-budget.sh
rm -f seed/.claude/hooks/test-bash-audit-log.sh
```

**Step 2.8 — Update settings.json:**
Remove hook registrations for the 4 deleted hooks. Ensure only 8 hooks remain.
If session-start.sh references should-dream.sh, update that reference.

**Step 2.9 — Update session-start.sh:**
- Change skill count from 24 to 17
- Update skill category listing to reflect new set

**Step 2.10 — Verify Phase 2:**
Run verification checks V9–V21 (see §7). All must pass.

**Step 2.11 — Commit Phase 2:**
```bash
git add -A && git commit -m "consolidate: 17 skills, 6 agents, 8 hooks, AGENTS.md guidance (v3.0-beta)"
```

---

### Phase 3: Release

**Goal:** Final cleanup, docs update, release tag.

**Step 3.1 — Update documentation:**
- `docs/BOOTSTRAP.md` — update for `_subdirectory: seed`
- `docs/SYNC.md` — update template-sync paths
- `docs/ASSET-LAYERS.md` — update layer paths
- `docs/FLAVORS.md` — update `_research/` → `seed/_research/`
- Write `docs/MIGRATION-v3.md` — migration guide for v2.0 projects (see §11)

**Step 3.2 — Clean up obsolete files:**
```bash
# Remove empty original directories (verify they're truly empty first)
rmdir seed-skills _research claude_code_course_files internal_docs outputs 2>/dev/null || true
# Remove HANDOFF.md at root if present (stale working copy)
rm -f HANDOFF.md
```

**Step 3.3 — Run full verification:**
Run ALL checks V1–V25 (see §7).

**Step 3.4 — Use /validate (Pipeline Gate):**
```bash
/validate
```
Must pass all 3 waves before release.

**Step 3.5 — Version & tag:**
```bash
echo "3.0.0" > VERSION
git add -A && git commit -m "release: Loam v3.0 — seed subdirectory architecture"
git tag v3.0.0
```

**Step 3.6 — Push:**
```bash
git push origin rework/v3-restructure
git push origin v3.0.0
```
Then open PR to merge `rework/v3-restructure` → `main`.

---

## 10. Skills & Agents to Use During Implementation

| Phase | Skill/Agent | Purpose |
|---|---|---|
| All | `/catchup` | Session start — understand current state |
| Phase 1 | `Explore` agent | Verify directory structure after moves |
| Phase 1 | Bash tool | File moves, symlink creation, verification commands |
| Phase 2 | Read tool | Read each dissolved skill's SKILL.md before removal |
| Phase 2 | Write/Edit tools | Rewrite AGENTS.md.jinja, merge agent content |
| Phase 2 | `diff-reviewer` agent | Review the skill consolidation diff |
| Phase 3 | `/validate` | Pipeline Gate before release |
| Phase 3 | `/multi-review` | Code review of the full restructure |
| Phase 3 | `/commit` | Conventional commit at each phase |

---

## 11. Migration Guide for v2.0 Projects

v3.0 changes `_subdirectory` from `"."` to `"seed"`. This is a structural change that breaks `copier update`.

**For existing v2.0 projects (like distbench):**

1. Back up project-local customizations:
   ```bash
   cp CLAUDE.md CLAUDE.md.backup
   cp -R .claude/rules/ .rules-backup/
   # Back up any project-local skills
   ```

2. Re-bootstrap from v3.0 template:
   ```bash
   cd .. && uvx copier copy gh:samyakjhaveri/loam ./my-project-v3
   ```

3. Restore customizations:
   ```bash
   # Merge your backup CLAUDE.md with the new template's CLAUDE.md
   # Copy project-local skills back
   # Copy project-local rules back
   ```

4. Copy project code:
   ```bash
   # Copy your actual project files (src/, tests/, etc.) from old to new
   ```

5. Verify:
   ```bash
   /catchup  # Should show correct skill count and framework version
   ```

---

## 12. Future: v3.1 JVC Deepening (SEPARATE RELEASE)

Deferred from v3.0 to reduce risk. Ship as v3.1 after v3.0 is stable.

| JVC Constraint | v3.1 Integration |
|---|---|
| 01 AI Writing Patterns | AGENTS.md three-section structure IS this (already in v3.0) |
| 04 Session Consistency | Session-end update protocol in workflow.md + /handoff enforcement |
| 05 Voice Architecture | AGENTS.md backbone IS this (already in v3.0) |
| 07 Scaling vs Automating | /create-skill scaling audit pre-check + layer-triage.md update |
| 02 Output Drift (enhanced) | self-critic agent gains drift-detection lens |
| 03 Context Hygiene (enhanced) | workflow.md token allocation + "remove before you add" |

---

## Constraints (Must NOT)

- Must NOT break `.claude/` internal references (skills referencing rules, hooks referencing other hooks) — path scanner confirmed these are all relative to `.claude/` and safe
- Must NOT modify `_tasks` logic in copier.yml — paths are relative to rendered project, not template
- Must NOT include JVC deepening work in v3.0 — ship separately as v3.1
- Must NOT delete dissolved skills before extracting their content into AGENTS.md
- Must NOT force-push to main — use feature branch + PR
- Must NOT skip /validate before tagging the release

## Done Looks Like

1. `bin/verify-template.sh` passes with ALL OK
2. `uvx copier copy --defaults -d project_name=test . /tmp/v3-test` produces a clean project with 17 skills, 6 agents, 8 hooks, no template machinery leaks
3. `uvx copier copy --defaults -d project_name=test -d is_research=true . /tmp/v3-test-research` produces a research project with 19 additional skills
4. Root `CLAUDE.md` describes the template repo (not a project)
5. `VERSION` reads `3.0.0`
6. Git tag `v3.0.0` exists
7. No files remain at old locations (`_research/`, `seed-skills/`, `claude_code_course_files/`, `TEMPLATE-*.md`)
