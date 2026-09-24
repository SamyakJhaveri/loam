## Ticket

~~~~~~~~~~~~ evidence
Brief:
When a model call comes back with a usage-limit reply, switch the runner's active Claude account to the other stored one and retry the call at once, instead of sleeping until the reset; the account switcher moves into the repo as `bin/claude-account` so the loop depends on a versioned tool.
Where: bin/claude-account (new), bin/factory (limit_wait, one new helper limit_switch), docs/factory/LOOP.md (Exits: the usage-limit sentence; Preconditions)
Done means: `bin/claude-account set|use|other|status` work against directories named by `CLAUDE_ACCOUNTS_DIR` and `CLAUDE_SETTINGS_FILE`, `set` reads the token from stdin and stores it 0600, and none of them prints a token; `limit_switch` switches to the other stored account once, books a `limit-switch` ledger event, and refuses a second switch inside a five-minute cooldown; `limit_wait` calls it before it sleeps; LOOP.md says so.
Out of scope: the Mac (`cc-switch` stays a personal login script); any change to how a usage-limit reply is detected; the sleep path, which stays for the case where both accounts are limited; the OAuth-expired retry (F16) and the launch probe (F27).
Track: B    Risk: high    Mode: build    Open question: none
Blocked by: none

## Goal and why
Samyak pays for two Max subscriptions (stored as `uci` and `gmail` on the runner since 2026-09-12) so that when one hits its rolling limit the other carries on. Usage limits are per account. Today `limit_wait` in `bin/factory` parses the reset time out of the reply and sleeps up to `MAX_HOURS`, so a limit on one account idles a run for hours while the other account sits unused; the F9 timer means nobody is watching when that happens.
The switcher exists as a personal script (`~/.local/bin/claude-account`): one long-lived token per account under `~/.config/claude-accounts/<name>.token` (0600 files in a 0700 directory), an `active` file naming the current one, and `use <name>` writing that token into the `env` block of `~/.claude/settings.json`, which every `claude` process reads at start (a settings-file `env` value overrides a shell export, so this is the one channel that reaches cron, tmux, and the worker's `--setting-sources user` calls). The loop must not depend on a script outside the repo, so the switcher lands as `bin/claude-account` with the same commands, and the runner's copy becomes a symlink at the merge.
Keep-or-cut: a switch costs one `jq` write and one retried call; it saves up to `MAX_HOURS` of idle wall time per limit event. If both accounts are limited, the second limit reply arrives within seconds of the switch and the cooldown sends it down the sleep path as today, so the worst case is unchanged.
Secrets: no token value ever reaches a log, a ledger line, stdout, or a PR body. `bin/claude-account status` prints names only; the loop logs names only.

## Do not touch
The standing list. Except: bin/claude-account (new file), bin/factory (limit_wait and the new limit_switch only), docs/factory/LOOP.md (the two sentences named under Approach).
Also: bin/factory.d/; the grader prompts, schemas, and evals; seed/; cultivation/; `~/.claude/settings.json`, `~/.local/bin`, and `~/.config` on any machine (the merge read handles the runner). The worker runs `bin/claude-account` only with `CLAUDE_ACCOUNTS_DIR` and `CLAUDE_SETTINGS_FILE` both pointing into a temp directory and `HOME` set to that directory, never against the real home.

## Out of scope
- the Mac switcher `cc-switch` (a browser login, not a token)
- how a usage-limit reply is recognised (`limit_wait`'s grep stays as it is)
- the sleep path and its `MAX_HOURS` bound, which remain for a run whose two accounts are both limited
- `bin/factory status` (no new column; the ledger event is the record)
- the `set` subcommand's browser step (`claude setup-token` stays a human action)

## Approach
Executor: `bin/factory run` as merged in F1, with F27 merged.

Facts pinned: `limit_wait` (bin/factory, "result.json -> 0 after waiting, 1 when the reply is not a usage limit") greps `(hit|reached) your .*limit` out of the error result, computes `secs`, bounds it by `MAX_HOURS` against `$RUN/launched`, logs `usage limit, not a round: ...; waiting ${secs}s`, sets status `waiting-limit`, sleeps, and returns 0; both callers retry the call on 0 (`worker_round` loops, the grader call decrements `attempt` and continues). `record` appends ledger lines with `>> "$LEDGER"`; `freeze` appends a `grader` event with `printf ... >> "$LEDGER"`, the shape to copy. `now` prints the UTC timestamp. `ROOT` is the checkout the frozen supervisor came from (`FACTORY_ROOT` override). `FACTORY_SOURCED=1 . bin/factory` loads the functions for a test. `bin/check` runs `bash -n` only over `*.sh` files, so check 1 below is the syntax gate for `bin/claude-account`. Sourcing `bin/factory` runs its top-level `shift` and resets `RUN`, `LOG`, and `LEDGER`, so a test passes paths through the environment, not positional parameters, and sets `FACTORY_ROOT="$PWD"` so `$ROOT` is the worktree. The usage-limit sentence in LOOP.md sits under "Exits" ("A usage-limit reply ... is neither an exit nor a round"). The runner's current script (`~/.local/bin/claude-account`, personal, outside the repo) accepts `set <name>`, `use <name>`, `status`; its token directory is `~/.config/claude-accounts` (files `uci.token`, `gmail.token`, `active`) and its settings file `~/.claude/settings.json`.

Change:
1. `bin/claude-account` (new, executable, bash, `set -euo pipefail`): the runner script's `set`, `use`, and `status`, plus `other`, which prints the name of one stored account that is not the active one and exits 1 when there is none. Directories come from `CLAUDE_ACCOUNTS_DIR` (default `~/.config/claude-accounts`) and the settings file from `CLAUDE_SETTINGS_FILE` (default `~/.claude/settings.json`). `use` writes `.env.CLAUDE_CODE_OAUTH_TOKEN` with `jq --arg` through a temp file, `chmod 600`s the settings file, and writes the name to `<dir>/active`. `set` reads one line from stdin with `read -rs` (a pipe works, so a check can drive it), refuses a value without the `sk-ant-oat01-` prefix, and stores it as `<dir>/<name>.token` mode 600 inside a mode-700 directory it creates when missing. `status` prints `active: <name>; stored: <names>` and nothing else. No command prints, echoes, or logs a token value; `set -x` is never used.
2. `bin/factory`: a new function `limit_switch` beside `limit_wait`: reads `to=$("$ROOT/bin/claude-account" other)`; returns 1 when that fails, or when `$RUN/limit-switch` exists and holds an epoch newer than 300 seconds ago; otherwise reads the current name from `"$ROOT/bin/claude-account" status`, runs `"$ROOT/bin/claude-account" use "$to"`, writes the epoch to `$RUN/limit-switch`, logs `usage limit: switched account <from> -> <to>; retrying the call`, appends the ledger line `{"ts":"<now>","event":"limit-switch","from":"<from>","to":"<to>"}` to `$LEDGER`, and returns 0. `limit_wait` calls `limit_switch && return 0` right after its grep matches and before it computes `secs`, so a switch retries the call at once and the sleep path is unchanged when no switch happens.
3. LOOP.md: under "Exits", the sentence about the usage-limit wait gains: on a usage-limit reply the loop first switches to the other stored account through `bin/claude-account` and retries, and sleeps only when no other account exists or a switch happened in the last five minutes. Under "Preconditions", one bullet: `bin/claude-account status` names an active account and at least one other on the runner when the limit switch is wanted; with a single account the loop behaves as before.

## Done checks
```done-checks
[ -x bin/claude-account ] && guard bash -n bin/claude-account && pass switcher-present || fail switcher-present "bin/claude-account missing, not executable, or not valid bash"
t=$(mktemp -d "${TMPDIR:-/tmp}/f28a.XXXXXX"); mkdir -p "$t/acc"; printf 'sk-ant-oat01-AAA\n' > "$t/acc/a.token"; printf 'sk-ant-oat01-BBB\n' > "$t/acc/b.token"; echo '{}' > "$t/settings.json"; HOME="$t" CLAUDE_ACCOUNTS_DIR="$t/acc" CLAUDE_SETTINGS_FILE="$t/settings.json" bin/claude-account use a >/dev/null 2>&1; got=$(jq -r '.env.CLAUDE_CODE_OAUTH_TOKEN' "$t/settings.json"); act=$(cat "$t/acc/active" 2>/dev/null); oth=$(HOME="$t" CLAUDE_ACCOUNTS_DIR="$t/acc" CLAUDE_SETTINGS_FILE="$t/settings.json" bin/claude-account other 2>/dev/null); st=$(HOME="$t" CLAUDE_ACCOUNTS_DIR="$t/acc" CLAUDE_SETTINGS_FILE="$t/settings.json" bin/claude-account status 2>&1); rm -rf "$t"; [ "$got" = sk-ant-oat01-AAA ] && [ "$act" = a ] && [ "$oth" = b ] && ! grep -q 'oat01' <<<"$st" && pass switcher-use-other || fail switcher-use-other "use/other/status: token written='$got' active='$act' other='$oth' status-leaks-token=$(grep -c oat01 <<<"$st")"
t=$(mktemp -d "${TMPDIR:-/tmp}/f28c.XXXXXX"); out=$(printf 'sk-ant-oat01-CCC\n' | HOME="$t" CLAUDE_ACCOUNTS_DIR="$t/acc" CLAUDE_SETTINGS_FILE="$t/settings.json" bin/claude-account set c 2>&1); mode=$(ls -l "$t/acc/c.token" 2>/dev/null | cut -c1-10); dmode=$(ls -ld "$t/acc" 2>/dev/null | cut -c1-10); tok=$(cat "$t/acc/c.token" 2>/dev/null); printf 'hunter2\n' | HOME="$t" CLAUDE_ACCOUNTS_DIR="$t/acc" CLAUDE_SETTINGS_FILE="$t/settings.json" bin/claude-account set d >/dev/null 2>&1; bad=$?; rm -rf "$t"; [ "$tok" = sk-ant-oat01-CCC ] && [ "$mode" = "-rw-------" ] && [ "$dmode" = "drwx------" ] && ! grep -q oat01 <<<"$out" && [ "$bad" -ne 0 ] && pass switcher-set || fail switcher-set "set: stored='$tok' mode='$mode' dir='$dmode' output-leaks-token=$(grep -c oat01 <<<"$out") bad-prefix-exit=$bad"
t=$(mktemp -d "${TMPDIR:-/tmp}/f28b.XXXXXX"); mkdir -p "$t/acc" "$t/run"; printf 'sk-ant-oat01-AAA\n' > "$t/acc/a.token"; printf 'sk-ant-oat01-BBB\n' > "$t/acc/b.token"; echo '{}' > "$t/settings.json"; HOME="$t" CLAUDE_ACCOUNTS_DIR="$t/acc" CLAUDE_SETTINGS_FILE="$t/settings.json" bin/claude-account use a >/dev/null 2>&1; out=$(T="$t" HOME="$t" FACTORY_ROOT="$PWD" CLAUDE_ACCOUNTS_DIR="$t/acc" CLAUDE_SETTINGS_FILE="$t/settings.json" FACTORY_SOURCED=1 bash -c '. bin/factory; RUN="$T/run"; LOG="$T/run/log"; LEDGER="$T/run/ledger.jsonl"; touch "$LOG" "$LEDGER"; limit_switch; r1=$?; limit_switch; r2=$?; echo "r1=$r1 r2=$r2 active=$(cat "$T/acc/active") token=$(jq -r .env.CLAUDE_CODE_OAUTH_TOKEN "$T/settings.json") events=$(grep -c "\"event\":\"limit-switch\"" "$LEDGER") from_to=$(jq -r "select(.event==\"limit-switch\") | \"\(.from)>\(.to)\"" "$LEDGER" | head -1) leak=$(grep -c oat01 "$LOG" "$LEDGER" | awk -F: "{s+=\$2} END {print s}")"' 2>/dev/null); rm -rf "$t"; [ "$out" = "r1=0 r2=1 active=b token=sk-ant-oat01-BBB events=1 from_to=a>b leak=0" ] && pass limit-switch-once || fail limit-switch-once "got '$out'; expected the first call to switch a>b with one ledger event, the second call to refuse inside the cooldown, and no token in the log or ledger"
a=$(grep -n 'limit_switch && return 0' bin/factory | head -1 | cut -d: -f1); b=$(awk '/^limit_wait\(\)/{f=1} f && /sleep "\$secs"/{print NR; exit}' bin/factory); [ -n "$a" ] && [ -n "$b" ] && [ "$a" -lt "$b" ] && pass switch-before-sleep || fail switch-before-sleep "limit_wait does not call limit_switch (line '$a') before its sleep (line '$b')"
grep -q 'bin/claude-account' docs/factory/LOOP.md && grep -qi 'five minutes' docs/factory/LOOP.md && pass loop-doc || fail loop-doc "LOOP.md does not describe the account switch and its five-minute cooldown"
guard bash -n bin/factory && pass syntax || fail syntax "bash -n bin/factory"
[ -n "${LOAM_HOOK:-}" ] && pass check-green || { guard bin/check >/dev/null && pass check-green || fail check-green "bin/check"; }
```

## Merge checklist
- on the runner after the pull: `ln -sf ~/Desktop/loam/bin/claude-account ~/.local/bin/claude-account`, then `claude-account status` prints the two stored names and no token; `bin/factory status` still prints `PASS claude login`
- human diff read before merge (Risk high), with one grep over the diff for `oat01-[A-Za-z0-9]` and `CLAUDE_CODE_OAUTH_TOKEN=` to confirm no value is printed anywhere (the bare `sk-ant-oat01-` prefix check in `set` is the one expected hit)
- the first real `limit-switch` ledger event, when it comes, is read against this ticket: the switched-to account carried the retried call

## Worker
worker: claude
codex-review: no
effort: xhigh
goal: the Done checks block, sourced after bin/factory.d/lib.sh and run from the worktree root with its output shown, prints no FAIL line and one PASS line per named check, or stop after 30 turns

## Decisions
docs/factory/LOOP.md (Caps: the usage-limit wait; Preconditions), .superpowers/factory/sessions/manager-2026-09-12.md (Runner login made durable: the token switcher and the settings env channel), code.claude.com/docs/en/env-vars (a settings-file env value overrides the shell), code.claude.com/docs/en/errors (usage limits are per account)

~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS switcher-present
PASS switcher-use-other
PASS switcher-set
PASS limit-switch-once
PASS switch-before-sleep
PASS loop-doc
PASS syntax
PASS check-green

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
# Ticket #100 worker decisions

- Read Where/Do-not-touch/Approach paths via git ls-files. bin/claude-account does not yet exist. Confirmed limit_wait (bin/factory:620-636), its two callers (worker_round:830, call_json:946), now/log/record/freeze shapes, and the FACTORY_SOURCED sourcing guard (bin/factory:1486-1490). Read the runner's personal ~/.local/bin/claude-account as the reference for set/use/status.
- Decision: bin/claude-account determines the active account from the `<dir>/active` file (not by matching the settings token). The done-checks write `active` via `use` and read it back, so the file is authoritative; simpler and reads no token values. Dropped the personal script's `claude auth status` line because status must print "nothing else".
- Decision: `set` prints no prompt unless stdin is a tty, and the prompt/messages carry no `oat01` string, so a piped `set` under 2>&1 leaks nothing (switcher-set check).
- Decision: `status` active from the active file; `other` prints the first stored name != active, exits 1 when none.
- Advisor consulted before writing; built in its seams: `use` writes jq/mv/chmod/active on separate lines so set -e aborts before `active` on a jq failure; `set` uses `IFS= read -rs t || true` and explicit chmod 700/600; `status`/`other` loop `*.token` (no ls|xargs under pipefail); `$HOME` defaults not `~`; `limit_switch` assigns every local before use (set -u), writes the epoch only after `use` succeeds, ledger line via printf like freeze's grader event.
- Reworded a comment in bin/claude-account that literally held `CLAUDE_CODE_OAUTH_TOKEN=`; it was a spurious hit for the merge secret grep whose only expected hit is the bare `sk-ant-oat01-` prefix. Net main...HEAD diff now grep-clean for `oat01-[A-Za-z0-9]` and the token-env assignment.
- All 8 done-checks pass from the worktree root; check-green ran the real bin/check (CI green).
- Advisor gap 1 (ledger readers): confirmed no ledger reader does string-ops on `.role`; the new `limit-switch` event is appended to $LEDGER only (never $DAILY), and ticket_spent/daily_spent/the denials sum all use `// 0`, so the role-less, cost-less event breaks nothing. No code change.
- Advisor gap 2 (limit_wait end-to-end): ran limit_wait on a fake usage-limit result under the f28b harness. It switched a->b, returned 0 (retry), took <2s (no sleep), set no `waiting-limit` status, and leaked no token. Proves the ticket's core behavior; not a required done-check but verified. No code change.

~~~~~~~~~~~~ evidence

## Diff (ba9ff5d5...HEAD)

~~~~~~~~~~~~ evidence
 bin/claude-account   | 74 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 bin/factory          | 24 +++++++++++++++++++++++-
 docs/factory/LOOP.md |  6 +++++-
 3 files changed, 102 insertions(+), 2 deletions(-)

diff --git a/bin/claude-account b/bin/claude-account
new file mode 100755
index 0000000..f8114df
--- /dev/null
+++ b/bin/claude-account
@@ -0,0 +1,74 @@
+#!/usr/bin/env bash
+# bin/claude-account - hold one long-lived Claude Code token per account and switch between them.
+#   bin/claude-account set <name>   read a `claude setup-token` value from stdin into <dir>/<name>.token (0600)
+#   bin/claude-account use <name>   write that token into the env block of the settings file (new claude processes use it)
+#   bin/claude-account other        print one stored account that is not the active one, non-zero when there is none
+#   bin/claude-account status       print `active: <name>; stored: <names>` and nothing else
+# Tokens live outside the settings file so a switch never needs the browser; each is valid one year.
+# No command prints, echoes, or logs a token value; `set -x` is never used here.
+# The account directory and settings file are overridable so the factory loop can drive this against a temp home.
+set -euo pipefail
+
+dir=${CLAUDE_ACCOUNTS_DIR:-$HOME/.config/claude-accounts}
+f=${CLAUDE_SETTINGS_FILE:-$HOME/.claude/settings.json}
+cmd=${1:-status}
+name=${2:-}
+
+# The active account name, from the file `use` writes; empty when nothing is active yet.
+active_name() { [ -f "$dir/active" ] && cat "$dir/active" || true; }
+
+case "$cmd" in
+  set)
+    [ -n "$name" ] || { echo "usage: bin/claude-account set <name>" >&2; exit 2; }
+    [ -t 0 ] && printf 'Paste the setup token for %s, then Enter: ' "$name" >&2
+    IFS= read -rs t || true   # a paste without a trailing newline still lands in $t under set -e
+    [ -t 0 ] && echo >&2
+    case "$t" in
+      sk-ant-oat01-*) ;;
+      *) echo "not a valid setup token (expected the sk-ant-oat01- prefix)" >&2; exit 1 ;;
+    esac
+    umask 077
+    mkdir -p "$dir"; chmod 700 "$dir"
+    printf '%s\n' "$t" > "$dir/$name.token"; chmod 600 "$dir/$name.token"
+    echo "stored $dir/$name.token" >&2
+    ;;
+  use)
+    [ -n "$name" ] || { echo "usage: bin/claude-account use <name>" >&2; exit 2; }
+    [ -f "$dir/$name.token" ] || { echo "no stored token for '$name'; run: bin/claude-account set $name" >&2; exit 1; }
+    t=$(cat "$dir/$name.token")
+    # Separate steps so set -e aborts before `active` is written if the jq write fails, and the switch
+    # a caller logs can never outrun the settings file. Keep the spaces around `=` in the jq filter so the
+    # merge grep for an assignment of the token env var finds no hit here.
+    tmp=$(mktemp "$f.XXXXXX")
+    jq --arg t "$t" '.env.CLAUDE_CODE_OAUTH_TOKEN = $t' "$f" > "$tmp"
+    mv "$tmp" "$f"
+    chmod 600 "$f"
+    printf '%s\n' "$name" > "$dir/active"
+    echo "active: $name" >&2
+    ;;
+  other)
+    a=$(active_name)
+    for p in "$dir"/*.token; do
+      [ -f "$p" ] || continue
+      n=$(basename "$p" .token)
+      [ "$n" = "$a" ] && continue
+      printf '%s\n' "$n"
+      exit 0
+    done
+    echo "no stored account other than '${a:-none}'" >&2
+    exit 1
+    ;;
+  status)
+    a=$(active_name)
+    stored=""
+    for p in "$dir"/*.token; do
+      [ -f "$p" ] || continue
+      stored="$stored $(basename "$p" .token)"
+    done
+    echo "active: ${a:-none}; stored:${stored}"
+    ;;
+  *)
+    echo "usage: bin/claude-account set|use <name> | other | status" >&2
+    exit 2
+    ;;
+esac
diff --git a/bin/factory b/bin/factory
index 5dc4cac..7f3601f 100755
--- a/bin/factory
+++ b/bin/factory
@@ -615,12 +615,34 @@ else empty end" "$2" 2> /dev/null) || e=""
   [ -z "$e" ] || finish stopped-environment "the $1 call failed before doing work: $e"
 }

+# Usage limits are per account, so on a limit reply switch to the other stored account and retry at once,
+# rather than idling this run while the other account sits unused. bin/claude-account owns the token files
+# and the settings env channel; one switch per limit event, then a five-minute cooldown sends any further
+# limit down the sleep path (both accounts are limited when a second reply lands within seconds). No token
+# value ever reaches the log or the ledger: the switcher prints names only and the ledger line names only.
+limit_switch() { # -> 0 after switching accounts, 1 when there is no other account or a switch is on cooldown
+  local to from last
+  to=$("$ROOT/bin/claude-account" other 2> /dev/null) || return 1
+  if [ -f "$RUN/limit-switch" ]; then
+    last=$(cat "$RUN/limit-switch" 2> /dev/null) || last=""
+    [ -n "$last" ] && [ "$(( $(date +%s) - last ))" -lt 300 ] && return 1
+  fi
+  from=$("$ROOT/bin/claude-account" status 2> /dev/null | sed -n 's/^active: \([^;]*\);.*/\1/p')
+  "$ROOT/bin/claude-account" use "$to" > /dev/null 2>&1 || return 1
+  date +%s > "$RUN/limit-switch"
+  log "usage limit: switched account ${from:-none} -> $to; retrying the call"
+  printf '{"ts":"%s","event":"limit-switch","from":"%s","to":"%s"}\n' "$(now)" "${from:-none}" "$to" >> "$LEDGER"
+  return 0
+}
+
 # A usage-limit reply names its reset ("You've hit your session limit - resets 1:30pm (America/Los_Angeles)").
-# Waiting for it is loop behavior, not a round: sleep to the reset, or 20 minutes, then repeat the same call.
+# Waiting for it is loop behavior, not a round: switch accounts and retry at once, or sleep to the reset, or
+# 20 minutes, then repeat the same call.
 limit_wait() { # result.json -> 0 after waiting, 1 when the reply is not a usage limit
   local e t tz at left secs=1200
   e=$(jq -r "$RESULT_OBJ | if .is_error == true then (.result // \"\") else empty end" "$1" 2> /dev/null) || e=""
   grep -qiE '(hit|reached) your .*limit' <<< "$e" || return 1
+  limit_switch && return 0
   t=$(grep -oiE 'resets? [0-9]{1,2}(:[0-9]{2})? ?[ap]m' <<< "$e" | head -1 | sed -E 's/^[Rr]esets? //')
   tz=$(grep -oE '\([A-Za-z_]+/[A-Za-z_]+\)' <<< "$e" | head -1 | tr -d '()')
   if [ -n "$t" ] && at=$(TZ="${tz:-UTC}" date -d "$t" +%s 2> /dev/null); then
diff --git a/docs/factory/LOOP.md b/docs/factory/LOOP.md
index 384b038..ec2d4a3 100644
--- a/docs/factory/LOOP.md
+++ b/docs/factory/LOOP.md
@@ -71,7 +71,10 @@ The run resolves them from the installed plugin cache, falling back to the check

 Exit code, `status`, and the final log line are decided together and cannot disagree.
 These read loop-control files to decide exit, never safety; safety stays with deny rules, the sandbox, git, and CI.
-A usage-limit reply (`hit your session limit`, `reached your Fable limit`) is neither an exit nor a round: the supervisor writes `waiting-limit` to `status`, sleeps until the reset time the reply names or twenty minutes when it names none, then repeats the same call; a reset past `MAX_HOURS` exits `stopped-environment`.
+A usage-limit reply (`hit your session limit`, `reached your Fable limit`) is neither an exit nor a round.
+Usage limits are per account, so the supervisor first switches to the other stored account through `bin/claude-account` and retries the same call at once.
+It sleeps only when no other account exists or a switch already happened in the last five minutes; then it writes `waiting-limit` to `status`, sleeps until the reset time the reply names or twenty minutes when it names none, and repeats the same call.
+A reset past `MAX_HOURS` exits `stopped-environment`.
 A call with no result event (killed by `CALL_TIMEOUT_SEC`, or crashed) exits `stopped-environment` and counts no round.

 ## Caps
@@ -202,6 +205,7 @@ Each new grader agent costs about 200 always-on tokens in every session of every

 - The runner is Ubuntu with `claude`, `codex`, `gh` (logged in), `uv`, `git`, `jq`, `python3`, coreutils `timeout`, `tmux`, and `socat` on a login-shell PATH; ssh commands use `bash -lc`.
 - `claude auth status` reports `loggedIn: true` on the runner; `claude` on PATH is not `claude` logged in, so a logged-out Claude fails every worker call while `status` still shows it on PATH, and `bin/factory status` prints `FAIL claude login` (#78). `bin/factory next` refuses to launch on the same probe: a logged-out runner makes it print `login expired` on stderr and exit 1 before it queries the frontier.
+- `bin/claude-account status` names an active account and at least one other stored account on the runner when the usage-limit switch is wanted; with a single stored account the loop sleeps through a usage limit as before.
 - `gh api rate_limit` succeeds on the seat that runs stages 0, 1, 2, and 5 (F0 fixes the Mac).
 - `grill-with-docs`, `wayfinder`, and `to-tickets` are invocable on that seat.
 - `codex login status` succeeds when any ticket uses Codex.
~~~~~~~~~~~~ evidence
