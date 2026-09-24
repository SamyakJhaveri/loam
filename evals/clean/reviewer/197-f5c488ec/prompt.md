## Ticket

~~~~~~~~~~~~ evidence
Brief:
Remove the `autoMemoryDirectory` key MEM-07 added to seed/.claude/settings.json and rewrite the HARNESS.md bullet that describes it, so each project keeps Claude Code's default per-project auto memory.
Where: seed/.claude/settings.json, seed/docs/HARNESS.md.
Done means: settings.json has no autoMemoryDirectory key and keeps cleanupPeriodDays 365 and every hook, deny, and sandbox key; a render carries neither the key nor `memstore/claude`; HARNESS.md says auto memory stays per project.
Out of scope: cleanupPeriodDays; the memory store, its hooks and scripts; the Always-on budget line on MEMORY.md; any migration of existing auto memory.
Blocked by: none

## Goal and why
MEM-07 (#175, PR #193, merged 2026-09-22) set `"autoMemoryDirectory": "~/memstore/claude"`. The key takes one fixed path, so every project rendered from Loam on a machine would share one MEMORY.md index instead of Claude Code's default `~/.claude/projects/<project>/memory/`, and Loam's own sessions (root `.claude` is `seed/.claude`) lost their existing memory index: a fresh `claude -p` in Loam on 2026-09-22 reported `/Users/samyakjhaveri/memstore/claude/`, a folder that did not exist.
Samyak chose on 2026-09-22 to keep auto memory per project: the store already keeps every session's scrubbed transcript per repository (traces/<repo>/), which is what "travels with the store" was for.
seed/.claude/settings.json is no longer pinned by the curated catalog (#183, PR #190), so no re-pin is needed.

## Do not touch
The standing list. Also: seed/.claude/hooks/, seed/bin/, seed/.loam/, seed/AGENTS.md.jinja, seed/CLAUDE.md.jinja, bin/factory, docs/research/.
Except: seed/.claude/settings.json, seed/docs/HARNESS.md (this ticket edits them).

## Out of scope
cleanupPeriodDays 365 stays.
The memory store, the mem-* hooks and scripts, and INDEX.md.
The Always-on budget bullet on MEMORY.md (seed/docs/HARNESS.md, about line 174).
Moving or merging anyone's existing auto memory.

## Approach
1. seed/.claude/settings.json: delete the `"autoMemoryDirectory": "~/memstore/claude",` line and nothing else; every other key stays byte for byte.
2. seed/docs/HARNESS.md, the Accepted risks bullet that starts "`settings.json` sets `autoMemoryDirectory`" (about lines 195 to 198): replace it with one bullet saying Claude auto memory stays in Claude Code's default per-project folder and is not moved into the store, because `autoMemoryDirectory` takes one fixed path that every project on the machine would share; the store keeps each session's scrubbed transcript per repository instead.
3. Commit before the checks run: the render check renders the committed HEAD.

## Done checks
```done-checks
python3 -c 'import json,sys; d=json.load(open("seed/.claude/settings.json")); h=d.get("hooks",{}); cmds=[x["command"] for e in h.values() for g in e for x in g["hooks"]]; j=" ".join(cmds); need=["mem-recall.sh","mem-capture.sh --throttle","fable-session-brief.sh","post-compact-reinject.sh"]; sys.exit(0 if "autoMemoryDirectory" not in d and d.get("cleanupPeriodDays")==365 and all(n in j for n in need) and sum("mem-capture.sh" in c for c in cmds)>=3 and len(d.get("permissions",{}).get("deny",[]))>=1 and "sandbox" in d else 1)' && pass settings-key-gone || fail settings-key-gone "autoMemoryDirectory is still set, or cleanupPeriodDays, a hook, a deny, or the sandbox key changed"
render_into; [ -n "$render_dir" ] || fail render "$render_err"; out=$(grep -rI 'memstore/claude' "$render_dir/.claude" "$render_dir/docs" 2>/dev/null); python3 -c 'import json,sys; sys.exit(0 if "autoMemoryDirectory" not in json.load(open(sys.argv[1])) else 1)' "$render_dir/.claude/settings.json" && [ -z "$out" ] && pass in-render || fail in-render "the render still sets autoMemoryDirectory or names memstore/claude: $out"
out=$(grep -n 'memstore/claude' seed/docs/HARNESS.md); [ -z "$out" ] && grep -qi 'per-project' seed/docs/HARNESS.md && pass harness-doc || fail harness-doc "HARNESS.md still names memstore/claude or does not say auto memory stays per-project: $out"
guard bin/check >/dev/null && pass check-green || fail check-green "bin/check"
```

## Worker
worker: claude
codex-review: no
effort: high
MAX_ROUNDS=2
goal: the done-checks block prints no FAIL line, or stop after 60 turns

## Decisions
#175, PR #193, docs/research/memory-design-2026-09-03.md (section 4.1), seed/docs/HARNESS.md

~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS settings-key-gone
PASS in-render
PASS harness-doc
PASS check-green

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
Followed the Approach as written: deleted only the autoMemoryDirectory line in seed/.claude/settings.json and replaced the one HARNESS.md Accepted-risks bullet with a per-project auto memory bullet; no other file touched.
docs/archive/specs/rebuild-research/research-cc-docs.md:83 still names autoMemoryDirectory as a Claude Code fact; left it, since it is archived research and not a Loam setting.
Done checks run from the worktree root after the commit (f60f78a3): PASS settings-key-gone, in-render, harness-doc, check-green.

~~~~~~~~~~~~ evidence

## Diff (aa494a74...HEAD)

~~~~~~~~~~~~ evidence
 seed/.claude/settings.json | 1 -
 seed/docs/HARNESS.md       | 8 ++++----
 2 files changed, 4 insertions(+), 5 deletions(-)

diff --git a/seed/.claude/settings.json b/seed/.claude/settings.json
index cad60b08..37cf172e 100644
--- a/seed/.claude/settings.json
+++ b/seed/.claude/settings.json
@@ -2,7 +2,6 @@
   "enabledPlugins": {
     "pyright-lsp@claude-plugins-official": true
   },
-  "autoMemoryDirectory": "~/memstore/claude",
   "cleanupPeriodDays": 365,
   "permissions": {
     "deny": [
diff --git a/seed/docs/HARNESS.md b/seed/docs/HARNESS.md
index 68166e39..ac3fe04a 100644
--- a/seed/docs/HARNESS.md
+++ b/seed/docs/HARNESS.md
@@ -192,10 +192,10 @@ removing it would cause a mistake.
   secret with no recognizable shape can therefore reach both the store's git
   history and the remote; forgetting a pushed trace means deleting the file,
   committing, and rewriting or reinitialising both the store repo and the remote.
-- `settings.json` sets `autoMemoryDirectory` to `~/memstore/claude`, so Claude
-  auto memory now lives in the store and travels with it through the store's git
-  history and remote, unscrubbed (settings cannot expand `LOAM_MEMSTORE`, so a
-  store moved elsewhere leaves auto memory at `~/memstore/claude`).
+- Claude auto memory stays in Claude Code's default per-project folder and is
+  not moved into the store: `autoMemoryDirectory` takes one fixed path, which
+  every project on the machine would share. The store keeps each session's
+  scrubbed transcript per repository instead.
 - Codex runs a repository hook only after the user trusts the project's `.codex`
   layer and reviews the hook definition once (Codex keeps a hash of it in its
   hooks state, and an edit to `hooks.json` asks again), so a Codex session before
~~~~~~~~~~~~ evidence
