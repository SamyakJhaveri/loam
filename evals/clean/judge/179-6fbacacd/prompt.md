## Ticket

~~~~~~~~~~~~ evidence
Brief:
Two machines that each capture or run the weekly job before pulling must not strand either one; today the loser of a race conflicts, aborts, and every later pull conflicts the same way, so it never syncs again.
Where: seed/.claude/hooks/mem-capture.sh (write .gitattributes; ignore the store report directory), seed/.claude/hooks/mem-recall.sh (disable rename detection on the pull), seed/bin/mem-weekly.sh (write .gitattributes; ignore and untrack the store report directory; disable rename detection on the pull), seed/docs/HARNESS.md (replace the append-only claim).
Done means: the done-checks block prints no FAIL line: a capture writes the INDEX union attribute, two machines that capture before pulling both keep every line, a handoff claimed on two machines does not strand either, regenerated reports never conflict, HARNESS states the truth, and a fresh render carries the attribute.
Out of scope: any third-party host; the ssh transport; the note gate; Codex hooks; any change to the abort safety net beyond what step 1 needs.
Blocked by: #173 (MEM-04b) merged, because both edit mem-capture.sh (this edge also implies #165 merged, since MEM-04b builds on it).

## Goal and why
MEM-05 (PR #176) shares the store through a bare git remote, but its review found that two machines writing between pulls strand the loser: both append a line to `traces/<repo>/INDEX.md`, the loser's `pull --rebase` conflicts, `rebase --abort` runs, and because the conflicting commit stays local, every later pull conflicts the same way, so that machine never syncs again.
A live two-store proof reproduced it for INDEX.md, for the wholesale-regenerated `reports/*.md`, and for a handoff claimed on two machines at once (git reads the two archive moves as a rename/rename conflict, which strands the machine for all future syncing, not just the handoff).
The fix keeps each conflicting class from ever conflicting: INDEX lines merge by union, reports become local, and the pull stops detecting renames so two archive moves apply as independent add-and-delete.
Decision: PR #176 review (round 2, medium finding and the manager's two-store proof comment), docs/research/memory-design-v2-2026-09-21.md (layer 3).

## Do not touch
The standing list. Also: seed/AGENTS.md.jinja, seed/CLAUDE.md.jinja, seed/.claude/settings.json, seed/bin/memsearch, seed/bin/mem-inspect, seed/.codex/, seed/.loam/, seed/.agents/, bin/factory, docs/architecture-working/.
Except: seed/.claude/hooks/mem-capture.sh, seed/.claude/hooks/mem-recall.sh, seed/bin/mem-weekly.sh, seed/docs/HARNESS.md (this ticket edits three MEM-05 scripts and their doc). `seed/.loam/runtime/assets/curated-catalog.json` has no entry for any of these four paths, so no catalog re-pin is needed; if a `support:` entry has appeared for one, add the catalog under Except in a decisions.md line and re-pin it as MEM-01 step 8 did.

## Out of scope
GitHub or any hosted remote; the transport is unchanged.
The ssh timeout, the offline-safe path, and the abort itself, which stays as the last-resort safety net for any conflict these three fixes do not cover.
The note gate (MEM-03) and Codex hooks (MEM-02).
Any model call.

## Approach
Same conventions as MEM-05: bash with `set -uo pipefail`, python3 for any timed subprocess, no jq, hooks exit 0 always, every git call with `-C "$STORE"` (or `cd "$STORE"` in the weekly job) and `GIT_TERMINAL_PROMPT=0`, branch always `main`. Commit as you go; `render_into` reads the committed HEAD.
1. INDEX.md union. In mem-capture.sh, beside the existing byte-identical `.gitignore` write, also write a byte-identical `.gitattributes` holding one line, `traces/*/INDEX.md merge=union`; write the identical line in mem-weekly.sh where it writes its `.gitignore`. The union driver takes lines from both sides instead of leaving conflict markers (git help gitattributes: "Run 3-way file level merge for text files, but take lines from both versions, instead of leaving conflict markers"), so two machines' INDEX lines both survive a rebase. A `notes/**/*.md merge=union` line is NOT wanted: MEM-03 writes one note file per session under a unique name, so two machines never write the same notes file and it cannot conflict. The handoff needs no attribute either, but it does need step 3.
2. reports/ is local. Every report is regenerated wholesale by mem-weekly.sh from the local traces, and `reports/counts.md` counts sessions seen on this machine, so reports have no cross-machine meaning; two machines' regenerated reports conflict on a pull exactly as INDEX did. Choice (a), the cheaper: gitignore `reports/` entirely rather than write per-hostname subdirs. In mem-capture.sh and mem-weekly.sh change the ignore line from `.throttle/\nreports/sync.log\n` to `.throttle/\nreports/\n` (byte-identical in both); in mem-weekly.sh replace `git rm --cached -q reports/sync.log` with `git rm -r --cached -q reports` so a store an older weekly job tracked reports into gets them untracked. Reports then never enter git and never conflict. The weekly commit still lands trace and note changes; a weekly run with no new traces commits nothing, which is fine and does not break the `weekly-pushes` behavior MEM-05 relied on, since traces committed during a capture already reached the remote.
3. Rename detection off on the pull, for the handoff. When a handoff is claimed on two machines at once, each archives `handoff/<repo>.md` to `handoff/<repo>/archive/<date>-<sid8>.md` under its own session id; git detects the same source renamed to two names and raises a rename/rename conflict, which the abort masks and which then strands the machine for all syncing. Add `-c merge.renames=false` to the `pull --rebase` in mem-recall.sh (inside the python subprocess arg list) and in mem-weekly.sh. With rename detection off the two archive moves apply as an independent add plus a delete both sides agree on, so the pull succeeds and both archives are kept. A re-check of the file after the pull does not fix this: the conflicting commit was made in an earlier session and the conflict is at the tree level, not the `[ -f ]` level, so the flag is the cheapest real fix. Residual, stated in HARNESS: in a truly simultaneous double-start the handoff is injected once on each machine (read twice total); this is benign, not a strand.
4. HARNESS.md. Replace the sentence "Store files are append-only, so a rebase does not conflict; on the rare conflict the hook logs one line and leaves the working tree untouched." with the truth: INDEX.md lines from two machines merge by union (`.gitattributes merge=union`); regenerated reports are local and never shared; a handoff claimed on two machines at once is archived under two names and injected once on each machine, because the pull disables rename detection so the two archive moves do not conflict; the abort remains the safety net for anything else.
5. mem-recall.sh's abort path is unchanged.

## Done checks
```done-checks
tmp=$(mktemp -d); store="$tmp/store"; mkdir -p "$store" "$tmp/repo"; git -C "$store" init -q -b main; printf '{"type":"user","message":{"content":"attr probe"}}\n' > "$tmp/t.jsonl"; printf '{"session_id":"attr00001","transcript_path":"%s/t.jsonl","cwd":"%s/repo"}' "$tmp" "$tmp" | LOAM_MEMSTORE="$store" seed/.claude/hooks/mem-capture.sh >/dev/null 2>&1; attr=$(git -C "$store" check-attr merge traces/x/INDEX.md 2>/dev/null); grep -q 'traces/\*/INDEX.md merge=union' "$store/.gitattributes" 2>/dev/null && grep -q 'merge: union' <<<"$attr" && pass gitattributes-written || fail gitattributes-written "capture did not write the INDEX union attribute"
tmp=$(mktemp -d); r="$tmp/remote.git"; git init -q --bare -b main "$r"; A="$tmp/A"; B="$tmp/B"; mkdir -p "$tmp/repo"; git init -q -b main "$A"; git -C "$A" remote add origin "$r"; cap(){ printf '{"type":"user","message":{"content":"%s"}}\n' "$3" > "$tmp/t-$2.jsonl"; printf '{"session_id":"%s","transcript_path":"%s/t-%s.jsonl","cwd":"%s/repo"}' "$2" "$tmp" "$2" "$tmp" | LOAM_MEMSTORE="$1" seed/.claude/hooks/mem-capture.sh >/dev/null 2>&1; }; rec(){ printf '{"session_id":"%s","cwd":"%s/repo"}' "$2" "$tmp" | LOAM_MEMSTORE="$1" seed/.claude/hooks/mem-recall.sh >/dev/null 2>&1; }; cap "$A" aaaaaaaa1 "first from A"; sleep 2; git -C "$tmp" clone -q -b main "$r" B >/dev/null 2>&1; cap "$A" cccccccc2 "A second before pull"; cap "$B" dddddddd3 "B second before pull"; sleep 2; rec "$B" eeeeeeee4; s=$?; ib="$B/traces/repo/INDEX.md"; [ "$s" = 0 ] && [ ! -d "$B/.git/rebase-merge" ] && grep -q 'A second before pull' "$ib" && grep -q 'B second before pull' "$ib" && cap "$B" fff00005 "B third to push" && sleep 2 && git -C "$tmp" clone -q -b main "$r" chk >/dev/null 2>&1 && grep -q 'A second before pull' "$tmp/chk/traces/repo/INDEX.md" && grep -q 'B second before pull' "$tmp/chk/traces/repo/INDEX.md" && rec "$A" 99999999 && grep -q 'B second before pull' "$A/traces/repo/INDEX.md" && pass race-survives || fail race-survives "a concurrent two-machine capture stranded a store"
tmp=$(mktemp -d); r="$tmp/remote.git"; git init -q --bare -b main "$r"; A="$tmp/A"; B="$tmp/B"; mkdir -p "$tmp/repo"; git init -q -b main "$A"; git -C "$A" remote add origin "$r"; cap(){ printf '{"type":"user","message":{"content":"%s"}}\n' "$3" > "$tmp/t-$2.jsonl"; printf '{"session_id":"%s","transcript_path":"%s/t-%s.jsonl","cwd":"%s/repo"}' "$2" "$tmp" "$2" "$tmp" | LOAM_MEMSTORE="$1" seed/.claude/hooks/mem-capture.sh >/dev/null 2>&1; }; rec(){ printf '{"session_id":"%s","cwd":"%s/repo"}' "$2" "$tmp" | LOAM_MEMSTORE="$1" seed/.claude/hooks/mem-recall.sh >/dev/null 2>&1; }; cap "$A" seedaaaa1 "seed"; sleep 2; mkdir -p "$A/handoff"; printf 'HANDOFF probe next step\n' > "$A/handoff/repo.md"; git -C "$A" add -A; git -C "$A" -c user.name=t -c user.email=t@t commit -qm h >/dev/null 2>&1; git -C "$A" push -q origin main; git -C "$tmp" clone -q -b main "$r" B >/dev/null 2>&1; git -C "$A" remote set-url origin "$tmp/nope.git"; git -C "$B" remote set-url origin "$tmp/nope.git"; rec "$A" claimaaa1; rec "$B" claimbbb2; git -C "$A" remote set-url origin "$r"; git -C "$B" remote set-url origin "$r"; git -C "$A" push -q origin main 2>/dev/null; mkdir -p "$A/traces/repo"; printf '2026-09-21 | zzzzzzzz | m@1 | host | later A line\n' >> "$A/traces/repo/INDEX.md"; git -C "$A" add -A; git -C "$A" -c user.name=t -c user.email=t@t commit -qm idx >/dev/null 2>&1; git -C "$A" push -q origin main 2>/dev/null; rec "$B" laterb33; [ ! -d "$B/.git/rebase-merge" ] && grep -q 'later A line' "$B/traces/repo/INDEX.md" 2>/dev/null && ! grep -qi 'could not apply' "$B/reports/sync.log" 2>/dev/null && pass handoff-race-survives || fail handoff-race-survives "a handoff claimed on two machines stranded a store"
tmp=$(mktemp -d); r="$tmp/remote.git"; git init -q --bare -b main "$r"; A="$tmp/A"; B="$tmp/B"; mkdir -p "$tmp/repo"; git init -q -b main "$A"; git -C "$A" remote add origin "$r"; cap(){ printf '{"type":"user","message":{"content":"%s"}}\n' "$3" > "$tmp/t-$2.jsonl"; printf '{"session_id":"%s","transcript_path":"%s/t-%s.jsonl","cwd":"%s/repo"}' "$2" "$tmp" "$2" "$tmp" | LOAM_MEMSTORE="$1" seed/.claude/hooks/mem-capture.sh >/dev/null 2>&1; }; cap "$A" seedaaaa1 "seed"; sleep 2; git -C "$tmp" clone -q -b main "$r" B >/dev/null 2>&1; cap "$A" awx00002 "A trace"; cap "$B" bwx00003 "B trace"; sleep 2; LOAM_MEMSTORE="$A" seed/bin/mem-weekly.sh >/dev/null 2>&1; LOAM_MEMSTORE="$B" seed/bin/mem-weekly.sh >/dev/null 2>&1; printf '{"session_id":"recb0001","cwd":"%s/repo"}' "$tmp" | LOAM_MEMSTORE="$B" seed/.claude/hooks/mem-recall.sh >/dev/null 2>&1; [ -z "$(git -C "$B" ls-files reports/)" ] && ! grep -qiE 'could not apply|weekly sync failed' "$B/reports/sync.log" 2>/dev/null && pass reports-local || fail reports-local "regenerated reports are tracked or conflicted on pull"
! tr '\n' ' ' < seed/docs/HARNESS.md | grep -qi 'so a rebase does not conflict' && grep -qiE 'merge=union|union' seed/docs/HARNESS.md && pass harness-doc || fail harness-doc "the append-only sentence remains or union is not named"
render_into; [ -n "$render_dir" ] || fail render "$render_err"; grep -q 'gitattributes' "$render_dir/.claude/hooks/mem-capture.sh" 2>/dev/null && grep -q 'merge=union' "$render_dir/.claude/hooks/mem-capture.sh" 2>/dev/null && pass render-writes-attr || fail render-writes-attr "the rendered mem-capture.sh does not write the INDEX union attribute"
[ -n "${LOAM_HOOK:-}" ] && pass check-green || { guard bin/check >/dev/null && pass check-green || fail check-green "bin/check"; }
```

## Merge checklist
- On the two machines that share a store, capture a session on each within the same minute before either pulls, then start a session on each and confirm both INDEX lines are present in both stores.

## Worker
worker: claude
codex-review: no
effort: xhigh
MAX_ROUNDS=3
ROUND_BUDGET_USD=20
goal: the done-checks block prints no FAIL line, or stop after 60 turns

## Decisions
PR #176 review (round 2, medium), docs/research/memory-design-v2-2026-09-21.md (layer 3), the manager's two-store proof comment on PR #176.

~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS gitattributes-written
PASS race-survives
PASS handoff-race-survives
PASS reports-local
PASS harness-doc
PASS render-writes-attr
PASS check-green

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
- Step 2 took choice (a): gitignore all of reports/ in mem-capture.sh and mem-weekly.sh (byte-identical '.throttle/\nreports/\n'), and mem-weekly.sh untracks it with git rm -r --cached, rather than per-hostname report subdirs.
- Step 3 uses -c merge.renames=false as a global git option before pull (it reaches the rebase child through GIT_CONFIG_PARAMETERS), per the ticket, not -X no-renames.
- The curated catalog has no entry for mem-capture.sh, mem-recall.sh, mem-weekly.sh, or HARNESS.md (grep found none), so no catalog re-pin.
- The .gitattributes holds only 'traces/*/INDEX.md merge=union' (no notes/** line, per the ticket); the recall abort path is unchanged.
- HARNESS.md also drops the stale 'reports included' wording in the mem-weekly.sh paragraph and states the handoff double-claim residual in the handoff section, since both would be false or missing after this change.
- Departed from step 3: -c merge.renames=false alone did not fix the handoff race on the installed git 2.43, because merge-ort ignores merge.renames (and -X no-renames) before git 2.50 (the 'if (!opt->detect_renames)' check in detect_and_process_renames first appears in v2.50.0 on git.kernel.org). Both pulls now also pass -s recursive: before 2.50 that is merge-recursive, which honors merge.renames=false; from 2.50 'recursive' names ort, which honors it. Verified on 2.43: -s recursive without the flag still conflicts, with the flag the double claim rebases clean and keeps both archives.
- Checked the 2.50 claim in the mem-recall.sh comment: v2.50.0 merge-ort.c has the detect_renames gate and reads merge.renames in merge_recursive_config via init_ui_merge_options, which sequencer.c calls, so the comment stands.

~~~~~~~~~~~~ evidence

## Diff (fe516809...HEAD)

~~~~~~~~~~~~ evidence
 seed/.claude/hooks/mem-capture.sh | 19 ++++++++++++-------
 seed/.claude/hooks/mem-recall.sh  | 11 ++++++++---
 seed/bin/mem-weekly.sh            | 41 ++++++++++++++++++++++-------------------
 seed/docs/HARNESS.md              | 25 +++++++++++++++++++------
 4 files changed, 61 insertions(+), 35 deletions(-)

diff --git a/seed/.claude/hooks/mem-capture.sh b/seed/.claude/hooks/mem-capture.sh
index 1c4fcb80..f92c15c8 100755
--- a/seed/.claude/hooks/mem-capture.sh
+++ b/seed/.claude/hooks/mem-capture.sh
@@ -292,13 +292,18 @@ if [ ! -d "$STORE/.git" ]; then
   fi
 fi
 if [ -d "$STORE/.git" ]; then
-  # Keep the ephemeral throttle marks and the sync log out of git: the marks are
-  # local per-session timestamps, and the log is appended on every failed push and
-  # by recall, so tracking it would dirty the tree and make the next pull --rebase
-  # refuse. Written on every capture, not only on init, so a store an older
-  # mem-weekly left with a stale 'traces/' ignore line is corrected and its traces
-  # resume syncing. Byte-identical to the string mem-weekly.sh writes.
-  printf '.throttle/\nreports/sync.log\n' > "$STORE/.gitignore" 2>/dev/null || true
+  # Keep the ephemeral throttle marks and reports/ out of git: the marks are local
+  # per-session timestamps, the sync log is appended on every failed push and by
+  # recall, and mem-weekly regenerates the other reports wholesale from this
+  # machine's traces, so tracking any of them would dirty the tree or conflict on
+  # the next pull --rebase. The attributes line merges INDEX.md by union, so two
+  # machines that each append a line before pulling both keep both lines instead
+  # of conflicting. Both files are written on every capture, not only on init, so
+  # a store an older mem-weekly left with a stale 'traces/' ignore line is
+  # corrected and its traces resume syncing. Byte-identical to what mem-weekly.sh
+  # writes.
+  printf '.throttle/\nreports/\n' > "$STORE/.gitignore" 2>/dev/null || true
+  printf 'traces/*/INDEX.md merge=union\n' > "$STORE/.gitattributes" 2>/dev/null || true
   mkdir -p "$STORE/reports" 2>/dev/null || true
   git -C "$STORE" add -A 2>/dev/null || true
   git -C "$STORE" -c user.name=memstore -c user.email=memstore@localhost \
diff --git a/seed/.claude/hooks/mem-recall.sh b/seed/.claude/hooks/mem-recall.sh
index b839edb8..c9fba632 100755
--- a/seed/.claude/hooks/mem-recall.sh
+++ b/seed/.claude/hooks/mem-recall.sh
@@ -14,8 +14,13 @@
 # Before building the manifest it pulls the shared store from its `origin` remote
 # (when one is set), bounded to five seconds, so a line another machine committed
 # shows up here; a timeout or failure logs one line to reports/sync.log and falls
-# back to the local store. It then claims a single per-repo handoff note left by
-# an earlier session on any machine: injects it once, archives it, and pushes.
+# back to the local store. The pull runs with rename detection off, so a handoff
+# two machines claimed at once rebases as two independent archive adds plus a
+# delete both sides agree on, not a rename/rename conflict. `-s recursive` is
+# what makes the switch hold: before git 2.50 the default ort backend ignores
+# merge.renames=false and the recursive backend honors it; from 2.50 `recursive`
+# names ort, which honors it. It then claims a single per-repo handoff note left
+# by an earlier session on any machine: injects it once, archives it, and pushes.
 #
 # Store root: $LOAM_MEMSTORE, default ~/memstore.
 # Exit codes: 0 = always (advisory hook).
@@ -123,7 +128,7 @@ finally:
         os.unlink(errpath)
     except Exception:
         pass
-' "$STORE" git -C "$STORE" -c user.name=memstore -c user.email=memstore@localhost pull --rebase -q origin main 2>/dev/null || true
+' "$STORE" git -C "$STORE" -c user.name=memstore -c user.email=memstore@localhost -c merge.renames=false pull --rebase -s recursive -q origin main 2>/dev/null || true
 fi

 # Handoff: claim the one per-repo handoff note, if present. Read it (cut at 1500
diff --git a/seed/bin/mem-weekly.sh b/seed/bin/mem-weekly.sh
index 39215065..d1994649 100755
--- a/seed/bin/mem-weekly.sh
+++ b/seed/bin/mem-weekly.sh
@@ -2,11 +2,11 @@
 # mem-weekly.sh - weekly maintenance for the memory store (run from cron).
 #
 # Deletes traces older than a year, regenerates the recurring-errors and counts
-# reports from the captured traces, commits the store (reports included) as a git
-# baseline, then pulls and pushes the shared remote when one is set. Reports are
-# committed before the pull so the working tree is clean for the rebase and no
-# stale report blocks the next session's recall pull. Zero model calls. The cron
-# line is documented in seed/docs/HARNESS.md; this ticket does not install it.
+# reports from the captured traces, commits the store as a git baseline, then
+# pulls and pushes the shared remote when one is set. Reports stay local: they are
+# gitignored, so two machines' regenerated reports never conflict on a pull and
+# the working tree is clean for the rebase. Zero model calls. The cron line is
+# documented in seed/docs/HARNESS.md; this ticket does not install it.
 #
 # The error-signature normalizer (first 100 chars, digits -> N) is ported from
 # SuperClaude src/superclaude/pm_agent/reflexion.py (_create_error_signature, MIT);
@@ -103,28 +103,31 @@ fi
   printf 'application %s\n' "${application:-0}"
 } > reports/counts.md

-# Commit the store as a git baseline, reports included, then share it. Traces and
-# INDEX.md are tracked and pushed once MEM-04's scrub (in mem-capture.sh) has run
-# over them. Only the ephemeral throttle marks and the churning sync log stay out
-# of git; the .gitignore is byte-identical to the one mem-capture.sh writes, so the
-# two never ping-pong a change. git rm --cached un-tracks a sync.log a pre-fix run
-# committed (a no-op otherwise). The commit lands the freshly regenerated reports,
-# so the working tree is clean before the pull and no stale report blocks a later
-# recall's pull --rebase.
+# Commit the store as a git baseline, then share it. Traces and INDEX.md are
+# tracked and pushed once MEM-04's scrub (in mem-capture.sh) has run over them.
+# The ephemeral throttle marks and reports/ stay out of git: every report is
+# regenerated wholesale from this machine's traces and has no meaning on another
+# machine. The .gitignore and the .gitattributes (INDEX.md merges by union, so two
+# machines' appended lines both survive a rebase) are byte-identical to the ones
+# mem-capture.sh writes, so the two never ping-pong a change. git rm -r --cached
+# un-tracks reports an older run committed (a no-op otherwise).
 [ -d .git ] || git init -q -b main 2>/dev/null
-printf '.throttle/\nreports/sync.log\n' > .gitignore
-git rm --cached -q reports/sync.log 2>/dev/null || true
+printf '.throttle/\nreports/\n' > .gitignore
+printf 'traces/*/INDEX.md merge=union\n' > .gitattributes
+git rm -r --cached -q reports 2>/dev/null || true
 git add -A 2>/dev/null \
   && git -c user.name=memstore -c user.email=memstore@localhost \
        commit -qm "weekly $(date +%F)" 2>/dev/null || true

 # Share the store: pull the remote's commits, then push this baseline. Foreground
-# (this runs from cron, not a hook). With no origin every step is skipped; a
-# conflict or unreachable remote aborts the rebase, logs one line, and leaves the
-# tree as it is.
+# (this runs from cron, not a hook). Rename detection is off, as in recall's pull,
+# so a handoff two machines archived under two names does not conflict; see
+# mem-recall.sh for why the pull names `-s recursive`. With no origin every step
+# is skipped; a conflict or unreachable remote aborts the rebase, logs one line,
+# and leaves the tree as it is.
 export GIT_TERMINAL_PROMPT=0
 if git remote get-url origin >/dev/null 2>&1; then
-  { git -c user.name=memstore -c user.email=memstore@localhost pull --rebase -q origin main \
+  { git -c user.name=memstore -c user.email=memstore@localhost -c merge.renames=false pull --rebase -s recursive -q origin main \
     && git push -q origin main ; } >> reports/sync.log 2>&1 \
     || { git rebase --abort 2>/dev/null; printf '%s weekly sync failed\n' "$(date +%F)" >> reports/sync.log; }
 fi
diff --git a/seed/docs/HARNESS.md b/seed/docs/HARNESS.md
index e5230969..75b6aac1 100644
--- a/seed/docs/HARNESS.md
+++ b/seed/docs/HARNESS.md
@@ -84,9 +84,10 @@ instead of grepping the raw file: `--summary` lists the turns, `--span A:B`
 prints a range, `--match RE` prints the turns whose text matches. `mem-weekly.sh`
 deletes traces older than a year, rewrites `reports/recurring-errors.md` (error
 lines normalized to a signature so runs differing only in a number collapse) and
-`reports/counts.md` (capture, retrieval, and application counts), commits the
-store as a git baseline with those reports included, then pulls and pushes the
-store's remote when one is set; add its cron line by hand, it is not installed:
+`reports/counts.md` (capture, retrieval, and application counts), which stay
+local and untracked, commits the store as a git baseline, then pulls and pushes
+the store's remote when one is set; add its cron line by hand, it is not
+installed:

     0 9 * * 0 <project>/bin/mem-weekly.sh

@@ -119,9 +120,17 @@ risks). A capture commits and pushes in the background; recall pulls at
 SessionStart and `mem-weekly.sh` pulls then pushes from cron. Every git call runs
 with `GIT_TERMINAL_PROMPT=0`, and recall's pull is bounded to five seconds, so an
 unreachable remote never blocks a session; it logs one line to
-`reports/sync.log` and continues with the local store. Store files are
-append-only, so a rebase does not conflict; on the rare conflict the hook logs
-one line and leaves the working tree untouched.
+`reports/sync.log` and continues with the local store.
+
+Two machines that each write before pulling do not strand either one. `INDEX.md`
+lines from two machines merge by union (the store's `.gitattributes` holds
+`traces/*/INDEX.md merge=union`), so both lines survive the rebase. The reports
+`mem-weekly.sh` regenerates are local and never shared: `reports/` is
+gitignored. A handoff claimed on two machines at once is archived under two names
+and injected once on each machine, because the pull disables rename detection
+(`-c merge.renames=false -s recursive`) so the two archive moves do not conflict.
+For anything else, the pull aborts the rebase, logs one line, and leaves the
+working tree untouched.

 ### The handoff

@@ -131,6 +140,10 @@ manifest's heading). The next session on any machine or harness, in the same
 repo, injects that file once under `## Handoff (claimed now)`, then archives it to
 `.loam/memory/handoff/<repo>/archive/<date>-<sid8>.md` and never reads it again.
 One writer per workstream, claimed once: it is not a shared last-writer-wins file.
+If sessions start on two machines at the same moment, before either has pulled
+the other's claim, each injects the handoff once (read twice in total) and
+archives it under its own session; both archives are kept and neither store is
+stranded.

 ## The one check

~~~~~~~~~~~~ evidence
