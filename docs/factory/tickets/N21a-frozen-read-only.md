# N21a: freeze leaves the run's frozen/ folder and base.sha read-only to the worker
Brief:
Make a run's `frozen/` folder, every file in it, and `base.sha` read-only once freeze returns, so a native worker cannot replace the frozen set or move the base the do-not-touch diff reads.
Where: bin/factory, docs/factory/LOOP.md, bin/tests/test_factory_auto_memory.py (a model for a sourced freeze test).
Done means: after `freeze` (first call and the early-return resume call), creating a file in `frozen/`, renaming a frozen file, and writing `base.sha` all fail; `check_frozen` still passes; Loam bin/check passes.
Out of scope: running the worker as another user; the classifier and deny rules; P7.
Track: B    Risk: medium    Mode: build    Open question: none
Blocked by: #713

## Goal and why
Owner ruling of 12 Nov 2026, 19:58 PT (NEEDS-SAMYAK N21.1, "Yes to all five"; distbench APPROVALS entry "Two factory sandbox gaps become factory tickets", PR SamyakJhaveri/distbench#509): make `frozen/` and `base.sha` read-only to the worker, supervisor-owned, `chmod a-w` after freezing.
The gap, found reviewing Loam PR 713: a native factory worker (no sandbox, auto mode) can write its own run folder. `freeze` ends with `chmod a-w "$RUN/frozen"/*`, which protects the files but not the folder, so the worker can delete `sha256` and a frozen file and write both again; and `base.sha`, which the do-not-touch diff and round 0 read, stays writable and is not in the frozen hash.
PR 713 adds the native worker and also edits `freeze`, so this ticket runs after it merges.

## Do not touch
The standing list. Except: bin/factory (this ticket edits `freeze` and its resume path).
Also: bin/factory.d/, bin/tests/test_factory_auto_memory.py.

## Out of scope
Running the worker under another uid, or any sandbox change: the worker shares the supervisor's uid, so it could `chmod u+w` back; that is a visible command the classifier sees, and this ticket only removes the silent write.
The deny rules and the classifier.
P7 and the shell digest.
A `gh` or push check (ticket N21b).

## Approach
Read first: `bin/factory` (`prepare_worktree`, `freeze`, `check_frozen`, `main_loop`, `cmd_run` and every place that reads or writes `$RUN/base.sha` or `$RUN/frozen`), `docs/factory/LOOP.md` steps 2, 3 and 6, and `bin/tests/test_factory_auto_memory.py` for how a test sources `bin/factory` and calls `freeze`; read any other code or test that bears on it, and stop and report if it contradicts this ticket.
Fixed: when `freeze` returns 0, on its first call and on the early return a resume takes, `$RUN/frozen`, every file in it, and `$RUN/base.sha` have no write bit (`chmod a-w`); the chmod is idempotent, and a failed chmod ends the run `stopped-environment`.
Fixed: nothing in the supervisor writes under `$RUN/frozen` or to `$RUN/base.sha` after `freeze` returns; if some path does today, it writes before the chmod or stops and reports.
Suggested: `check_frozen` also compares `base.sha` with a copy recorded at freeze, so a `chmod u+w` and rewrite is still caught; any code or test that deletes a run folder makes it writable first.
Update `docs/factory/LOOP.md` step 3 ("owned outside the worker's write scope") to say what is now enforced.
A better route inside this scope: take it and log the deviation in decisions.md; outside it, stop and report.

## Done checks
```done-checks
predict frozen-read-only d=$(mktemp -d "${TMPDIR:-/tmp}/n21a.XXXXXX") && mkdir -p "$d/run/frozen" && git rev-parse HEAD > "$d/run/base.sha" && FACTORY_SOURCED=1 FACTORY_ROOT="$PWD" FACTORY_RUNS_ROOT="$d/runs" bash -c '. bin/factory; RUN=$1/run; LOG="$RUN/factory.log"; LEDGER="$RUN/ledger.jsonl"; DECISIONS="$RUN/decisions.md"; GRADERS_DIR="$PWD/cultivation/marketplace/sam-cc-setup/agents"; IS_FILE=1; KEY=t; BODY=x; freeze && freeze && check_frozen' bin/factory "$d" > "$d/out" 2>&1 && ( : > "$d/run/frozen/planted" ) 2>/dev/null && ( : >> "$d/run/base.sha" ) 2>/dev/null
d=$(mktemp -d "${TMPDIR:-/tmp}/n21a.XXXXXX") && mkdir -p "$d/run/frozen" && git rev-parse HEAD > "$d/run/base.sha" && FACTORY_SOURCED=1 FACTORY_ROOT="$PWD" FACTORY_RUNS_ROOT="$d/runs" bash -c '. bin/factory; RUN=$1/run; LOG="$RUN/factory.log"; LEDGER="$RUN/ledger.jsonl"; DECISIONS="$RUN/decisions.md"; GRADERS_DIR="$PWD/cultivation/marketplace/sam-cc-setup/agents"; IS_FILE=1; KEY=t; BODY=x; freeze && freeze && check_frozen' bin/factory "$d" > "$d/out" 2>&1 && ! ( : > "$d/run/frozen/planted" ) 2>/dev/null && ! mv "$d/run/frozen/checks.sh" "$d/run/frozen/moved.sh" 2>/dev/null && ! ( : >> "$d/run/base.sha" ) 2>/dev/null && pass frozen-read-only || fail frozen-read-only "after freeze (twice) and check_frozen, a new file in frozen/, a rename inside it, or an append to base.sha succeeded, or freeze failed; see $d/out"
guard bin/check >/dev/null && pass check-green || fail check-green "bin/check"
```

## Worker
worker: claude
codex-review: yes
effort: high
contract: 2
goal: the done-checks block prints no FAIL line, or stop after 60 turns

## Decisions
Owner ruling 12 Nov 2026 19:58 PT, NEEDS-SAMYAK N21.1 (recorded in distbench `~/.local/state/distbench/evidence/2026-11-12-lean-plan/OWNER-ANSWERS.md` on jhaveris and in APPROVALS by SamyakJhaveri/distbench#509).
The gap as reported: the review of Loam PR 713 (its PR body, "Open, not fixed here").
Checked on Loam main 867b4dcf at 20:02 PT on 12 Nov: the predict line holds (freeze and check_frozen succeed, then a file can be created in `frozen/` and `base.sha` appended to).
