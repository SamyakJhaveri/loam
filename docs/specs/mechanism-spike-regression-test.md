# mechanism-spike-regression-test

> Spec derived from the mechanism spike (Part 0.5 of the Phase-1 campaign).
> Turns the one-off manual probes into a re-runnable regression guard, so the findings stay true as Copier/Loam evolve.
> Evidence + probe sequence: `~/.claude/plans/2026-07-19-mechanism-spike-findings.md` (per-probe commands + Appendix verdict table).
> Generated via `/gen-spec`, 2026-07-19. **Status: implemented (2026-07-20, PRs #1/#2, main bc4ae34).**
> Decided (high value, no architecture dependency). This is "put the probes into practice" made literal.

## Identity

- **Name:** mechanism-spike-regression-test
- **Owner:** Sam
- **Status:** implemented (2026-07-20, PRs #1/#2, main bc4ae34)
- **Scope:** A reproducible, version-pinned end-to-end script that recreates the spike's probe chain in a disposable scratch dir and asserts each finding. New file(s) under `bin/` (plus optional wiring). Read-only on canonical (clones into scratch, exactly like the spike). Encodes the current behavior as assertions so a future Copier/Loam change that alters it fails loudly.
- **Related:** `copier-update-timestamp-conflict.md` (its fix flips assertion #8 red→green); `template-sync-promote-generic-user.md` (its fix updates the PR-target assertion).

## Inputs

- **The verdicts to encode** — `~/.claude/plans/2026-07-19-mechanism-spike-findings.md`, Appendix "verdict table" (the authoritative list of what must stay true / must change).
- **The exact probe sequence** actually run this session — findings §1 (copier copy + promote), §2 (fork + Edge A/Edge B), §3 (conflicts). Every command is quoted there.
- **Version pins (record at runtime, warn-not-fail on drift):** copier `9.17.0`, git `2.55.0` (the versions the findings were Verified against).
- **Existing harness to reuse, not reinvent:** `bin/verify-template.sh` (the repo's E2E gate + `lib.sh` helpers), the `render-gate` skill's TDD pattern. Do NOT hand-roll a new assertion framework — plain `bash` `set -e` + `[[ ]]`/`grep` assertions, matching the house style of `bin/*.sh`.

## Behavior

A single script (proposed `bin/spike-probes.sh`) that runs the full chain in a scratch dir it creates and cleans up. It clones canonical, removes the clone's `origin` (so no push can reach the real repo), and asserts:

1. **Bootstrap metadata:** after `copier copy`, `.copier-answers.yml` exists, `template-manifest.json` does not, and the project has no `bin/`.
2. **Upward promote (script path):** `template-sync.sh promote --layer generic …` from the project creates a `sync/*` branch + commit with the asset at `seed/.claude/rules/…`, exit 0. Assert the printed PR command contains `--repo samyakjhaveri/loam`. **This is a change-detector**, marked in-script as the single line to update when `template-sync-promote-generic-user.md` reworks targeting.
3. **Skill precondition:** with no manifest present, the SKILL.md documented pre-flight would refuse — a static assertion against SKILL.md's text (this assertion is updated/removed once SPEC `template-sync-promote-generic-user` aligns the skill).
4. **Edge A broken:** a forked "personal Loam" has no `.copier-answers.yml`; `copier update` there exits non-zero and stderr contains `Cannot obtain old template references`.
5. **Edge A fallback works:** `git merge upstream/main` of a non-overlapping canonical change is clean (exit 0) and preserves the personal divergence file.
6. **Edge B works:** `copier update --defaults` in a project made from the personal Loam advances `_commit`, pulls the new file, preserves divergence, exit 0.
7. **Conflict shapes:** same-line git merge → `UU`; modify/delete → `UD`; `copier update` overlap → in-file `before/after updating` markers; a template file deletion propagates to the project on update.
8. **Timestamp assertion (the red one, then the end-to-end guard):** first render the same template commit twice with the same answers and a ≥2-second gap, then assert `CLAUDE.md` and `README.md` are byte-identical. This deterministic root-cause oracle FAILS on the pre-fix baseline and PASSES after `copier-update-timestamp-conflict` lands. Once it is green, create an empty template commit (a new revision with **no rendered content change**), run `copier update --defaults` to that revision, and assert `_commit` advances with zero unmerged files or conflict markers. The render comparison supplies deterministic red→green proof; the forced update guards the promised Copier behavior.

## Outputs

- **New:** `bin/spike-probes.sh` — self-contained, scratch-only, asserts every item above, exits non-zero on the first failed assertion, and traps-cleans its scratch dir on any exit.
- **Version log** printed at the top of every run (copier + git versions actually used).
- **Wiring (D1, grilled 2026-07-19 — standalone only):** a separate script — **NOT** the per-commit `/validate` gate, **NOT** a `bin/verify-template.sh` flag, and **NOT** wired into `bin/release.sh`. It clones + runs Copier several times (slow), so run it manually on Copier/Loam version bumps and pre-release; the only cross-reference is a one-line pointer in the release-checklist docs. Respect the validation-slimming decision (do not fatten the commit gate).

## Constraints (must NOT)

- MUST NOT run any mutating git/copier command against `~/Desktop/loam` — clone into a scratch dir, remove the clone's `origin`, work only there (mirror the spike's guardrails exactly).
- MUST NOT `git push` or open a PR — record the printed `gh pr create`, never execute it.
- MUST NOT leave scratch dirs behind — `trap` cleanup on EXIT.
- MUST NOT hard-fail solely on a Copier/git version mismatch — log a warning; the findings are pinned to copier 9.17.0 and behavior may legitimately change on upgrade (that is signal, surfaced as a warning, not a crash).
- MUST NOT be added to the per-commit `/validate` gate in a way that materially slows it without an opt-in.
- MUST NOT depend on network access to GitHub (all remotes are local scratch clones).

## Acceptance Criteria

1. Running `bin/spike-probes.sh` on current `main` (before the SPEC 1/3 fixes) reproduces every spike verdict: it passes all "current behavior" assertions and fails **only** on assertion #8 (the intentional red timestamp test).
2. Before-vs-after the run, `git -C ~/Desktop/loam rev-parse HEAD` is unchanged and `git -C ~/Desktop/loam status --porcelain` is empty (canonical untouched) — asserted by the script itself.
3. The scratch dir does not exist after the script exits (success or failure).
4. The run output records the copier and git versions used.
5. After `copier-update-timestamp-conflict` is implemented, assertion #8 passes with **no other edit** to `bin/spike-probes.sh`.
6. The script documents, in a header comment, the exact single line to change for assertion #2 (PR target) when `template-sync-promote-generic-user` reworks targeting.
7. `bin/spike-probes.sh` is executable and passes `bash -n` (syntax) and, if the repo lints shell, `shellcheck` at the same level as the other `bin/*.sh`.
