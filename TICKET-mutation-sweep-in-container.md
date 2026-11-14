# factory: the mutation sweep runs each pytest run in a disposable container, never on the host
Brief:
Where: `bin/factory.d/mutation_sweep.py` (`run`, `main`, `stop`, and the process-group code it replaces), `bin/factory` (`cmd_next`'s env forwarding, `cmd_run`'s launch log), `bin/tests/test_factory_mutation_sweep.py`, `docs/factory/LOOP.md` (Mutation sweep).
Done means: with `FACTORY_SWEEP_IMAGE` set, the baseline and every mutant run inside a disposable container, so a mutant that SIGKILLs a host process group or deletes a host file reaches neither; with it unset the sweep runs no test and its reason says so; a container that cannot start stops the run, never falls back to the host.
Out of scope: the image a target uses (each target's launcher sets it), the landing gate and the worker's own checks, in-code kill guards in any target.
Track: B    Risk: high (a mutant run on the host SIGKILLed every samyak process on jhaveris, 13 Nov 18:55 PT)    Mode: build    Open question: none
Edit: `bin/factory.d/mutation_sweep.py`, `bin/tests/test_factory_mutation_sweep.py`, `bin/factory`, `docs/factory/LOOP.md`
Blocked by: none

## Goal and why
On 13 Nov a distbench run (R543) passed its round-2 checks and the sweep wrote a force-true mutant into `end_orphans` (`if (int(fields[3]) in sessions) or True:` in `src/distbench/runner.py`), then ran `python3 -m pytest -q -x -p no:cacheprovider tests/test_runner.py` on the host.
That mutant SIGKILLs every process group in `/proc` but 0, 1 and its own: 50 s later every samyak process on jhaveris was dead (the user manager, gdm's session, sshd's user side, every tmux server, every factory run, the landing gate).
`run` (`mutation_sweep.py:449-474`) starts pytest with `start_new_session=True` (`:458-459`), the subreaper and `kill_orphans` (`:400-446`) only clean up after it: none bounds what a test signals or deletes.
A PID namespace and a filesystem of its own are the one bound a mutant cannot edit; the next ticket of this kind is already queued (a distbench `sweep.sh remove` that deletes a user's files under `/tmp` and the home).
Evidence on jhaveris: `~/.local/state/distbench/evidence/2026-11-13-lean/host-kill/CAUSE.md` and `proof/` (the mutant reproduced in a container), `mutant-left-in-worktree.diff`.

## Do not touch
The standing list.
Except: `bin/factory` (this ticket forwards and logs `FACTORY_SWEEP_IMAGE`), `bin/factory.d/mutation_sweep.py` (this ticket's subject).

## Out of scope
Building or choosing any target's sweep image; distbench sets its own in its launcher.
Moving the landing gate (`bin/check`) or the worker's checks into containers.
In-code kill or delete guards in a target's code (distbench files its own).
The sweep's operators, edit choice, ordering, `MAX_EDITS` and result shape.

## Approach
1. Subtract first: delete `kill_group`, `subreaper`, `kill_orphans`, `SUBREAPER` and `start_new_session`, and the LOOP.md lines on the session and the subreaper; ending the container ends every process in its namespace, so no host-side process cleanup stays.
2. Every pytest run, the baseline included, runs in a fresh container of `FACTORY_SWEEP_IMAGE`: `--network none`, Docker's own PID namespace, `--user` the helper's uid and gid, `HOME` and `/tmp` inside the container, a pids and a memory cap, and the sweep worktree copied in (`docker create`, `docker cp`, `docker start -a`, as a prototype did); no host path is writable from the container.
3. One container name per sweep worktree, fixed (`loam-sweep-` and 12 hex of the sha256 of its resolved path): `docker rm -f` that name before each run, after it, on a timeout and in `stop`; a sweep killed mid-run leaves a container the next sweep of that worktree removes. Never select containers by a filter or a comparison, so no flip or force-true of the sweep's own code can remove another container.
4. `FACTORY_SWEEP_IMAGE` unset or empty: no run, `mutants` empty, `reason` `FACTORY_SWEEP_IMAGE is unset; the sweep never runs tests on the host` (a result, as `no committed test in the diff` is). Set, but `docker` missing or the container failing to start: the helper exits non-zero, which `run_mutation_sweep` already turns into `stopped-environment` (`bin/factory:3165-3168`).
5. `bin/factory`: `cmd_next` forwards `FACTORY_SWEEP_IMAGE` to the tmux session as it forwards `FACTORY_JUDGE` (`:4333`); `cmd_run` logs it once at launch. The result shape and the killed-or-survived rule do not change; a timeout counts container start.
6. Tests: the helper tests set `FACTORY_SWEEP_IMAGE` to an image built once per class from `python:3.12-slim` plus pytest and run only where `docker` exists, marked as the Linux-only tests are; keep the endless-loop and orphan tests as behavior (no process outlives the sweep). A new test uses the done checks' fixture. A test fixture signals or deletes only what the test itself made: never a loop over `/proc`, never `kill -1`; this ticket's own sweep runs on the host with the old helper.

## Done checks
Every line here, predicts included, is safe on the host at base: the fixture's one mutant signals only the sentinel `sleep` its own line started and deletes only the file its own line planted.
A fixture that signals every group in `/proc` (the 13 Nov shape) runs only inside a container until this lands.
At base the sweep runs the mutant on the host, so the sentinel dies and the planted file goes; after the fix both stay.
Proof of both outcomes, each run inside a container: base `main` 5459b047 prints `FAIL contained` and `FAIL no-image` with both predicts exiting 0; a prototype of steps 2 and 4 prints `PASS contained` and `PASS no-image`.
```done-checks
guard docker build -q -t loam-sweep-check - <<< $'FROM python:3.12-slim\nRUN pip install -q pytest' > /dev/null && pass image || fail image "could not build the check image loam-sweep-check from python:3.12-slim"
predict contained d=$(mktemp -d); setsid sleep 600 & s=$!; touch "$d/planted"; git init -q "$d/r" && printf 'def act(flag):\n    pass\n' > "$d/r/victim.py" && git -C "$d/r" add -A && git -C "$d/r" -c user.name=t -c user.email=t@t commit -qm base && b=$(git -C "$d/r" rev-parse HEAD) && printf 'import contextlib\nimport os\nfrom pathlib import Path\n\n\ndef act(flag):\n    if flag:\n        with contextlib.suppress(OSError):\n            os.killpg(%d, 9)\n        with contextlib.suppress(OSError):\n            Path("%s").unlink()\n' "$s" "$d/planted" > "$d/r/victim.py" && printf 'from victim import act\n\n\ndef test_act():\n    act(False)\n' > "$d/r/test_victim.py" && git -C "$d/r" add -A && git -C "$d/r" -c user.name=t -c user.email=t@t commit -qm head; FACTORY_SWEEP_IMAGE=loam-sweep-check python3 -I bin/factory.d/mutation_sweep.py "$d/r" "$b" "$d/out.json" 600; ! { kill -0 "$s" 2> /dev/null && [ -e "$d/planted" ]; }; ok=$?; kill "$s" 2> /dev/null; exit $ok
predict no-image d=$(mktemp -d); setsid sleep 600 & s=$!; touch "$d/planted"; git init -q "$d/r" && printf 'def act(flag):\n    pass\n' > "$d/r/victim.py" && git -C "$d/r" add -A && git -C "$d/r" -c user.name=t -c user.email=t@t commit -qm base && b=$(git -C "$d/r" rev-parse HEAD) && printf 'import contextlib\nimport os\nfrom pathlib import Path\n\n\ndef act(flag):\n    if flag:\n        with contextlib.suppress(OSError):\n            os.killpg(%d, 9)\n        with contextlib.suppress(OSError):\n            Path("%s").unlink()\n' "$s" "$d/planted" > "$d/r/victim.py" && printf 'from victim import act\n\n\ndef test_act():\n    act(False)\n' > "$d/r/test_victim.py" && git -C "$d/r" add -A && git -C "$d/r" -c user.name=t -c user.email=t@t commit -qm head; env -u FACTORY_SWEEP_IMAGE python3 -I bin/factory.d/mutation_sweep.py "$d/r" "$b" "$d/out.json" 600; ! { kill -0 "$s" 2> /dev/null && [ -e "$d/planted" ]; }; ok=$?; kill "$s" 2> /dev/null; exit $ok
d=$(mktemp -d); setsid sleep 600 & s=$!; touch "$d/planted"; git init -q "$d/r" && printf 'def act(flag):\n    pass\n' > "$d/r/victim.py" && git -C "$d/r" add -A && git -C "$d/r" -c user.name=t -c user.email=t@t commit -qm base && b=$(git -C "$d/r" rev-parse HEAD) && printf 'import contextlib\nimport os\nfrom pathlib import Path\n\n\ndef act(flag):\n    if flag:\n        with contextlib.suppress(OSError):\n            os.killpg(%d, 9)\n        with contextlib.suppress(OSError):\n            Path("%s").unlink()\n' "$s" "$d/planted" > "$d/r/victim.py" && printf 'from victim import act\n\n\ndef test_act():\n    act(False)\n' > "$d/r/test_victim.py" && git -C "$d/r" add -A && git -C "$d/r" -c user.name=t -c user.email=t@t commit -qm head; FACTORY_SWEEP_IMAGE=loam-sweep-check python3 -I bin/factory.d/mutation_sweep.py "$d/r" "$b" "$d/out.json" 600 > "$d/log" 2>&1; kill -0 "$s" 2> /dev/null && [ -e "$d/planted" ] && jq -e '.baseline_sec != null and (.mutants | length) == 1' "$d/out.json" > /dev/null; ok=$?; kill "$s" 2> /dev/null; [ $ok = 0 ] && pass contained || fail contained "a sweep with FACTORY_SWEEP_IMAGE set killed a host process or deleted a host file its mutant named, or ran no mutant; evidence in $d"
d=$(mktemp -d); setsid sleep 600 & s=$!; touch "$d/planted"; git init -q "$d/r" && printf 'def act(flag):\n    pass\n' > "$d/r/victim.py" && git -C "$d/r" add -A && git -C "$d/r" -c user.name=t -c user.email=t@t commit -qm base && b=$(git -C "$d/r" rev-parse HEAD) && printf 'import contextlib\nimport os\nfrom pathlib import Path\n\n\ndef act(flag):\n    if flag:\n        with contextlib.suppress(OSError):\n            os.killpg(%d, 9)\n        with contextlib.suppress(OSError):\n            Path("%s").unlink()\n' "$s" "$d/planted" > "$d/r/victim.py" && printf 'from victim import act\n\n\ndef test_act():\n    act(False)\n' > "$d/r/test_victim.py" && git -C "$d/r" add -A && git -C "$d/r" -c user.name=t -c user.email=t@t commit -qm head; env -u FACTORY_SWEEP_IMAGE python3 -I bin/factory.d/mutation_sweep.py "$d/r" "$b" "$d/out.json" 600 > "$d/log" 2>&1; kill -0 "$s" 2> /dev/null && [ -e "$d/planted" ] && jq -e '(.mutants | length) == 0 and (.reason | test("FACTORY_SWEEP_IMAGE"))' "$d/out.json" > /dev/null; ok=$?; kill "$s" 2> /dev/null; [ $ok = 0 ] && pass no-image || fail no-image "a sweep with FACTORY_SWEEP_IMAGE unset ran a test on the host or gave no reason naming FACTORY_SWEEP_IMAGE; evidence in $d"
guard bin/check > /dev/null && pass check-green || fail check-green "bin/check"
```

## Merge checklist
- Distbench sets `FACTORY_SWEEP_IMAGE` in `bin/factory-isc` to an image with its test dependencies (a distbench ticket; `distbench-agent` runs `tests/test_runner.py`), then confirms the next distbench run's `mutation sweep:` line in `factory.log` shows counts, not `not run`.
- Until both have landed, no factory mutation sweep runs on jhaveris for a diff that adds a line choosing a signal or deletion target (distbench R543, W32).

## Worker
worker: claude
codex-review: yes
effort: high
contract: 2
goal: the done-checks block prints no FAIL line, or stop after 60 turns

## Decisions
Host-kill analysis of 13 Nov 2026 (lead lean-night-1): the sender was this sweep's force-true mutant of distbench R543's `end_orphans`, reproduced in a container (CAUSE.md, `proof/out-mutant.txt`); a PID namespace is the guard a mutant cannot edit, in-code guards are defense in depth only.
Unset image means no sweep, not a host sweep: a target without an image loses the sweep visibly (`not run:` in the PR body) instead of risking the host.
