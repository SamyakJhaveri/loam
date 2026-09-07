# Review: audit session 4 (new hooks)

Reviewer: Claude Fable 5.1, fresh context, 2026-09-04, effort high.
Branch `fix/audit-s4-hooks` at `11d476a`, checked out in `~/Desktop/loam`; local `main` in the worktree `/private/tmp/loam-audit-s3-reviews`.
Scope reviewed: `git diff main...fix/audit-s4-hooks` (24 files, +2398 / -67), commits `5aee49a`, `e8df75d`, `b49e744`, `11d476a`, the session 4 block, Research additions B and F, and the Execution log entry.
Workers: four Opus agents (tests, upstream payload shapes, gate reproduction, drift), then an ultracode workflow of Opus 4.8 skeptics at xhigh, two per finding, plus one completeness critic.
No file in the repo was edited by the review except this one.

## Verdict: FIX

Every tagged item is implemented, wired, in the contract, and tested, and the four checks pass on this branch (output below).
The design matches the handoff and the report.
Two findings are High and block a merge as-is, because each makes a shipped gate silently miss its main case:

1. Both commit gates read the index before `git add` runs, so `git add -A && git commit` and `git commit -a` bypass them.
2. The mutation gate never scores a newly added file.

Five Medium findings ride along because each is a few lines in a file the High fixes already touch: the audit log's exit code is `?` on every successful command, the claim trigger has no word boundaries, the mutation gate has no baseline run, the tamper scan flags words inside strings and docstrings, and a bad transcript line disables the claim leg.
The exact fix list is in "Fixes required".

## Checks run on this branch

`uvx pytest -q bin/tests`

```
217 passed, 379 subtests passed in 386.67s (0:06:26)
EXIT=0
```

`bin/verify-template.sh` (stage lines)

```
contract unit tests: OK
Copier scratch render: OK
rendered harness contract: OK
validate seed/.claude: OK
validate --strict seed/.agents/skills: OK
validate --strict cultivation/marketplace: OK
parse cultivation/marketplace/sam-cc-setup/hooks/hooks.json: OK
Codex probe normal-push: OK (prompt)
Codex probe force-push: OK (forbidden)
Codex probe force-with-lease: OK (forbidden)
stale-counts: OK
skill-listing weight: OK (<= 2750 tokens; research target is ~2000)

verify-template: PASSED
EXIT=0
```

`bin/harness-smoke.sh`

```
== stage 1: render the working-tree seed ==
render: OK
== stage 2: rendered harness contract ==
contract: OK
== stage 3: skill-listing token weight (Score B) ==
score.B seed_listing_tokens=101 plugin_listing_tokens=2704

harness-smoke: PASS
EXIT=0
```

`bash -n` on every file in `seed/.claude/hooks/`: all eleven clean.
`stop-verify-gate.sh` is 159 lines, under the 160 cap in item 3.

### Verify line: every new hook against a synthetic stdin envelope

Run from a scratch git repo so no log lands in Loam.
Each block shows the envelope's key fields, then the hook output and exit code.

`write-rewrite-guard.sh`, 100-line file:

```
{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"big.txt already exists with 100 lines. Prefer Edit; use Write only if most of the file is changing."}}
exit=0
```

10-line file: no output, exit 0. `REWRITE_GUARD_LINES=5` on the 10-line file: the advisory fires, exit 0.

`bash-length-advisory.sh`, 401-character command:

```
{"hookSpecificOutput":{"hookEventName":"PreToolUse","additionalContext":"Long command (401 chars). Split it into steps so each result is readable."}}
exit=0
```

400 characters: no output, exit 0.
The hook also fired live in this session on a 470-character command, which proves it dispatches from the root `.claude` symlink.

`post-compact-reinject.sh`:

```
Post-compaction reminders: 1. Finish the whole task; do not stop early or ask permission for work already requested. 2. Keep changes to what the task asks; report pre-existing bugs as follow-ups. 3. Surgically edit files. 4. Batch independent tool calls. 5. Re-read HANDOFF.md if present and run the verify command it names before claiming anything.
exit=0
```

`skill-usage-log.sh`, `{"cwd":"<scratch>","tool_input":{"skill":"catchup","args":"--brief"}}`:

```
2026-09-04T10:34:20-07:00 catchup --brief
exit=0
```

`bash-audit-log.sh`, PostToolUse with `tool_response.exit_code: 0` and `EXPERIMENT_ACTIVE=exp1` (this envelope shape is synthetic, see finding H1):

```
2026-09-04T10:34:20-07:00 | exit=0 | exp1 | echo hi
-- experiment mirror: experiments/exp1/logs/commands/2026-09-04.log
2026-09-04T10:34:20-07:00 | exit=0 | exp1 | echo hi
```

PostToolUseFailure with `"error":"Command failed with exit code 1"`: `exit=1 | - | false`.
PostToolUse with the real key set (`stdout`, `stderr`, `interrupted`): `exit=? | - | ls`.
Malformed JSON: `exit=? | - | unparseable`.

`harness-hygiene.sh` with `cwd` = the Loam root: no output, exit 0 (matches decision (d)).
A worker's throwaway repo whose CLAUDE.md names `docs/missing.md`, an absent `bin/verify-template.sh`, `nonexistent-tool --flag`, `v2.0.0`, `Node.js`, `asyncio.gather`, `model: opus`, `/goal`, and a present `README.md`:

```
Harness hygiene: 3 stale reference(s) in agent docs
  CLAUDE.md: docs/missing.md (missing path)
  CLAUDE.md: bin/verify-template.sh (missing path)
  CLAUDE.md: nonexistent-tool (command not found)
exit: 0
```

`stop-verify-gate.sh` leg 4, synthetic transcripts, Stop envelope with `last_assistant_message`:

| Case | Final message | Evidence in turn | Exit |
|------|---------------|------------------|------|
| a | All tests pass. | none | 2, unverified-claim block |
| b | All tests pass. | Bash result `5 passed in 0.1s` | 0 |
| c | Tests pass, not verified. | none | 0 |
| d | All tests pass. | Bash result `2 failed, 5 passed in 0.1s` | 2 |
| e | verify-template PASSED. | Agent result `verify-template: PASSED` | 0 |
| f | All tests pass. | Bash `5 passed` in the previous turn only | 2 |
| g | This hook passes the payload through unchanged. | none | 2 (the `passes` residual) |
| h | The fix is unverified. | none | 2 (finding M1) |
| i | Edited the file. | none | 0 |

The block text is item 3's sentence verbatim.

`test-tamper-scan.sh` (worker runs in a throwaway repo, real hook, staged changes):

| Case | Result |
|------|--------|
| `@pytest.mark.skip(reason="slow")` added | exit 2, `new skip/xfail` |
| `rows = data[1:]  # skip the header row` | exit 0 |
| `def test_x(monkeypatch):` | exit 2, `new mock/patch` (finding M5) |
| `rel=1e-6` to `rel=1e-3` | exit 2, `loosened tolerance 1e-6 -> 1e-3` |
| `rel=1e-6` to `rel=1e-9` | exit 0 |
| `return 42` in src plus `== 42` in test | exit 2, `expected literal 42 equals a new return value in src/calc.py` |
| `return 0` plus `== 0` | exit 0 |
| same as row 1 with `-m "Test-changes: ..."` | exit 0 |
| `git grep commit`, `git log --grep=commit` | exit 0 |
| `git -C <path> commit -m x` | fires |
| test-only commit with `== 42` | exit 0 |
| malformed JSON, empty stdin | exit 0 |

My own run, unstaged skip decorator in the working tree, empty index:

```
### unstaged skip, command: git add -A && git commit -m x
exit 0
### unstaged skip, command: git commit -a -m x
exit 0
### same change staged, command: git commit -m x
Test integrity scan: 1 flagged line(s) in staged tests:
  tests/test_a.py:2: new skip/xfail: @pytest.mark.skip(reason="slow")
Justify each under a 'Test-changes:' line in the commit message, then retry.
exit 2
```

`mutation-gate.sh` (worker, cosmic-ray 8.7.0 in a scratch venv symlinked as the throwaway repo's `.venv`):

| Case | Result |
|------|--------|
| untested `mul` added to a tracked file | exit 2, `11 surviving mutant(s) on lines this commit changes`, 3 s wall clock |
| test for `mul` added | exit 0 |
| new untested file `src/extra.py` | exit 0, every mutant `skipped / Filtered git` (finding H3) |
| `-m "Mutants: justified"` | exit 0 |
| after each run | `git worktree list` shows only the main tree; staged source unmutated |
| test-command `false` | exit 0, no output (finding M2) |
| SIGTERM at 8 s | exit 143, trap ran, worktree removed, `cosmic-ray exec` child still running |
| SIGKILL at 8 s | exit 137, worktree entry and tmp tree leaked; a later run did not prune it (finding M3) |

Codex `pre-tool-policy.py`, apply_patch envelopes (`tool_input.command` holds the patch text; the Codex source confirms this shape at `codex-rs/core/src/hook_runtime.rs:229`):

| Patch target | Decision |
|--------------|----------|
| `.env` | deny, "Patches to .env files are blocked by repository policy." |
| `config/.env.local` | deny, .env reason |
| `runs/2026-09-04_x/results/metrics.json` | deny, "Patches to sealed run results are blocked by repository policy." |
| `build/out.js` | deny, "Patches to generated outputs are blocked by repository policy." |
| `src/app.py` | allow, silent |
| `src/results/helpers.py` | allow (results only sealed under runs/ or experiments/) |
| `docs/build/index.md` | deny, generated (residual: segment matched anywhere) |
| `../.env` | deny |

Bash `git push -f origin main`: deny.
Bash `git push --force-if-includes origin main`: allow, silent (see L1).

## Scope: every tagged item, nothing extra

| Item | Where | Status |
|------|-------|--------|
| 1 write-rewrite-guard, PreToolUse Write, 80 lines, `REWRITE_GUARD_LINES` | `seed/.claude/hooks/write-rewrite-guard.sh:44-56`, `settings.json:50-58` | done, message byte-identical |
| 2 post-compact-reinject, SessionStart compact | `post-compact-reinject.sh:15`, `settings.json:126-134` | done, text verbatim |
| 3 stop-gate evidence leg, BLOCK | `stop-verify-gate.sh:109-147` | done, trigger and block text verbatim; extensions in decision (f) |
| 4 bash-length-advisory, 400 chars | `bash-length-advisory.sh:33-36` | done |
| 5 Codex apply_patch policy, `git push -f` and `--force-if-includes` forbidden | `seed/.codex/hooks.json:14-24`, `pre-tool-policy.py:731-830`, `default.rules:56-68` | done |
| 6 `/goal` gotcha | `seed/CLAUDE.md.jinja:19` | done, verbatim |
| B mutation gate | `mutation-gate.sh` | done, with the gaps in H2, H3, M2, M3 |
| B tamper scan plus failing-test-first rule | `test-tamper-scan.sh`, `seed/AGENTS.md.jinja:32` | done |
| B harness hygiene at SessionStart | `harness-hygiene.sh` | done, narrowed to inline code spans (L3) |
| B skill usage log | `skill-usage-log.sh`, `.gitignore:36`, `copier.yml:19` | done |
| B command capture with exit code and experiment name | `bash-audit-log.sh`, `settings.json:100-124` | wired; exit code dead on the success path (H1) |
| F cwd rule for run-logging hooks | `bash-audit-log.sh:39`, `skill-usage-log.sh:15`, `harness-hygiene.sh:25`, plus the three gates | done |
| FINDINGS row 1, ruff probe | `stop-verify-gate.sh:78-95` | closed by `5aee49a`; same module-first, `No module named ruff`, PATH-fallback pattern as `ruff-after-edit.sh:27-30` |
| FINDINGS row 3, fanout xhigh | `plan-review-fanout.js:162-170,198-199,227` | closed by `e8df75d` |

Every file in the diff stat is justified by one of these rows, the contract, the tests, or the docs commit.
`bin/harness-smoke.sh` changed two comment lines to follow the audit hook to PostToolUse.
The move to PostToolUse is stated in Research B itself ("Command capture: PostToolUse on Bash appending command, exit code, timestamp"), so it is not drift.
`PostToolUseFailure` is not in that bullet but is a real event and is the only path that yields a numeric exit code today.

## Drift against the report and the handoff

Checked by a worker against `docs/plans/2026-09-02-harness-audit-synthesis.md`.

- Item 2's reminder list in the report includes a STATE.md pointer; the handoff text drops it and the hook follows the handoff. Handoff is binding; no action.
- Item 3: four documented extensions beyond the item text, all logged in decision (f) or the Codex round: Agent, Task, and Workflow results count as evidence; a failure-marker veto; per-result evaluation; `last_assistant_message` preferred over the transcript. Success tokens gained `\b`. No token added or removed.
- Item 5: "sealed result namespaces" and "generated outputs" have no path definition in the report (its only uses describe the eval-bench project's registry file and a sentinel file). The session defined sealed as a `results` segment under `runs/` or `experiments/` (consistent with the run-folder contract at handoff lines 292-295) and generated as `build`, `dist`, `htmlcov`, `__pycache__`, `.pytest_cache`, `*.egg-info`, `.coverage`. Reasonable defaults, logged as a residual by the lead.
- Research B hygiene says "extract every path, file, and command named"; the hook scans inline backtick spans only, first token only, and commands only in spans of two or more tokens. Fenced code blocks are not scanned. Decision (d) documents the heuristics but not this narrowing.
- Decision (c)'s trigger regex, decision (d)'s silent Loam root, and decision (a)'s gitignore claim were each re-run and hold.
- The Execution log's "real cosmic-ray run that listed eight survivors" left no artifact; a worker's fresh run listed eleven survivors on one changed line, so the mechanism holds even if the number is transcript-only.

## Findings

Each finding was reproduced by me or a worker with the real hook, then handed to two Opus 4.8 skeptics at xhigh: one tried to refute the finding, one tried to refute the proposed fix.
All eight findings survived.
Where a skeptic refuted or amended the fix, the amended fix is the one listed.
Labels (H1, M3, ...) are the ids used in the verification workflow; the section headers carry the final severity, which the skeptics moved for H1 and M3.

### High

**H2. Both commit gates are blind to `git add -A && git commit` and `git commit -a`.**
`seed/.claude/hooks/test-tamper-scan.sh:41` reads `git diff --cached`; `seed/.claude/hooks/mutation-gate.sh:85` reads `git diff --cached --name-only` and line 165 overlays the scratch worktree from the same index.
Both run at PreToolUse, before the command stages anything.
Reproduced three times (my run above, two workers): an unstaged skip decorator passes both commands with exit 0 and is blocked only when staged first.
Both forms are the common way an agent commits.
The skeptic amended the fix: `git add -A` into a temp index over-captures for `commit -a`, because `-a` commits tracked changes only (a `git commit -a --dry-run --short` shows the untracked test file as `??`).

**H3. The mutation gate never scores a newly added file.**
`mutation-gate.sh:160-168`: `git worktree add --detach` gives the scratch tree an index equal to HEAD, and `git checkout-index --prefix` writes the staged files without updating that index, so an added file is untracked there.
`git diff HEAD --stat` inside the scratch tree is empty for it, and `cr-filter-git` with `branch = "HEAD"` marks every mutant `skipped / Filtered git`.
Worker reproduction: a new untested `src/extra.py` passed with exit 0 and no NOTE; the same function added to a tracked file was blocked with 11 survivors.
A new module is the largest kind of change the gate exists for.

### Medium

**H1. The audit log's exit code is `?` on every successful command.**
`seed/.claude/hooks/bash-audit-log.sh:49` reads `tool_response.exit_code`.
A real Claude Code Bash response has no such key.
A worker scanned 6,026 Bash results in local transcripts: zero carry `exit_code`; every one carries `stdout`, `stderr`, `interrupted`, `isImage`, `noOutputExpected`, and 55 carry `returnCodeInterpretation` (prose such as "No matches found" for a tolerated grep exit 1).
The live log agrees: 598 of 603 new-format lines read `exit=?`; the five digits all came from the PostToolUseFailure path.
My live probe `cat /nonexistent-file-for-audit-probe-296ebfb9` logged `exit=1` through that path.
The comments at lines 7 and 31 assert a field that does not exist, and the tests at `bin/tests/test_seed_claude_hooks.py:741-824` feed the phantom key.
Medium, not High: a `?` is honest, and the log stays readable as "digit means failure".
The skeptic refuted my first fix (default to 0): a grep with no match exits 1, fires PostToolUse, and would be logged as 0.

**M1. The claim trigger has no word boundaries.**
`seed/.claude/hooks/stop-verify-gate.sh:124`: `verified|all tests pass|tests pass|passes|confirmed|re-verified|PASSED` with `re.I`.
"unverified", "unconfirmed", "bypassed", and "surpasses" all trip it; case (h) above shows "The fix is unverified." blocked and told to write "not verified".
The success tokens at line 140 do carry `\b`, but the token `exit 0` does not match the common `exit=0` output style; the gate blocked one of this review's own messages for that reason.

**M2. The mutation gate has no baseline, so a broken test command reads as "every mutant killed".**
`mutation-gate.sh:204-215` runs init, filter, exec, dump, never `cosmic-ray baseline`.
Worker: `test-command = "false"` gave exit 0 with no output on an untested change.
cosmic-ray splits `test-command` with `shlex` and no shell (`cosmic_ray/testing.py:62-63`), so `sleep 30 && python -m pytest -q` fails instantly and also kills every mutant.
The header at lines 95-110 does not say the value takes no shell operators.

**M5. The tamper scan flags `mock`, `patch`, and `skip` inside strings, docstrings, and the bare `monkeypatch` fixture name.**
`test-tamper-scan.sh:93` matches the bare words; `strip_comment` at lines 105-124 strips comments only.
Critic confirmed: a staged test whose docstring says "we patch the config and mock nothing real" is blocked.
A worker rebuilt the session's own commits and ran the real hook: `5aee49a` (4 flagged lines in `bin/tests/test_rendered_harness_contract.py`) and `e8df75d` (6 flagged lines in `bin/tests/test_seed_claude_hooks.py`) would each have been blocked by their own scan; no session commit carries a `Test-changes:` line.
They landed because hooks load at session start.
The Loam root `.claude` is a symlink to `seed/.claude`, so every future Loam test commit meets this scan.
Every flagged line is fixture or assertion text, so this is noise, not tampering; the skeptic measured that blanking string contents clears `e8df75d` fully and cuts `5aee49a` from 4 flags to 2 (a variable literally named `patch`), which is what the escape hatch is for.

**M4. One unparseable transcript line disables the claim leg for the whole session.**
`stop-verify-gate.sh:112-116` loads every line in one comprehension inside one try; any failure exits 0.
Worker reproduced exit 0 with one bad line and a bare claim.
Low likelihood (0 of 199 local transcripts has a bad line), so this is defense in depth; the older SESSION parser at lines 43-59 is already per-line tolerant.

### Low

**M3. The SIGKILL recovery promise is wrong; the SIGTERM path is fine.**
`mutation-gate.sh:17` and `:158` promise `git worktree prune` recovers a run killed at the hook timeout, and `b49e744` says the leak is "now pruned at the next run".
Worker: under SIGKILL the trap is skipped, the mktemp tree survives, and prune is a no-op because prune only drops entries whose directory is gone; a later successful run left the stale entry in place.
Under SIGTERM the EXIT trap runs and the worktree is removed (`bash -c 'trap "echo TRAPPED" EXIT; sleep 30'` killed with TERM prints TRAPPED, rc 143), so this matters only if Claude Code kills a timed-out hook with SIGKILL, which the review did not establish.
The skeptic refuted my fixed-path fix: two concurrent sessions would clobber one scratch tree.
The checkout itself was never mutated in any kill test, so the safety claim at lines 11-16 holds.

**L1. `git push --force-if-includes` is a no-op on its own.**
`man git-push`: "If the option is passed without specifying --force-with-lease ... it is a no-op."
The rule at `seed/.codex/rules/default.rules:63-68` is per item 5 and harmless, but its justification says the pre-tool hook blocks it, and `pre-tool-policy.py` allows `git push --force-if-includes origin main` silently (probe above).
The `-f` rule at lines 56-61 is the one that does the work.

**L2. Multi-line commands shatter the audit log.**
`bash-audit-log.sh:59` writes the raw command; heredocs and `python3 -c` bodies carry their newlines into the file.
A worker counted 509 well-formed entries spanning 1,525 lines in the live log.
The lead listed this as a residual; it is bigger than "stays multi-line" suggests.

**L3. Harness hygiene scans inline code spans only.**
`harness-hygiene.sh:52` matches single-backtick spans; fenced code blocks are never scanned, and a bare backticked tool name (one token) is never command-checked (`:136`).
Research B says "every path, file, and command named"; decision (d) documents the heuristics but not this narrowing.
No false positive was found in either run above.

**L4. Test gaps and duplication.**
Five of the six hooks that read the payload `cwd` have tests that set `cwd` to the directory the hook already runs in, so deleting the cwd handling would not fail them (`bin/tests/test_seed_claude_hooks.py:936, :996, :1093, :1111, :1304`); only the audit-log test at `:801-813` points cwd at a second repo.
Nothing asserts the cosmic-ray config the gate writes (`:1364` checks that a log exists and never reads it).
The mutation gate has no malformed-JSON test and no zero-survivor test (the fake tool at `:1268` always emits a survivor).
`_payload` and `_stage` are duplicated verbatim across two classes (`:1111`, `:1304`); `_shim` at `:1249-1266` re-implements the loop at `:137-147`; `TestTamperScanTests` at `:1102` doubles the word Test.
The contract probes only the `.env` family (`bin/rendered_harness_contract.py:1167`), and the comment at `seed/.codex/hooks/pre-tool-policy.py:26` claims the contract reads all three families from the tuple.

**L5. By-design behaviors worth knowing, no change asked.**
The stop gate is one-shot: after one block, the retry passes through the pre-existing `stop_hook_active` guard at `stop-verify-gate.sh:18`.
A Bash result that merely echoes the claim phrase counts as evidence, per item 3's "or the same phrase".
The claim leg now runs on turns with no edits, so a conversational answer such as "the auth test passes" blocks until it carries output or "not verified"; this is Samyak's decision and it hit this reviewer twice.
The escape hatches are read from the command string only (`test-tamper-scan.sh:32`, `mutation-gate.sh:53`), so `git commit -F` or an editor commit cannot carry a justification.
`skill-usage-log.sh:31` falls back to a `name` key that no real Skill payload uses.

### Refuted or resolved during verification

- Drift checker and critic both raised that the Codex apply_patch envelope might not carry the patch in `tool_input.command`, which would fail closed. The payload checker settled it from Codex source: `codex-rs/core/src/hook_runtime.rs:229` reads `command` for both `Bash` and `apply_patch`, `apply_patch.rs:282` documents the raw patch text as that command, and the lowercase `apply_patch` is the canonical tool name with `Edit` and `Write` as aliases. No finding.
- Critic flagged `plan-review-fanout.js` as out of scope. It closes FINDINGS row 3, which session 3's log assigned to session 4. In scope.
- Critic checked and cleared: `PostToolUseFailure` and the SessionStart `compact` matcher are documented events; the rendered `.gitignore.jinja:37` covers `skill-usage.log` through `*.log`.

## Fixes required

Ordered by the file they touch.
Each is a few lines; none changes the design.

1. `seed/.claude/hooks/test-tamper-scan.sh:41` (H2). When the command matches `\bgit\s+add\b`, stage into a temp index with `git add -A`; when the commit carries `-a` or `--all`, stage with `git add -u`; otherwise keep the real index. Concretely: `TMPI=$(mktemp); cp "$(git rev-parse --git-path index)" "$TMPI"; GIT_INDEX_FILE=$TMPI git add -u` (or `-A`), then `GIT_INDEX_FILE=$TMPI git diff --cached -U0 --no-color`, then remove `$TMPI`. Add two tests: unstaged skip under `git add -A && git commit` blocks; an untracked test file under `git commit -a` does not block.
2. `seed/.claude/hooks/mutation-gate.sh:85` and `:165` (H2). Build the same temp index and thread `GIT_INDEX_FILE=$TMPI` through both the `--name-only` read and the `checkout-index` overlay.
3. `seed/.claude/hooks/mutation-gate.sh`, after line 168 (H3). Add, in the script's fail-open style: `if ! git -C "$TREE" add -A 2>/dev/null; then echo "NOTE: mutation gate skipped: could not index the scratch worktree" >&2; exit 0; fi`. Add a test with a new untested file that expects exit 2.
4. `seed/.claude/hooks/mutation-gate.sh:203` (M2). Before the first `cosmic-ray init`, run `"$CR" baseline "$cfg"` once per run (guard with a `BASELINE_DONE` flag); on failure set `FAILED_STEP="cosmic-ray baseline (test command does not pass on unmutated code)"` so the existing NOTE-and-exit-0 block at lines 221-225 handles it. In the header near line 21, say `test-command` is split with shlex and takes no shell operators. Add a test with `test-command = "false"` that expects exit 0 plus the NOTE.
5. `seed/.claude/hooks/mutation-gate.sh:17` and `:158` (M3). Rewrite both comments to say a SIGKILLed run leaves a worktree entry that prune cannot drop until its directory is removed. No code change.
6. `seed/.claude/hooks/bash-audit-log.sh:47-49` (H1). In the PostToolUse branch: `?` when `tool_response` is not a dict, when `interrupted` is true, or when `returnCodeInterpretation` is present (a tolerated non-zero exit); otherwise `0`. Fix the comments at lines 7 and 31 to say the response carries no exit code. Add a test with the real key set expecting `exit=0`, and one with `returnCodeInterpretation` expecting `exit=?` (the second is the one that fails the naive fix).
7. `seed/.claude/hooks/stop-verify-gate.sh:124` (M1). Wrap the trigger: `\b(?:verified|all tests pass|tests pass|passes|confirmed|re-verified|PASSED)\b`. At line 140 widen `exit 0` to `exit[ =]0`. Add a test that "unverified" with no evidence exits 0 and one that a Bash result `exit=0` backs a claim.
8. `seed/.claude/hooks/stop-verify-gate.sh:112-116` (M4). Keep `open()` inside the exit-0 try; move only the per-line `json.loads` into a try/continue loop. Stay under item 3's 160-line cap by merging the two early exits at lines 121-125 into one condition.
9. `seed/.claude/hooks/test-tamper-scan.sh:135` (M5). Add a `strip_strings` helper in the style of `strip_comment` that blanks the contents of quoted string literals, and apply it for the SKIP and MOCK checks only: `code = strip_strings(strip_comment(txt))`. Add a test that a docstring mentioning "patch" and "mock" passes and that `@patch("x")` still blocks. From this commit on, Loam's own test commits will need a `Test-changes:` line whenever a fixture literally contains one of these words.

Optional, not required for merge: L1 justification wording, L2 escape newlines as `\n` at `bash-audit-log.sh:59`, L4 test cleanups.

## Verdicts on the residuals the log lists for the reviewer

- `passes` blocks a doc-only turn until the message says "not verified": confirmed (case g above). Keep the word; it is in item 3's list. Add word boundaries (M1) so "bypasses" and "surpasses" stop matching; "passes" as a verb still trips it, which is the accepted cost of Samyak's list.
- Tamper scan's literal clause on `return 42` plus `assert f() == 42` in one commit: keep, by design. It is Research B verbatim, and the two-commit rule in `seed/AGENTS.md.jinja:32` makes the clause fire only when the rule is broken: a test-only commit has no non-test returns (`test-tamper-scan.sh:84`), and an implementation-only commit has no test files and exits at line 79.
- Sealed and generated families match segment names anywhere in a path: confirmed (`docs/build/index.md` denied). Acceptable for a deny-on-patch policy; Codex can still edit through Bash. Note it in the rendered CLAUDE.md if a project keeps a `docs/build/` tree.
- One audit line per command, multi-line commands stay multi-line: confirmed and worse than the log implies. A worker counted 509 well-formed entries spanning 1,525 lines in the live log, so about two thirds of the lines are command fragments. Replace embedded newlines with the two characters `\n` when writing the line (L2). Not required for merge.
- Hygiene reports a backticked command that is not installed on the box: confirmed by design; the run against Loam's root was silent.
- `cr-filter-git` skips mutants in a filename with a space: upstream, not checked.
- `FORBIDDEN_RENDERED_PATHS` entry `post-compact-recovery.sh` names an old hook: confirmed unrelated to `post-compact-reinject.sh`; leave it.

## Verdicts on the two Codex findings the lead rejected

- Narrowing the claim trigger by dropping `passes`: the lead was right to keep it. Samyak's item 3 lists the word. The correct repair is word boundaries, not removal (M1).
- Relaxing the expected-equals-new-return clause: the lead was right to keep it. The clause plus the failing-test-first rule form one mechanism, checked above. The trivial-literal set at `test-tamper-scan.sh:128` already removes the noisy cases.

## Taste

- The seven new hooks follow the existing shape: bash wrapper, `set -uo pipefail`, one Python block, `exit 0` on anything unparseable. They read like `stop-verify-gate.sh` and `concurrent-checkout-guard.sh`.
- `mutation-gate.sh` is 241 lines for an opt-in gate; the worktree-plus-index overlay is the right call given cosmic-ray mutates in place, and the fixes above add about fifteen lines to it.
- The tests reuse the base class helpers (`run_hook`, `commit_file`, `git`, `_ruffless_path`). Two helpers are duplicated verbatim across classes and one class name doubles the word Test (L4).
- No refactor of adjacent code; the concurrent guard and ruff-after-edit are untouched.

## Applied (2026-09-04, same session, on Samyak's instruction)

All nine fixes landed in `de9e107` on `fix/audit-s4-hooks`, with 13 new tests and the four Low residuals as rows in `docs/findings/FINDINGS.md`.
Two skeptic amendments were adopted as written: the audit log logs `?` when `returnCodeInterpretation` is present, and the `commit -a` case stages with `add -u`, not `add -A`.
One case the tests found: a repo with no index file yet (nothing ever staged), where the index copy now starts empty.

Checks on `de9e107`:

```
uvx pytest -q bin/tests      230 passed, 379 subtests passed in 325.69s
bin/verify-template.sh       verify-template: PASSED
bin/harness-smoke.sh         harness-smoke: PASS
```

Verify line, rerun against the fixed hooks:

- Stop gate cases a to i: unchanged except (h), "The fix is unverified." now exits 0.
- Tamper scan: the unstaged skip decorator now exits 2 under `git add -A && git commit` and under `git commit -a`; the real index stays empty.
- Mutation gate, real cosmic-ray 8.7.0: a brand-new untested `src/extra.py` now exits 2 with 11 survivors on `src/extra.py:2` in 3.3 s, under both `git commit` and `git add -A && git commit`; the checkout and worktree list are unchanged after each run; `test-command = "false"` exits 0 with `NOTE: mutation gate skipped: cosmic-ray baseline (test command does not pass on unmutated code) failed`.

## Next step

Open the pull request for `fix/audit-s4-hooks` (seed behavior changes use a branch and PR), then start session 5 from `main` after the merge.
