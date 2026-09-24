## Ticket

~~~~~~~~~~~~ evidence
Brief:
Give verdict_consistent a fixture test in bin/check, and record in the research notes which borrowed loop mechanisms already landed as factory code so nobody re-implements them.
Where: bin/factory (the dispatch guard only), bin/factory.d/fixtures/, bin/check, docs/research/loop-repos.md
Done means: bin/check proves an inconsistent grader JSON is refuted and a consistent one is not, and loop-repos.md says where each of four borrowed mechanisms landed.
Out of scope: any change to what verdict_consistent accepts; the trigram stuck detector; the graders.
Track: B    Risk: medium    Mode: build    Open question: none
Blocked by: #56 (merged as PR #57); PR #59 (verdict_consistent on jq 1.7) merged 2026-09-09 as e0a24a7, so the runner's jq is covered

## Goal and why
`docs/research/loop-repos.md` lists mechanisms to steal from the loop repos, and most of them have since landed as code without the note saying so.
`verdict_consistent` landed in F1 (`bin/factory`, the function above `call_json`) with no test that it refutes what it should; PR #59 found it refuting every verdict on the runner's jq 1.7, which a fixture would have caught.
This ticket adds that fixture test and closes the record on four mechanisms, so the subtraction method has a keep-or-cut line for the gate.

## Do not touch
The standing list. Except: bin/factory (a three-line dispatch guard only, nothing inside any function), bin/factory.d/fixtures/grader-inconsistent.json, bin/factory.d/fixtures/grader-consistent.json, bin/check (one new step), docs/research/loop-repos.md.
Also: the graders and every grader file; evals/.

## Out of scope
- changing what `verdict_consistent` accepts or rejects
- the loop-engineering trigram `errorSignature` comparison; the `stuck` exit already stops on the same failing set twice
- a lazy-load routing table; the worker prompt already receives only the ticket, the failing lines, and the findings
- any per-role model resolution beyond the roles block

## Approach
Executor: `bin/factory run` as merged in F1.

Pinned before writing: `verdict_consistent` exists on `main` at `bin/factory` (`grep -n 'verdict_consistent()' bin/factory` prints one line), and `bin/factory eval` replays `evals/<grader>/` cases through a live grader call, so it is not the entry point for one JSON file. The entry point this ticket adds is a source guard.

Change:
1. `bin/factory`, directly above the final `case "$CMD" in` dispatch: `[ "${FACTORY_SOURCED:-}" = 1 ] && return 0 2> /dev/null` so a test can load the functions with `FACTORY_SOURCED=1 . bin/factory` and call `verdict_consistent` without running a subcommand. Nothing else in the file changes.
2. Two fixtures: `bin/factory.d/fixtures/grader-inconsistent.json`, the judge object `{"verdict":"pass","rows":{},"fixes":["one fix"],"backlog":[]}` (a pass that ships a fix); `bin/factory.d/fixtures/grader-consistent.json`, the same object with `"verdict":"fail"`. Judge schema field names only (`schema_for` in `bin/factory`); the judge has no findings array.
3. `bin/check`, one step after the factory lint step: capture first, then compare (the checks run under pipefail): `out=$(FACTORY_SOURCED=1 bash -c '. bin/factory; verdict_consistent bin/factory.d/fixtures/grader-inconsistent.json' 2>&1); r=$?`; call `bad` unless `r` is non-zero; then the consistent fixture must return 0. The step is named `factory verdict gate`.
4. `docs/research/loop-repos.md`: one line per item saying where it landed, placed after the line that names the item: the LongHorizon-Harness and loop-engineering items in the intro list under "Borrow three things", and the two super-simple-software-factory bullets in its Steal list. Exact text, so the done check can find it: LongHorizon-Harness per-role model resolution "landed as the roles block"; loop-engineering `errorSignature` stuck detection "landed as the stuck exit"; super-simple-software-factory `verdict_consistent` "landed as verdict_consistent in F1"; its lazy-load routing table "landed as the prefix cut of 2026-09-09". Pattern: the correction lines already in that file under super-simple-software-factory.

Ledger line for the manager: `grep -c 'is inconsistent' <run>/factory.log` per ticket. If it stays zero over three tickets, cut the gate.

## Done checks
```done-checks
grep -q 'FACTORY_SOURCED' bin/factory && pass source-guard || fail source-guard "bin/factory has no FACTORY_SOURCED guard"
test -f bin/factory.d/fixtures/grader-inconsistent.json && test -f bin/factory.d/fixtures/grader-consistent.json && pass fixtures || fail fixtures "a grader fixture is missing"
out=$(FACTORY_SOURCED=1 bash -c '. bin/factory; verdict_consistent bin/factory.d/fixtures/grader-inconsistent.json' 2>&1); r=$?; [ "$r" -ne 0 ] && [ -z "$out" ] && pass refutes || fail refutes "inconsistent fixture not refuted, or an error was printed: $out"
out=$(FACTORY_SOURCED=1 bash -c '. bin/factory; verdict_consistent bin/factory.d/fixtures/grader-consistent.json' 2>&1); r=$?; [ "$r" -eq 0 ] && pass accepts || fail accepts "consistent fixture refuted: $out"
grep -q 'factory verdict gate' bin/check && pass wired-into-check || fail wired-into-check "bin/check has no verdict gate step"
n=$(grep -c 'landed as the roles block\|landed as the stuck exit\|landed as verdict_consistent in F1\|landed as the prefix cut of 2026-09-09' docs/research/loop-repos.md); [ "$n" -eq 4 ] && pass record || fail record "expected four landed lines in loop-repos.md, found $n"
guard bash -n bin/factory bin/check && pass syntax || fail syntax "bash -n"
[ -n "${LOAM_HOOK:-}" ] && pass check-green || { guard bin/check >/dev/null && pass check-green || fail check-green "bin/check"; }
```

## Merge checklist
- after three tickets have run under this gate, read `grep -c 'is inconsistent'` over their factory.log files and decide keep or cut

## Worker
worker: claude
codex-review: no
effort: xhigh
goal: the Done checks block, sourced after bin/factory.d/lib.sh and run from the worktree root with its output shown, prints no FAIL line and one PASS line per named check, or stop after 40 turns

## Decisions
docs/factory/LOOP.md (Grader-round cap and precedence), docs/research/loop-repos.md, the 2026-09-09 brainstorm plan `~/.claude/plans/i-want-to-take-cached-peach.md`

~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS source-guard
PASS fixtures
PASS refutes
PASS accepts
PASS wired-into-check
PASS record
PASS syntax
PASS check-green

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
# Ticket #64 worker decisions

- Guard placement: put the source guard directly above the final `case "$CMD" in` line in `bin/factory` (literal reading of the Approach). The `CMD=`/`shift` lines above it run on source but are silent. Sourcing is silent: all top-level code before the dispatch is variable assignments and `set -uo pipefail`, no `-e`, no stdout/stderr.
- Probe before writing: on the current tree the refute command prints the usage text and exits rc=2 (a false positive: non-zero for the wrong reason). So the check must also require empty output, not just a non-zero exit.
- `bin/check` step mirrors the done-check: refute branch is `[ "$r" -ne 0 ] && [ -z "$out" ]`, not `r -ne 0` alone. A broken guard (rc=2 + usage text) is then not counted as a refutation. Still one new step named `factory verdict gate`.
- loop-repos.md: exactly four new physical lines, one per phrase, since `grep -c` counts lines and the file has no "landed as" today. The stuck-exit line records that the `errorSignature()` trigram comparison itself was not ported (ticket Out of scope); the stuck exit stops on the same failing set twice.
- Commit attribution: the session system-reminder mandates the `Co-Authored-By: Claude Opus 4.8 (1M context) <noreply@anthropic.com>` trailer and says it "replaces any earlier attribution guidance", and every recent factory commit (e.g. 26a8517) carries it. Repo convention plus the explicit session reminder win over the global CLAUDE.md "never co-author" default, which is written for hand-authored commits, not this loop. Trailer added.

## Post-write verification
- Advisor consulted before writing and again at done; acted on: the refute half of the `bin/check` step requires empty output (not just non-zero exit); the stuck-exit line records that the trigram comparison itself was not ported.
- Negative controls: the new `bin/check` step's `bad` fires (two FAIL lines, FAIL=1) for a broken guard (FACTORY_SOURCED unset -> usage text, rc=2) and for swapped fixtures (consistent object in the refute slot). The gate is not vacuous.
- "prefix cut of 2026-09-09" verified against docs/factory/LOOP.md:97: --strict-mcp-config and --disable-slash-commands drop the MCP schemas and skills listing, cutting the grader prefix from 27k to 9.9k tokens. The loop-repos.md line matches the source; no trim needed. (~/.claude/plans/i-want-to-take-cached-peach.md is not present in this worktree.)
- Done-checks block, sourced after bin/factory.d/lib.sh from the worktree root: 8 PASS, 0 FAIL (check-green ran the full bin/check).

~~~~~~~~~~~~ evidence

## Diff (ccb39b90...HEAD)

~~~~~~~~~~~~ evidence
 bin/check                                       | 9 +++++++++
 bin/factory                                     | 4 ++++
 bin/factory.d/fixtures/grader-consistent.json   | 1 +
 bin/factory.d/fixtures/grader-inconsistent.json | 1 +
 docs/research/loop-repos.md                     | 4 ++++
 5 files changed, 19 insertions(+)

diff --git a/bin/check b/bin/check
index b33b231..14aae2f 100755
--- a/bin/check
+++ b/bin/check
@@ -77,5 +77,14 @@ reject_out=$(bin/factory lint bin/factory.d/fixtures/S5.before.md 2>&1); reject_
 { [ "$reject_rc" -eq 1 ] && grep -q "'skip'" <<<"$reject_out"; } \
   || bad "bin/factory lint did not reject S5.before.md on 'skip' (exit $reject_rc)"

+step "factory verdict gate"
+# verdict_consistent must refute a pass that ships a fix, and accept the same object as a fail (#64).
+# Capture first (these checks run under pipefail), then compare. The refute half also requires empty
+# output: a broken guard exits non-zero with usage text, and that must not count as a refutation.
+out=$(FACTORY_SOURCED=1 bash -c '. bin/factory; verdict_consistent bin/factory.d/fixtures/grader-inconsistent.json' 2>&1); r=$?
+{ [ "$r" -ne 0 ] && [ -z "$out" ]; } || bad "verdict_consistent did not refute the inconsistent grader fixture (exit $r): $out"
+out=$(FACTORY_SOURCED=1 bash -c '. bin/factory; verdict_consistent bin/factory.d/fixtures/grader-consistent.json' 2>&1); r=$?
+[ "$r" -eq 0 ] || bad "verdict_consistent refuted the consistent grader fixture (exit $r): $out"
+
 if [ "$FAIL" -ne 0 ]; then echo; echo "check: FAILED"; exit 1; fi
 echo; echo "check: PASSED"
diff --git a/bin/factory b/bin/factory
index afee148..281f349 100755
--- a/bin/factory
+++ b/bin/factory
@@ -1012,6 +1012,10 @@ usage() { # [cmd...] - one line per named command, all five when none is named

 CMD="${1:-}"
 shift 2> /dev/null || true
+# `FACTORY_SOURCED=1 . bin/factory` loads the functions for a test (bin/check's verdict gate) without
+# running a subcommand. `return` works only in a sourced script; 2> /dev/null hides the error if the
+# guard is ever hit while the file runs as a program.
+[ "${FACTORY_SOURCED:-}" = 1 ] && return 0 2> /dev/null
 case "$CMD" in
   lint) [ $# -eq 1 ] || usage lint
         lint "$1" ;;
diff --git a/bin/factory.d/fixtures/grader-consistent.json b/bin/factory.d/fixtures/grader-consistent.json
new file mode 100644
index 0000000..962ef0c
--- /dev/null
+++ b/bin/factory.d/fixtures/grader-consistent.json
@@ -0,0 +1 @@
+{"verdict":"fail","rows":{},"fixes":["one fix"],"backlog":[]}
diff --git a/bin/factory.d/fixtures/grader-inconsistent.json b/bin/factory.d/fixtures/grader-inconsistent.json
new file mode 100644
index 0000000..32e67c5
--- /dev/null
+++ b/bin/factory.d/fixtures/grader-inconsistent.json
@@ -0,0 +1 @@
+{"verdict":"pass","rows":{},"fixes":["one fix"],"backlog":[]}
diff --git a/docs/research/loop-repos.md b/docs/research/loop-repos.md
index be17c79..95bc3a1 100644
--- a/docs/research/loop-repos.md
+++ b/docs/research/loop-repos.md
@@ -21,7 +21,9 @@ LongHorizon-Harness is the closest technical fit but sets `bypassPermissions` fo
 The supervisor to write instead is small: a bash `while` loop per ticket that runs `claude -p` with `--model` and `--effort` for the worker, runs the ticket's done checks as real commands and reads their exit codes, then invokes a second fresh-context `claude -p` as the Fable 5.1 judge, appending one JSON line per round to a per-ticket run directory.
 Borrow three things.
 Per-role model, agent, and effort resolution from LongHorizon-Harness's `_resolve_role_model` in `cli.py`.
+Correction, 2026-09-10: this landed as the roles block in `bin/factory` (WORKER_MODEL, GRADER_MODEL, WORKER_ADVISOR, and their efforts; see docs/factory/ARCHITECTURE.md, Models and roles).
 The ledger circuit breaker from loop-engineering's `tools/loop-context/src/context-manager.ts`, including its normalized `errorSignature()` trigram comparison to detect a stuck loop.
+Correction, 2026-09-10: the `errorSignature()` trigram comparison itself was not ported; the stuck detection landed as the stuck exit, which stops when the same failing check set repeats twice.
 The lock-guarded daily spend ledger from loop-engineering's `daily-spend.ts`, which gives the dollar cap that none of the runnable candidates provide.
 That is perhaps two hundred lines of shell and one small state file.

@@ -226,10 +228,12 @@ A parse failure re-prompts the same session with context intact rather than rest
 Steal:
 - The four-line brief and the intent-versus-precision rule, which is the highest-value item across all nine repos for our missing brief stage.
 - `verdict_consistent`, because nothing currently polices our two judges for self-contradiction.
+  - Correction, 2026-09-10: this landed as verdict_consistent in F1 (`bin/factory`, the function above `call_json`); #64 adds its fixture gate to `bin/check`.
 - "A known command is code, not an agent", because our loop likely spends model turns on work that is already a shell script.
 - Verbatim unparsed failure output as the fixer's spec, with no summarizing layer between the error and the fix.
 - Phases defaulting to fail plus one call that decides exit code, status, and banner together, which kills the green-banner-over-red-suite bug.
 - The lazy-load routing table and its argument that volunteered state is guessed state, spent before you know the task.
+  - Correction, 2026-09-10: this landed as the prefix cut of 2026-09-09, where the grader call drops the MCP schemas and skills listing so its prompt prefix is 9.9k tokens instead of 27k (`bin/factory`, the `call_json` comment), and the worker prompt already carries only the ticket, the failing lines, and the findings.

 Reject:
 - The Vue visualizer, roughly 120KB of frontend for a dashboard we do not need.
~~~~~~~~~~~~ evidence
