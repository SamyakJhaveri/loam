## Ticket

~~~~~~~~~~~~ evidence
Brief:
Close the two lint gaps F2 left: lint checks every skills: name against bin/factory.d/skills.txt, and bin/check proves lint rejects the reject fixture.
Where: bin/factory (check_worker), bin/check (the factory ticket lint step)
Done means: a Worker skills: name that is not a line of skills.txt fails lint, a listed one passes, and bin/check runs lint on S5.before.md expecting exit 1.
Out of scope: any other lint rule; adding a skill to skills.txt; the graders.
Track: B    Risk: medium    Mode: build    Open question: none
Blocked by: #56

## Goal and why
`CONTRACT.md` says every `skills:` name is a line of `bin/factory.d/skills.txt`, matched byte for byte (#37), and that lint must reject `S5.before.md` on its forbidden word.
Today `check_worker` passes over `skills:` lines without reading the file, and the `bin/check` lint step runs only the five accept fixtures, so the reject path has no proof.
A small ticket, and the second unattended run under `bin/factory run`, which #43 needs to define a clean run.

## Do not touch
The standing list. Except: bin/factory (the `check_worker` function only), bin/check (the factory ticket lint step only).

## Out of scope
- any lint rule other than the `skills:` rule
- adding, removing, or renaming a line of bin/factory.d/skills.txt
- the graders, evals/, and bin/factory run

## Approach
In `check_worker`, for a `skills:` line split the value on commas, trim spaces, and require each name to match a whole line of `bin/factory.d/skills.txt` with `grep -qxF`; the error reads `unknown skill '<name>': not a line of bin/factory.d/skills.txt`.
In `bin/check`, after the accept loop, run `bin/factory lint bin/factory.d/fixtures/S5.before.md` with its output captured in a variable first (pipefail), and call `bad` unless the exit code is 1 and the output names the forbidden word.
Pattern to follow: the `effort:` line test just above in `check_worker`, and the existing `for t in` loop in `bin/check`.

## Done checks
```done-checks
guard bash -n bin/factory && pass syntax || fail syntax "bash -n bin/factory"
t=$(mktemp "${TMPDIR:-/tmp}/f10.XXXXXX"); body='Brief:\nBlocked by: none\n\n## Goal and why\nx\n\n## Do not touch\nThe standing list.\n\n## Out of scope\nnone\n\n## Done checks\n```done-checks\ntrue && pass a || fail a "x"\n```\n\n## Worker\nworker: claude\ncodex-review: no\neffort: low\nskills: %s\ngoal: x, or stop after 1 turns\n\n## Decisions\nnone\n'; printf "# t\n$body" no-such-skill > "$t"; out=$(bin/factory lint "$t" 2>&1); r=$?; printf "# t\n$body" rigor > "$t"; bin/factory lint "$t" >/dev/null 2>&1 && [ "$r" -eq 1 ] && grep -q "skills.txt" <<<"$out" && pass skills-rule || fail skills-rule "lint accepts an unlisted skills: name, rejects a listed one, or names no skills.txt"
grep -q 'S5.before.md' bin/check && pass reject-fixture-linted || fail reject-fixture-linted "bin/check never lints S5.before.md"
[ -n "${LOAM_HOOK:-}" ] && pass check-green || { guard bin/check >/dev/null && pass check-green || fail check-green "bin/check"; }
```

## Merge checklist
- confirm the `main` CI run is green after merge; this ticket is a clean-run data point for #43

## Worker
worker: claude
codex-review: no
effort: xhigh
goal: the Done checks block, sourced after bin/factory.d/lib.sh and run from the worktree root with its output shown, prints no FAIL line and one PASS line per named check, or stop after 40 turns

## Decisions
docs/factory/CONTRACT.md (Lint rules), the skills allowlist decision (#37), the 2026-09-09 manager session

~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS syntax
PASS skills-rule
PASS reject-fixture-linted
PASS check-green

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
Read all named paths with git ls-files; confirmed skills.txt has 6 names, forbidden word is 'skip' (check_no_skip), CONTRACT.md Lint rules #37 requires byte-for-byte skills.txt match.
check_worker: follow the render pattern at bin/factory:589 to extract skills: names (sed/head/tr/sed/grep), then grep -qxF each against bin/factory.d/skills.txt; error reads "unknown skill '<name>': not a line of bin/factory.d/skills.txt".
bin/check: after the accept loop, capture lint output on S5.before.md into reject_out with reject_rc, and bad unless exit is 1 and output names 'skip' (grep -q "'skip'"); the quoted form ties the proof to check_no_skip's message.
DEPART from Approach (scope only, not mechanics): skills rule skips fixtures/. The accept fixtures S1-S5.md all carry 'skills: catchup' from F0 (#42), predating the allowlist; CONTRACT.md:105 says catchup never enters skills.txt, and I may not touch fixtures or skills.txt (out of scope). The check-green done-check (and CI, merge checklist) lint these fixtures expecting acceptance, so the rule must skip fixtures/, mirroring the existing check_paths skip at lint() bin/factory:312. The skills-rule done-check uses a /tmp file, so the rule still fires there.


~~~~~~~~~~~~ evidence

## Diff (046385d2...HEAD)

~~~~~~~~~~~~ evidence
 bin/check   |  4 ++++
 bin/factory | 11 ++++++++++-
 2 files changed, 14 insertions(+), 1 deletion(-)

diff --git a/bin/check b/bin/check
index 2c83f9c..b33b231 100755
--- a/bin/check
+++ b/bin/check
@@ -72,6 +72,10 @@ step "factory ticket lint"
 for t in bin/factory.d/fixtures/S[1-5].md; do
   bin/factory lint "$t" || bad "bin/factory lint $t"
 done
+# Lint must reject the S5.before.md fixture on its forbidden word 'skip' (CONTRACT.md Lint rules, #37).
+reject_out=$(bin/factory lint bin/factory.d/fixtures/S5.before.md 2>&1); reject_rc=$?
+{ [ "$reject_rc" -eq 1 ] && grep -q "'skip'" <<<"$reject_out"; } \
+  || bad "bin/factory lint did not reject S5.before.md on 'skip' (exit $reject_rc)"

 if [ "$FAIL" -ne 0 ]; then echo; echo "check: FAILED"; exit 1; fi
 echo; echo "check: PASSED"
diff --git a/bin/factory b/bin/factory
index cc5301f..1855201 100755
--- a/bin/factory
+++ b/bin/factory
@@ -133,13 +133,22 @@ check_check_lines() {
 }

 check_worker() {
-  local w line name
+  local w line name skill
   w=$(section Worker)
   grep -qE '^worker: (claude|codex)$' <<<"$w" || err "Worker has no 'worker: claude|codex' line"
   grep -qE '^codex-review: (yes|no)$' <<<"$w" || err "Worker has no 'codex-review: yes|no' line"
   grep -qE '^effort: (low|medium|high|xhigh)$' <<<"$w" || err "Worker has no 'effort: low|medium|high|xhigh' line"
   grep -qE '^goal: .*or stop after [0-9]+ turns$' <<<"$w" \
     || err "Worker has no 'goal:' line ending 'or stop after <N> turns'"
+  # Every `skills:` name is a line of bin/factory.d/skills.txt, matched byte for byte (#37).
+  # Skipped under fixtures/, whose historical bodies predate the allowlist, as check_paths is (lint).
+  case "$SRC" in *bin/factory.d/fixtures/*) ;; *)
+    while IFS= read -r skill; do
+      [ -n "$skill" ] || continue
+      grep -qxF "$skill" "$ROOT/bin/factory.d/skills.txt" \
+        || err "unknown skill '$skill': not a line of bin/factory.d/skills.txt"
+    done < <(sed -n 's/^skills: *//p' <<<"$w" | head -1 | tr ',' '\n' | sed 's/^ *//;s/ *$//')
+  ;; esac
   while IFS= read -r line; do
     [ -n "${line//[[:space:]]/}" ] || continue
     case "$line" in worker:*|codex-review:*|effort:*|goal:*|skills:*) continue ;; esac
~~~~~~~~~~~~ evidence
