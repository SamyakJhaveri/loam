## Ticket

~~~~~~~~~~~~ evidence
Brief:
Give a rendered project one named place in bin/check for its own deterministic checks, and one rule for when to add one.
Where: seed/bin/check.jinja, seed/docs/WORKERS.md.
Done means: the rendered bin/check carries a "Project checks" stage with a one-line rule and no checks; WORKERS.md carries the rule with the trigger "second recurrence"; a fresh render has both; bin/check passes.
Out of scope: any shipped project check; any change to the always-on prose (AGENTS.md, CLAUDE.md); any hook.
Blocked by: #151 (the copier helper fix; the render-check-green guard needs a render whose own bin/check passes).

## Goal and why
A rendered bin/check is a flat script with no place for a project's own checks, and nothing in the seed says when a pattern the docs already ban should become a check (docs/research/curation-2026-09-20.md, row R3 and pick 4).
The rule that repeated corrections become a deterministic check, not a third prose copy, lives only in the owner's memory today; the seed should carry it.

## Do not touch
The standing list. Also: seed/AGENTS.md.jinja, seed/CLAUDE.md.jinja, seed/.claude/, seed/.codex/, docs/.
Except: seed/bin/check.jinja (this ticket edits it).

## Out of scope
A shipped check; any always-on prose line; hooks; the Loam repo's own bin/check.

## Approach
1. In seed/bin/check.jinja, before the final FAIL summary, add a stage headed by exactly the comment `# Project checks: one line per deterministic check this project adds, each 'cmd || bad "name"'.` and a second comment line `# Add one at the second recurrence of a pattern the docs already ban; the rule is under Project checks in WORKERS.md.` No check lines under it.
2. In seed/docs/WORKERS.md add a section `## Project checks` of at most six lines: the stage exists in bin/check; add a check at the second recurrence of a pattern the docs already ban, so the correction becomes a failure the agent cannot argue with; keep each check one line, deterministic, and named; never add a check that cannot fail; a check that only restates prose is a duplicate and is removed.
3. Keep the `{% raw %}` block intact; the new comments contain no Jinja delimiters.

## Done checks
```done-checks
grep -q '^# Project checks: one line per deterministic check' seed/bin/check.jinja && grep -q 'second recurrence' seed/bin/check.jinja && pass stage-in-seed || fail stage-in-seed "the project-checks stage is missing from check.jinja"
grep -q '^## Project checks' seed/docs/WORKERS.md && grep -q 'second recurrence' seed/docs/WORKERS.md && pass rule-in-workers || fail rule-in-workers "WORKERS.md has no Project checks section with the trigger"
render_into; [ -n "$render_dir" ] || fail render "$render_err"; grep -q '^# Project checks:' "$render_dir/bin/check" && bash -n "$render_dir/bin/check" && pass stage-in-render || fail stage-in-render "the rendered bin/check lacks the stage or fails bash -n"
guard sh -c '[ -n "$1" ] && cd "$1" && bin/check >/dev/null 2>&1' _ "$render_dir" && pass render-check-green || fail render-check-green "bin/check fails in the render"
guard bin/check >/dev/null && pass check-green || fail check-green "bin/check"
```

## Worker
worker: claude
codex-review: no
effort: high
MAX_ROUNDS=2
goal: the done-checks block prints no FAIL line, or stop after 40 turns

## Decisions
docs/research/curation-2026-09-20.md (pick 4), seed/docs/HARNESS.md (The one check)

~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS stage-in-seed
PASS rule-in-workers
PASS stage-in-render
PASS render-check-green
PASS check-green

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
- Followed the Approach exactly; no departures.
- check.jinja (c13c04d2): added a "Project checks" stage before the final FAIL summary, inside the {% raw %} block, with the two mandated comment lines and no check lines.
- WORKERS.md (c13c04d2): added a "## Project checks" section (6 wrapped body lines, within the six-line cap) carrying the rule and the "second recurrence" trigger.
- Comments contain no Jinja delimiters, so {% raw %} stays intact.
- Round 2: no code change needed; the c13c04d2 edits are verified green. Consulted the advisor; it confirmed the diagnosis and the ABANDON call.
- Evidence (frozen checks.sh, this round, from worktree root): as-is = PASS stage-in-seed, rule-in-workers, stage-in-render, render-check-green; FAIL check-green (exit 1). With the two exports prepended = all 5 PASS (exit 0).
- Cause of the check-green FAIL: check-green runs the Loam repo's own bin/check, which fails at the "factory package qualification and independent rebuild" gate because LOAM_FACTORY_TOOLCHAIN and LOAM_FACTORY_COPIER are unset in the supervisor's process tree. The seed edits do not affect it; bin/check passes (exit 0) on c13c04d2 once both are exported.
- Who sets these vars: only .github/workflows/test.yml:55-56 (CI). bin/factory and bin/factory.d never export them, so the local launch relies on the operator's shell exporting them per CONTRIBUTING.md:11-15. This is an operator/launch-setup gap, not a launcher bug and not an in-scope code defect.
- The ticket's "Done means ... bin/check passes" is met in the documented environment (CONTRIBUTING.md:11-15). The FAIL is a harness/launch gap, not a defect.
- ABANDON check-green bin/check fails at the factory-qualification gate because LOAM_FACTORY_TOOLCHAIN and LOAM_FACTORY_COPIER are unset in the supervisor's process tree; it passes (exit 0) on c13c04d2 with both exported; the Loam bin/check is out of scope and no in-scope edit can supply the parent process's env; the fix belongs at launch (export the two vars per CONTRIBUTING.md:11-15, as CI does in .github/workflows/test.yml:55-56). Not edited, weakened, or routed around.
- Round 3: no edit needed. The c13c04d2 seed edits are correct and complete. Ran the frozen checks.sh (frozen/checks.sh) from the worktree root exactly as the supervisor does: all 5 PASS, exit 0 (stage-in-seed, rule-in-workers, stage-in-render, render-check-green, check-green). bin/check on its own returns exit 0; the factory-qualification gate passes because the loam toolchain resolves in this process tree. The round-2 check-green FAIL (unset LOAM_FACTORY_TOOLCHAIN/COPIER) did not reproduce; it was an env/launch gap, not a defect. Retracting the round-2 ABANDON: check-green is green. Working tree clean; nothing to commit.

~~~~~~~~~~~~ evidence

## Diff (fad17cbf...HEAD)

~~~~~~~~~~~~ evidence
 seed/bin/check.jinja | 3 +++
 seed/docs/WORKERS.md | 8 ++++++++
 2 files changed, 11 insertions(+)

diff --git a/seed/bin/check.jinja b/seed/bin/check.jinja
index 23aa42aa..b0b8e467 100755
--- a/seed/bin/check.jinja
+++ b/seed/bin/check.jinja
@@ -24,5 +24,8 @@ git diff --check "$(git hash-object -t tree /dev/null)" HEAD -- || bad "whitespa

 if { [ -d tests ] || [ -d test ]; } && command -v pytest >/dev/null 2>&1; then pytest -q || bad "pytest"; fi

+# Project checks: one line per deterministic check this project adds, each 'cmd || bad "name"'.
+# Add one at the second recurrence of a pattern the docs already ban; the rule is under Project checks in WORKERS.md.
+
 if [ "$FAIL" -ne 0 ]; then echo "check: FAILED"; exit 1; fi
 echo "check: PASSED"{% endraw %}
diff --git a/seed/docs/WORKERS.md b/seed/docs/WORKERS.md
index 1ac73f56..242f37e8 100644
--- a/seed/docs/WORKERS.md
+++ b/seed/docs/WORKERS.md
@@ -38,3 +38,11 @@ whole files or logs. The repository state wins over the handoff.

 A worker brief and its report use the same seven headings, so an interrupted
 worker's findings are read from its report, never rebuilt from a transcript.
+
+## Project checks
+
+`bin/check` carries a Project checks stage for the checks this project adds. Add
+a check at the second recurrence of a pattern the docs already ban, so the
+correction becomes a failure the agent cannot argue with. Keep each check one
+line, deterministic, and named. Never add a check that cannot fail. A check that
+only restates prose is a duplicate; remove it.
~~~~~~~~~~~~ evidence
