## Ticket

~~~~~~~~~~~~ evidence
Brief:
Point Claude's own auto memory at the memory store and keep local transcripts for a year: two settings.json keys, the catalog re-pin the pinned settings file needs, and one HARNESS.md sentence.
Where: seed/.claude/settings.json, seed/docs/HARNESS.md, seed/.loam/runtime/assets/curated-catalog.json, docs/architecture-working/asset-intake/loam-inventory.json, seed/.loam/runtime/release-manifest.json and the regenerated files under seed/.loam/runtime/.
Done means: the done-checks block prints no FAIL line: settings.json carries autoMemoryDirectory and cleanupPeriodDays with every existing hook, deny, and sandbox key intact, the render carries the keys, the catalog re-pin qualifies, and HARNESS.md names the setting.
Out of scope: the AGENTS.md pointer (MEM-06); any hook or script change; syncing auto memory across machines; Codex memories.
Blocked by: #173 (MEM-04b).

## Goal and why
The 2026-09-03 design asks that Claude's built-in auto memory live inside the memory store so it travels with the store and is reviewed weekly, and that local transcripts be kept a year rather than the 30-day default (docs/research/memory-design-2026-09-03.md, sections 4.1 and 5.5; docs/research/memory-design-v2-2026-09-21.md, layers 1 and 3).
The official docs confirm two keys: autoMemoryDirectory (an absolute or `~/`-prefixed path, code.claude.com/docs/en/memory) and cleanupPeriodDays (days of local transcript retention, default 30, code.claude.com/docs/en/settings-reference and /data-usage).
Tradeoff to accept and state: settings.json cannot expand `$LOAM_MEMSTORE`, and the docs require an absolute or `~/`-prefixed value, so the directory is pinned to `~/memstore/claude`, the default store location; a user who moves the store by setting LOAM_MEMSTORE elsewhere gets auto memory left at `~/memstore/claude`, which is the closest form the setting supports and matches the design's own value.

## Do not touch
The standing list. Also: seed/AGENTS.md.jinja, seed/CLAUDE.md.jinja, seed/.claude/hooks/, seed/bin/, seed/.codex/, seed/.agents/, seed/.loam/, bin/factory, docs/architecture-working/.
Except: seed/.claude/settings.json, seed/.loam/runtime/assets/curated-catalog.json (only the entry with id support:seed/.claude/settings.json), docs/architecture-working/asset-intake/loam-inventory.json (only the row whose source_path is seed/.claude/settings.json), seed/.loam/runtime/release-manifest.json and any tracked file under seed/.loam/runtime/ that the build regenerates, seed/docs/HARNESS.md. This ticket edits settings.json and HARNESS.md; the rest is provenance bookkeeping for that one edit.

## Out of scope
The AGENTS.md memory pointer (MEM-06).
Any hook or script change; any new key beyond the two named.
Syncing auto memory across machines, and Codex memories.
Rewriting any hook, deny, or sandbox key in settings.json; they stay byte for byte.

## Approach
Same conventions as MEM-01. seed/.claude/settings.json gains two top-level keys and nothing else changes:

    "autoMemoryDirectory": "~/memstore/claude",
    "cleanupPeriodDays": 365,

Keep every existing hook command, deny prefix, and sandbox key byte for byte. The value `~/memstore/claude` is the design's section 4.1 value and sits inside the default store `${LOAM_MEMSTORE:-$HOME/memstore}`; the docs require an absolute or `~/`-prefixed path, so this is the closest expressible form (see Goal). cleanupPeriodDays is a plain integer number of days.

seed/.claude/settings.json is pinned by the curated catalog, so re-pin it exactly as MEM-01 step 8 did, after the edit is final:
1. Recompute the entry: in a node one-liner import extractSourceUnits and sha256 from seed/.loam/runtime/dist/src/assets/units.js (the real export name; #154's text said extractUnits and GUARD-01's run corrected it) over the file, and write the new source.sha256 and per-unit start, end, and sha256 into the one entry with id support:seed/.claude/settings.json, changing nothing else in seed/.loam/runtime/assets/curated-catalog.json.
2. Prove it with `node bin/factory-catalog-provenance.mjs` and `node seed/.loam/runtime/launcher.mjs qualify catalog`, both printing passed (LOAM_FACTORY_TOOLCHAIN and LOAM_FACTORY_COPIER are exported in the runner's login shell).
3. Set sha256 and bytes on the row whose source_path is seed/.claude/settings.json in docs/architecture-working/asset-intake/loam-inventory.json to the new file's values.
4. Regenerate the runtime release manifest with `npm --prefix seed/.loam/runtime ci --ignore-scripts && npm --prefix seed/.loam/runtime run build`, and commit every tracked file that changed under seed/.loam/runtime/ with the catalog and the inventory. Prove the stack with `node seed/.loam/runtime/launcher.mjs qualify package`, then bin/check. Record the new digests in decisions.md.

seed/docs/HARNESS.md: add one sentence in The hooks or Accepted risks that names autoMemoryDirectory and says Claude auto memory now lives in the store under `~/memstore/claude` and travels with it, and one Always-on budget line: auto memory adds at most the first 200 lines or 25 KB of MEMORY.md to the context at session start (the docs' read limit). render_into renders the committed HEAD, so commit before the render check runs.

## Done checks
```done-checks
python3 -c 'import json,sys; d=json.load(open("seed/.claude/settings.json")); h=d.get("hooks",{}); cmds=[x["command"] for e in h.values() for g in e for x in g["hooks"]]; j=" ".join(cmds); need=["mem-recall.sh","mem-capture.sh --throttle","fable-session-brief.sh","post-compact-reinject.sh"]; sys.exit(0 if d.get("autoMemoryDirectory")=="~/memstore/claude" and d.get("cleanupPeriodDays")==365 and all(n in j for n in need) and sum("mem-capture.sh" in c for c in cmds)>=3 and len(d.get("permissions",{}).get("deny",[]))>=1 and "sandbox" in d else 1)' && pass settings-keys || fail settings-keys "autoMemoryDirectory or cleanupPeriodDays is wrong, or a hook, deny, or sandbox key was dropped"
render_into; [ -n "$render_dir" ] || fail render "$render_err"; python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); sys.exit(0 if d.get("autoMemoryDirectory")=="~/memstore/claude" and d.get("cleanupPeriodDays")==365 else 1)' "$render_dir/.claude/settings.json" && pass in-render || fail in-render "the render is missing the auto-memory keys"
grep -q 'autoMemoryDirectory' seed/docs/HARNESS.md && pass harness-doc || fail harness-doc "HARNESS.md does not name autoMemoryDirectory"
guard sh -c 'N="${LOAM_FACTORY_TOOLCHAIN:?set LOAM_FACTORY_TOOLCHAIN}/bin/node"; "$N" seed/.loam/runtime/launcher.mjs qualify catalog && "$N" bin/factory-catalog-provenance.mjs' >/dev/null 2>&1 && pass catalog-repin || fail catalog-repin "catalog qualify or provenance failed; re-pin settings.json as MEM-01 step 8 did"
[ -n "${LOAM_HOOK:-}" ] && pass check-green || { guard bin/check >/dev/null && pass check-green || fail check-green "bin/check"; }
```

## Worker
worker: claude
codex-review: no
effort: xhigh
MAX_ROUNDS=3
ROUND_BUDGET_USD=20
goal: the done-checks block prints no FAIL line, or stop after 60 turns

## Decisions
docs/research/memory-design-2026-09-03.md (sections 4.1 and 5.5), docs/research/memory-design-v2-2026-09-21.md (layers 1 and 3)

~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS settings-keys
PASS in-render
PASS harness-doc
PASS catalog-repin
PASS check-green

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
- Departure from Approach steps 1-4 (catalog re-pin, inventory row, npm build, manifest): #183 (b4e03233) deleted the support:seed/.claude/settings.json catalog entry and its inventory row, and 3e2f2936 made ASSET-LAYERS say a live working file is never pinned; git grep finds no entry, row, or release-manifest reference, so there is nothing to re-pin and no new digests to record; proof is qualify catalog and factory-catalog-provenance passing after the edit.
- Tradeoff accepted: settings.json cannot expand $LOAM_MEMSTORE and the docs require an absolute or ~/-prefixed path, so autoMemoryDirectory is pinned to ~/memstore/claude (the design's section 4.1 value, inside the default store); a user who sets LOAM_MEMSTORE elsewhere keeps auto memory at ~/memstore/claude.
- settings.json: the two keys go right after enabledPlugins via a two-line insert (git diff -U0 shows 2 added, 0 removed lines), so every hook, deny, and sandbox line stays byte for byte; no json round-trip.
- HARNESS.md: the sentence sits in Accepted risks because mem-capture.sh and mem-weekly.sh gitignore only .throttle/ and reports/ then git add -A, so ~/memstore/claude is committed and pushed unscrubbed; it also states the LOAM_MEMSTORE tradeoff in one parenthetical; the Always-on budget gains the 200-line / 25 KB MEMORY.md bullet.
- Result: frozen checks.sh run from the worktree root at 4413be1b printed PASS for settings-keys, in-render, harness-doc, catalog-repin, check-green and no FAIL line.

~~~~~~~~~~~~ evidence

## Diff (360fd6fe...HEAD)

~~~~~~~~~~~~ evidence
 seed/.claude/settings.json | 2 ++
 seed/docs/HARNESS.md       | 6 ++++++
 2 files changed, 8 insertions(+)

diff --git a/seed/.claude/settings.json b/seed/.claude/settings.json
index 1499335e..cad60b08 100644
--- a/seed/.claude/settings.json
+++ b/seed/.claude/settings.json
@@ -2,6 +2,8 @@
   "enabledPlugins": {
     "pyright-lsp@claude-plugins-official": true
   },
+  "autoMemoryDirectory": "~/memstore/claude",
+  "cleanupPeriodDays": 365,
   "permissions": {
     "deny": [
       "Bash(rm -rf:*)",
diff --git a/seed/docs/HARNESS.md b/seed/docs/HARNESS.md
index 75b6aac1..68166e39 100644
--- a/seed/docs/HARNESS.md
+++ b/seed/docs/HARNESS.md
@@ -171,6 +171,8 @@ removing it would cause a mistake.
   capture runs at most once per ten minutes. The scrub adds one regex pass over
   the transcript per capture. Recall waits at most five seconds for a pull from
   the store's remote; the capture's push runs in the background and never waits.
+- Auto memory: Claude Code adds at most the first 200 lines or 25 KB of
+  `MEMORY.md` to the context at session start.

 ## Accepted risks, stated rather than hidden

@@ -190,6 +192,10 @@ removing it would cause a mistake.
   secret with no recognizable shape can therefore reach both the store's git
   history and the remote; forgetting a pushed trace means deleting the file,
   committing, and rewriting or reinitialising both the store repo and the remote.
+- `settings.json` sets `autoMemoryDirectory` to `~/memstore/claude`, so Claude
+  auto memory now lives in the store and travels with it through the store's git
+  history and remote, unscrubbed (settings cannot expand `LOAM_MEMSTORE`, so a
+  store moved elsewhere leaves auto memory at `~/memstore/claude`).
 - Codex runs a repository hook only after the user trusts the project's `.codex`
   layer and reviews the hook definition once (Codex keeps a hash of it in its
   hooks state, and an edit to `hooks.json` asks again), so a Codex session before
~~~~~~~~~~~~ evidence
