# Reflection: Paper Final Polish

**Date:** 2026-04-27
**Session work:** NeurIPS paper Phases 5.6-5.7 plus full session-critique — P1 reviewer improvements, review-sim P0/P1 narrative restructuring, deslop, data consistency fixes, writing quality improvements.
**Files touched:** 8 files across paper sections, appendix, and HANDOFF.

## What Surprised Me

- **"Two" vs "four" OMP-target directions was wrong in the abstract and intro since the structural rewrite session.** The abstract and Contribution #1 said "two OpenMP-target case-study directions" while every other section (experimental-setup, results, related-work) said "four." This survived two prior paper-claim-audits and a review simulation because those audits focused on *numbers* (percentages, CIs), not *word-form counts* embedded in prose. The data-auditor Opus agent caught it by reading cross-sectionally. Lesson: word-form claims ("two directions") are harder to audit than numeric claims ("62.7%") because they don't appear in JSON files.

- **The HeCBench 513 vs 516 discrepancy was supposedly "harmonized" in Phase 3 but benchmark-curation.tex was missed.** The HANDOFF explicitly says "HeCBench 513->516 inconsistency harmonized (4 occurrences)" but the main body file still had 513. The fix was applied only to the appendix. This is a pattern: when a harmonization fix is applied, it's easy to miss the one occurrence in a different file from where the fix was focused.

- **The appendix had two contradictory descriptions of the same HeCBench selection funnel** (272 in one place, 327/325/242 in another). These were written at different times and never cross-checked. The compressed version (272) was stale from an earlier analysis. The appendix is long enough (~1200 lines) that internal contradictions can hide.

## Pattern Proposal

**Target:** `.claude/rules/known-issues.md` (new section) or CLAUDE.md

```
## Cross-Section Consistency Checks (paper)

After editing ANY paper section, grep for key counts across ALL .tex files:
  grep -rn '513\|516' docs/paper/NeurIPS_ready_version/
  grep -rn 'two.*case-study\|four.*case-study\|OMP.target.*direction' docs/paper/NeurIPS_ready_version/

Key counts that must agree everywhere:
- HeCBench kernels: 516
- OMP-target directions: four (not two)
- Total directions: ten (six standard + four OMP-target)
- Specs: 96 total, 87 PASS, 9 KNOWN_FAIL
- Kernels: 35
```

**Why:** Two of the three data-consistency bugs found today were cross-section disagreements where one file was updated and another was not. A mechanical grep catches these in seconds.

## Prompt Improvement

**Original approach:** The task prompt said "Implement Phase 5.6 (P1 findings)" and listed 4 specific items. This was effective for the P1 work. But the subsequent review-sim and session-critique revealed 12 additional issues that could have been caught earlier.

**Better approach:** For final-polish sessions before a deadline, front-load the session-critique *before* doing the P1 work, not after. The critique finds the structural issues (data inconsistencies, narrative framing) that the P1 items don't cover. Then do P1 + critique fixes together in one pass.

```
ultrathink. This is the final polish session before NeurIPS submission (May 1).

Step 1: Run /session-critique on the paper as-is (all-opus). Get the full
  finding list before making any changes.
Step 2: Merge the critique findings with the P1 items from HANDOFF.md.
Step 3: Implement everything in one coordinated pass.
Step 4: Run paper-claim-audit + codex review.
Step 5: Validate, commit, push.
```

## Gotcha Discovered

**Symptom:** The Codex review of commit 5e0e4bd flagged "ten bidirectional translation directions among CUDA, OpenMP, and OpenCL" as imprecise — 4 of the 10 directions involve OpenMP-target, a fourth API not in the listed set.

**Root cause:** When writing the LASSI differentiation, I summarized "six standard + four OMP-target = ten" as "ten bidirectional directions among CUDA, OpenMP, and OpenCL" — dropping "OpenMP-target" from the API list because it felt redundant with "OpenMP." But OpenMP-target is a distinct API variant in this benchmark (different compiler, different execution model), and omitting it from the enumeration is technically wrong.

**Fix:** Changed to "six standard bidirectional directions among CUDA, OpenMP, and OpenCL plus four OpenMP-target case-study directions." Commit 51e2b25.

**Status:** Not a known-issues.md item (paper prose, not infrastructure). But the pattern — collapsing an API list for brevity and losing precision — is worth noting for future paper edits.
