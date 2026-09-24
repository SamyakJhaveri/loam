## Ticket

~~~~~~~~~~~~ evidence
Brief:
Let the memory store follow the user to a second machine through git, so a session on jhaveris sees what a session on the Mac learned, and let one session leave a handoff that the next session on either harness or machine reads exactly once.
Where: seed/.claude/hooks/mem-capture.sh (commit and push after a capture), seed/.claude/hooks/mem-recall.sh (pull at start, handoff injection), seed/bin/mem-weekly.sh (the store's .gitignore keeps only the throttle-mark directory, so traces and INDEX.md are tracked; push after the weekly commit), seed/docs/HARNESS.md (the remote setup and the handoff path).
Done means: the done-checks block prints no FAIL line: a capture commits and pushes to a bare remote, a start pulls a commit made elsewhere, a start with an unreachable remote still prints the manifest and exits 0 within ten seconds, a handoff file is injected once and archived, the weekly run pushes, a fresh render carries all of it.
Out of scope: any third-party host; conflict resolution beyond append-only files; the note gate; Codex hooks beyond what MEM-02 wired.
Blocked by: MEM-04 merged (the scrub must land before anything is pushed).

## Goal and why
The per-user store is invisible on the runner today: jhaveris holds 80 MB of Claude sessions and 137 MB of Codex sessions and no store, so a session there starts with nothing (docs/research/memory-design-v2-2026-09-21.md, "What the evidence settled").
The store is already a git repository after mem-weekly.sh runs; giving it a bare remote on jhaveris over the ssh that bin/runner already uses shares it with no third party, and the store's files are append-only so a rebase never conflicts.
A claim-once handoff is the cheapest cross-harness, cross-machine continuity the literature supports: one writer per workstream, read once, archived, never a shared last-writer-wins file.
Decision: docs/research/memory-design-v2-2026-09-21.md (layer 3, picks R4 and Q4, Q7 of 2026-09-21).

## Do not touch
The standing list. Also: seed/AGENTS.md.jinja, seed/CLAUDE.md.jinja, seed/.claude/settings.json, seed/.claude/hooks/fable-session-brief.sh, seed/.claude/hooks/post-compact-reinject.sh, seed/.codex/, seed/.loam/, seed/.agents/, seed/bin/memsearch, seed/bin/mem-inspect, bin/factory, docs/architecture-working/.
Except: seed/.claude/hooks/mem-capture.sh, seed/.claude/hooks/mem-recall.sh, seed/bin/mem-weekly.sh (this ticket edits three MEM-01 scripts). If seed/.loam/runtime/assets/curated-catalog.json has gained a support: entry for any of them, add the catalog under Except in a decisions.md line and re-pin it as MEM-01 step 8 did.

## Out of scope
GitHub or any hosted remote; the remote is a path the user configures.
Merging or rewriting store files; on a pull conflict the hook logs one line to `$STORE/reports/sync.log` and leaves the working tree untouched.
The note gate (MEM-03), Codex hooks.json (MEM-02), the inspect command (MEM-04).
Any model call.

## Approach
Same conventions as MEM-01 and MEM-04: bash with `set -uo pipefail`, python3 for JSON and for any timed subprocess, no jq, hooks exit 0 always. Every git call runs with `-C "$STORE"` and `GIT_TERMINAL_PROMPT=0`. The store's branch is always `main`: initialize with `git init -q -b main`, and every push and pull names `origin main` explicitly, never a bare `HEAD` refspec. A remote is configured only when `$STORE` has an `origin` remote; without one every sync step is a no-op and the hooks behave exactly as MEM-04 left them.
MEM-01 as merged (PR #163, commit edbeb02) writes a traces line into the store's .gitignore so a deleted trace leaves no copy in git history. This ticket reverses that on purpose: the store syncs through git, INDEX.md lives under traces/, and MEM-04's scrub runs before any commit, so the design record's rule (traces gzipped a year, INDEX forever, scrubbed before commit) holds. Step 3 and step 4 carry the change; do not leave the traces line in the .gitignore, or every capture after the first weekly run stops syncing.
1. seed/.claude/hooks/mem-capture.sh: after a trace or INDEX line is newly written, `git init -q` the store when it is not a repository, `git add -A`, `git commit -qm "capture <date> <repo> <sid8>"`; when `origin` exists, push in the background and return at once: `( git -C "$STORE" push -q origin main >>"$STORE/reports/sync.log" 2>&1 & )`. The hook never waits on the network.
2. seed/.claude/hooks/mem-recall.sh: before building the manifest, when `origin` exists, run `git -C "$STORE" pull --rebase -q origin main` through `python3 -c 'import subprocess,sys; ...'` with `timeout=5`; on timeout or failure append one line to `$STORE/reports/sync.log` and continue with the local store. Then the handoff: when `$STORE/handoff/<repo>.md` exists, print `## Handoff (claimed now)` and the file (cut at 1500 bytes; the whole manifest stays under the 4000-byte cap, and the INDEX lines and hint bullets are trimmed before the handoff is), then move it to `$STORE/handoff/<repo>/archive/<date>-<sid8>.md`, commit, and background-push as in step 1. The manifest's `Loaded:` line from MEM-04 reports `1 handoff` when one was claimed. The `Not loaded:` line gains: `to hand off to the next session on any machine, write .loam/memory/handoff/<repo>.md`.
3. seed/bin/mem-weekly.sh: write the store's .gitignore with the throttle-mark directory only (drop the traces line and the comment that says traces stay out of git); after the weekly commit, when `origin` exists, `git pull --rebase -q origin main` then `git push -q origin main`, both foreground (cron, not a hook), logging to `reports/sync.log`.
4. seed/docs/HARNESS.md: a subsection "Sharing the store between machines": on the machine that will hold the remote, `git init --bare ~/memstore.git`; on every machine, `git -C ~/memstore remote add origin <host>:memstore.git` (an ssh alias such as `jhaveris`); the first capture on a new machine clones instead when `LOAM_MEMSTORE_REMOTE` is set and `~/memstore` is absent. State plainly: the remote holds scrubbed transcripts; keep it on a machine you own; never point it at a public host. Replace the Accepted risks sentences that say `traces/` is gitignored and a deleted transcript leaves no copy in git history with: traces are tracked and pushed once scrubbed; a secret with no recognizable shape can reach the store's history and the remote; forgetting a pushed trace means deleting the file, committing, and rewriting or reinitialising both the store repo and the remote. Describe the handoff path and the claim-once rule. Add one Always-on budget line: recall waits at most five seconds for a pull.
5. Commit as you go; render_into needs the commits.

## Done checks
```done-checks
guard bash -n seed/.claude/hooks/mem-capture.sh seed/.claude/hooks/mem-recall.sh seed/bin/mem-weekly.sh 2>/dev/null && pass scripts-present || fail scripts-present "a script is missing or fails bash -n"
tmp=$(mktemp -d); git -C "$tmp" init -q --bare remote.git; git -C "$tmp" init -q repo; store="$tmp/store"; mkdir -p "$store"; git -C "$store" init -q -b main; git -C "$store" remote add origin "$tmp/remote.git"; printf '{"type":"user","message":{"content":"sync probe one"}}\n' > "$tmp/t.jsonl"; printf '{"session_id":"abcdef1234","transcript_path":"%s/t.jsonl","cwd":"%s/repo"}' "$tmp" "$tmp" | LOAM_MEMSTORE="$store" seed/.claude/hooks/mem-capture.sh >/dev/null 2>&1; sleep 2; git -C "$tmp/remote.git" log --oneline 2>/dev/null | grep -q 'capture' && pass capture-pushes || fail capture-pushes "the bare remote has no capture commit two seconds after a capture"
git -C "$tmp" clone -q "$tmp/remote.git" other 2>/dev/null; mkdir -p "$tmp/other/traces/repo"; printf '2026-09-21 | elsewher | main@1111111 | otherhost | made elsewhere\n' >> "$tmp/other/traces/repo/INDEX.md"; git -C "$tmp/other" add -A; git -C "$tmp/other" -c user.email=t@t -c user.name=t commit -qm elsewhere; git -C "$tmp/other" push -q origin HEAD:main 2>/dev/null; out=$(printf '{"session_id":"x","cwd":"%s/repo"}' "$tmp" | LOAM_MEMSTORE="$store" seed/.claude/hooks/mem-recall.sh 2>/dev/null); grep -q 'made elsewhere' <<<"$out" && pass recall-pulls || fail recall-pulls "a line committed on another clone did not appear in the manifest after recall"
mkdir -p "$store/handoff"; printf 'HANDOFF probe: next step is X\n' > "$store/handoff/repo.md"; out1=$(printf '{"session_id":"h1h1h1h1h1","cwd":"%s/repo"}' "$tmp" | LOAM_MEMSTORE="$store" seed/.claude/hooks/mem-recall.sh 2>/dev/null); out2=$(printf '{"session_id":"h2h2h2h2h2","cwd":"%s/repo"}' "$tmp" | LOAM_MEMSTORE="$store" seed/.claude/hooks/mem-recall.sh 2>/dev/null); grep -q 'HANDOFF probe' <<<"$out1" && [ "${#out1}" -lt 4000 ] && ! grep -q 'HANDOFF probe' <<<"$out2" && [ ! -e "$store/handoff/repo.md" ] && ls "$store/handoff/repo/archive/"*h1h1h1h1*.md >/dev/null 2>&1 && pass handoff-once || fail handoff-once "the handoff was not injected exactly once and archived under the claiming session"
git -C "$store" remote set-url origin "$tmp/does-not-exist.git"; start=$(date +%s); out=$(printf '{"session_id":"x","cwd":"%s/repo"}' "$tmp" | LOAM_MEMSTORE="$store" seed/.claude/hooks/mem-recall.sh 2>/dev/null); s=$?; el=$(( $(date +%s) - start )); [ "$s" = 0 ] && [ "$el" -le 10 ] && grep -q '^Loaded:' <<<"$out" && grep -q . "$store/reports/sync.log" && pass offline-safe || fail offline-safe "recall exit $s after ${el}s, or no manifest, or no sync.log line with an unreachable remote"
git -C "$store" remote set-url origin "$tmp/remote.git"; LOAM_MEMSTORE="$store" seed/bin/mem-weekly.sh >/dev/null 2>&1; git -C "$tmp/remote.git" log --oneline 2>/dev/null | grep -q 'weekly' && pass weekly-pushes || fail weekly-pushes "the bare remote has no weekly commit after mem-weekly.sh"
if git -C "$store" check-ignore -q traces/repo/INDEX.md; then fail traces-tracked "mem-weekly.sh still gitignores traces, so captures after the weekly run never sync"; else printf '{"type":"user","message":{"content":"sync probe two"}}\n' > "$tmp/t2.jsonl"; printf '{"session_id":"bbbbbbbb22","transcript_path":"%s/t2.jsonl","cwd":"%s/repo"}' "$tmp" "$tmp" | LOAM_MEMSTORE="$store" seed/.claude/hooks/mem-capture.sh >/dev/null 2>&1; sleep 2; [ "$(git -C "$tmp/remote.git" log --oneline 2>/dev/null | grep -c capture)" -ge 2 ] && pass traces-tracked || fail traces-tracked "a capture after the weekly run did not reach the remote"; fi
grep -q 'memstore.git' seed/docs/HARNESS.md && grep -qi 'handoff' seed/docs/HARNESS.md && grep -q 'LOAM_MEMSTORE_REMOTE' seed/docs/HARNESS.md && ! tr '\n' ' ' < seed/docs/HARNESS.md | grep -qi 'leaves no copy in git history' && pass harness-doc || fail harness-doc "HARNESS.md does not describe the remote setup, the handoff, or LOAM_MEMSTORE_REMOTE, or still says a deleted trace leaves no copy in git history"
render_into; [ -n "$render_dir" ] || fail render "$render_err"; [ -x "$render_dir/.claude/hooks/mem-recall.sh" ] && grep -q 'pull --rebase' "$render_dir/.claude/hooks/mem-recall.sh" && grep -q 'Handoff (claimed now)' "$render_dir/.claude/hooks/mem-recall.sh" && grep -q 'push' "$render_dir/.claude/hooks/mem-capture.sh" && pass in-render || fail in-render "the rendered hooks lack the pull, the claimed-handoff heading, or the push"
[ -n "${LOAM_HOOK:-}" ] && pass check-green || { guard bin/check >/dev/null && pass check-green || fail check-green "bin/check"; }
```

## Merge checklist
- On jhaveris run `git init --bare ~/memstore.git`; on the Mac add the remote to ~/memstore; run one session on each machine and confirm the other machine's next manifest shows the new INDEX line.
- Write a handoff on the Mac, start a Codex session on jhaveris in the same repo, confirm it is claimed there and archived.

## Worker
worker: claude
codex-review: no
effort: xhigh
MAX_ROUNDS=3
ROUND_BUDGET_USD=20
goal: the done-checks block prints no FAIL line, or stop after 60 turns

## Decisions
docs/research/memory-design-v2-2026-09-21.md (layer 3, picks R4), docs/research/memory-design-2026-09-03.md (section 3, "Per-user store, git-tracked"), docs/architecture-working/tickets/README.md (Curation verdicts)

~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS scripts-present
PASS capture-pushes
PASS recall-pulls
PASS handoff-once
PASS offline-safe
PASS weekly-pushes
PASS traces-tracked
PASS harness-doc
PASS in-render
PASS check-green

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
# Ticket #165 decisions

- Opened every Where/Do-not-touch/Approach path with git ls-files. curated-catalog.json has NO support: entry for mem-capture/mem-recall/mem-weekly, so no catalog re-pin is needed (MEM-01 step 8 not repeated).
- Probe 1 (advisor): ran check-3 setup verbatim. init.defaultBranch=main here; bare remote HEAD=main; clone checks out main with content; push/pull origin main all succeed. check-3 works, no ABANDON.
- Probe 2 (advisor): grepped bin/tests/. Only the rendered project's .gitignore (.loam/memory line) and hook names/executability are pinned. Nothing pins the store .gitignore content, the Loaded: format, or the HARNESS sentence I remove. check-green stays green.
- Follow the Approach. capture: git add -A + commit + background push; recall: pull --rebase (python3 timeout=5) + claim-once handoff; weekly: .gitignore=.throttle only + foreground pull/push.
- sync.log tracking: ticket says git add -A and .gitignore=.throttle only, so reports/sync.log is tracked. It only churns when sync is already failing and self-heals at the next successful capture commit. Followed the ticket literally rather than gitignoring sync.log.
- Handoff placed right after the Loaded: line, before INDEX lines/hints, then head -c 4000, so INDEX/hints are trimmed before the handoff (ticket trim-priority sentence).
- Advisor adjustments applied: committer identity on the pull too; git clone -b main with init -b main + remote add fallback; guard empty session_id sid8 (nosession); </dev/null on background pushes; refreshed stale "silent when no index" docstring/HARNESS text and the capture/weekly HARNESS bullets.
- Departure (advisor, merge checklist only): HARNESS.md uses `git init --bare -b main ~/memstore.git` and notes a pre-existing store may need `git -C ~/memstore branch -M main` once, because an old mem-weekly created the store without -b main.
- capture writes the store .gitignore (.throttle/ only) only on its init branch, matching weekly, so weekly's check-6 commit still has content (.gitignore) and weekly-pushes passes.
- Placed weekly's pull/push right after the weekly commit (tree clean) and before report generation, so a later week's freshly regenerated (dirty) reports never block the rebase.
- Advisor round 2: a conflicted pull --rebase left git mid-rebase, violating the out-of-scope "leaves the working tree untouched" rule and wedging the store (two machines appending INDEX lines is a textbook conflict). Added git rebase --abort on failure in both recall's python except branch and weekly's failure branch. Verified with a real conflicting-append test: recall exits 0, no rebase-merge dir, tracked INDEX has no conflict markers, local commits preserved, failure logged. All 10 checks still PASS after the fix.
- Confirmed MEM-05 = #165 from docs/research/memory-design-v2-2026-09-21.md line 109; commit subject MEM-05 is correct.
- Worktree clean after check runs except the two intended edits; no pytest cache leaked.

## Round 2 (reviewer findings)

- Finding 3 (sync.log tracked): SUPERSEDES the round-1 line "sync.log ... is tracked ... followed the ticket literally". reports/sync.log is now gitignored in BOTH mem-capture.sh and mem-weekly.sh (byte-identical `.throttle/\nreports/sync.log\n`), plus `git rm --cached -q reports/sync.log` once in weekly. Reason: recall and every failed/rejected push append to sync.log; a tracked sync.log dirties the tree and the next `git pull --rebase` refuses with "unstaged changes", wedging sync until a capture commits it. This is a deliberate departure from step 3's "throttle-mark directory only": the throttle dir plus the churning log stay out of git.
- Finding 5 (capture .gitignore only on init): SUPERSEDES the round-1 line "capture writes the store .gitignore ... only on its init branch ... so weekly's check-6 commit still has content". capture now writes the .gitignore unconditionally (every capture, not only on init) before `git add -A`, so a store an older mem-weekly left with a stale `traces/` ignore line is corrected and its traces resume syncing.
- Weekly reorder (consequence of findings 3+5, advisor-confirmed): findings 3+5 remove both sources of "content to commit" that made check-6 pass in round 1 (round-1 capture never wrote .gitignore because the check pre-created .git; and the dirty tracked sync.log). Fix: mem-weekly.sh now regenerates the reports BEFORE the git baseline commit and commits them, then pulls/pushes with a clean tree. This is strictly more correct than round 1's order: round 1 left reports/*.md modified-and-uncommitted from week 2 on, which would make the NEXT recall's pull --rebase refuse (the same bug finding 3 flags for sync.log). Round-1 decisions.md line "Placed weekly's pull/push ... before report generation, so ... regenerated (dirty) reports never block the rebase" is SUPERSEDED: committing the reports in the baseline leaves the tree clean for both weekly's pull and recall's pull.
- Finding 4 (recall pull timeout does not bound a real ssh remote): rewrote the recall pull python to Popen with start_new_session=True, stderr to a temp file (not a pipe), os.killpg(SIGKILL) on TimeoutExpired before rebase --abort, then read the temp file for the log line. No done-check exercises this branch (check-5 offline-safe uses a nonexistent LOCAL path that fails in milliseconds). MANUAL TEST (not a done-check): origin=ssh://nohost.invalid, GIT_SSH_COMMAND='sh -c "sleep 30"'; recall exited 0 in 6s (under the 10s bound), logged "recall pull: timeout" to sync.log, printed the manifest, and left no .git/rebase-merge dir. Labeled manual, not check-covered.
- Finding 1 (label unverified behaviour): the conflicting-append `git rebase --abort` behaviour (recall and weekly) is NOT covered by any done-check PASS line. The round-1 "verified with a real conflicting-append test" was a MANUAL test I ran, not a done-check. Only the ten listed done-checks were measured (all PASS). The PR body must carry this label.
- Finding 2 (PR body in evidence bundle): per the worker prompt I write no PR text; decisions.md is where the unverified labels live, and the supervisor's PR body must carry the finding-1 and finding-4 "manual, not check-covered" labels from here.
- Known limitation (not blocking, out of scope): reports/*.md are regenerated wholesale and counts.md includes a per-machine session count, so two machines both running mem-weekly.sh will conflict on `pull --rebase` and abort/log (leaving the tree untouched). Out of scope per the ticket ("conflict resolution beyond append-only files"). The reorder neither causes nor worsens this; reports were tracked in round 1's ordering too.
- All 10 done-checks PASS, 0 FAIL, after the fixes (scripts-present, capture-pushes, recall-pulls, handoff-once, offline-safe, weekly-pushes, traces-tracked, harness-doc, in-render, check-green). Worktree clean.

~~~~~~~~~~~~ evidence

## Diff (29488622...HEAD)

~~~~~~~~~~~~ evidence
 seed/.claude/hooks/mem-capture.sh |  56 ++++++++++++++++++++++++++++++++++++++++++++++++--------
 seed/.claude/hooks/mem-recall.sh  | 134 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++----------
 seed/bin/mem-weekly.sh            |  45 ++++++++++++++++++++++++++++++++-------------
 seed/docs/HARNESS.md              |  85 ++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++-----------------
 4 files changed, 272 insertions(+), 48 deletions(-)

diff --git a/seed/.claude/hooks/mem-capture.sh b/seed/.claude/hooks/mem-capture.sh
index 55b32e41..b046c951 100755
--- a/seed/.claude/hooks/mem-capture.sh
+++ b/seed/.claude/hooks/mem-capture.sh
@@ -8,7 +8,8 @@
 # Zero model calls. Idempotent on the scrubbed content's sha256 (kept beside the
 # trace as <date>-<sid8>.sha), so a repeat capture adds no file and no line.
 # After a capture it links <repo-toplevel>/.loam/memory -> $STORE when absent.
-# Prints nothing.
+# It then commits the store and, when an `origin` remote is set, pushes it in the
+# background so a second machine sees what this session learned. Prints nothing.
 #
 # Usage: mem-capture.sh [--throttle SECONDS]
 #   --throttle SECONDS  exit 0 without capturing when this session_id was captured
@@ -27,6 +28,14 @@ set -uo pipefail

 STORE="${LOAM_MEMSTORE:-$HOME/memstore}"

+# First capture on a new machine with no local store: clone the shared remote so
+# this machine starts from what other machines already learned, not from empty.
+# When the remote is empty or unreachable the clone is a no-op and the sync step
+# below inits a fresh main branch instead.
+if [ ! -d "$STORE" ] && [ -n "${LOAM_MEMSTORE_REMOTE:-}" ]; then
+  GIT_TERMINAL_PROMPT=0 git clone -q -b main "$LOAM_MEMSTORE_REMOTE" "$STORE" 2>/dev/null || true
+fi
+
 THROTTLE=0
 if [ "${1:-}" = "--throttle" ]; then
   THROTTLE="${2:-600}"
@@ -256,12 +265,43 @@ fi

 # Only an actual write earns an INDEX line, and one session gets one line: a
 # transcript keeps growing after Stop fires, so SessionEnd re-copies under the
-# same name (sha unchanged -> changed=0) and must not add a second line.
+# same name (sha unchanged -> changed=0, exited above) and must not add a second
+# line. A resumed session that changed only its trace skips the line but still
+# syncs the new trace below.
 [ "$CHANGED" = "1" ] || exit 0
-grep -q " | $SID8 | " "$DST/INDEX.md" 2>/dev/null && exit 0
-BRANCH="$(git -C "$CWD" rev-parse --abbrev-ref HEAD 2>/dev/null)"
-SHORT="$(git -C "$CWD" rev-parse --short HEAD 2>/dev/null)"
-HOST="$(hostname -s 2>/dev/null || hostname 2>/dev/null)"
-printf '%s | %s | %s@%s | %s | %s\n' \
-  "$(date +%F)" "$SID8" "$BRANCH" "$SHORT" "$HOST" "$FIRST" >> "$DST/INDEX.md"
+if ! grep -q " | $SID8 | " "$DST/INDEX.md" 2>/dev/null; then
+  BRANCH="$(git -C "$CWD" rev-parse --abbrev-ref HEAD 2>/dev/null)"
+  SHORT="$(git -C "$CWD" rev-parse --short HEAD 2>/dev/null)"
+  HOST="$(hostname -s 2>/dev/null || hostname 2>/dev/null)"
+  printf '%s | %s | %s@%s | %s | %s\n' \
+    "$(date +%F)" "$SID8" "$BRANCH" "$SHORT" "$HOST" "$FIRST" >> "$DST/INDEX.md"
+fi
+
+# Sync the store through git: commit the new trace and INDEX line, then push to the
+# shared remote in the background so the hook never waits on the network. With no
+# origin every step is a local commit and nothing leaves the machine. The scrub
+# (above) runs before this, so only scrubbed transcripts ever reach the history.
+export GIT_TERMINAL_PROMPT=0
+if [ ! -d "$STORE/.git" ]; then
+  git -C "$STORE" init -q -b main 2>/dev/null || true
+  if [ -n "${LOAM_MEMSTORE_REMOTE:-}" ] && ! git -C "$STORE" remote get-url origin >/dev/null 2>&1; then
+    git -C "$STORE" remote add origin "$LOAM_MEMSTORE_REMOTE" 2>/dev/null || true
+  fi
+fi
+if [ -d "$STORE/.git" ]; then
+  # Keep the ephemeral throttle marks and the sync log out of git: the marks are
+  # local per-session timestamps, and the log is appended on every failed push and
+  # by recall, so tracking it would dirty the tree and make the next pull --rebase
+  # refuse. Written on every capture, not only on init, so a store an older
+  # mem-weekly left with a stale 'traces/' ignore line is corrected and its traces
+  # resume syncing. Byte-identical to the string mem-weekly.sh writes.
+  printf '.throttle/\nreports/sync.log\n' > "$STORE/.gitignore" 2>/dev/null || true
+  mkdir -p "$STORE/reports" 2>/dev/null || true
+  git -C "$STORE" add -A 2>/dev/null || true
+  git -C "$STORE" -c user.name=memstore -c user.email=memstore@localhost \
+    commit -qm "capture $(date +%F) $REPO $SID8" 2>/dev/null || true
+  if git -C "$STORE" remote get-url origin >/dev/null 2>&1; then
+    ( git -C "$STORE" push -q origin main </dev/null >>"$STORE/reports/sync.log" 2>&1 & )
+  fi
+fi
 exit 0
diff --git a/seed/.claude/hooks/mem-recall.sh b/seed/.claude/hooks/mem-recall.sh
index 2d52598b..b839edb8 100755
--- a/seed/.claude/hooks/mem-recall.sh
+++ b/seed/.claude/hooks/mem-recall.sh
@@ -2,14 +2,21 @@
 # mem-recall.sh - inject a short memory manifest at SessionStart.
 #
 # Hook event: SessionStart (matcher startup|resume|clear). Reads the hook JSON
-# on stdin (cwd) and prints to stdout; Claude Code adds stdout to the context.
-# Zero model calls. Prints nothing when the store has no INDEX for this repo.
+# on stdin (cwd, session_id) and prints to stdout; Claude Code adds stdout to the
+# context. Zero model calls. Prints nothing when the store has neither an INDEX
+# nor a claimed handoff for this repo.
 #
 # The manifest names what it loaded (recent sessions, hint bullets, handoff), the
 # last INDEX lines, what exists but was not loaded and the one command to reach
 # it, and the four trust labels every recalled item must carry (layers 3 and 5 of
 # docs/research/memory-design-v2-2026-09-21.md). Output is capped at 4000 bytes.
 #
+# Before building the manifest it pulls the shared store from its `origin` remote
+# (when one is set), bounded to five seconds, so a line another machine committed
+# shows up here; a timeout or failure logs one line to reports/sync.log and falls
+# back to the local store. It then claims a single per-repo handoff note left by
+# an earlier session on any machine: injects it once, archives it, and pushes.
+#
 # Store root: $LOAM_MEMSTORE, default ~/memstore.
 # Exit codes: 0 = always (advisory hook).

@@ -17,17 +24,24 @@ set -uo pipefail

 STORE="${LOAM_MEMSTORE:-$HOME/memstore}"

-CWD="$(cat | python3 -c '
+FIELDS="$(cat | python3 -c '
 import json, sys
 try:
     payload = json.load(sys.stdin)
 except Exception:
     sys.exit(0)
 if isinstance(payload, dict):
-    sys.stdout.write(str(payload.get("cwd") or ""))
+    cwd = str(payload.get("cwd") or "")
+    sid = str(payload.get("session_id") or "")
+    sys.stdout.write(cwd + "\t" + sid)
 ' 2>/dev/null)"

+CWD="${FIELDS%%$'\t'*}"
+SID="${FIELDS#*$'\t'}"
+[ "$FIELDS" = "$CWD" ] && SID=""
 [ -n "$CWD" ] || CWD="$PWD"
+SID8="$(printf '%s' "$SID" | cut -c1-8)"
+[ -n "$SID8" ] || SID8="nosession"

 # Key by the origin remote so recall reads the same directory mem-capture writes
 # across the factory's per-worktree checkouts. Fall back to the toplevel basename
@@ -46,11 +60,105 @@ repo_key() {
 }

 REPO="$(repo_key "$CWD")"
+
+# Sync: pull the shared remote first, so an INDEX line another machine committed is
+# visible below. Bounded to five seconds through python3; a timeout or non-zero
+# exit logs one line to reports/sync.log and leaves the local store as it is.
+if git -C "$STORE" remote get-url origin >/dev/null 2>&1; then
+  GIT_TERMINAL_PROMPT=0 python3 -c '
+import subprocess, sys, os, signal, tempfile, datetime
+store = sys.argv[1]
+
+def logline(msg):
+    os.makedirs(os.path.join(store, "reports"), exist_ok=True)
+    with open(os.path.join(store, "reports", "sync.log"), "a", encoding="utf-8") as fh:
+        fh.write("%s recall pull: %s\n" % (datetime.date.today().isoformat(), " ".join(str(msg).split())[:200]))
+
+def abort():
+    # A conflicted or timed-out rebase must leave the tree untouched, so undo it.
+    # Harmless ("no rebase in progress") when the pull failed before rebasing.
+    try:
+        subprocess.run(["git", "-C", store, "rebase", "--abort"],
+                       stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, timeout=5)
+    except Exception:
+        pass
+
+# Run the pull in its own session so a real ssh remote that hangs can be killed
+# whole: killpg reaches the git fetch and ssh grandchildren, which a plain
+# subprocess timeout leaves running (they inherit the pipe and keep it open, so
+# the five-second bound would not hold). stderr goes to a file, not a pipe, so
+# there is nothing to drain after the kill and wait() returns at once.
+fd, errpath = tempfile.mkstemp()
+os.close(fd)
+try:
+    ef = open(errpath, "wb")
+    p = subprocess.Popen(sys.argv[2:], stdout=subprocess.DEVNULL,
+                         stderr=ef, start_new_session=True)
+    try:
+        rc = p.wait(timeout=5)
+    except subprocess.TimeoutExpired:
+        try:
+            os.killpg(os.getpgid(p.pid), signal.SIGKILL)
+        except Exception:
+            pass
+        try:
+            p.wait(timeout=5)
+        except Exception:
+            pass
+        ef.close()
+        abort()
+        logline("timeout")
+    else:
+        ef.close()
+        if rc != 0:
+            try:
+                with open(errpath, "rb") as rf:
+                    msg = rf.read().decode("utf-8", "replace").strip()[:200]
+            except Exception:
+                msg = ""
+            abort()
+            logline(msg or "nonzero exit")
+finally:
+    try:
+        os.unlink(errpath)
+    except Exception:
+        pass
+' "$STORE" git -C "$STORE" -c user.name=memstore -c user.email=memstore@localhost pull --rebase -q origin main 2>/dev/null || true
+fi
+
+# Handoff: claim the one per-repo handoff note, if present. Read it (cut at 1500
+# bytes), archive it under the claiming session so the next session never re-reads
+# it, then commit and background-push the archive. One writer, read once.
+HANDOFF_FILE="$STORE/handoff/$REPO.md"
+HANDOFF_TEXT=""
+HANDOFF_N=0
+if [ -f "$HANDOFF_FILE" ]; then
+  HANDOFF_TEXT="$(head -c 1500 "$HANDOFF_FILE" 2>/dev/null)"
+  HANDOFF_N=1
+  mkdir -p "$STORE/handoff/$REPO/archive" 2>/dev/null || true
+  mv "$HANDOFF_FILE" "$STORE/handoff/$REPO/archive/$(date +%F)-$SID8.md" 2>/dev/null || true
+  export GIT_TERMINAL_PROMPT=0
+  if [ -d "$STORE/.git" ]; then
+    mkdir -p "$STORE/reports" 2>/dev/null || true
+    git -C "$STORE" add -A 2>/dev/null || true
+    git -C "$STORE" -c user.name=memstore -c user.email=memstore@localhost \
+      commit -qm "handoff $(date +%F) $REPO $SID8" 2>/dev/null || true
+    if git -C "$STORE" remote get-url origin >/dev/null 2>&1; then
+      ( git -C "$STORE" push -q origin main </dev/null >>"$STORE/reports/sync.log" 2>&1 & )
+    fi
+  fi
+fi
+
 INDEX="$STORE/traces/$REPO/INDEX.md"
-[ -f "$INDEX" ] || exit 0
+# Nothing to show only when there is neither an index nor a claimed handoff.
+[ -f "$INDEX" ] || [ "$HANDOFF_N" -eq 1 ] || exit 0

-INDEX_LINES="$(tail -n 5 "$INDEX")"
-N_SESS="$(printf '%s\n' "$INDEX_LINES" | grep -c .)"
+INDEX_LINES=""
+N_SESS=0
+if [ -f "$INDEX" ]; then
+  INDEX_LINES="$(tail -n 5 "$INDEX")"
+  N_SESS="$(printf '%s\n' "$INDEX_LINES" | grep -c .)"
+fi

 TRACES_DIR="$STORE/traces/$REPO"
 TRACES_COUNT="$(find "$TRACES_DIR" -type f \( -name '*.jsonl' -o -name '*.jsonl.gz' \) 2>/dev/null | wc -l | tr -d ' ')"
@@ -73,12 +181,18 @@ if [ -d "$NOTES_DIR" ]; then
   fi
 fi

+# The handoff sits right after Loaded: and before the INDEX lines and hint
+# bullets, so head -c 4000 trims those before it ever reaches the handoff.
 {
   printf '## Memory (%s)\n' "$REPO"
-  printf 'Loaded: %s recent sessions, %s hint bullets, 0 handoff\n' "$N_SESS" "$HINT_N"
-  printf '%s\n' "$INDEX_LINES"
+  printf 'Loaded: %s recent sessions, %s hint bullets, %s handoff\n' "$N_SESS" "$HINT_N" "$HANDOFF_N"
+  if [ -n "$HANDOFF_TEXT" ]; then
+    printf '## Handoff (claimed now)\n'
+    printf '%s\n' "$HANDOFF_TEXT"
+  fi
+  [ -n "$INDEX_LINES" ] && printf '%s\n' "$INDEX_LINES"
   [ -n "$HINT_BULLETS" ] && printf '%s\n' "$HINT_BULLETS"
-  printf 'Not loaded: %s notes, %s traces under .loam/memory; reach them with memsearch <pattern> or mem-inspect <session>; do not grep the raw traces.\n' "$NOTES_COUNT" "$TRACES_COUNT"
+  printf 'Not loaded: %s notes, %s traces under .loam/memory; reach them with memsearch <pattern> or mem-inspect <session>; do not grep the raw traces. To hand off to the next session on any machine, write .loam/memory/handoff/%s.md.\n' "$NOTES_COUNT" "$TRACES_COUNT" "$REPO"
   printf 'Label every recalled item before acting on it: supported (the trace shows it), contradicts (the current repo or host disagrees), near-match (similar task, different conditions), insufficient (not enough to act); check git log -1, hostname, and tool versions first.\n'
 } | head -c 4000
 exit 0
diff --git a/seed/bin/mem-weekly.sh b/seed/bin/mem-weekly.sh
index 6cda466d..39215065 100755
--- a/seed/bin/mem-weekly.sh
+++ b/seed/bin/mem-weekly.sh
@@ -1,10 +1,12 @@
 #!/usr/bin/env bash
 # mem-weekly.sh - weekly maintenance for the memory store (run from cron).
 #
-# Deletes traces older than a year, commits the store as a git baseline, then
-# regenerates the recurring-errors and counts reports from the captured traces.
-# Zero model calls. The cron line is documented in seed/docs/HARNESS.md; this
-# ticket does not install it.
+# Deletes traces older than a year, regenerates the recurring-errors and counts
+# reports from the captured traces, commits the store (reports included) as a git
+# baseline, then pulls and pushes the shared remote when one is set. Reports are
+# committed before the pull so the working tree is clean for the rebase and no
+# stale report blocks the next session's recall pull. Zero model calls. The cron
+# line is documented in seed/docs/HARNESS.md; this ticket does not install it.
 #
 # The error-signature normalizer (first 100 chars, digits -> N) is ported from
 # SuperClaude src/superclaude/pm_agent/reflexion.py (_create_error_signature, MIT);
@@ -30,15 +32,6 @@ if [ -d traces ]; then
   done
 fi

-# The baseline holds reports and native-memory caches only. Traces stay out of git so
-# that deleting a trace file forgets it (HARNESS.md, Accepted risks); a git history of
-# transcripts would keep a pasted secret after the file is gone.
-[ -d .git ] || git init -q 2>/dev/null
-printf 'traces/\n.throttle/\n' > .gitignore
-git add -A 2>/dev/null \
-  && git -c user.name=memstore -c user.email=memstore@localhost \
-       commit -qm "weekly $(date +%F)" 2>/dev/null || true
-
 # Recurring errors: extract error lines from every trace (gzipped and plain),
 # normalize each to a signature (first 100 chars, digits -> N) so runs that differ
 # only in a port or pid collapse into one recurrence, and count the top 20.
@@ -109,4 +102,30 @@ fi
   printf 'retrieval %s\n' "${retrieval:-0}"
   printf 'application %s\n' "${application:-0}"
 } > reports/counts.md
+
+# Commit the store as a git baseline, reports included, then share it. Traces and
+# INDEX.md are tracked and pushed once MEM-04's scrub (in mem-capture.sh) has run
+# over them. Only the ephemeral throttle marks and the churning sync log stay out
+# of git; the .gitignore is byte-identical to the one mem-capture.sh writes, so the
+# two never ping-pong a change. git rm --cached un-tracks a sync.log a pre-fix run
+# committed (a no-op otherwise). The commit lands the freshly regenerated reports,
+# so the working tree is clean before the pull and no stale report blocks a later
+# recall's pull --rebase.
+[ -d .git ] || git init -q -b main 2>/dev/null
+printf '.throttle/\nreports/sync.log\n' > .gitignore
+git rm --cached -q reports/sync.log 2>/dev/null || true
+git add -A 2>/dev/null \
+  && git -c user.name=memstore -c user.email=memstore@localhost \
+       commit -qm "weekly $(date +%F)" 2>/dev/null || true
+
+# Share the store: pull the remote's commits, then push this baseline. Foreground
+# (this runs from cron, not a hook). With no origin every step is skipped; a
+# conflict or unreachable remote aborts the rebase, logs one line, and leaves the
+# tree as it is.
+export GIT_TERMINAL_PROMPT=0
+if git remote get-url origin >/dev/null 2>&1; then
+  { git -c user.name=memstore -c user.email=memstore@localhost pull --rebase -q origin main \
+    && git push -q origin main ; } >> reports/sync.log 2>&1 \
+    || { git rebase --abort 2>/dev/null; printf '%s weekly sync failed\n' "$(date +%F)" >> reports/sync.log; }
+fi
 exit 0
diff --git a/seed/docs/HARNESS.md b/seed/docs/HARNESS.md
index 78acbe02..e5230969 100644
--- a/seed/docs/HARNESS.md
+++ b/seed/docs/HARNESS.md
@@ -55,15 +55,20 @@ per-tool latency.
   sha256 (kept beside the trace as `<date>-<sid8>.sha`), so a repeat capture adds
   no file and no line. After a capture it links `<repo>/.loam/memory` to the
   store when that path is free. The `Stop` entry passes `--throttle 600`, so a
-  burst of stops captures at most once per ten minutes.
+  burst of stops captures at most once per ten minutes. It then commits the store
+  and, when an `origin` remote is set, pushes it in the background, so a second
+  machine sees the trace; the hook never waits on the network.
 - `mem-recall.sh` (SessionStart `startup|resume|clear`): prints a manifest to
-  stdout, which Claude Code adds to the context. A `Loaded:` line names how many
-  recent sessions, hint bullets, and handoffs it injected; the last five
-  `INDEX.md` lines follow; a `Not loaded:` line names the notes and traces it did
-  not open and points at `memsearch <pattern>` or `mem-inspect <session>` to
-  reach them; a trust rule closes it, labelling every recalled item supported,
-  contradicts, near-match, or insufficient. Capped at 4000 bytes, silent when the
-  store has no index for the repo.
+  stdout, which Claude Code adds to the context. When an `origin` remote is set it
+  first pulls the store (bounded to five seconds) so a line another machine
+  committed shows up here. A `Loaded:` line names how many recent sessions, hint
+  bullets, and handoffs it injected; a claimed handoff, the last five `INDEX.md`
+  lines, and the newest hint bullets follow; a `Not loaded:` line names the notes
+  and traces it did not open and points at `memsearch <pattern>` or
+  `mem-inspect <session>` to reach them, and at the handoff path; a trust rule
+  closes it, labelling every recalled item supported, contradicts, near-match, or
+  insufficient. Capped at 4000 bytes, silent when the store has no index and no
+  handoff for the repo.

 Codex runs the same two scripts through `.codex/hooks.json`, which registers
 `mem-capture.sh` on SessionEnd, PreCompact, and Stop (the Stop entry throttled)
@@ -77,14 +82,56 @@ alike) and the repo's `docs/` with ripgrep (or `grep`/`zgrep`) and cuts the
 output at 80 lines. `mem-inspect <session>` reads one captured trace by turn
 instead of grepping the raw file: `--summary` lists the turns, `--span A:B`
 prints a range, `--match RE` prints the turns whose text matches. `mem-weekly.sh`
-deletes traces older than a year, commits the store as a git baseline, and
-rewrites `reports/recurring-errors.md` (error lines normalized to a signature so
-runs differing only in a number collapse) and `reports/counts.md` (capture,
-retrieval, and application counts); add its cron line by hand, it is not
-installed:
+deletes traces older than a year, rewrites `reports/recurring-errors.md` (error
+lines normalized to a signature so runs differing only in a number collapse) and
+`reports/counts.md` (capture, retrieval, and application counts), commits the
+store as a git baseline with those reports included, then pulls and pushes the
+store's remote when one is set; add its cron line by hand, it is not installed:

     0 9 * * 0 <project>/bin/mem-weekly.sh

+## Sharing the store between machines
+
+The store is a git repository, so a second machine can see what the first
+learned by giving the store a remote. Use a machine you own; no third-party host
+is involved.
+
+1. On the machine that will hold the remote, create a bare repository:
+
+        git init --bare -b main ~/memstore.git
+
+2. On every machine, point the local store at it over an ssh alias (say
+   `jhaveris`, the same alias `bin/runner` uses):
+
+        git -C ~/memstore remote add origin jhaveris:memstore.git
+
+   A store an older `mem-weekly.sh` created may sit on `master`; run
+   `git -C ~/memstore branch -M main` once so `origin main` matches.
+
+3. On a brand-new machine with no `~/memstore` yet, set `LOAM_MEMSTORE_REMOTE`
+   to the same URL. The first capture then clones the shared store instead of
+   starting empty, so the machine sees the shared history from its first session.
+
+The remote holds scrubbed transcripts, the same content as the local store.
+Keep it on a machine you own and never point it at a public host: a secret with
+no recognizable shape can reach the store's history and the remote (see Accepted
+risks). A capture commits and pushes in the background; recall pulls at
+SessionStart and `mem-weekly.sh` pulls then pushes from cron. Every git call runs
+with `GIT_TERMINAL_PROMPT=0`, and recall's pull is bounded to five seconds, so an
+unreachable remote never blocks a session; it logs one line to
+`reports/sync.log` and continues with the local store. Store files are
+append-only, so a rebase does not conflict; on the rare conflict the hook logs
+one line and leaves the working tree untouched.
+
+### The handoff
+
+To hand the next session a single instruction, write
+`.loam/memory/handoff/<repo>.md` (the repo key is the name in the recall
+manifest's heading). The next session on any machine or harness, in the same
+repo, injects that file once under `## Handoff (claimed now)`, then archives it to
+`.loam/memory/handoff/<repo>/archive/<date>-<sid8>.md` and never reads it again.
+One writer per workstream, claimed once: it is not a shared last-writer-wins file.
+
 ## The one check

 `bin/check` runs ruff, shell syntax, whitespace, and pytest. The agent runs it by
@@ -109,7 +156,8 @@ removing it would cause a mistake.
   now sits in the listing.
 - Memory hooks: recall adds at most 4000 bytes at SessionStart, and the Stop
   capture runs at most once per ten minutes. The scrub adds one regex pass over
-  the transcript per capture.
+  the transcript per capture. Recall waits at most five seconds for a pull from
+  the store's remote; the capture's push runs in the background and never waits.

 ## Accepted risks, stated rather than hidden

@@ -123,9 +171,12 @@ removing it would cause a mistake.
   stored; a secret with no recognizable shape can still be stored, so delete the
   trace to forget it. The store under `LOAM_MEMSTORE` (default `~/memstore`) is
   per user, outside every repository, never rendered and never committed to the
-  project. The weekly baseline commit in the store covers reports and
-  native-memory caches only; `traces/` is gitignored there, so a deleted
-  transcript leaves no copy in git history.
+  project. The store is itself a git repository: `traces/` and `INDEX.md` are
+  tracked and pushed to the store's own remote once the scrub has run over them,
+  so the trace history and any configured remote hold scrubbed transcripts. A
+  secret with no recognizable shape can therefore reach both the store's git
+  history and the remote; forgetting a pushed trace means deleting the file,
+  committing, and rewriting or reinitialising both the store repo and the remote.
 - Codex runs a repository hook only after the user trusts the project's `.codex`
   layer and reviews the hook definition once (Codex keeps a hash of it in its
   hooks state, and an edit to `hooks.json` asks again), so a Codex session before
~~~~~~~~~~~~ evidence
