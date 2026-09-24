## Ticket

~~~~~~~~~~~~ evidence
Brief:
Add the small factory support NAV-01 needs before any arm runs: an arm-C prompt file the loop appends only when the launch's arm is C, an arm read from FACTORY_NAV_ARM or popped from the pre-registered order file nav-order at the runs root, a nav_arm field on every ledger line, and a stdlib metrics script that reads a run directory and prints the eight protocol metrics.
Where: bin/factory (nav_c_append added and called in build_worker_prompt, nav_arm_resolve added and called in cmd_run, nav_arm added in record), bin/factory.d/_nav_c.md (new), bin/factory.d/nav01-metrics.py (new).
Done means: the done-checks block prints no FAIL line: the arm-C file lands in the assembled worker prompt only when the arm is C, a launch with FACTORY_NAV_ARM unset pops its arm from nav-order, a ledger line carries nav_arm, and nav01-metrics.py prints a row with the eight metrics for a run directory.
Out of scope: installing Semble or the language-server plugin on the runner; running any arm; editing _common.md; the results file docs/research/nav-01-results.md; NAV-01 itself.
Blocked by: #165 (MEM-05).

## Goal and why
NAV-01 is pre-registered and frozen; it needs three pieces in the factory before the first ticket runs, so no one hand-edits the frozen _common.md between launches and a missed revert cannot contaminate a baseline.
The pieces are the arm-C append, the arm source (FACTORY_NAV_ARM in the environment, else the first line popped from the runs-root file nav-order, so the ten-minute timer launches labeled runs in the pre-registered order and nobody pauses it or launches by hand), the nav_arm ledger field that labels each run's arm, and nav01-metrics.py, which computes every metric the protocol reads from files the factory already writes.
Decision: docs/research/memory-design-v2-2026-09-21.md (layer 2, tracked and present in your worktree). The frozen protocol is docs/plans/2026-09-21-memory-v2/nav-01-protocol.md, but docs/plans is gitignored (.gitignore), so that file is not committed and is absent from the worktree this ticket runs in; its Arms and Metrics are restated in full under Approach below, which is the authoritative copy for this ticket.

## Do not touch
The standing list. Also: bin/factory.d/_common.md, bin/factory.d/lib.sh, the grader prompts and schemas, seed/. The protocol docs/plans/2026-09-21-memory-v2/nav-01-protocol.md is gitignored and absent from the worktree, so you cannot open or edit it here and no diff can touch it; treat the Approach as its frozen restatement.
Except: bin/factory (only nav_c_append and its one call in build_worker_prompt, nav_arm_resolve and its one call in cmd_run, and the nav_arm field in record), bin/factory.d/_nav_c.md (created), bin/factory.d/nav01-metrics.py (created). No path this ticket touches is pinned by seed/.loam/runtime/assets/curated-catalog.json, so no re-pin is needed.

## Out of scope
Any runner install (uv tool install semble, the language-server plugin or its binaries).
Running an arm, or writing docs/research/nav-01-results.md.
Editing bin/factory.d/_common.md or any grader prompt.
Any change to how a round is graded, scored, or exited.

## Approach
Read bin/factory whole first, then bin/factory.d/lib.sh and docs/factory/CONTRACT.md. The frozen protocol lives under the gitignored docs/plans and is not in your worktree; its Arms and Metrics are restated in this Approach, so build from the steps below and from the in-tree docs/research/memory-design-v2-2026-09-21.md (layer 2), not from a file you cannot open. Same conventions as the rest of bin/factory: bash, set -uo pipefail already set at the top, JSON through jq, no new dependency. The metrics script is python3 stdlib only.
1. bin/factory.d/_nav_c.md (new): one paragraph, no front matter. It tells the worker that for any "where is" question it runs `semble search "<query>" . --top-k 8 --content all --format json` first and opens only the files that command returns (the flags are the Semble README's: `--top-k`, not `-k`; `--content all` includes markdown and JSON, which the default `code` excludes). This is the arm-C instruction from the protocol; nobody hand-edits the frozen _common.md.
2. bin/factory: add a small function beside build_worker_prompt, `nav_c_append() { [ "${FACTORY_NAV_ARM:-}" = C ] && cat "$ROOT/bin/factory.d/_nav_c.md" >> "$1"; return 0; }`. Call it as `nav_c_append "$pf"` inside build_worker_prompt on the line right after the one that writes "$BODY" and the frozen _common.md into "$pf" (the `{ printf '%s\n\n' "$BODY"; cat "$RUN/frozen/_common.md"; } > "$pf"` line). It reads the immutable source file through $ROOT, so no freeze copy is needed; base and arm B append nothing. This is the smallest correct change to prompt assembly: the append is one seam, testable on its own and invoked by the assembler.
3. bin/factory: add `nav_arm_resolve() { [ -n "${FACTORY_NAV_ARM+x}" ] && return 0; local f="$RUNS_ROOT/nav-order" a; [ -s "$f" ] || return 0; a=$(head -n 1 "$f"); [ -n "$a" ] || return 0; export FACTORY_NAV_ARM="$a"; tail -n +2 "$f" > "$f.tmp" && mv "$f.tmp" "$f"; return 0; }` beside nav_c_append, and call it as `nav_arm_resolve` in cmd_run on the line right after `date -u +%s > "$RUN/launched"` and before the stop_requested line. Semantics: an environment FACTORY_NAV_ARM (even empty) wins and nothing is popped; otherwise the first line of $RUNS_ROOT/nav-order (one arm per line, no blank lines, written by the NAV-01 session before the first launch) becomes the arm and is removed from the file; no file or an empty file means base. It runs once per launch: exec_frozen re-execs the frozen copy with the environment, so the exported value stops a second pop. It runs before freeze and before round 0, so the whole run, graders included, carries one arm.
4. bin/factory: in `record` (the one function that writes every worker and grader ledger line), add a `nav_arm` field to the JSON object it builds, valued `${FACTORY_NAV_ARM:-base}`. Add `--arg nav "${FACTORY_NAV_ARM:-base}"` to both jq invocations (the primary and the fallback) and `nav_arm:$nav` to both objects, next to `ts`. This is the smallest correct change: record is the single writer of the round lines, so one edit labels the worker line and every grader line; the two freeze `event` lines are metadata and keep their shape.
5. bin/factory.d/nav01-metrics.py (new, python3 stdlib, executable): argparse with positional run directories, `--runs-root` and `--issues` (a comma list that expands to `<runs-root>/<issue>/*/` directories holding a `status` file), and `--json`. For each run directory print one row with the protocol's eight metrics, reading only files the factory writes:
   - rounds to pr-opened: the highest N among round-N.checks (or the worker ledger lines' round) when `status` reads `pr-opened`, else n/a.
   - worker turns in round 1: the count of `type == "assistant"` lines in round-1.jsonl.
   - worker tokens in round 1: `usage.input_tokens + usage.output_tokens` from the round-1 worker ledger line (fall back to the round-1.jsonl result event's usage).
   - worker cost per ticket: the sum of `cost_usd` over ledger lines with role worker.
   - turns to first correct file: walk the assistant messages of round-1.jsonl in order; for each, take the file_path of a Read/Edit/Write/NotebookEdit tool_use and the path-like tokens of a Bash command, and return the 1-based index of the first assistant message whose candidate path matches a path in the final saved diff; n/a when none. The final diff is the highest-numbered round-N.diff the run wrote; its paths come from its `diff --git a/... b/...` lines. Match on equality, a trailing-path suffix, or basename, because a worker's file_path is absolute under the worktree while a diff path is repo-relative.
   - grader outcome: from the last round that has a round-N.judge.json, print the first failing grader and the judge score. First failing is judge when its verdict is not pass, else reviewer when round-N.review.json has a high or medium finding, else codex-review when round-N.codex-review.json has a critical or high finding, else none. The judge score is the count of `rows` values equal to "pass" over the number of rows.
   - honesty: for arm C, the count of Bash tool_use calls in round-1.jsonl whose command contains `semble search`; for arm B, the count of tool_use calls whose name equals `LSP` compared case-insensitively (equality, never a substring match: a substring match would also count unrelated tools such as skillspector); printed as a tool-use count. For the base arm print `-`.
   - setup cost: the round-1 worker ledger line's duration in whole seconds (its `duration_ms`), the wall time of the first round; the token half of setup is the round-1 token count above.
   The arm of a run is the `nav_arm` of its first worker ledger line, or base when the field is absent (older runs). The JSON output keys are exactly rounds, turns_r1, tokens_r1, cost_usd, first_file_turn, grader, honesty, setup, and arm, so the done-check reads them by name. Output is a markdown table by default and a JSON array under `--json`. The script names no model of its own; it reads model and arm from the ledger.

## Done checks
```done-checks
[ -x bin/factory.d/nav01-metrics.py ] && [ -f bin/factory.d/_nav_c.md ] && grep -qi 'semble search' bin/factory.d/_nav_c.md && pass files-present || fail files-present "nav01-metrics.py missing or not executable, or _nav_c.md missing its semble line"
t=$(mktemp -d); sig=$(head -1 bin/factory.d/_nav_c.md 2>/dev/null); FACTORY_SOURCED=1 FACTORY_ROOT="$PWD" T="$t" bash -c '. bin/factory; : > "$T/p"; FACTORY_NAV_ARM=C nav_c_append "$T/p"; : > "$T/q"; nav_c_append "$T/q"' 2>/dev/null; grep -qF "$sig" "$t/p" && ! grep -qF "$sig" "$t/q" && sed -n '/^build_worker_prompt() {/,/^}/p' bin/factory | grep -q 'nav_c_append' && pass nav-prompt || fail nav-prompt "arm-C text did not land, leaked into the base prompt, or build_worker_prompt does not call nav_c_append"
t=$(mktemp -d); res="$t/res.json"; printf '{"total_cost_usd":0.5,"duration_ms":1000,"num_turns":5,"permission_denials":[],"subtype":"success","usage":{"input_tokens":10,"output_tokens":20}}\n' > "$res"; FACTORY_SOURCED=1 FACTORY_ROOT="$PWD" T="$t" R="$res" bash -c '. bin/factory; LOG=/dev/null; LEDGER="$T/ledger.jsonl"; DAILY="$T/daily.jsonl"; KEY=navtest; FACTORY_NAV_ARM=C record 1 worker "claude-opus-4-8[1m]" "$R"; record 2 judge fable "$R"' 2>/dev/null; w=$(jq -r 'select(.role=="worker").nav_arm' "$t/ledger.jsonl" 2>/dev/null); b=$(jq -r 'select(.role=="judge").nav_arm' "$t/ledger.jsonl" 2>/dev/null); [ "$w" = C ] && [ "$b" = base ] && pass ledger-nav-arm || fail ledger-nav-arm "worker nav_arm='$w' (want C), judge nav_arm='$b' (want base)"
t=$(mktemp -d); f="$t/123/abc12345"; mkdir -p "$f"; printf 'pr-opened\n' > "$f/status"; printf '{"role":"worker","round":1,"nav_arm":"C","cost_usd":9.5,"duration_ms":120000,"usage":{"input_tokens":100,"output_tokens":200}}\n{"role":"judge","round":1,"nav_arm":"C","cost_usd":1.0}\n' > "$f/ledger.jsonl"; printf '{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Bash","input":{"command":"semble search \\"where is x\\" . -k 8 --format json"}}]}}\n{"type":"assistant","message":{"content":[{"type":"tool_use","name":"Read","input":{"file_path":"/tmp/wt/seed/bin/foo.sh"}}]}}\n{"type":"result","subtype":"success","usage":{"input_tokens":100,"output_tokens":200}}\n' > "$f/round-1.jsonl"; printf 'diff --git a/seed/bin/foo.sh b/seed/bin/foo.sh\n' > "$f/round-1.diff"; printf 'PASS x\n' > "$f/round-1.checks"; printf '{"verdict":"pass","rows":{"correct":"pass","verified":"pass","honest":"pass"}}\n' > "$f/round-1.judge.json"; printf '{"verdict":"merge","findings":[]}\n' > "$f/round-1.review.json"; row=$(python3 bin/factory.d/nav01-metrics.py --json "$f" 2>/dev/null); ok=$(printf '%s' "$row" | python3 -c 'import json,sys; r=json.load(sys.stdin)[0]; k=["rounds","turns_r1","tokens_r1","cost_usd","first_file_turn","grader","honesty","setup"]; print("yes" if all(c in r for c in k) and r["arm"]=="C" and r["rounds"]==1 and r["turns_r1"]==2 and r["tokens_r1"]==300 and r["cost_usd"]==9.5 and r["first_file_turn"]==2 and str(r["honesty"])=="1" else "no")' 2>/dev/null); [ "$ok" = yes ] && python3 bin/factory.d/nav01-metrics.py "$f" 2>/dev/null | grep -q '| C |' && pass metrics-row || fail metrics-row "the script did not print a row with the eight metrics and the fixture values for the arm-C fixture"
t=$(mktemp -d); printf 'C\nbase\n' > "$t/nav-order"; FACTORY_SOURCED=1 FACTORY_ROOT="$PWD" T="$t" bash -c '. bin/factory; RUNS_ROOT="$T"; unset FACTORY_NAV_ARM; nav_arm_resolve; printf "%s\n" "${FACTORY_NAV_ARM:-unset}" > "$T/got"; nav_arm_resolve; printf "%s\n" "${FACTORY_NAV_ARM:-unset}" >> "$T/got"; unset FACTORY_NAV_ARM; nav_arm_resolve; printf "%s\n" "${FACTORY_NAV_ARM:-unset}" >> "$T/got"; unset FACTORY_NAV_ARM; nav_arm_resolve; printf "%s\n" "${FACTORY_NAV_ARM:-unset}" >> "$T/got"; FACTORY_NAV_ARM= nav_arm_resolve; printf "%s\n" "$(wc -l < "$T/nav-order" | tr -d " ")" >> "$T/got"' 2>/dev/null; [ "$(tr '\n' ' ' < "$t/got" 2>/dev/null)" = "C C base unset 0 " ] && sed -n '/^cmd_run() {/,/^}/p' bin/factory | grep -q 'nav_arm_resolve' && pass nav-order || fail nav-order "nav_arm_resolve did not pop C then base then nothing from nav-order, an environment value did not win, or cmd_run does not call it"
python3 -m py_compile bin/factory.d/nav01-metrics.py >/dev/null 2>&1 && pass py-compile || fail py-compile "nav01-metrics.py does not compile"
ruff check bin/factory.d/nav01-metrics.py >/dev/null 2>&1 && pass ruff || fail ruff "ruff check nav01-metrics.py"
guard bash -n bin/factory && pass factory-syntax || fail factory-syntax "bash -n bin/factory"
[ -n "${LOAM_HOOK:-}" ] && pass check-green || { guard bin/check >/dev/null && pass check-green || fail check-green "bin/check"; }
```

## Merge checklist
- on the runner after the pull: `bin/runner 'python3 ~/Desktop/loam/bin/factory.d/nav01-metrics.py --runs-root ~/.local/state/loam-factory/runs --issues <an existing issue dir>'` prints one row per run and no traceback, before the first arm launches.

## Worker
worker: claude
codex-review: no
effort: xhigh
MAX_ROUNDS=3
ROUND_BUDGET_USD=15
goal: the done-checks block prints no FAIL line, or stop after 60 turns

## Decisions
docs/research/memory-design-v2-2026-09-21.md (layer 2, tracked). The frozen protocol docs/plans/2026-09-21-memory-v2/nav-01-protocol.md (Arms, Metrics, Immutable to the worker) is gitignored and not in the worktree; its content is restated under Approach.

~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS files-present
PASS nav-prompt
PASS ledger-nav-arm
PASS metrics-row
PASS nav-order
PASS py-compile
PASS ruff
PASS factory-syntax
PASS check-green

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
Read bin/factory whole, bin/factory.d/lib.sh, docs/factory/CONTRACT.md, and confirmed every Where/Do-not-touch/Approach path with git ls-files before editing.
Added nav_c_append and nav_arm_resolve verbatim from the Approach snippets, placed beside build_worker_prompt; nav_c_append is called right after the _common.md write in build_worker_prompt, nav_arm_resolve right after `date -u +%s > "$RUN/launched"` in cmd_run.
record: added `--arg nav "${FACTORY_NAV_ARM:-base}"` and `nav_arm` next to `ts` in both jq objects; primary uses escaped \$nav (double-quoted string), fallback uses $nav (single-quoted), so the primary jq still runs and cost_usd is not zeroed by the fallback.
_nav_c.md: one paragraph, no front matter; first line carries the `semble search "<query>" . --top-k 8 --content all --format json` command (the grep signature) so both files-present and nav-prompt checks match.
nav01-metrics.py: python3 stdlib only, executable; argparse with positional run dirs, --runs-root (default ~/.local/state/loam-factory/runs), --issues (comma list expanding to <runs-root>/<issue>/*/ dirs with a status file), and --json. JSON keys are exactly the nine the done-check reads; markdown table by default. Rehearsed the merge-checklist line over every existing issue dir: no traceback, older runs read arm=base and honesty=-, codex null costs sum to 0.0, and an unparseable judge prints "judge 0/0".

~~~~~~~~~~~~ evidence

## Diff (78cdd680...HEAD)

~~~~~~~~~~~~ evidence
 bin/factory                    |  21 ++++++++--
 bin/factory.d/_nav_c.md        |   4 ++
 bin/factory.d/nav01-metrics.py | 371 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 3 files changed, 392 insertions(+), 4 deletions(-)

diff --git a/bin/factory b/bin/factory
index 872e962e..3ac35dac 100755
--- a/bin/factory
+++ b/bin/factory
@@ -561,16 +561,16 @@ record() { # round role model result.json [advisor_calls] [advisor_usd] [workflo
   # not bound Codex, #41) and `usage` carries its verbatim token counters; ticket_spent, daily_spent, and
   # cmd_status all read cost_usd // 0, so null is safe.
   local line acalls="${5:-0}" ausd="${6:-0}" wagents="${7:-0}" wusd="${8:-0}" codex="${9:-0}"
-  line=$(jq -c --argjson round "$1" --arg role "$2" --arg model "$3" --arg ts "$(now)" \
+  line=$(jq -c --argjson round "$1" --arg role "$2" --arg model "$3" --arg ts "$(now)" --arg nav "${FACTORY_NAV_ARM:-base}" \
     --argjson acalls "$acalls" --argjson ausd "$ausd" --argjson wagents "$wagents" --argjson wusd "$wusd" --argjson codex "$codex" \
     "$RESULT_OBJ | {round:\$round, role:\$role, model:\$model, cost_usd:(if \$codex == 1 then null else (.total_cost_usd // 0) end), \
 duration_ms:(.duration_ms // 0), num_turns:(.num_turns // 0), denials:((.permission_denials // []) | length), \
 subtype:(.subtype // \"unknown\"), usage:(.usage // null), advisor_calls:\$acalls, advisor_usd:\$ausd, \
 workflow_agents:\$wagents, workflow_usd:\$wusd, \
-ts:\$ts}" "$4" 2> /dev/null) \
-    || line=$(jq -nc --argjson round "$1" --arg role "$2" --arg model "$3" --arg ts "$(now)" \
+nav_arm:\$nav, ts:\$ts}" "$4" 2> /dev/null) \
+    || line=$(jq -nc --argjson round "$1" --arg role "$2" --arg model "$3" --arg ts "$(now)" --arg nav "${FACTORY_NAV_ARM:-base}" \
       --argjson acalls "$acalls" --argjson ausd "$ausd" --argjson wagents "$wagents" --argjson wusd "$wusd" --argjson codex "$codex" \
-      '{round:$round, role:$role, model:$model, cost_usd:(if $codex == 1 then null else 0 end), duration_ms:0, num_turns:0, denials:0, subtype:"unknown", usage:null, advisor_calls:$acalls, advisor_usd:$ausd, workflow_agents:$wagents, workflow_usd:$wusd, ts:$ts}')
+      '{round:$round, role:$role, model:$model, cost_usd:(if $codex == 1 then null else 0 end), duration_ms:0, num_turns:0, denials:0, subtype:"unknown", usage:null, advisor_calls:$acalls, advisor_usd:$ausd, workflow_agents:$wagents, workflow_usd:$wusd, nav_arm:$nav, ts:$ts}')
   printf '%s\n' "$line" >> "$LEDGER"
   printf '%s' "$line" | jq -c --arg date "$(today)" --arg ticket "$KEY" \
     '{date:$date, ticket:$ticket, role:.role, cost_usd:.cost_usd}' >> "$DAILY"
@@ -738,9 +738,21 @@ workflow_ledger() { # round stream.jsonl result.json -> "<agents> <usd>" on stdo
   printf '%s %s\n' "$agents" "$usd"
 }

+# NAV-01 (docs/research/memory-design-v2-2026-09-21.md): the arm-C worker prompt gets the Semble
+# search instruction appended; base and arm B append nothing. Reads the immutable source through
+# $ROOT, so no freeze copy is needed and nobody hand-edits the frozen _common.md between launches.
+nav_c_append() { [ "${FACTORY_NAV_ARM:-}" = C ] && cat "$ROOT/bin/factory.d/_nav_c.md" >> "$1"; return 0; }
+
+# NAV-01: the arm of a launch. An environment FACTORY_NAV_ARM (even empty) wins and nothing is popped;
+# otherwise the first line of $RUNS_ROOT/nav-order becomes the arm and is removed, so the timer launches
+# the pre-registered order. No file, an empty file, or a blank first line means base. Runs once per
+# launch: exec_frozen re-execs with the exported value, which stops a second pop.
+nav_arm_resolve() { [ -n "${FACTORY_NAV_ARM+x}" ] && return 0; local f="$RUNS_ROOT/nav-order" a; [ -s "$f" ] || return 0; a=$(head -n 1 "$f"); [ -n "$a" ] || return 0; export FACTORY_NAV_ARM="$a"; tail -n +2 "$f" > "$f.tmp" && mv "$f.tmp" "$f"; return 0; }
+
 build_worker_prompt() { # round -> prompt path (pending until the call returns a result); non-zero when a Codex skill will not resolve
   local round="$1" pf="$RUN/pending.prompt.md" prev=$((round - 1)) s sf
   { printf '%s\n\n' "$BODY"; cat "$RUN/frozen/_common.md"; } > "$pf"
+  nav_c_append "$pf"   # arm C appends the Semble instruction; base and arm B append nothing (NAV-01)
   # Skills per role (LOOP.md): a Claude worker gets one Skill-tool sentence per `skills:` name (never a
   # slash command, which would swallow the body, #37/#40); a Codex worker has no Skill tool and swallows
   # an unknown `/<skill>` line (#41), so it gets each named skill's body pasted (skill_file resolves it).
@@ -1227,6 +1239,7 @@ cmd_run() {
   WORKTREE="${FACTORY_WORKTREE:-$MAIN_CHECKOUT-$(printf '%s' "$KEY" | tr '[:upper:]' '[:lower:]')}"
   [ -f "$RUN/started" ] || date -u +%s > "$RUN/started"
   date -u +%s > "$RUN/launched"
+  nav_arm_resolve   # NAV-01: fix this launch's arm before freeze and round 0, so the whole run carries one arm
   stop_requested && finish stopped "FACTORY_STOP is present at launch"
   assert_parallel
   prepare_worktree
diff --git a/bin/factory.d/_nav_c.md b/bin/factory.d/_nav_c.md
new file mode 100644
index 00000000..6b33c07e
--- /dev/null
+++ b/bin/factory.d/_nav_c.md
@@ -0,0 +1,4 @@
+For any "where is" or "where does" question about this repository, before you open, grep, or guess at any file, first run `semble search "<query>" . --top-k 8 --content all --format json` and open only the files that command returns.
+Semble is a semantic code-search tool; put your question in plain words as `<query>` and pass `.` as the repository root.
+Use `--top-k 8`, not `-k`, to ask for the eight best matches, and `--content all` so the results include markdown and JSON files, which the default `--content code` leaves out.
+Let the search point you at the files, then read them; do not fall back to a blind path search first.
diff --git a/bin/factory.d/nav01-metrics.py b/bin/factory.d/nav01-metrics.py
new file mode 100755
index 00000000..ca8535a2
--- /dev/null
+++ b/bin/factory.d/nav01-metrics.py
@@ -0,0 +1,371 @@
+#!/usr/bin/env python3
+"""NAV-01 metrics (docs/research/memory-design-v2-2026-09-21.md).
+
+Reads one or more factory run directories and prints the eight protocol metrics
+per run, from files the factory already writes. python3 stdlib only; names no
+model of its own - it reads model and arm from the ledger.
+
+Usage:
+  nav01-metrics.py [RUN_DIR ...] [--runs-root DIR --issues a,b,c] [--json]
+
+A run directory is <runs-root>/<issue>/<sha>/, holding a `status` file, a
+`ledger.jsonl`, and per-round `round-N.jsonl` / `round-N.checks` /
+`round-N.diff` / `round-N.*.json`. The arm of a run is the `nav_arm` of its
+first worker ledger line, or `base` when that field is absent (older runs).
+"""
+from __future__ import annotations
+
+import argparse
+import json
+import os
+import sys
+
+# The JSON output keys, in column order; the done-check reads them by name.
+COLUMNS = ["rounds", "turns_r1", "tokens_r1", "cost_usd", "first_file_turn", "grader", "honesty", "setup", "arm"]
+NA = "n/a"
+FILE_TOOLS = {"Read", "Edit", "Write", "NotebookEdit"}
+DEFAULT_RUNS_ROOT = os.path.expanduser("~/.local/state/loam-factory/runs")
+
+
+# ---- readers ----------------------------------------------------------------
+
+def read_jsonl(path):
+    """The parsed dict objects of a JSONL file; unparseable lines skipped, [] when absent."""
+    out = []
+    try:
+        with open(path, encoding="utf-8", errors="replace") as fh:
+            for line in fh:
+                line = line.strip()
+                if not line:
+                    continue
+                try:
+                    obj = json.loads(line)
+                except json.JSONDecodeError:
+                    continue
+                if isinstance(obj, dict):
+                    out.append(obj)
+    except OSError:
+        pass
+    return out
+
+
+def read_json(path):
+    """Parse one JSON object from a file; None when absent or unparseable."""
+    try:
+        with open(path, encoding="utf-8", errors="replace") as fh:
+            obj = json.load(fh)
+    except (OSError, json.JSONDecodeError):
+        return None
+    return obj if isinstance(obj, dict) else None
+
+
+def read_status(run):
+    try:
+        with open(os.path.join(run, "status"), encoding="utf-8", errors="replace") as fh:
+            return fh.read().strip()
+    except OSError:
+        return ""
+
+
+def round_numbers(run, suffix):
+    """The N>=1 of every round-N<suffix> file under run, ascending (round-0 excluded)."""
+    ns = []
+    try:
+        names = os.listdir(run)
+    except OSError:
+        return ns
+    for name in names:
+        if name.startswith("round-") and name.endswith(suffix):
+            middle = name[len("round-"):-len(suffix)]
+            if middle.isdigit() and int(middle) >= 1:
+                ns.append(int(middle))
+    return sorted(ns)
+
+
+def tool_uses(events):
+    """Yield (name, input_dict) for every tool_use block across the events."""
+    for event in events:
+        msg = event.get("message")
+        content = msg.get("content") if isinstance(msg, dict) else None
+        if not isinstance(content, list):
+            continue
+        for block in content:
+            if isinstance(block, dict) and block.get("type") == "tool_use":
+                inp = block.get("input")
+                yield block.get("name"), inp if isinstance(inp, dict) else {}
+
+
+def worker_line(lines, round_n):
+    for obj in lines:
+        if obj.get("role") == "worker" and obj.get("round") == round_n:
+            return obj
+    return None
+
+
+def arm_of(lines):
+    for obj in lines:
+        if obj.get("role") == "worker":
+            nav = obj.get("nav_arm")
+            return nav if isinstance(nav, str) and nav else "base"
+    return "base"
+
+
+# ---- the eight metrics ------------------------------------------------------
+
+def metric_rounds(run, lines):
+    if read_status(run) != "pr-opened":
+        return NA
+    ns = round_numbers(run, ".checks")
+    if ns:
+        return max(ns)
+    rounds = [o.get("round") for o in lines if o.get("role") == "worker" and isinstance(o.get("round"), int)]
+    return max(rounds) if rounds else NA
+
+
+def metric_turns_r1(events):
+    return sum(1 for e in events if e.get("type") == "assistant")
+
+
+def _usage_tokens(usage):
+    if not isinstance(usage, dict):
+        return None
+    try:
+        return int(usage.get("input_tokens", 0) or 0) + int(usage.get("output_tokens", 0) or 0)
+    except (TypeError, ValueError):
+        return None
+
+
+def metric_tokens_r1(lines, events):
+    worker = worker_line(lines, 1)
+    tokens = _usage_tokens(worker.get("usage")) if worker else None
+    if tokens is None:
+        for e in events:
+            if e.get("type") == "result":
+                tokens = _usage_tokens(e.get("usage"))
+                break
+    return tokens if tokens is not None else NA
+
+
+def metric_cost(lines):
+    total = 0.0
+    seen = False
+    for obj in lines:
+        if obj.get("role") != "worker":
+            continue
+        seen = True
+        cost = obj.get("cost_usd")
+        if isinstance(cost, (int, float)):
+            total += cost
+    return total if seen else NA
+
+
+def diff_paths(run):
+    """Repo-relative paths of the highest-numbered round-N.diff's `diff --git a/.. b/..` lines."""
+    ns = round_numbers(run, ".diff")
+    if not ns:
+        return []
+    seen, out = set(), []
+    try:
+        with open(os.path.join(run, f"round-{max(ns)}.diff"), encoding="utf-8", errors="replace") as fh:
+            for line in fh:
+                if not line.startswith("diff --git "):
+                    continue
+                for tok in line.split()[2:]:
+                    path = tok[2:] if tok.startswith(("a/", "b/")) else tok
+                    if path and path not in seen:
+                        seen.add(path)
+                        out.append(path)
+    except OSError:
+        return []
+    return out
+
+
+def bash_path_tokens(command):
+    """Path-like tokens of a shell command: whitespace-split, quotes stripped, keep tokens
+    with a '/' or a filename extension; '.' and '..' dropped."""
+    tokens = []
+    for raw in command.split():
+        tok = raw.strip("'\"`(),;:")
+        if not tok or tok in (".", ".."):
+            continue
+        if "/" in tok:
+            tokens.append(tok)
+            continue
+        root, ext = os.path.splitext(tok)
+        if root and len(ext) > 1:
+            tokens.append(tok)
+    return tokens
+
+
+def path_matches(candidate, dps):
+    """Equality, a trailing-path suffix, or an equal non-empty basename (worker paths are
+    absolute under the worktree; diff paths are repo-relative)."""
+    if not candidate:
+        return False
+    cbase = os.path.basename(candidate.rstrip("/"))
+    for dp in dps:
+        if candidate == dp or candidate.endswith("/" + dp) or dp.endswith("/" + candidate):
+            return True
+        if cbase and cbase == os.path.basename(dp.rstrip("/")):
+            return True
+    return False
+
+
+def metric_first_file_turn(events, dps):
+    if not dps:
+        return NA
+    idx = 0
+    for event in events:
+        if event.get("type") != "assistant":
+            continue
+        idx += 1
+        candidates = []
+        msg = event.get("message")
+        content = msg.get("content") if isinstance(msg, dict) else None
+        for block in content if isinstance(content, list) else []:
+            if not isinstance(block, dict) or block.get("type") != "tool_use":
+                continue
+            inp = block.get("input")
+            inp = inp if isinstance(inp, dict) else {}
+            if block.get("name") in FILE_TOOLS:
+                for key in ("file_path", "notebook_path"):
+                    value = inp.get(key)
+                    if isinstance(value, str) and value:
+                        candidates.append(value)
+            elif block.get("name") == "Bash":
+                cmd = inp.get("command")
+                if isinstance(cmd, str):
+                    candidates.extend(bash_path_tokens(cmd))
+        if any(path_matches(c, dps) for c in candidates):
+            return idx
+    return NA
+
+
+def metric_grader(run):
+    ns = round_numbers(run, ".judge.json")
+    if not ns:
+        return NA
+    n = max(ns)
+    judge = read_json(os.path.join(run, f"round-{n}.judge.json"))
+    if judge is None:
+        return NA
+    rows = judge.get("rows")
+    if isinstance(rows, dict) and rows:
+        score = f"{sum(1 for v in rows.values() if v == 'pass')}/{len(rows)}"
+    else:
+        score = "0/0"
+    if judge.get("verdict") != "pass":
+        first = "judge"
+    elif _has_finding(run, n, "review", ("high", "medium")):
+        first = "reviewer"
+    elif _has_finding(run, n, "codex-review", ("critical", "high")):
+        first = "codex-review"
+    else:
+        first = "none"
+    return f"{first} {score}"
+
+
+def _has_finding(run, n, stem, severities):
+    doc = read_json(os.path.join(run, f"round-{n}.{stem}.json"))
+    if not doc:
+        return False
+    return any(isinstance(f, dict) and f.get("severity") in severities for f in doc.get("findings") or [])
+
+
+def metric_honesty(arm, events):
+    if arm == "C":
+        return sum(1 for name, inp in tool_uses(events)
+                   if name == "Bash" and isinstance(inp.get("command"), str) and "semble search" in inp["command"])
+    if arm == "B":
+        return sum(1 for name, _ in tool_uses(events) if isinstance(name, str) and name.lower() == "lsp")
+    return "-"
+
+
+def metric_setup(lines):
+    worker = worker_line(lines, 1)
+    ms = worker.get("duration_ms") if worker else None
+    return int(ms) // 1000 if isinstance(ms, (int, float)) else NA
+
+
+# ---- assembly and output ----------------------------------------------------
+
+def metrics_for(run):
+    lines = read_jsonl(os.path.join(run, "ledger.jsonl"))
+    events = read_jsonl(os.path.join(run, "round-1.jsonl"))
+    arm = arm_of(lines)
+    dps = diff_paths(run)
+    return {
+        "rounds": metric_rounds(run, lines),
+        "turns_r1": metric_turns_r1(events),
+        "tokens_r1": metric_tokens_r1(lines, events),
+        "cost_usd": metric_cost(lines),
+        "first_file_turn": metric_first_file_turn(events, dps),
+        "grader": metric_grader(run),
+        "honesty": metric_honesty(arm, events),
+        "setup": metric_setup(lines),
+        "arm": arm,
+    }
+
+
+def run_label(run):
+    run = os.path.normpath(run)
+    parent = os.path.basename(os.path.dirname(run))
+    base = os.path.basename(run)
+    return f"{parent}/{base}" if parent else base
+
+
+def cell(value):
+    return f"{round(value, 4)}" if isinstance(value, float) else str(value)
+
+
+def markdown(rows):
+    header = ["run"] + COLUMNS
+    out = ["| " + " | ".join(header) + " |", "| " + " | ".join("---" for _ in header) + " |"]
+    for label, row in rows:
+        out.append("| " + " | ".join([label] + [cell(row[c]) for c in COLUMNS]) + " |")
+    return "\n".join(out)
+
+
+def collect_runs(args):
+    runs = list(args.run_dirs)
+    if args.issues:
+        for issue in args.issues.split(","):
+            issue = issue.strip()
+            if not issue:
+                continue
+            issue_dir = os.path.join(args.runs_root, issue)
+            try:
+                names = sorted(os.listdir(issue_dir))
+            except OSError:
+                print(f"warning: no issue directory {issue_dir}", file=sys.stderr)
+                continue
+            for name in names:
+                run = os.path.join(issue_dir, name)
+                if os.path.isfile(os.path.join(run, "status")):
+                    runs.append(run)
+    return runs
+
+
+def main():
+    ap = argparse.ArgumentParser(description="NAV-01 metrics for factory run directories.")
+    ap.add_argument("run_dirs", nargs="*", metavar="RUN_DIR", help="a run directory <runs-root>/<issue>/<sha>")
+    ap.add_argument("--runs-root", default=DEFAULT_RUNS_ROOT, help="runs root that --issues expands under")
+    ap.add_argument("--issues", help="comma list of issue dirs under --runs-root to expand into run directories")
+    ap.add_argument("--json", action="store_true", help="print a JSON array instead of a markdown table")
+    args = ap.parse_args()
+
+    runs = collect_runs(args)
+    if not runs:
+        print("no run directories: pass RUN_DIR, or --issues with --runs-root", file=sys.stderr)
+        return 2
+
+    rows = [(run_label(run), metrics_for(run)) for run in runs]
+    if args.json:
+        print(json.dumps([row for _, row in rows]))
+    else:
+        print(markdown(rows))
+    return 0
+
+
+if __name__ == "__main__":
+    raise SystemExit(main())
~~~~~~~~~~~~ evidence
