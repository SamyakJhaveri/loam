# N21b: the supervisor stops a run whose branch on origin holds a push it did not make
Brief:
Record every push of the run branch the supervisor makes, and stop the run when the branch's head on origin is not the supervisor's last recorded push, so a worker's disguised `git push` is caught even when the classifier misses it.
Where: bin/factory, docs/factory/LOOP.md.
Done means: a push to the run branch made outside the supervisor ends the run `stopped-environment` naming the remote sha; a push through the supervisor's own push function passes the check; Loam bin/check passes.
Out of scope: changing the deny rules or the classifier; `gh` calls other than pushes; branches other than the run's.
Track: B    Risk: medium    Mode: build    Open question: none
Blocked by: #713

## Goal and why
Owner ruling of 12 Nov 2026, 19:58 PT (NEEDS-SAMYAK N21.2, "Yes to all five"; distbench APPROVALS entry "Two factory sandbox gaps become factory tickets", PR SamyakJhaveri/distbench#509): keep the classifier as the guard and add a factory-side check that only the supervisor pushed the branch, comparing the remote head with the supervisor's own push log.
The gap, found reviewing Loam PR 713: the worker deny rules match by command prefix, so a disguised `git push` (through a variable, a script or another tool) is stopped only by the auto-mode classifier, and nothing in the factory notices if one gets through.
PR 713 adds the native worker and edits `open_pr`, so this ticket runs after it merges.

## Do not touch
The standing list. Except: bin/factory (this ticket adds the push log and its check, and routes `open_pr`'s push through them).
Also: bin/factory.d/.

## Out of scope
The deny rules, worker settings and the classifier: the classifier stays the guard; this check detects, it does not prevent.
`gh` calls that do not push (issue or PR edits, API calls) and pushes to branches other than the run's `$BRANCH`.
Rewriting history the supervisor already pushed.

## Approach
Read first: `bin/factory` (`open_pr` and its push of `$BRANCH`, `main_loop` and its `check_frozen` calls around `worker_round`, `cmd_run`'s publish replay from `publish.intent`, `finish`, `net`, and the alert call in `finish`), `docs/factory/LOOP.md` (the run directory layout and the publish step); read any other code or test that bears on it, and stop and report if it contradicts this ticket.
Fixed interface: `push_branch` is the supervisor's only push of `$BRANCH`: it pushes HEAD of `$WORKTREE` to `origin` `$BRANCH` through `net`, and on success appends one line `<pushed sha> <UTC time>` to `$RUN/push.log`; `open_pr` uses it in place of its inline push.
Fixed interface: `check_pushes` reads the head of `refs/heads/$BRANCH` on `origin` from `$WORKTREE` (`git ls-remote` through `net`); when the branch exists there and its sha is not the sha on the last line of `$RUN/push.log` (or the log is missing or empty), it calls `finish stopped-environment` with a message that contains `not pushed by the supervisor` and the remote sha; when the branch is absent and the log is empty it returns 0; when origin gives no reply it logs one line and returns 0.
Fixed: `main_loop` calls `check_pushes` after each worker round, next to the `check_frozen` there, and `open_pr` calls it before `push_branch`; a file ticket, which never pushes, therefore stops if its branch ever appears on origin.
Update `docs/factory/LOOP.md` (run directory layout and the publish step) to name `push.log` and the check.
A better route inside this scope: take it and log the deviation in decisions.md; outside it, stop and report.

## Done checks
```done-checks
predict worker-push-stops ! grep -q '^check_pushes()' bin/factory
out=; d=$(mktemp -d "${TMPDIR:-/tmp}/n21b.XXXXXX") && G="git -c user.name=t -c user.email=t@t -c commit.gpgsign=false -c init.defaultBranch=main" && $G init -q --bare "$d/o.git" && $G clone -q "$d/o.git" "$d/wt" 2>/dev/null && $G -C "$d/wt" commit -q --allow-empty -m one && $G -C "$d/wt" push -q origin HEAD:refs/heads/factory/t && mkdir -p "$d/run" && out=$(FACTORY_SOURCED=1 FACTORY_ROOT="$PWD" FACTORY_RUNS_ROOT="$d/runs" bash -c '. bin/factory; finish() { echo "FINISH $*"; exit 3; }; RUN=$1/run; LOG="$RUN/factory.log"; LEDGER="$RUN/ledger.jsonl"; WORKTREE=$1/wt; BRANCH=factory/t; check_pushes; echo "RETURNED $?"' bin/factory "$d" 2>&1) ; grep -q '^FINISH stopped-environment .*not pushed by the supervisor' <<<"$out" && grep -q "$(git -C "$d/wt" rev-parse HEAD)" <<<"$out" && pass worker-push-stops || fail worker-push-stops "a push to the run branch with no push.log line must make check_pushes call finish stopped-environment with 'not pushed by the supervisor' and the remote sha; got: $out"
predict supervisor-push-passes ! grep -q '^push_branch()' bin/factory
out=; d=$(mktemp -d "${TMPDIR:-/tmp}/n21b.XXXXXX") && G="git -c user.name=t -c user.email=t@t -c commit.gpgsign=false -c init.defaultBranch=main" && $G init -q --bare "$d/o.git" && $G clone -q "$d/o.git" "$d/wt" 2>/dev/null && $G -C "$d/wt" commit -q --allow-empty -m one && mkdir -p "$d/run" && out=$(GIT_AUTHOR_NAME=t GIT_AUTHOR_EMAIL=t@t GIT_COMMITTER_NAME=t GIT_COMMITTER_EMAIL=t@t FACTORY_SOURCED=1 FACTORY_ROOT="$PWD" FACTORY_RUNS_ROOT="$d/runs" bash -c '. bin/factory; finish() { echo "FINISH $*"; exit 3; }; RUN=$1/run; LOG="$RUN/factory.log"; LEDGER="$RUN/ledger.jsonl"; WORKTREE=$1/wt; BRANCH=factory/t; check_pushes && push_branch && check_pushes && echo CLEAN && git -C "$WORKTREE" commit -q --allow-empty -m two && git -C "$WORKTREE" push -q origin HEAD:refs/heads/factory/t && check_pushes; echo "RETURNED $?"' bin/factory "$d" 2>&1) ; grep -q '^CLEAN$' <<<"$out" && grep -q '^FINISH stopped-environment .*not pushed by the supervisor' <<<"$out" && pass supervisor-push-passes || fail supervisor-push-passes "check_pushes must pass before any push and after push_branch, then stop the run once a later commit is pushed outside push_branch; got: $out"
guard bin/check >/dev/null && pass check-green || fail check-green "bin/check"
```

## Worker
worker: claude
codex-review: yes
effort: high
contract: 2
goal: the done-checks block prints no FAIL line, or stop after 60 turns

## Decisions
Owner ruling 12 Nov 2026 19:58 PT, NEEDS-SAMYAK N21.2 (recorded in distbench `~/.local/state/distbench/evidence/2026-11-12-lean-plan/OWNER-ANSWERS.md` on jhaveris and in APPROVALS by SamyakJhaveri/distbench#509).
The gap as reported: the review of Loam PR 713 (its PR body, "Open, not fixed here").
Residual hole, accepted by the ruling: a worker push to another branch, or a push the worker later reverts by force-pushing the supervisor's sha back before the check runs, is not seen; the classifier remains the guard for both.
