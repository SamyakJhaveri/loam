# Future Work — Loam v3.x

Items identified during v3.0 implementation. Address as we go.

---

## Depth-on-Demand for Dissolved Skills

**Context:** v3.0 dissolved 4 skills (karpathy-guidelines, model-route, security, scalability) into AGENTS.md persistent context. This gains always-available guidance but loses depth.

**The tradeoff:** AGENTS.md has ~500-token summaries of security and scalability. The original skills had 4 reference files each (~15KB total). For dedicated security reviews or scalability audits, the condensed version may be insufficient.

**Potential solutions:**
1. Keep the detailed reference files in `cultivation/retired/` and document how to pull them in for deep reviews
2. Create a `/deep-review security` mode that loads the full reference files on demand
3. Use path-scoped rules to load detailed patterns when editing security-sensitive code paths (auth handlers, API endpoints, database queries)

**Design principle at stake:** Availability x Depth = roughly constant. The question is whether we can break this constraint with smart demand-paging — load summaries always, details on trigger.

---

## Render Test (V21) Post-Commit Verification

**Context:** Copier's `copier copy` uses git history, not the working tree. V21 (full render test) cannot validate uncommitted changes.

**Action:** After every phase commit, re-run V21 to verify rendered project matches expected counts. This is a Phase 3 task.

---

## Skill Composition / Middleware Pattern

**Context:** The 24-skill Unix-philosophy design had composition overhead in an LLM context. Skills can't pipe into each other like Unix tools because each load costs tokens.

**Future exploration:** If Claude Code adds skill composition (skill-within-skill loading), revisit whether some AGENTS.md sections should become composable micro-skills again. Monitor Claude Code release notes for this feature.

---

## Phase 2 Multi-Review Findings (2026-05-19)

Findings from 4-agent parallel review (style, correctness, security, performance) of the Phase 2 consolidation. Grouped by priority. Address before Phase 3 release.

### Resolution Status (2026-05-19)

| Item | Status | Notes |
|------|--------|-------|
| C1 | **Fixed** | `{{PROJECT_ROOT}}` → `git rev-parse --show-toplevel` |
| C2 | **Fixed** | `sys.argv` pattern eliminates injection |
| C3 | **Fixed** | Same `sys.argv` pattern |
| C4 | **Fixed** | All 6 dangling agent refs updated |
| H1 | **Fixed** | Skill list updated to actual 17 directories |
| H2 | **Fixed** | spec-auditor → plan-reviewer (spec audit mode) |
| H3 | **Fixed** | regression-checker/test-synthesizer → verification-lead |
| H4 | **Fixed** | Removed hardcoded model version string |
| M1 | Already resolved | Descriptions 30-39 words — acceptable |
| M2 | Addressed via C2 | Injection fixed; pure-bash alternative deferred (low priority) |
| M3 | Already resolved | `effort: max` present in plan-reviewer |
| M4 | Out of scope | Intentional independent copies (1 line each) |
| M5 | **Fixed** | Provenance moved to Jinja comment |
| M6 | **Fixed** | Token budget corrected to ~2,000 |
| M7 | Accepted as-is | Intentional for multi-agent compatibility |
| M8 | **Fixed** | Bare `ultrathink` removed |

### Critical — Runtime-Breaking

**C1. `{{PROJECT_ROOT}}` literal in self-critic.md:22**
The `cd {{PROJECT_ROOT}}` line is raw Jinja syntax inside an agent `.md` file. Agent files are NOT rendered by Copier — they're passed as-is to Claude Code. The agent will try to `cd` into a literal directory named `{{PROJECT_ROOT}}`, which will fail. Fix: replace with `$(git rev-parse --show-toplevel)` to match how verification-lead.md handles it (line 24-25).

**C2. Command injection in dream-hook.sh:23 and session-start.sh:63**
`$LAST_TS` is interpolated directly into a `python3 -c` code string: `python3 -c "...datetime.fromisoformat('$LAST_TS'...)..."`. If `.last-dream` contains a crafted timestamp like `2024-01-01'; import os; os.system("evil") #`, the shell expands it inside the Python string before Python parses it. Fix: pass timestamp as `sys.argv[1]` instead — `python3 -c "import sys; from datetime import datetime; print(int(datetime.fromisoformat(sys.argv[1].replace('Z','+00:00')).timestamp()))" "$LAST_TS"`.

**C3. Command injection in verification-lead.md:116**
`python3 -c "import ast; ast.parse(open('$py').read())"` — the `$py` variable comes from `git diff --name-only` output. A crafted filename could inject into the code string. Fix: same `sys.argv` pattern — `python3 -c "import ast,sys; ast.parse(open(sys.argv[1]).read())" "$py"`.

**C4. 6 dangling references to deleted agents**
These files still reference agents that were removed in Phase 2. They will cause runtime failures when skills try to spawn non-existent agents:
- `seed/.claude/skills/validate/SKILL.md:84,88` — references `code-simplifier` as a separate Wave 3 agent. Should say self-critic handles code simplification as advisory WARN.
- `seed/.claude/skills/agent-team/SKILL.md:199,202` — lists `spec-auditor` and `consistency-checker` as available agents. Both deleted; absorbed into plan-reviewer and verification-lead respectively.
- `seed/.claude/skills/session-critique/teammates.md:43,79` — references `consistency-checker` and `code-simplifier` agents for spawning. Both deleted.

### High — Stale References

**H1. known-issues.md:10 lists 4 retired skills as active**
The Skill Tiering Convention entry lists `karpathy-guidelines`, `reflect`, `scalability`, `security` as "core workflow skills" with default auto-activate. All four were dissolved/merged in Phase 2. The list needs updating to reflect the 17-skill set.

**H2. spec-conventions.md:42 references deleted spec-auditor**
Says "reviewed by spec-auditor" in the spec lifecycle section. Should say "reviewed by plan-reviewer (spec audit mode)".

**H3. self-critic.md:66,77 references deleted agents inline**
- Line 66: "regression-checker wasn't run (it runs as part of this validation loop — verify it passed)" — regression-checker no longer exists as a separate agent; its checks are inlined in verification-lead Wave 1/2.
- Line 77: "test-synthesizer (Wave 2) cleans up /tmp/validate_*" — test-synthesizer no longer exists.

**H4. Hardcoded model version in self-critic.md:143**
Output template says "Opus 4.7 as of 2026-04-16". This will go stale. Other agents use generic names without version dates. Remove the version string or use "most capable model available."

### Medium — Quality / Performance

**M1. Agent frontmatter descriptions inconsistently long**
verification-lead (60+ words), plan-reviewer (~50 words), self-critic (~55 words) vs. siblings explorer (35), diff-reviewer (30), security-scanner (32). The absorbed-agent provenance notes ("Absorbs X, Y, Z") are operational history, not trigger descriptions. Consider moving provenance to the body.

**M2. python3 fork on every session start/stop**
dream-hook.sh and session-start.sh both spawn `python3 -c` for date parsing (~50-150ms). A pure-bash alternative using `stat -f %m` (macOS) or `date -d` (Linux) would avoid the fork entirely. Low absolute cost but runs on every session.

**M3. plan-reviewer missing `effort: max` frontmatter**
verification-lead.md and self-critic.md both have `effort: max`. plan-reviewer.md does not. As Wave 3 peers in the validation pipeline, they should be consistent. Also, plan-reviewer's `maxTurns: 15` may be tight now that it also handles spec auditing.

**M4. Duplicated date-parsing logic**
dream-hook.sh (lines 8-29) and session-start.sh (lines 49-69) contain identical should-dream logic. If the logic needs fixing, two files must be updated. Consider extracting to a shared sourced script.

**M5. AGENTS.md.jinja ships provenance note to downstream projects**
Line 4 parenthetical "(karpathy-guidelines, model-route, security, scalability)" names former skills. Useful for template authors but meaningless to downstream project users. Consider wrapping in a Jinja comment `{# ... #}`.

**M6. AGENTS.md.jinja token budget mismatch**
Header claims "~4,500 tokens" but actual content is ~1,350 tokens. The number was inherited from the spec without re-measurement. Not a problem (cheaper than declared) but will mislead future authors about headroom.

**M7. §3 Hard Constraints partially overlaps workflow.md anti-patterns**
Items 2, 6, 7, 8, 10 in §3 closely mirror anti-patterns in workflow.md lines 199-228. Both files are always-loaded. ~150 tokens of redundancy per session. The duplication is intentional for emphasis but worth naming as a deliberate cost.

**M8. `ultrathink` bare directive in dream/SKILL.md:6**
Bare `ultrathink` on line 6 sits outside any section heading, before the `# Memory Consolidation` title. Every other skill starts with `# Title` immediately after `---`. If this is a Claude Code directive, it should be inside the frontmatter or documented as intentional.

### Low — Advisory

- Session-start brief duplicates some CLAUDE.md ICM routing table content (~380 tokens)
- `rm -rf` deny-list in settings.json is bypassable with `rm -r -f` or extra spaces
- Empty `### Project Conventions` placeholder in AGENTS.md.jinja loads ~10 tokens of no signal
- self-critic.md:42-55 Python inline has a minor path traversal bypass in the `.claude/hooks/` containment check
- settings.json ruff inline command runs `ruff check .` on full tree without `--exclude` for `.venv/node_modules`
- verification-lead Wave 2 doc-consistency check runs even when CLAUDE.md isn't among changed files
