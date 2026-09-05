# Session 5 review - repair sync and promote inventions

Date: 2026-09-04.
Branch: `fix/audit-s5-sync`, commits `4f128ad` (work) and `51f32b7` (log entry), unpushed.
Reviewer: a fresh session with no context from the implementation session.
The session prompt named Claude Fable 5.1; the session ran on Claude Opus 4.8 as lead with four Opus 4.8 workers (hooks, parity and attach, docs and scope, gate runner).
Inputs read in order: the session 5 block (handoff lines 481-495), Gap review items 1 and 3, Research additions A, C, and F, the report decision at handoff line 122, the full diff (`git diff main...fix/audit-s5-sync`, 32 files, 1443 added lines), and the Execution log entry (handoff lines 630-644).

## Verdict: FIX

The session delivered every tagged item and the deviations it logged are sound.
Five defects block a merge.
Each is small.
None needs a design change.

## Required fixes

1. `bin/loam-attach.sh:70` and `:80`.
   The refusal gate keys only on `settings.json`, but line 80 runs `rm -rf "$DST/.claude/hooks"` unconditionally.
   A target with its own hooks and no `settings.json` loses them with exit 0 and no message.
   Reproduced by the parity worker: a `my-own-hook.sh` in the target was gone after a plain attach.
   Fix: extend the guard to `[ -e "$DST/.claude/settings.json" ] || [ -d "$DST/.claude/hooks" ]`, and replace lines 80-81 with `mkdir -p` plus `cp "$SEED/hooks/"*.sh`.
   Add a test in `bin/tests/test_loam_attach.py` that plants a foreign hook and asserts it survives `--force`.
2. `bin/loam-attach.sh:115-128`.
   The `.gitignore` block is appended with `>>` and no trailing-newline guard.
   On a file ending without a newline the marker glues onto the last pattern (`node_modules/# Loam harness ...`), which kills that pattern and defeats the `grep -qxF` marker check, so every later run appends the block again.
   Fix: before the append, `if [ -s "$GI" ] && [ -n "$(tail -c 1 "$GI")" ]; then printf '\n' >> "$GI"; fi`.
   Add a test that writes `node_modules/` with no newline, attaches twice, and asserts one marker.
3. `seed/.claude/hooks/pre-commit-gate.sh:31`.
   The trigger regex matches `git commit` anywhere in the command text, including inside quotes.
   `test-tamper-scan.sh` and `mutation-gate.sh` share the regex but normally exit 0; this gate blocks with exit 2 unless a fresh sentinel exists.
   The gate is live in Loam through the root symlink and fired on this reviewer's read-only probe (`echo "git commit"` inside a loop) and twice on the hooks worker (`grep -r "git commit" .`).
   Fix: have the Python extractor at lines 16-26 emit a quote-blanked copy of the command and grep that, reusing the `strip_strings` idea at `test-tamper-scan.sh:150-168`.
   The hooks worker prototyped this: all six true positives kept, both false positives gone.
4. `seed/agent-parity.toml` renders into every project.
   It is not in `copier.yml:_exclude` (lines 12-26).
   Line 5 says "Samyak's binding rule", line 11 names distbench, and line 21 names `bin/agent_parity/parity.py`, which does not exist in a rendered project.
   This breaks AGENTS.md rule 2 (rendered content stays generic).
   Fix: add `- "agent-parity.toml"` to `_exclude` with a one-line comment, and reword lines 5 and 11 without the name and without distbench.
5. Three plugin skills still describe the pre-session-5 commit model.
   `cultivation/marketplace/sam-cc-setup/skills/ship/SKILL.md:56-58` says "There is no sentinel file to check" in the skill that runs `git commit`.
   `cultivation/marketplace/sam-cc-setup/skills/bootstrap-cc-setup/SKILL.md:49` says "the gate design was retired 2026-08-14".
   `cultivation/marketplace/sam-cc-setup/skills/sam_handoff/SKILL.md:11-17` writes `HANDOFF.md` with five fields (Goal, Current Progress, What Worked, What Didn't Work, Next Steps), while `seed/AGENTS.md.jinja:43` and `seed/.agents/skills/catchup/SKILL.md:18` now mandate seven headings for the same file.
   Decision (c) fixed the same sentence in `validate/SKILL.md` but stopped there; the log lists `sam_handoff` as a residual, but it is a live contradiction between two shipped artifacts, not a cosmetic one.
   Fix: mirror the `validate/SKILL.md:16-19` wording in `ship` and `bootstrap-cc-setup`, and rewrite `sam_handoff` steps 3 to the seven fields.

Two one-line fixes to land in the same pass:

6. `bin/rendered_harness_contract.py:1531`.
   `kind is None` makes `wants_scaffold` false, so a project whose answers file predates `project_kind` and has a `pyproject.toml` gets "pyproject.toml must not render for project_kind unset".
   Fix: `if kind is None: return` before line 1531.
7. `seed/.claude/hooks/run-validate-waves.sh:17` and `seed/CLAUDE.md.jinja:26`.
   The usage line says `./.claude/hooks/run-validate-waves.sh`, which does not match the allow rule `Bash(.claude/hooks/run-validate-waves.sh:*)` at `seed/.claude/settings.json:15`, so an agent that copies the usage line gets a permission prompt.
   Drop the `./`.
   `CLAUDE.md.jinja:26` reads "X (...) and Y (...), and Z (...)"; fix the conjunction.

## Gate output

Run by this review on `51f32b7`, from the worktree root, on 2026-09-04.
The first attempt ran the suite four times in parallel across workers and another session; the machine hit load 40 and the runs starved.
The duplicates were killed and the numbers below are from single runs.

```text
$ git status --porcelain
(clean)

$ uvx pytest -q bin/tests
272 passed, 381 subtests passed in 1399.38s (0:23:19)
exit=0

$ bin/verify-template.sh
== stage 1: contract unit tests ==
== stage 2: Copier scratch render from HEAD ==
== stage 3: rendered harness contract ==
== stage 4: Claude native validation ==
== stage 5: Codex native policy probes ==
== stage 6: skill frontmatter names ==
== stage 7: stale numeric claims in prose ==
== stage 8: skill-listing token weight ==
== stage 9: Claude/Codex parity BOM ==
verify-template: PASSED
exit=0

$ bin/harness-smoke.sh
== stage 1: render the working-tree seed ==   render: OK
== stage 2: rendered harness contract ==      contract: OK
== stage 3: skill-listing token weight (Score B) ==
score.B seed_listing_tokens=101 plugin_listing_tokens=2704
harness-smoke: PASS
exit=0

$ python3 bin/agent_parity/parity.py check
parity check passed
exit=0
```

Session Verify line, "attach test output pasted", reproduced on a scratch directory with no git repo:

```text
$ bin/loam-attach.sh <scratch>/attach-t1
[loam-attach]   attached Loam harness to <scratch>/attach-t1
[loam-attach] settings.json:        copied
[loam-attach] hooks/:               14 scripts copied
[loam-attach] settings.local.json:  written
[loam-attach] .gitignore:           ignore lines appended
[loam-attach] note: <scratch>/attach-t1 is not a git repo; hooks that need git stay quiet until 'git init'
EXIT=0

$ ./.claude/hooks/bash-length-advisory.sh < env1.json   # 455-character command
{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"Long command (455 chars). Split it into steps so each result is readable."}}
EXIT=0

$ bin/loam-attach.sh <scratch>/attach-t1
loam-attach: <scratch>/attach-t1/.claude/settings.json exists; re-run with --force to overwrite
EXIT=1
```

Item 2 verify, a `--vcs-ref=HEAD` render with `project_kind=typescript`: `pyright-lsp` count 0, JSON valid, no `pyproject.toml`, contract exit 0.
With `project_kind=python`: count 1, JSON valid, `pyproject.toml` present.

Post-check leftovers: only gitignored caches and logs; no `.validation_passed` sentinel; no tracked file modified.
The one untracked file is this review.

## Correctness and engineering practice

Verified OK, with evidence from the workers' probes:

- The three hooks carry no distbench path or name (grep for `distbench|/validate|validation-loop|known-issues|agent-memory` across all three returns nothing).
- `sentinel-cleanup.sh` behaves as its header says across eight envelopes: tracked in-repo Edit deletes both sentinels; gitignored path keeps them; path outside the repo keeps them; relative path and Write delete; malformed JSON and missing `file_path` delete (fail-safe); exit 0 in all cases.
- `run-validate-waves.sh` with no `pyproject.toml` prints both skip notes, exits 0, and writes `waves_passed=2`.
- `pre-commit-gate.sh` probes: no sentinel plus `git commit` exits 2 "sentinel missing"; `pytest -q` exits 0; `git grep commit` exits 0; `git -C sub commit` exits 2; bundled writer-plus-commit exits 2 with the correct hint.
- The regex works on macOS BSD grep 2.6.0 (probe: `git commit`, `git -C /x commit`, `git -c a=b commit` fire; `git grep commit`, `git log commit`, `gitx commit` pass).
- `settings.json` matchers and events are exact (`PreToolUse` on `Bash`, `PostToolUse` on `Edit|Write`).
- Both event-wired hooks are in `CLAUDE_HOOK_ROUTES` (`bin/rendered_harness_contract.py:90`, `:95`), and all three are in `REQUIRED_RENDERED_PATHS` (`:47-49`); `run-validate-waves.sh` is correctly absent from routes since it is a script, not a hook.
- Decision (c), no staging replay, is sound: the gate compares mtimes over `git diff --name-only HEAD` plus untracked files, which is staging-independent.
- `parity.py check` is bidirectional. Injecting a fake skill and a fake hook into a scratch seed fails with `Codex skill unclassified: fakeskill` and `Claude hook unclassified: .claude/hooks/fake-hook.sh`; deleting two mirrors fails with `declared but absent`; replacing the `catchup` symlink with a directory fails with `shared skill is not a symlink`.
- `seed/agent-parity.toml` matches the tree exactly: 1 skill (`find seed/.agents/skills -name SKILL.md`), 14 hooks, 0 agents, 0 workflows, 1 Codex hook.
- The `project_kind` render: typescript gives `pyright-lsp` count 0, valid JSON, no `pyproject.toml`, contract exit 0; python gives count 1, valid JSON, `pyproject.toml` present, settings identical to the seed file.
- `bin/loam-attach.sh` on a non-git directory copies settings and 14 hooks, writes `settings.local.json`, and a copied `bash-length-advisory.sh` fires with the advisory JSON on a 455-character command; a second run without `--force` exits 1 with "re-run with --force".
- shellcheck: the three hooks are clean; `loam-attach.sh` has only the SC1091 info every `bin/` script that sources `lib.sh` produces.
- `harness-smoke.sh:43-45` now matches its comment (dirty seed exits 1). The lost log row on that exit matches the two existing early exits at lines 51 and 57, and no automated caller exists.
- `verify-template.sh:228-235` follows the stage 8 shape; the summary is a bare `FAIL -ne 0` check, so no count can drift.
- `~/Desktop/teach-parbench` is at its original seven entries with no `.claude` or `.gitignore` residue.
- `~/Desktop/distbench` has no modified tracked file and no new commit (`410c07e`); the three untracked files there are personal exports with today's date, not from this session.

Lower-severity correctness notes, not blocking:

- `run-validate-waves.sh:28-31, 49, 70`: the `RUN_VALIDATE_WAVE*_CMD` seams are `eval`'d, so `RUN_VALIDATE_WAVE1_CMD=true RUN_VALIDATE_WAVE2_CMD=true` writes a passing sentinel on a repo with a real ruff error, labelled `validated_by=validate-skill`.
  A hand-written sentinel already clears the gate, so this adds no new bypass; it does make the one audit field lie.
  Cheapest honest fix: write `validated_by=$VALIDATED_BY-override` when a seam is used.
- `pre-commit-gate.sh:32-40`: ROOT comes from the envelope `cwd`, so `cd /tmp/other && git commit` in an unrelated repo is gated against this repo's sentinel.
  distbench had a FOREIGN policy for this; it was dropped.
  Same pattern as `test-tamper-scan.sh:33-37`, so it is a harness-wide choice, not a session 5 defect.
- `run-validate-waves.sh:35, 40, 44`: `uv run python -c 'import X'` syncs the project and can leave `.venv/`, `uv.lock`, and `.ruff_cache/` behind; only `.venv/` is gitignored.
  `uv run --no-sync` plus `.ruff_cache/` in the gitignore would remove the side effect.
- `bin/agent_parity/parity.py:163`: `target` is outside the `try/except ParityError` that guards `source` at 159, so an escaping symlink exits 2 with one line and hides every other error.
  Still fail-closed.
- `seed/.agents/skills/catchup/SKILL.md:19`: "when that fails within a few seconds" has no mechanism; `timeout` is absent on macOS (exit 127).
  `git -c http.lowSpeedLimit=1 -c http.lowSpeedTime=5 ls-remote ...` bounds it without `timeout`.
- `cultivation/marketplace/sam-cc-setup/skills/agent-team/SKILL.md:43`: `baseRef: "head"` is described as carrying a dirty branch; it carries the current HEAD commit, not uncommitted changes.
  The handoff's own line 277 has the same loose wording.

## Intent and scope

Every item tagged for session 5 is present.
Coverage, with the log's stated reason for each deviation:

| Obligation (handoff line) | Status | Evidence |
|---|---|---|
| catchup reads `_commit`, ls-remote, VERSION offline, red flag (487) | DONE | `catchup/SKILL.md:19, 32, 47`; ls-remote uses the HTTPS URL because `gh:` is Copier-only; the offline leg needs a reachable `_src_path` |
| `project_kind` question, five choices (488) | DONE | `copier.yml:40-44` |
| gate `pyproject.toml` on python, research, mixed (488) | DONE | conditional filename `seed/{% if ... %}pyproject.toml{% endif %}.jinja` |
| rename `settings.json` to `.jinja` (488) | DEVIATED, sound | `copier.yml:46-52` post-render strip; decision (a): the rename would remove Loam's own live settings through the root symlink |
| contract and tests for both kind branches (488) | DONE | `bin/rendered_harness_contract.py:1515-1560`; `test_rendered_harness_contract.py -k kind` 7 passed |
| parity BOM copied, distbench entries stripped, check-only (489) | DONE | `bin/agent_parity/parity.py`; decision (d) |
| `seed/agent-parity.toml`, mirror or unsupported (489) | DONE, see fix 4 | `seed/agent-parity.toml:1-63` |
| parity as verify-template stage 9 (489) | DONE | `bin/verify-template.sh:228-235` |
| three sentinel hooks copied and generalized, wired, gitignored (490) | DONE | `seed/.claude/hooks/`, `seed/.claude/settings.json`, `seed/.gitignore.jinja:44`; 13 tests |
| `bin/loam-attach.sh`, refuse without `--force`, test on teach-parbench (491) | DONE, see fixes 1 and 2 | `bin/loam-attach.sh`; `docs/SYNC.md:17-22`; log line 632 |
| distbench archive note, not edited (492) | DONE | `docs/2026-09-03-distbench-archive-note.md`; decision (e) moves it out of gitignored `docs/plans/` |
| root `AGENTS.md:63-64` overlap (493) | DEVIATED, sound | no-op; session 2 removed the seed copies (grep of `seed/AGENTS.md.jinja` is empty) |
| harness-smoke comment vs behavior (493) | DONE | `bin/harness-smoke.sh:43-45` |
| Gap 1: `RULINGS.md` ledger (151-154) | DONE | `seed/docs/decisions/RULINGS.md`; routed from `seed/CLAUDE.md.jinja:35` |
| Gap 1: invariants block (154-156) | DEVIATED, sound | `seed/AGENTS.md.jinja:35-39`; decision (b): `FORBIDDEN_RENDERED_PATHS` at `bin/rendered_harness_contract.py:60` forbids `.claude/rules` |
| Gap 1: ticket prompts reference, not restate (155) | prose only | `seed/AGENTS.md.jinja:38`; no prompt template in the seed to wire |
| Gap 1: CONTEXT.md Skip column with a reason (156-158) | DONE | `scaffold-context/SKILL.md:36-39, 71-73, 96` |
| Gap 3: lock-file convention plus hook (164-167) | DONE as amended | Research F line 288 says "Replace gap item 3's lock-file hook with this note"; `seed/AGENTS.md.jinja:21` is that note |
| Gap 3: brief and report under `.superpowers/sdd/<task>/` (167-168) | DONE | `agent-team/SKILL.md:141`, `brief-report-template.md`, `teammate-prompt.md:112`; `.superpowers/` gitignored |
| Gap 3: state-freshness gate in catchup (168-169) | DONE | `catchup/SKILL.md:28-31` |
| Research A: CONTEXT.md on demand, no token claim, short AGENTS.md (198-203) | DONE | no always-load wiring; `seed/AGENTS.md.jinja` 44 to 53 lines |
| Research C: fixed-schema HANDOFF replaces the four-line one (225-229) | DONE in seed, see fix 5 | `seed/AGENTS.md.jinja:43`; seven headings (the six named plus "Written at") |
| Research C: worktree isolation default for implementers (230-232) | DONE | `agent-team/SKILL.md:36-48`, `scenarios.md:9`; all eight claims verified against `claude --help` and code.claude.com/docs/en/worktrees |
| Research F: hooks read `cwd`, not `CLAUDE_PROJECT_DIR` (279-281) | DONE | `agent-team/SKILL.md:46`; the three hooks read `cwd` |
| report decision: repair forward sync, keep the layers (122) | DONE | `docs/SYNC.md:3` now names three mechanisms |

Drift from the report: none beyond the logged deviations, each of which holds on inspection.
Out of scope: two lines, the title em dashes at `seed/AGENTS.md.jinja:1` and `seed/CLAUDE.md.jinja:1`.
Both match the global writing convention and are harmless, but the log does not disclose them.

## Taste

- The three hooks read like `test-tamper-scan.sh` and `mutation-gate.sh`: same extractor, same root resolution, same exit protocol.
- `parity.py` is a clean subtraction from upstream: `apply`, `report`, `catalog`, adapters, plugins, commands, and the effort policy are gone; no unused imports.
  The agents and workflows legs (lines 114-131, 176-196, 223-237) are inert because the seed has none; keeping them is the right call for upstream fidelity, but one docstring sentence should say so.
- `pre-commit-gate.sh:58` starts its step numbering at 3; steps 1 and 2 were cut from the distbench original and the numbers were not renumbered.
- The trigger regex is now byte-duplicated in three hooks (`test-tamper-scan.sh:30`, `mutation-gate.sh:57`, `pre-commit-gate.sh:31`).
  Handoff line 629 said reuse; an identical-line check beside `_check_distribution_mirrors` would keep them from drifting.
- `bin/verify-template.sh:229` uses a bare `--root seed` where every other stage uses `"$ROOT"`.
- `run-validate-waves.sh:91-97` writes `timestamp`, `git_hash`, and `changed_files` that the gate never reads.
- `seed/docs/decisions/RULINGS.md:3-4` describes a pipe-delimited line and then ships a Markdown table; the two agree in substance but the prose should describe the table.
- `agent-team/brief-report-template.md` duplicates the seven-heading block verbatim for brief and report; `brief.md` carries three headings its author cannot fill at brief time.
- No em dash (U+2014) in any added line: `git diff main...fix/audit-s5-sync | grep '^+' | grep <U+2014>` exits 1.
- New skill prose is plain; no padding found.

## Thoroughness

- The Execution log (handoff line 632) names each check with its decisive output, and this review reproduced them independently (see Gate output).
- Tests: `test_seed_claude_hooks.py` adds 13 behavioral tests for the trio; `test_agent_parity.py` and `test_loam_attach.py` assert on exit codes and messages.
  Gaps: `test_loam_attach.py:24-25` always starts from an empty target, so no test sees a pre-existing `.gitignore` or hooks directory, which is why fixes 1 and 2 shipped.
  `test_agent_parity.py:63-66` (`test_clean_base_passes`) duplicates `test_real_seed_check_passes` because every declared file exists.
  No test covers the pyproject-present skip notes or the stale and `waves_passed=1` gate branches.
- `bin/verify-template.sh:35-36` and `bin/harness-smoke.sh:52-54` render with `--defaults` only, so the typescript branch is proven by the session's manual render and by fixtures, not by the gate.
- Docs left stale by the third mechanism: `README.md:74` still calls `docs/SYNC.md` "Forward updates and reverse promotion"; root `AGENTS.md` does not list `bin/loam-attach.sh` under Common commands or the `bin/` layout row; `docs/SYNC.md:20` does not say attach replaces the hooks directory.

## Deferred, for Samyak to rule on

- Whether the FOREIGN-repo policy from distbench's gate should return.
- Whether `verify-template.sh` should add a typescript render and contract call.
- Whether the `RUN_VALIDATE_WAVE*_CMD` seams should be gated on a test marker or only labelled.

## Risks

- The commit gate is live in Loam now.
  Until fix 3 lands, any Bash call whose text contains `git commit` inside quotes is blocked when the sentinel is stale.
- `settings.local.json` written by attach bakes this worktree's absolute marketplace path; a lasting attach must run from `~/Desktop/loam`.
- This review did not run the Codex round; the handoff makes the fresh-context review the review for this session.
