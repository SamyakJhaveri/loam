## Ticket

~~~~~~~~~~~~ evidence
Brief:
A `bin/factory eval` call made by a run's Rows measured line appends its cost to that run's ledger, so the ticket and daily caps see it and the ledger total is the real spend.
Where: bin/factory (run_eval, measure_rows)
Done means: after a run's measure step, ledger.jsonl carries one line per eval call with role eval and the call's cost_usd, ledger-daily.jsonl carries the same cost, and a stand-alone `bin/factory eval` outside a run writes no ledger line.
Out of scope: how often the replay runs; the graders; evals/ cases.
Track: B    Risk: medium    Mode: build    Open question: none
Blocked by: #46

## Goal and why
The F3 run (#46, PR #58) booked 18.20 usd in its ledger, but its two Rows measured steps ran twelve live Fable calls each, 12.6 usd per round, printed in `round-N.measure` and recorded nowhere.
Real spend was about 43.5 usd; `assert_caps` and `bin/factory status` saw 18.20.
Every ticket with a `bin/factory eval` row has the same hole, so the ticket and daily budgets cannot hold.

## Do not touch
The standing list. Except: bin/factory (`run_eval` and `measure_rows` only).

## Out of scope
- when or how often `measure_rows` runs
- the graders, their schemas, and evals/ cases
- bin/factory status columns

## Approach
`cmd_run` already knows `$LEDGER`, `$DAILY`, `$KEY`, and `$ROUND`; export them as `FACTORY_LEDGER`, `FACTORY_DAILY`, `FACTORY_KEY`, `FACTORY_ROUND` before `measure_rows` evaluates a row, so the child `bin/factory eval` sees them.
In `run_eval`, after each `claude -p` reply, when `FACTORY_LEDGER` is set append one line to it in the same shape `record` writes (`round` from `FACTORY_ROUND`, `role` `eval`, `model` `$EVAL_MODEL`, `cost_usd` from `total_cost_usd`, `duration_ms`, `num_turns`, `denials` 0, `subtype`, `ts`), and the `{date, ticket, role, cost_usd}` line to `FACTORY_DAILY`.
Do not call `record` from `run_eval`: eval runs as a child process with its own globals.
A stand-alone `bin/factory eval` has no `FACTORY_LEDGER` and writes nothing.
Pattern to follow: `record` for the two line shapes; the `FACTORY_<NAME>` convention of `apply_caps` for the environment names.

## Done checks
```done-checks
guard bash -n bin/factory && pass syntax || fail syntax "bash -n bin/factory"
grep -q 'FACTORY_LEDGER' bin/factory && pass ledger-env || fail ledger-env "run_eval never reads FACTORY_LEDGER"
d=$(mktemp -d "${TMPDIR:-/tmp}/f15.XXXXXX"); mkdir -p "$d/bin" "$d/evals/judge/c1"; printf '{"verdict":"pass"}\n' > "$d/evals/judge/c1/expected.json"; echo x > "$d/evals/judge/c1/prompt.md"; printf '#!/usr/bin/env bash\necho "{\\"type\\":\\"result\\",\\"subtype\\":\\"success\\",\\"total_cost_usd\\":0.25,\\"duration_ms\\":10,\\"num_turns\\":1,\\"result\\":\\"{\\\\\\"verdict\\\\\\":\\\\\\"pass\\\\\\",\\\\\\"rows\\\\\\":{},\\\\\\"fixes\\\\\\":[]}\\"}"\n' > "$d/bin/claude"; chmod +x "$d/bin/claude"; : > "$d/ledger.jsonl"; : > "$d/daily.jsonl"; ( cd "$d" && PATH="$d/bin:$PATH" EVALS_DIR="$d/evals" FACTORY_LEDGER="$d/ledger.jsonl" FACTORY_DAILY="$d/daily.jsonl" FACTORY_KEY=t FACTORY_ROUND=1 "$OLDPWD/bin/factory" eval judge > /dev/null 2>&1 ); n=$(grep -c '"role":"eval"' "$d/ledger.jsonl"); c=$(jq -s 'map(.cost_usd)|add' "$d/ledger.jsonl"); m=$(grep -c '"ticket":"t"' "$d/daily.jsonl"); [ "$n" -eq 1 ] && [ "$c" = "0.25" ] && [ "$m" -eq 1 ] && pass eval-booked || fail eval-booked "expected one eval line at 0.25 usd in both ledgers, got ledger=$n cost=$c daily=$m"
d=$(mktemp -d "${TMPDIR:-/tmp}/f15b.XXXXXX"); mkdir -p "$d/bin" "$d/evals/judge/c1"; printf '{"verdict":"pass"}\n' > "$d/evals/judge/c1/expected.json"; echo x > "$d/evals/judge/c1/prompt.md"; printf '#!/usr/bin/env bash\necho "{\\"type\\":\\"result\\",\\"subtype\\":\\"success\\",\\"total_cost_usd\\":0.25,\\"result\\":\\"{\\\\\\"verdict\\\\\\":\\\\\\"pass\\\\\\",\\\\\\"rows\\\\\\":{},\\\\\\"fixes\\\\\\":[]}\\"}"\n' > "$d/bin/claude"; chmod +x "$d/bin/claude"; ( cd "$d" && PATH="$d/bin:$PATH" EVALS_DIR="$d/evals" "$OLDPWD/bin/factory" eval judge > /dev/null 2>&1 ); guard test ! -e "$d/ledger.jsonl" && pass standalone-silent || fail standalone-silent "a stand-alone eval wrote a ledger"
[ -n "${LOAM_HOOK:-}" ] && pass check-green || { guard bin/check >/dev/null && pass check-green || fail check-green "bin/check"; }
```

## Merge checklist
- the next `bin/factory run` with a Rows measured eval row shows role eval lines in its ledger and `bin/factory status` spend includes them

## Worker
worker: claude
codex-review: no
effort: xhigh
goal: the Done checks block, sourced after bin/factory.d/lib.sh and run from the worktree root with its output shown, prints no FAIL line and one PASS line per named check, or stop after 40 turns

## Decisions
docs/factory/LOOP.md (Ledger), the 2026-09-10 manager session: F3 booked 18.20 usd of about 43.5

~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS syntax
PASS ledger-env
PASS eval-booked
PASS standalone-silent
PASS check-green

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
- Read bin/factory: run_eval (241-310), record (538-558), apply_caps (432-442), measure_rows (833-844), cmd_run (1094-1140), eval dispatch (1286-1298). Confirmed FACTORY_<NAME> convention (apply_caps) and the two ledger line shapes (record: LEDGER line + DAILY {date,ticket,role,cost_usd}).
- Plan: (1) measure_rows exports FACTORY_LEDGER=$LEDGER, FACTORY_DAILY=$DAILY, FACTORY_KEY=$KEY, FACTORY_ROUND=$1 at the top, before the row loop, so the child `bin/factory eval` inherits them. (2) run_eval, after each `claude -p` reply, when FACTORY_LEDGER is set, appends one ledger line (round=FACTORY_ROUND, role=eval, model=$EVAL_MODEL, cost_usd=total_cost_usd, duration_ms, num_turns, denials 0, subtype, ts) and the {date,ticket,role,cost_usd} daily line. No call to record (eval is a child with its own globals).
- Export in measure_rows (not cmd_run) is a constraint, not a preference: the Do-not-touch exception names only run_eval and measure_rows, so editing cmd_run would breach it. The four names are not cap names, so no apply_caps collision, and only a `bin/factory eval` child reads them.
- Frozen-copy caveat: the supervisor runs $RUN/frozen/factory, frozen at launch, so this ticket's own run uses the old measure_rows and shows no eval lines. The merge checklist targets the next run. This is expected, not a miss.
- Applied advisor guidance: empty-out fallback keyed on `[ -n "$eline" ]` (jq exits 0 on empty stdin, so `||` alone would write a blank line); append placed right after the spent= line, inside the attempt loop, so every reply books; kept the field subset (no usage/advisor/workflow) since ticket_spent, daily_spent, cmd_status read only cost_usd//0.
- Done: all five done-checks PASS (no FAIL) and bin/check green; committed as c98fd70, diff scoped to run_eval + measure_rows only.

~~~~~~~~~~~~ evidence

## Diff (e3faa1fe...HEAD)

~~~~~~~~~~~~ evidence
 bin/factory | 20 +++++++++++++++++++-
 1 file changed, 19 insertions(+), 1 deletion(-)

diff --git a/bin/factory b/bin/factory
index e3938cc..69645c6 100755
--- a/bin/factory
+++ b/bin/factory
@@ -240,7 +240,7 @@ grader_rubric() {

 run_eval() {
   local grader="$1" budget="${EVAL_BUDGET_USD:-10}" gf schema rubric dir name out res exp got erows grows
-  local spent=0 cases=0 mism=0 ok attempt
+  local spent=0 cases=0 mism=0 ok attempt eline
   gf=$(grader_file "$grader") || return 2
   schema=$(schema_for "$grader" 2> /dev/null)
   [ -n "$schema" ] || { echo "eval: no bin/factory.d/$grader.schema.json" >&2; return 2; }
@@ -269,6 +269,21 @@ run_eval() {
         --setting-sources user --output-format json 2>/dev/null)
       spent=$(awk -v a="$spent" -v b="$(jq -r "$RESULT_OBJ | .total_cost_usd // 0" <<<"$out" 2>/dev/null)" \
         'BEGIN {printf "%.4f", a + (b + 0)}')
+      # When a run's measure step drives this eval (FACTORY_LEDGER is set), book each reply's cost to
+      # that run's ledger and daily ledger, so the ticket and daily caps see it (#76). A stand-alone
+      # eval has no FACTORY_LEDGER and books nothing. run_eval is a child process with its own globals,
+      # so it cannot call record; it writes the two line shapes record writes, itself.
+      if [ -n "${FACTORY_LEDGER:-}" ]; then
+        eline=$(jq -c --argjson round "${FACTORY_ROUND:-0}" --arg role eval --arg model "$EVAL_MODEL" --arg ts "$(now)" \
+          "$RESULT_OBJ | {round:\$round, role:\$role, model:\$model, cost_usd:(.total_cost_usd // 0), \
+duration_ms:(.duration_ms // 0), num_turns:(.num_turns // 0), denials:0, subtype:(.subtype // \"unknown\"), ts:\$ts}" \
+          <<<"$out" 2>/dev/null)
+        [ -n "$eline" ] || eline=$(jq -nc --argjson round "${FACTORY_ROUND:-0}" --arg role eval --arg model "$EVAL_MODEL" --arg ts "$(now)" \
+          '{round:$round, role:$role, model:$model, cost_usd:0, duration_ms:0, num_turns:0, denials:0, subtype:"unknown", ts:$ts}')
+        printf '%s\n' "$eline" >> "$FACTORY_LEDGER"
+        printf '%s' "$eline" | jq -c --arg date "$(today)" --arg ticket "${FACTORY_KEY:-}" \
+          '{date:$date, ticket:$ticket, role:.role, cost_usd:.cost_usd}' >> "$FACTORY_DAILY"
+      fi
       res=$(jq -r "$RESULT_OBJ | .result // \"\"" <<<"$out" 2>/dev/null)
       # Fallback: if a reply still carries code fences or prose around the object, the object runs
       # from the first brace to the last, so cut to those before parsing the verdict.
@@ -832,6 +847,9 @@ do_not_touch_hits() { # -> the changed paths the ticket fenced off

 measure_rows() { # round; Rows measured is `<row>: <command> | <baseline>` per line (CONTRACT.md)
   local out="$RUN/round-$1.measure" line row rest
+  # Export the run's ledger, daily ledger, ticket key, and round so a `bin/factory eval` row books its
+  # cost to this run (#76); run_eval reads these four names, mirroring apply_caps's FACTORY_<NAME>.
+  export FACTORY_LEDGER="$LEDGER" FACTORY_DAILY="$DAILY" FACTORY_KEY="$KEY" FACTORY_ROUND="$1"
   : > "$out"
   while IFS= read -r line; do
     line=${line#- }
~~~~~~~~~~~~ evidence
