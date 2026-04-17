# Andrej Karpathy Skills Integration Audit

**Date:** 2026-04-16
**Source:** https://github.com/forrestchang/andrej-karpathy-skills
**Local installation (plugin cache):** `/home/samyak/.claude/plugins/cache/karpathy-skills/andrej-karpathy-skills/1.0.0/`
**Local installation (marketplace worktree):** `/home/samyak/.claude/plugins/marketplaces/karpathy-skills/` (git remote `forrestchang/andrej-karpathy-skills`)
**Project-level duplicate:** `/home/samyak/Desktop/parbench_sam/.claude/skills/andrej-karpathy-skills/karpathy-guidelines/SKILL.md` (byte-identical to plugin SKILL.md)
**Overall verdict:** PARTIALLY WORKING

## Summary

The plugin is installed, enabled in user settings, and its single skill (`karpathy-guidelines`) is correctly surfaced to Claude Code — the skill list at session start confirms it is loadable as `andrej-karpathy-skills:karpathy-guidelines`. Content integrity is perfect (the skill file matches upstream exactly). However, two integration hygiene issues exist: (1) the local plugin snapshot is 3 commits behind upstream (harmless — README-only drift), and (2) the skill is duplicated in the project repo at `.claude/skills/andrej-karpathy-skills/` while ALSO being loaded as a plugin, with no entry in `CLAUDE.md`'s project skills table to document either path. The four guiding principles are embedded verbatim in `CLAUDE.md` §Behavioral Guidelines, so the *content* reaches Claude; the *skill triggering* mechanism is what is underdocumented.

## Per-skill status

| Skill | Upstream (main @ c9a44ae8) | Local (@ fb8fdb0a) | Description match | Likely triggers in ParBench? | Status |
|---|---|---|---|---|---|
| `karpathy-guidelines` | present: `skills/karpathy-guidelines/SKILL.md` | present in plugin cache AND project `.claude/skills/` | IDENTICAL (byte-for-byte) | YES — ParBench is entirely a Python + C/CUDA coding repo; description matches any "writing, reviewing, or refactoring code" trigger | WORKING |

Upstream has only this one skill. There are no additional upstream skills; there are no project-added extras beyond the duplicate copy.

## Gaps & issues

### 1. Local plugin snapshot is 3 commits behind upstream (MINOR — cosmetic only)

- Local cache commit: `fb8fdb0a` (2026-04-13)
- Upstream HEAD: `c9a44ae8` (2026-04-15)
- Diff scope: 3 README-only commits (`c9a44ae` "Update README with project and social media links", `331a3ac` same, `9ec6bef` "Fix readme")
- Impact on skill behavior: **zero**. SKILL.md, CLAUDE.md, and plugin.json are unchanged between these revisions — confirmed by reading the upstream README vs local, and by diffing the local files against their content-equivalent upstream paths.
- Fix cost: <1 min (`/plugin update andrej-karpathy-skills@karpathy-skills` or `cd ~/.claude/plugins/marketplaces/karpathy-skills && git pull`).

### 2. Project-level duplicate of the skill exists outside plugin management (MEDIUM — source of confusion)

- Path: `/home/samyak/Desktop/parbench_sam/.claude/skills/andrej-karpathy-skills/karpathy-guidelines/SKILL.md`
- Content: byte-identical to the plugin-cached version (`diff` returns empty).
- Created: 2026-04-14 10:20 (after the 2026-04-13 plugin install → likely a manual copy).
- Problem: Claude Code may load the skill from either location, with no clear source of truth. If a user updates the plugin (new upstream version) but forgets the project-level copy, the project's version silently drifts — or vice versa.
- Also: the project copy is NOT committed to git (not tracked by the repo), so it is a local-machine-only artifact that does not travel with the repo.

### 3. CLAUDE.md does not mention the karpathy plugin (MINOR — documentation gap, validation finding confirmed)

- `grep -i 'karpathy\|andrej-karpathy'` against `CLAUDE.md` returns **zero matches**.
- The Wave-3 consistency-checker earlier today was RIGHT: the `.claude/skills/andrej-karpathy-skills/` directory exists with no entry in CLAUDE.md's Project Skills table.
- However, this is partially a wash: the four principles themselves ARE embedded verbatim in `CLAUDE.md` §Behavioral Guidelines (lines 14–74), with attribution-free text. So the content is present; only the *provenance* and *skill name* are undocumented.

### 4. Duplication between embedded principles and skill surface (MINOR — low risk)

- `CLAUDE.md` §Behavioral Guidelines contains the same 4 principles as `karpathy-guidelines` SKILL.md, verbatim in phrasing.
- Effect: the principles are double-loaded — once as always-on CLAUDE.md content, and once as a skill offered to Claude. Not broken (redundancy is safe), but it means the skill trigger mechanism is somewhat vestigial: Claude already has these principles in-context. The skill description still legitimately fires for code-review/refactor scenarios where it may nudge behavior.

## Integration with this repo

- **CLAUDE.md skills table:** ABSENT. The project's skill inventory table (rows for `creating-agent-teams`, `augment-test`, `catchup`, etc.) does not include `karpathy-guidelines`. This is an inconsistency that the Wave-3 checker already flagged.
- **User-level settings (`~/.claude/settings.json`):** plugin is correctly enabled — `"andrej-karpathy-skills@karpathy-skills": true` under `enabledPlugins`. The marketplace is registered in `extraKnownMarketplaces`. This side is clean.
- **Project-level settings (`.claude/settings.json`):** no reference to the karpathy plugin or any skill override. Only `claude-md-management@claude-plugins-official` is listed there. No conflict.
- **Hook conflicts:** None. Hooks under `.claude/hooks/` (`pre-commit-gate.sh`, `protect-cuda-omp-results.sh`, etc.) are orthogonal to skill loading; they operate on Bash/Edit/Write tool calls, not on Skill invocation.

## Recommended next actions

Ordered from highest to lowest value; each is low-risk.

1. **Add a skills-table row in `CLAUDE.md`.** (Owner: adversarial-reviewer or user, cost: 2 min.)
   Proposed row under the existing Project Skills table:
   ```
   | karpathy-guidelines | Behavioral guidelines to reduce common LLM coding mistakes (Andrej Karpathy's observations) — plugin surface for the principles already embedded in §Behavioral Guidelines | plugin: andrej-karpathy-skills@karpathy-skills |
   ```
   This closes the Wave-3 consistency-checker finding and makes the plugin's role in the project explicit.

2. **Decide on the project-level duplicate at `.claude/skills/andrej-karpathy-skills/`.** (Owner: user, cost: 1 min.)
   Two clean options:
   - **Option A (recommended):** Delete the project-level copy. The user-level plugin already provides the skill globally. The duplicate is unversioned, ungitignored, and drift-prone.
   - **Option B:** Keep and commit it to the repo. This makes the skill travel with the repo (useful for teammates without the plugin installed), but then the plugin should be disabled per-project to avoid shadowing, and the project copy must be manually updated on upstream changes.
   Do not leave the current in-between state.

3. **Update the local plugin snapshot.** (Owner: user, cost: <1 min.)
   Run `/plugin update andrej-karpathy-skills@karpathy-skills` to pull `c9a44ae8`. Zero behavioral impact (README only), but keeps the install-health signal clean.

4. **Optional: reference the source in `CLAUDE.md` §Behavioral Guidelines.** (Owner: user, cost: 1 min.)
   Add a single attribution line (e.g., "Adapted from Andrej Karpathy's observations on LLM coding pitfalls via the `karpathy-guidelines` plugin.") so future maintainers know the provenance of these 4 principles and don't accidentally edit them out of sync with upstream.

## Evidence appendix

**Paths read:**
- `/home/samyak/.claude/plugins/installed_plugins.json` — confirms plugin enrolled at `fb8fdb0a`, 2026-04-13T20:08
- `/home/samyak/.claude/plugins/known_marketplaces.json` — confirms marketplace source `forrestchang/andrej-karpathy-skills`
- `/home/samyak/.claude/plugins/cache/karpathy-skills/andrej-karpathy-skills/1.0.0/{CLAUDE.md,README.md,.claude-plugin/plugin.json,.claude-plugin/marketplace.json,skills/karpathy-guidelines/SKILL.md}` — all 5 files read and inspected
- `/home/samyak/.claude/settings.json` — confirms `enabledPlugins."andrej-karpathy-skills@karpathy-skills": true`
- `/home/samyak/Desktop/parbench_sam/.claude/settings.json` — confirms no project-level conflict
- `/home/samyak/Desktop/parbench_sam/CLAUDE.md` — confirms embedded 4 principles (lines 14–74) and confirms absence of any karpathy/andrej mention
- `/home/samyak/Desktop/parbench_sam/.claude/skills/andrej-karpathy-skills/karpathy-guidelines/SKILL.md` — confirms project-level duplicate

**Commands run:**
- `git log -1 --format='%H %ci %s'` in `~/.claude/plugins/marketplaces/karpathy-skills/` → `fb8fdb0a 2026-04-14`
- `git ls-remote origin HEAD` → `c9a44ae835fa2f5765a697216692705761a53f40`
- `git log fb8fdb0a..c9a44ae8 --format='%h %ci %s'` → 3 README-only commits between 2026-04-16 00:45 and 01:47 (+0800)
- `diff /home/samyak/Desktop/parbench_sam/.claude/skills/andrej-karpathy-skills/karpathy-guidelines/SKILL.md /home/samyak/.claude/plugins/cache/karpathy-skills/andrej-karpathy-skills/1.0.0/skills/karpathy-guidelines/SKILL.md` → empty (files identical)
- `grep -i 'karpathy\|andrej-karpathy' CLAUDE.md` → no matches

**URLs fetched:**
- `https://github.com/forrestchang/andrej-karpathy-skills` → confirms single `skills/karpathy-guidelines/` directory upstream; no other skills
- `https://api.github.com/repos/forrestchang/andrej-karpathy-skills/commits/main` → confirms upstream HEAD `c9a44ae8`, 2026-04-15T17:47:20Z

**Session-log signal:**
- Skill list at session start included `andrej-karpathy-skills:karpathy-guidelines: Behavioral guidelines to reduce common LLM coding mistakes. Use when writing, reviewing, or refactoring code to avoid overcomplication, make surgical changes, surface assumptions, and define verifiable success criteria.` → confirms the skill is reachable and its description is the one that would govern trigger eligibility. That description would plausibly match any ParBench coding task (harness, eval, augmentation, spec edits), so triggering is expected to be frequent.
