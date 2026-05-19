# HANDOFF — Distbench Bootstrap (Phase 3 Complete)

> Working state for the next session. Last updated: 2026-05-19T~05:15Z
> **Start here.** Read this entire document, then act on the critique findings before Phase 4.

## Goal

Bootstrap a new distributed systems benchmarking project ("distbench") from the Loam Copier template. Four sequential phases: commit pending fixes, rename framework to "Loam", port skills from parbench, render distbench.

## Current Progress

- [x] **Phase 1: Pre-flight commit** — DONE (prior session)
- [x] **Phase 2: Rename to Loam** — DONE (prior session, commit `31a19e69`)
- [x] **Phase 3: Port + merge parbench skills** — DONE (this session, 3 commits)
- [x] **Phase 3.5: Session critique** — DONE (findings below, awaiting user decisions)
- [ ] **Phase 3.6: Apply critique fixes** — NOT STARTED (next session)
- [ ] **Phase 4: Render distbench** — NOT STARTED
- [ ] **Push to remote** — NOT DONE (intentionally held until Phase 4 succeeds)

### Phase 3 Commits (this session)

```
bb711b8a port: research-flavor skills from parbench (eval pipeline + grill-research + augment-test)
0fa777c1 port: agent tooling + core agents from parbench (agent-team, model-route, session-critique, 3 agents)
ffa87380 port: spec-first workflow from parbench (gen-spec, spec-check, spec-validator, spec-auditor, spec-conventions)
```

### What was ported (23 files total)

**CORE (to `.claude/`) — 6 new skills, 4 new agents, 1 new rule:**

| Type | Name | Source concept | Generalization |
|------|------|---------------|----------------|
| skill | gen-spec | Parbench benchmark spec generator | Generic spec-first development wizard |
| skill | spec-check | Parbench single-spec validator | Generic single-spec health check |
| skill | spec-validator | Parbench spec conventions checker | Generic spec validator (NOTE: overlaps spec-check — see critique #4) |
| skill | agent-team (4 files) | Parbench multi-agent team launcher | Generic TeamCreate coordinator with advisor pattern |
| skill | model-route | Parbench model routing advisor | Opus/Sonnet routing (no Haiku per user preference) |
| skill | session-critique (2 files) | Parbench session review | Generic adversarial post-implementation review |
| agent | spec-auditor | Parbench bulk spec auditor | Generic bulk spec document auditor |
| agent | consistency-checker | Parbench doc/code cross-checker | Generic CLAUDE.md vs filesystem consistency |
| agent | regression-checker | Parbench metric baseline checker | Generic framework metric regression detection |
| agent | test-synthesizer | Parbench runtime test generator | Generic temp-test-and-cleanup pattern |
| rule | spec-conventions | Parbench spec naming rules | Generic spec document structure conventions |

**RESEARCH (to `_research/`) — 6 new skills, 1 new agent:**

| Type | Name | Source concept | Generalization |
|------|------|---------------|----------------|
| skill | eval-run | Parbench interactive eval launcher | Generic foreground eval batch launcher |
| skill | eval-grader | Parbench result classifier | Generic eval result grading pipeline |
| skill | overnight-eval | Parbench tmux eval campaign | Generic long-running eval with tmux |
| skill | post-eval | Parbench post-batch pipeline | Generic post-eval analysis pipeline |
| skill | grill-research | Parbench research interrogation | Generic adversarial hypothesis checker |
| skill | augment-test | Parbench C-augmentation tester | Generic augmentation testing workflow |
| agent | eval-batcher | Parbench batch dispatcher | Generic background eval agent |

**10 existing research skills compared and confirmed equal or better in Loam — no merges needed.**
**aris-shared-references: identical to existing `_research/skills/shared-references/` — skipped.**

### Final Counts

| Layer | Before | After |
|-------|--------|-------|
| Core skills | 19 | 25 |
| Core agents | 7 | 11 |
| Core rules | 11 | 12 |
| Research skills | 13 | 19 |
| Research agents | 2 | 3 |

## Session Critique Findings (AWAITING USER DECISIONS)

A 3-member team (advisor=Opus, self-critic=Opus, code-reviewer=Sonnet) reviewed all 23 ported files. **Overall verdict: PASS with 9 actionable findings.**

Zero parbench contamination found. All user decisions (no Haiku, Opus/Sonnet only, ultrathink) confirmed respected.

### Tier 1 — User must decide (policy calls)

#### #5 (HIGH): Haiku policy contradiction

**The problem:** Two files in the framework now contradict each other:
- `.claude/rules/workflow.md` line ~86 says: *"Exception: user may switch to Haiku for commit/push (faster, cheaper for transactional git ops)."*
- `.claude/skills/model-route/SKILL.md` (ported this session) says: *"Haiku is never used. Not for commits, not for lookups, not for anything."*

**Why it matters:** Any future session that reads both files gets conflicting instructions. Claude Code loads `workflow.md` always (it's in `.claude/rules/`), and model-route is a skill that can be invoked. A model routing question would get two different answers depending on which file Claude reads first.

**Options:**
- **A) Update workflow.md to remove the Haiku exception** — makes both files consistent with the user's explicitly stated preference ("use opus 4.6 or opus 4.7 or sonnet for everything... never use haiku"). This is the clean fix. One-line edit in workflow.md.
- **B) Keep the Haiku exception in workflow.md, soften model-route** — preserves the option for cheap transactional ops, but contradicts what the user said this session.

**Recommendation: A.** The user was explicit. The Haiku exception in workflow.md is a pre-existing artifact from before the user stated this preference.

---

#### #4 (HIGH): spec-check and spec-validator are ~80% duplicated

**The problem:** Both skills check the same things on the same inputs:
- Structure check (required sections present)
- Reference check (files referenced exist on disk)
- Acceptance criteria quality (verifiable, specific, independent)
- Naming conventions

The only things spec-validator adds beyond spec-check:
- Kebab-case filename enforcement
- Constraint completeness check (Must NOT section non-empty and specific)
- Can run on "all specs" when no argument given

The line `spec-validator/SKILL.md:66` literally says *"Complements /spec-check (which also checks individual specs)"* — acknowledging the overlap without justifying it.

**Why it matters:** A user in a fresh project types `/spec-` and sees three confusable options (spec-check, spec-validator, spec-auditor). They can't tell which to use. Three independent reviewers (code-simplifier in Wave 3, the advisor, and the code-reviewer) all flagged this independently.

**Options:**
- **A) Merge spec-validator's 2 unique checks into spec-check, delete spec-validator.** The pipeline becomes: `gen-spec` (author) → `spec-check` (validate one) → `spec-auditor` (validate all). Three tools, zero confusion. Session-start.sh count drops 25→24. Gen-spec's Phase 3 reference to `/spec-validator` changes to `/spec-check`.
- **B) Keep both, add clearer documentation explaining the boundary** — technically works but doesn't fix the root cause (they do the same thing).

**Recommendation: A.** Three reviewers independently said the same thing. The merge is clean — add 2 checks to spec-check, delete one directory, update 2 cross-references.

---

### Tier 2 — Bugs to fix (clear right answer, need user approval)

#### #1 (MEDIUM): agent-team frontmatter name mismatches directory

**The problem:** The directory is `.claude/skills/agent-team/` but the frontmatter says `name: creating-agent-teams`. Claude Code matches skills by directory name for `/skill-name` invocation but uses the frontmatter `name:` for description matching. This mismatch can cause mis-routing.

**Fix:** Change `name: creating-agent-teams` to `name: agent-team` in `.claude/skills/agent-team/SKILL.md` line 2. One-line edit.

---

#### #6 (MEDIUM): spec-auditor agent missing permissionMode

**The problem:** `.claude/agents/spec-auditor.md` has `tools: Read, Glob, Grep, Bash` but no `permissionMode: dontAsk`. Every other agent with Bash access (consistency-checker, regression-checker, test-synthesizer, diff-reviewer, security-scanner) has `permissionMode: dontAsk`. Without it, spec-auditor prompts the user for permission on every single bash command, making it unusable as a background agent.

**Fix:** Add `permissionMode: dontAsk` and `maxTurns: 15` to the frontmatter. Two-line addition.

---

#### #7 (MEDIUM): 6 research skills missing `auto-activate: false`

**The problem:** Per `.claude/rules/known-issues.md` tiering convention, specialized/heavy skills must have `auto-activate: false` to prevent false-positive auto-invocation. None of the 6 new research skills have this field:
- `_research/skills/eval-run/SKILL.md`
- `_research/skills/eval-grader/SKILL.md`
- `_research/skills/overnight-eval/SKILL.md`
- `_research/skills/post-eval/SKILL.md`
- `_research/skills/grill-research/SKILL.md`
- `_research/skills/augment-test/SKILL.md`

**Why it matters:** Without this flag, these 6 skills compete for auto-invocation whenever a research user types anything eval-related. With 25+ core skills already competing, adding 6 more specialized ones without tiering creates noise.

**Fix:** Add `auto-activate: false` to each SKILL.md frontmatter. Six one-line edits.

---

#### #10 (MEDIUM): augment-test writes to core rules file

**The problem:** `_research/skills/augment-test/SKILL.md` Phase 5 instructs the agent to add new bugs to `.claude/rules/known-issues.md`. This couples a research-flavor skill to a core framework file. A research project could pollute the core rules file with domain-specific failure modes.

**Fix:** Change the target from `.claude/rules/known-issues.md` to a research-specific file like `docs/known-failures.md`. One-line edit.

---

### Tier 3 — Advisory (defer or skip)

#### #2 (LOW): agent-team hard-coded scenario list

`.claude/skills/agent-team/SKILL.md` line 22 hard-codes the valid scenario names. Adding a scenario to `scenarios.md` requires a second edit here — two-place update. Not blocking; note for future maintenance.

#### #8 (LOW): eval-batcher generic placeholders

`_research/agents/eval-batcher.md` uses `<eval-script>` and `<analysis-script>` placeholders without guidance on how to discover actual paths. Cosmetic — the `<angle-bracket>` convention is self-documenting.

#### #9 (LOW): Template header cosmetic

`agent-team/advisor-prompt.md` and `teammate-prompt.md` contain `[FILL]` placeholders. New users reading these files cold may be confused. But the first line already says "Fill in every [FILL] placeholder" — low priority.

---

## What Worked (this session)

- **Karpathy guidelines skill** framed the porting discipline well — read before copy, verify after write, surgical changes only
- **Parallel subagent comparison** of 10 research skills was efficient — one agent, 10 diffs, clear IDENTICAL/MERGE_NEEDED verdicts in 26 seconds
- **verify-template.sh after each batch** caught the skill count mismatch immediately (19→25)
- **sentinel-cleanup awareness** — doing ALL file writes before `/validate`, then committing via Bash only (no Edit/Write to trigger cleanup), worked perfectly
- **3-wave /validate** passed cleanly on the first run — no fix loops needed
- **Session critique team** (advisor=Opus, self-critic=Opus, code-reviewer=Sonnet) found real issues that /validate's probabilistic wave missed (policy contradictions, naming bugs)

## What Didn't Work / Traps to Avoid

- **Self-critic incorrectly scoped out the spec workflow** — it claimed ffa87380 (the first session commit) "predated this port." It didn't. The advisor caught and corrected this. Lesson: when briefing a self-critic agent, explicitly list the commit hashes AND the files in scope, not just the range.
- **The original plan's "Done looks like" said ~31 core skills** — actual was 25. The plan counted agents and rules as skills. Always verify counts against `find .claude/skills -mindepth 1 -maxdepth 1 -type d | wc -l`.
- **spec-check/spec-validator overlap was avoidable** — during porting, I generalized each parbench file independently without checking if two source files mapped to the same concept. Should have diffed the generalized outputs against each other before writing.

## Next Steps (for the next session)

1. **Read this entire HANDOFF.md first**
2. **Present the 9 critique findings to the user and get decisions** — use the Tier 1/2/3 structure above. The user has seen the summary table but wants a detailed breakdown (this document provides it).
3. **Apply approved fixes** — all are small edits (1-6 lines each). The spec-check/spec-validator merge (#4) is the largest: merge 2 checks, delete a directory, update 2 cross-references, update session-start.sh count.
4. **Run `/validate` after fixes** — re-creates the sentinel
5. **Commit fixes** as a single "critique fixes" commit
6. **Do NOT push to remote** until Phase 4 succeeds
7. **Execute Phase 4: Render distbench** — see `docs/multi_session_prompts/2026-05-18-distbench-bootstrap.md` Phase 4 section. Key command:
   ```bash
   cd ~/Desktop
   uvx copier copy --trust \
     --vcs-ref HEAD \
     --data project_name=distbench \
     --data is_research=true \
     --data github_repo=samyakjhaveri/distbench \
     ~/Desktop/loam ./distbench
   ```
   **MUST include `--vcs-ref HEAD`** — without it, Copier silently drops files.

## Hot Files

**Critique fixes (Tier 1+2):**
- `.claude/rules/workflow.md` ~line 86 — remove Haiku exception (#5)
- `.claude/skills/spec-check/SKILL.md` — merge spec-validator checks into this (#4)
- `.claude/skills/spec-validator/` — DELETE entire directory (#4)
- `.claude/skills/gen-spec/SKILL.md` — update cross-reference from /spec-validator to /spec-check (#4)
- `.claude/hooks/session-start.sh` — update count 25→24, update "Spec workflow" line (#4)
- `.claude/skills/agent-team/SKILL.md` line 2 — fix `name:` field (#1)
- `.claude/agents/spec-auditor.md` — add permissionMode + maxTurns (#6)
- 6 `_research/skills/*/SKILL.md` files — add `auto-activate: false` (#7)
- `_research/skills/augment-test/SKILL.md` — change known-issues.md ref (#10)

**Phase 4 (render + bootstrap):**
- `copier.yml` — template config
- `bin/verify-template.sh` — reference for `--vcs-ref HEAD` flag
- Output: `~/Desktop/distbench/`

## Blockers

None. All critique findings are documented with clear fix instructions. Phase 4 plan is ready.

## Open Tech Debt

- `pre-commit-gate.sh:93-95` — `waves_passed` check is fail-open (from prior sessions)
- `eval-grader/post-eval` minor classification overlap — both have a "classify failure modes" step. Future cleanup: have post-eval invoke eval-grader for its classification step.
- `advisor-guided-implementation` scenario in agent-team/scenarios.md is a no-op alias for `feature-implementation` — cosmetic, remove when convenient
