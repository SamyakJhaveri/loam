# Blind review - rebuild structure design

> Reviewer: sam-cc-setup:plan-reviewer (fresh context, blind: design doc + criteria + rulings only).
> Date: 2026-08-29. Verdict: APPROVE_WITH_CHANGES (11 findings).
> The elegance reviewer's pass is in rebuild-structure-design-review-elegance.md.

## 1. CRITICAL - Renaming `reassess-hooks.json` -> `hooks.json` activates a hooks file whose handlers mostly do not exist

Concerns: design § "seed/.codex/ (fix + rename)", row "Rename `reassess-hooks.json` -> `hooks.json`".

seed/.codex/reassess-hooks.json wires five handlers:
- PreToolUse -> `.codex/hooks/pre-tool-policy.py` - DOES NOT SHIP
- PostToolUse -> `.codex/hooks/post-tool-policy.py` - DOES NOT SHIP
- PostCompact -> `.codex/hooks/post-compact-recovery.sh` - ships
- SessionStart -> `.codex/hooks/session-start.sh` - DOES NOT SHIP
- Stop -> `.codex/hooks/stop-verify-gate.sh` - DOES NOT SHIP

Evidence: `git ls-files seed/.codex` returns exactly one hook script, post-compact-recovery.sh. The file is harmless today only because Codex never loads a file named `reassess-hooks.json` [CDX defect 1]; the rename is precisely what makes four dangling handlers fire in every rendered project. research-codex-docs.md defect 3 audited dangling references in config.toml and never audited hooks.json, so the design inherited the gap. Required: in the same step, either ship the four scripts or delete their blocks, leaving only PostCompact.

## 2. CRITICAL - `bin/release.sh` marked KEEP contradicts the deletion of `hub-ci.sh`

Concerns: target-tree line `release.sh  KEEP` vs. the deletion-table row for hub-ci.sh.

reassess-bin/release.sh:86 is:
  bash "$SELF_DIR/hub-ci.sh" || die "hub-ci failed - refusing to release (run: bin/hub-ci.sh)"
Deleting hub-ci.sh under D-1 while keeping release.sh byte-identical means every release aborts at that line. release.sh must be EDIT, not KEEP.

Same row, resolvable now rather than "at execution": the design defers lib.sh ("delete unless a survivor still sources it"). reassess-bin/release.sh:20 sources it, so the verdict is KEEP. The only other survivors that sourced it (verify-template.sh, lint-skill-descriptions.sh) are being rewritten or absorbed, so lib.sh survives solely for release.sh.

## 3. HIGH - the one skill the rebuild ships is never validated

Concerns: § "bin/verify-template.sh (rewrite target)", check 1.

Check 1 names `seed/.claude` plus each marketplace bundle. After the design's deletions, seed/.claude contains hooks/, rules/, settings.json and NO skills/ or agents/ directory, so check 1 validates nothing in the seed. The catchup skill lives at seed/.agents/skills/catchup/SKILL.md, and the `.claude/skills/catchup` symlink is deliberately uncommitted - and would not help anyway: research-cc-docs.md:472 records that `claude plugin validate` "does not follow symlinks inside the named directory". Check 1 must additionally name `seed/.agents/skills`.

## 4. HIGH - the copier symlink guard fails on a dangling symlink and aborts `copier update`

Concerns: § "copier.yml (edit)" item 2.

`[ -e .claude/skills/catchup ]` dereferences the link. If the link exists but its target does not (target moved, `.agents/` removed, partially-rendered tree), `-e` is false, the guard passes, and `ln -s` then fails with "File exists"; a failing `_tasks` step aborts the update. Open assumption 3 asserts this is safe; it is not, for that case. Use `[ -e X ] || [ -L X ] || ln -s ...`, or `ln -sfn`.

## 5. HIGH - symlink task ordering relative to git-init is unspecified

Concerns: § "copier.yml (edit)" items 2 and 3.

copier.yml's git task is `git init -b main ... && git add . && git commit`. If the new symlink task is appended after it, the rendered project's initial commit omits .claude/skills/catchup. The symlink step must be ordered BEFORE git-init and the design should say so. Related: the design's `_tasks` inventory omits the existing fourth task, `rm -f _gh_setup.sh`.

## 6. MEDIUM - the plugin cleanup targets a file with no agent references and misses the ones that have them

Concerns: § "cultivation/marketplace/sam-cc-setup (plugin layer)", Skills bullets.

"Rewire `validate/` waves to the surviving agents" rests on a false premise: skills/validate/SKILL.md names no agent at all, and its line 11 states deep adversarial review is deliberately outside the pass. Nothing to rewire.

The actual dangling references left by removing plan-reviewer and elegance-reviewer sit in files the design waves off with "All other plugin skills are untouched this rebuild":
- workflows/plan-review-fanout.js - an installed workflow built on the plan-reviewer checklist and agent roster (lines 3, 7, 122, 156). The design never mentions the `workflows/` directory at all.
- skills/elegance-review/SKILL.md:17,29 invoke the elegance-reviewer agent; :34 points at `.claude/reference/elegance-reviewer-design.md`.
- README.md documents the removed agents.

## 7. MEDIUM - the kept Codex PostCompact hook reads a file D-6 guarantees will never exist

Concerns: § "seed/.codex/", row "Keep `hooks/post-compact-recovery.sh`", against D-6.

seed/.codex/hooks/post-compact-recovery.sh branches on `.claude/rules/known-issues.md` and reports its entry count. That file does not exist today, and D-6 folds the gotchas into CLAUDE.md.jinja, so the branch is permanently dead. The `-f` guard makes it fail soft, which is worse than loud. Repoint it at the rendered CLAUDE.md or drop the branch.

## 8. MEDIUM - bin/ repopulation drops `.ip-terms.example`, and the IP gate degrades silently

Concerns: target-tree `bin/` block, against rebuild-ledger.md:95.

The design's bin/ block omits .ip-terms.example (tracked) and the gitignored real .ip-terms. ip-sweep.sh:24 defaults `IP_TERMS_FILE=bin/.ip-terms`; at line 73, when that file is absent it prints a WARN and SKIPS the content sweep, and `IP_SWEEP_STRICT=1` (how release.sh:92 calls it) does not make that fatal. A release then passes its IP gate having swept nothing - exactly the silent cap the design itself forbids in its CI note [CTX P20]. The move is otherwise a fix: the hardcoded `bin/` paths in ip-sweep.sh are broken today (there is no bin/) and become correct once the scripts land there.

## 9. MEDIUM - CLAUDE.md.jinja + AGENTS.md.jinja institutionalize a duplicate directive home, against design rule 2 / [CTX P4]

Concerns: § "AGENTS.md.jinja", the sentence "Where both harnesses need the same directive, AGENTS.md.jinja is the Codex home and CLAUDE.md.jinja the Claude home; the two must agree."

[CTX P4] is "one directive, one home", and its verdict for a restated directive is DELETE the copy. The design instead mandates two hand-maintained copies of the shared subset in two always-loaded files - the drift failure P4 names. A native single-home exists and the design never weighs it: Claude Code reads AGENTS.md through a `@AGENTS.md` import or an `ln -s AGENTS.md CLAUDE.md` symlink [CC §1], and the design's own rule 4 says prefer the native feature. Either adopt the bridge for the shared subset, or state why it was rejected (the Windows symlink caveat and the fact that `@`-imports do not save context are both plausible reasons, but they need to be on the page).

## 10. LOW - the docs/specs archive move undercounts and strands this document's own citations

docs/specs/ holds NINE pre-teardown files, not eight. One of them, cliefnotes-wisdom.md, is the resolution target for the `[N-xxxx]` citations this design uses, and CLAUDE.md defines `_archive/` as "human-only reference docs; not loaded into Claude context". Archiving it dangles the design's own norm references.

## 11. LOW - internal contradiction on whether the catchup symlink is a seed asset

Target-tree line 59 lists the symlink as a seed entry; line 131 says "The symlink is NOT checked into the template." An executor following the tree literally would commit it, and committing it is actively harmful - see finding 3 on `claude plugin validate` and symlinks.

## Checked and found sound (no action)

- The symlink target resolves correctly in both frames [CDX §2.6] [CC §3].
- CI claims verify: test.yml is PR-only and runs the agent-sync tests (correctly deleted under D-1); release.yml already runs bin/verify-template.sh on tag push.
- The other three Codex config fixes match research-codex-docs defects 2, 3 and 4 exactly.
- Agent arithmetic is right: 13 on disk, 6 removed, 7 survivors, 8 after step 2.
- Clarification, not a defect: the settings.json entry being removed is PostToolUse with matcher `Compact`; `Compact` is not a tool name and the real event is `PostCompact`, so that hook has never fired. Removing it is still correct; D-6 costs nothing behaviorally.

## VERDICT: APPROVE_WITH_CHANGES

Required changes before execution:
1. Strip the four dangling handler blocks from seed/.codex/hooks.json (or ship the scripts) as part of the rename step.
2. Change release.sh from KEEP to EDIT: remove the hub-ci.sh invocation at line 86. Record lib.sh as KEEP, since release.sh:20 sources it.
3. Add `seed/.agents/skills` to verify-template.sh check 1.
4. Fix the symlink guard to `[ -e X ] || [ -L X ] || ln -s ...` (or `ln -sfn`) and correct open assumption 3.
5. State that the symlink `_tasks` step runs BEFORE the git-init task; include the existing `rm -f _gh_setup.sh` task in the inventory.
6. Replace the `validate/` rewire item with the real reference cleanup: workflows/plan-review-fanout.js, skills/elegance-review/SKILL.md, and the plugin README.md.
7. Repoint or delete the `.claude/rules/known-issues.md` branch in seed/.codex/hooks/post-compact-recovery.sh.
8. Add .ip-terms.example to the bin/ block and decide whether a missing term file should fail ip-sweep.sh under IP_SWEEP_STRICT=1.
9. Either adopt the `@AGENTS.md`/symlink bridge for the CLAUDE.md/AGENTS.md shared subset, or record why it was rejected.
10. Correct "8 pre-teardown specs" to 9 and exclude cliefnotes-wisdom.md from the archive move (or re-home the `[N-xxxx]` citations).
11. Annotate target-tree line 59 as "created by copier task, not committed" so it cannot be executed literally.
