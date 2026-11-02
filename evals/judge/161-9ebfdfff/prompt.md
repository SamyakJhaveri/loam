## Ticket

~~~~~~~~~~~~ evidence
Brief:
Let a Codex session in a rendered project land in the same memory store as a Claude session, through the same four scripts, and make the weekly report count capture, retrieval, and application, not only recurring errors.
Where: seed/.codex/config.toml (the hooks line), seed/.codex/hooks.json (new), seed/.claude/hooks/mem-capture.sh (the Codex rollout line shape for the INDEX line), seed/bin/mem-weekly.sh (three counts), seed/docs/HARNESS.md (The hooks, Accepted risks), docs/BOOTSTRAP.md (the .codex/ bullet), seed/.loam/runtime/assets/curated-catalog.json (the support entry that pins seed/.codex/config.toml), bin/tests/test_render_smoke.py (a Codex hooks.json assertion), and the repo key computed from the remote name in mem-capture.sh, mem-recall.sh, and memsearch.
Done means: the done-checks block prints no FAIL line: hooks on in the Codex config, a hooks.json that registers the MEM-01 scripts on SessionEnd, PreCompact, Stop, and SessionStart, capture proven on a fake Codex rollout payload with the first user message in the INDEX line, the weekly report carrying three labeled counts, a fresh render carrying all of it, the docs updated.
Out of scope: Codex native memories ([features] memories); the note gate (MEM-03); any model call; any change to mem-recall.sh or memsearch beyond the repo-key function; the factory.
Blocked by: #154 (MEM-01) merged.

## Goal and why
MEM-01 excluded Codex only because the seed sets `features.hooks = false`; Codex hooks are Claude-compatible, verified in openai/codex at `a866315` on 2026-09-21: the same event names, the same stdin JSON (`session_id`, `transcript_path`, `cwd`), exit 2 on Stop blocks the stop, `transcript_path` is the rollout JSONL under `~/.codex/sessions/`, and a repo ships hooks in `.codex/hooks.json` with the same shape as `.claude/settings.json` (docs/research/memory-crossref-2026-09-21.md, "What the memo adds").
Codex rollout lines are `{timestamp, type, payload}`, not Claude's `{type, message}`, so the INDEX first-user-message field needs the second shape.
The memo's one measurement idea worth taking is to count capture, retrieval, and application separately; three grep lines in `mem-weekly.sh` do it, and they were folded here because MEM-01 was mid-run with a frozen prompt when the pick landed.
Decision: docs/research/memory-crossref-2026-09-21.md, "The plan".

## Do not touch
The standing list. Also: seed/AGENTS.md.jinja, seed/CLAUDE.md.jinja, seed/.claude/settings.json, seed/.claude/hooks/fable-session-brief.sh, seed/.claude/hooks/post-compact-reinject.sh, seed/.codex/rules/, seed/.loam/, seed/.agents/, bin/factory, docs/architecture-working/.
Except: seed/.codex/config.toml (one line), seed/.codex/hooks.json (created), seed/.claude/hooks/mem-capture.sh (the Codex line shape and the repo-key function), seed/.claude/hooks/mem-recall.sh and seed/bin/memsearch (the repo-key function only), seed/bin/mem-weekly.sh (three counts and the repo-key function), seed/.loam/runtime/assets/curated-catalog.json (only the entry with id support:seed/.codex/config.toml and its units), docs/architecture-working/asset-intake/loam-inventory.json (only the row whose source_path is seed/.codex/config.toml), seed/.loam/runtime/release-manifest.json and any tracked file under seed/.loam/runtime/ that the build regenerates (provenance bookkeeping for the one re-pin, as MEM-01 #154 granted), bin/tests/test_render_smoke.py (one new assertion that the render carries .codex/hooks.json with the four events).

## Out of scope
Codex native memories: `[features] memories` stays as the user has it; nothing in the seed sets it.
MEM-03's note gate and any second Stop entry.
Any change to mem-recall.sh or memsearch beyond the repo-key function in Approach step 0; any change to the Claude hook entries in seed/.claude/settings.json.
Any model call, SQLite, embeddings.
The trust step a Codex user performs once (documented, not automated).

## Approach
Same conventions as MEM-01: bash with `set -uo pipefail`, JSON through python3, no jq, hooks exit 0 always, store root `${LOAM_MEMSTORE:-$HOME/memstore}`.
0. Repo key. In every script that computes `<repo>` (mem-capture.sh, mem-recall.sh, memsearch, mem-weekly.sh counts), replace the basename of `git rev-parse --show-toplevel` with: the basename of `git -C cwd remote get-url origin` with a trailing `.git` and any trailing slash removed; fall back to the toplevel basename when there is no origin; fall back to the basename of cwd when there is no git. Put it in one function in each script; no shared library file. Reason: the factory's worktrees are named `loam-154`, `loam-hang`, and so on, and each would otherwise start with an empty memory.
1. seed/.codex/config.toml: change `hooks = false` to `hooks = true` under `[features]` (Codex 0.153 and later default it on; the explicit line stays so the intent is visible). Touch nothing else; `default_permissions` must stay above the first table.
2. seed/.codex/hooks.json: a top-level `hooks` object with the same shape Codex parses (`hooks` -> event name -> array of `{matcher, hooks: [{type: "command", command, timeout}]}`): `SessionEnd` and `PreCompact` running mem-capture.sh (timeout 10), `Stop` running mem-capture.sh with `--throttle 600` (timeout 10), `SessionStart` with matcher `startup|resume|clear` running mem-recall.sh (timeout 5). Name each script by the same relative form the Claude entries in seed/.claude/settings.json use; the scripts read `cwd` from the payload, so they do not depend on the hook's working directory.
3. seed/.claude/hooks/mem-capture.sh: when extracting the first user message for the INDEX line, handle both line shapes in the one python3 pass: Claude (`type == "user"`, `message.content` as a string or a list of text blocks) and Codex (`type == "event_msg"` with `payload.type == "user_message"` and the text in `payload.message`, or `payload.type == "item_completed"` whose `payload.item.type == "user_message"` with the text in `payload.item.text` or `payload.item.message`). Ignore a user message that starts with `<` (injected context). Change nothing else in the script.
4. seed/bin/mem-weekly.sh: after the recurring-errors report, write `$STORE/reports/counts.md` with three lines: `capture <traces> traces, <sessions> sessions seen` where traces is the count of `traces/*/*.jsonl` and sessions is the count of `*.jsonl` directly under `${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects/*/` plus `rollout-*.jsonl` under `${CODEX_HOME:-$HOME/.codex}/sessions/`, or `n/a` when neither directory exists; `retrieval <n>` where n is the number of trace lines containing `memsearch`; `application <n>` where n is the number of trace lines matching `APPLICABLE|STALE|UNVERIFIED`. Plain grep -c over `traces/`, summed; no other change.
5. seed/docs/HARNESS.md: in The hooks, say the same scripts run under Codex through `.codex/hooks.json`; add one Accepted risks line: Codex runs a repo hook only after the user trusts the project's `.codex` layer and reviews the hook definition once (a hash is kept in Codex's hooks state; an edit to hooks.json asks again), so a Codex session before that step captures nothing. docs/BOOTSTRAP.md: rewrite the `.codex/` bullet (line 21): hooks ship in `.codex/hooks.json`, `features.hooks` is on, inert until the project is trusted. Do not write a digit followed by "seed hooks" or "shipped hooks".
6. Re-pin the catalog entry support:seed/.codex/config.toml exactly as MEM-01 step 8 did for settings.json (extractUnits and sha256 from seed/.loam/runtime/dist/src/assets/units.js; node bin/factory-catalog-provenance.mjs and node seed/.loam/runtime/launcher.mjs qualify catalog both print passed). Record the new digest in decisions.md.
7. bin/tests/test_render_smoke.py: one assertion that the render's `.codex/hooks.json` parses and names SessionEnd, PreCompact, Stop, SessionStart. If `seed/.codex/hooks/__pycache__/` is present in the worktree, remove it; it is an orphan with no source.
8. Commit as you go; render_into needs the commits.

## Done checks
```done-checks
grep -Eq '^hooks *= *true' seed/.codex/config.toml && python3 -c 'import tomllib;d=tomllib.load(open("seed/.codex/config.toml","rb"));import sys;sys.exit(0 if d["default_permissions"]=="loam" and d["features"]["hooks"] is True and d["features"]["multi_agent"] is True else 1)' && pass hooks-on || fail hooks-on "features.hooks is not true or the config lost a key"
python3 -c 'import json,sys;h=json.load(open("seed/.codex/hooks.json"))["hooks"];c=lambda e:" ".join(x["command"] for g in h[e] for x in g["hooks"]);sys.exit(0 if "mem-capture.sh" in c("SessionEnd") and "mem-capture.sh" in c("PreCompact") and "mem-capture.sh --throttle" in c("Stop") and "mem-recall.sh" in c("SessionStart") and any("startup" in (g.get("matcher") or "") for g in h["SessionStart"]) else 1)' && pass hooks-json || fail hooks-json "hooks.json lacks an event, a script, or the SessionStart matcher"
tmp=$(mktemp -d); printf '{"timestamp":"2026-09-21T00:00:00Z","type":"session_meta","payload":{"id":"c0dec0de1234"}}\n{"timestamp":"2026-09-21T00:00:01Z","type":"event_msg","payload":{"type":"user_message","message":"codex memstore probe"}}\n' > "$tmp/rollout.jsonl"; for i in 1 2; do printf '{"session_id":"c0dec0de1234","transcript_path":"%s/rollout.jsonl","cwd":"%s","hook_event_name":"SessionEnd"}' "$tmp" "$PWD" | LOAM_MEMSTORE="$tmp/store" seed/.claude/hooks/mem-capture.sh >/dev/null 2>&1; done; n=$(ls "$tmp/store/traces"/*/*.jsonl 2>/dev/null | wc -l | tr -d ' '); idx=$(cat "$tmp/store/traces"/*/INDEX.md 2>/dev/null); [ "$n" = 1 ] && [ "$(grep -c c0dec0de <<<"$idx")" = 1 ] && grep -q 'codex memstore probe' <<<"$idx" && pass codex-capture || fail codex-capture "trace files: $n; INDEX lacks the session or the Codex first message"
printf '{"type":"user","message":{"content":"claude probe"}}\n{"type":"assistant","message":{"content":[{"type":"text","text":"ran memsearch; label STALE"}]}}\n' > "$tmp/c.jsonl"; printf '{"session_id":"abcdef1234","transcript_path":"%s/c.jsonl","cwd":"%s"}' "$tmp" "$PWD" | LOAM_MEMSTORE="$tmp/store" seed/.claude/hooks/mem-capture.sh >/dev/null 2>&1; LOAM_MEMSTORE="$tmp/store" seed/bin/mem-weekly.sh >/dev/null 2>&1; cnt=$(cat "$tmp/store/reports/counts.md" 2>/dev/null); grep -Eq '^capture [0-9]+ traces' <<<"$cnt" && grep -Eq '^retrieval [0-9]+' <<<"$cnt" && grep -Eq '^application [0-9]+' <<<"$cnt" && [ "$(grep -E '^retrieval' <<<"$cnt" | awk '{print $2}')" -ge 1 ] && [ "$(grep -E '^application' <<<"$cnt" | awk '{print $2}')" -ge 1 ] && pass weekly-counts || fail weekly-counts "counts.md missing or a count is zero: $cnt"
grep -q 'hooks.json' seed/docs/HARNESS.md && grep -qi 'trust' seed/docs/HARNESS.md && grep -q 'hooks.json' docs/BOOTSTRAP.md && ! grep -q 'features.hooks. is off' docs/BOOTSTRAP.md && pass docs-updated || fail docs-updated "HARNESS.md or BOOTSTRAP.md does not describe the Codex hooks or the trust step"
git -C "$tmp" init -q wt-a && git -C "$tmp/wt-a" remote add origin git@example.com:someone/probe-repo.git && git -C "$tmp" init -q wt-b-other-name && git -C "$tmp/wt-b-other-name" remote add origin https://example.com/someone/probe-repo.git; for d in wt-a wt-b-other-name; do printf '{"session_id":"%s0000000","transcript_path":"%s/c.jsonl","cwd":"%s/%s"}' "$d" "$tmp" "$tmp" "$d" | LOAM_MEMSTORE="$tmp/store" seed/.claude/hooks/mem-capture.sh >/dev/null 2>&1; done; [ -d "$tmp/store/traces/probe-repo" ] && [ "$(ls "$tmp/store/traces/probe-repo"/*.jsonl* 2>/dev/null | wc -l | tr -d ' ')" = 2 ] && pass repo-key || fail repo-key "two worktrees of the same remote did not land in traces/probe-repo"
render_into; [ -n "$render_dir" ] || fail render "$render_err"; [ -f "$render_dir/.codex/hooks.json" ] && grep -Eq '^hooks *= *true' "$render_dir/.codex/config.toml" && [ -x "$render_dir/.claude/hooks/mem-capture.sh" ] && pass in-render || fail in-render "the render lacks hooks.json, the hooks line, or the capture script"
[ -n "${LOAM_HOOK:-}" ] && pass check-green || { guard bin/check >/dev/null && pass check-green || fail check-green "bin/check"; }
```

## Merge checklist
- In a fresh render, trust the project in Codex, review the hook definitions when Codex asks, run one Codex turn, and confirm ~/memstore/traces/<project>/INDEX.md gained a line with the first prompt.
- Confirm a Claude session in the same render still lands its line.

## Worker
worker: claude
codex-review: no
effort: xhigh
MAX_ROUNDS=3
ROUND_BUDGET_USD=25
goal: the done-checks block prints no FAIL line, or stop after 60 turns

## Decisions
docs/research/memory-crossref-2026-09-21.md ("What the memo adds", "The plan"), docs/research/memory-design-2026-09-03.md (section 4.5), docs/research/curation-2026-09-20.md (pick 1), docs/architecture-working/tickets/README.md (Curation verdicts)

~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS hooks-on
PASS hooks-json
PASS codex-capture
PASS weekly-counts
PASS docs-updated
PASS repo-key
PASS in-render
PASS check-green

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
- State on entry: prior rounds already implemented every Approach step (hooks-on, hooks.json, mem-capture Codex+repo-key, mem-recall/memsearch/mem-weekly repo-key, weekly counts, docs, catalog re-pin, render-smoke assertion). Running frozen/checks.sh showed 7 PASS and only check-green FAIL: bin/check failed four provenance/rebuild cases (package.valid-payload, rebuild.exact, render.exact-payload, provenance.inventory-dispositions).
- Root cause: round-1 revert 6dce2a8a undid the inventory and release-manifest re-pin, claiming both are do-not-touch. That claim is wrong. The ticket Except clause names both, and the supervisor's frozen exempt.txt lists docs/architecture-working/asset-intake/loam-inventory.json, seed/.loam/runtime/, and seed/.loam/runtime/release-manifest.json. The gate at frozen/factory:904-905 fails a file only when under protected AND not under exempt, so editing them is allowed.
- Reversed the revert. Did NOT run `git revert 6dce2a8a`: that would restore 37438684's manifest whose catalog digest (2e6113f1) is stale after a5cd4b8c edited the catalog notes.
- Inventory: `git checkout 37438684 -- loam-inventory.json`. config.toml is byte-identical since 37438684, so the row (sha256 c874a9599f28af31ab6077ca31c4b0f53a53ff4b5b814ce8bcf8e8fa6a0670a2, bytes 920) is exact. Only that one row changed.
- Manifest: regenerated via createReleaseManifest from dist/src/installation/package.js on the runtime root, written with JSON.stringify(m,null,2)+"\n" (proven byte-identical round-trip on the committed file). Only two fields changed: files["assets/curated-catalog.json"] e9ad044e -> ff611c91 (current catalog digest) and sourceDigest 7071d0c1 -> ce781464. outputDigest and dependencyDigest unchanged; 106 file keys, same order.
- Kept the a5cd4b8c catalog notes edit ("hooks on"): in scope (the config.toml entry), accurate, and reverting it would only force a second manifest regeneration.
- Config.toml digest: c874a9599f28af31ab6077ca31c4b0f53a53ff4b5b814ce8bcf8e8fa6a0670a2. Current catalog digest: ff611c917dca5223a33d4ec1b03bfbd7e8ff84b8ca251ea6782c2db231d3d27e.
- Step 7 orphan: seed/.codex/hooks/__pycache__ absent; nothing to remove.
- After the fix: qualify package 14/14, qualify catalog 5/5, catalog-provenance 3/3 all pass on the working tree.

~~~~~~~~~~~~ evidence

## Diff (ed5c98dd...HEAD)

~~~~~~~~~~~~ evidence
 bin/tests/test_render_smoke.py                             |  7 +++++++
 docs/BOOTSTRAP.md                                          |  2 +-
 docs/architecture-working/asset-intake/loam-inventory.json |  4 ++--
 seed/.claude/hooks/mem-capture.sh                          | 74 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++-------------
 seed/.claude/hooks/mem-recall.sh                           | 19 ++++++++++++++++++-
 seed/.codex/config.toml                                    |  2 +-
 seed/.codex/hooks.json                                     | 49 +++++++++++++++++++++++++++++++++++++++++++++++++
 seed/.loam/runtime/assets/curated-catalog.json             |  6 +++---
 seed/.loam/runtime/release-manifest.json                   |  4 ++--
 seed/bin/mem-weekly.sh                                     | 20 ++++++++++++++++++++
 seed/bin/memsearch                                         | 19 ++++++++++++++++++-
 seed/docs/HARNESS.md                                       | 13 ++++++++++++-
 12 files changed, 194 insertions(+), 25 deletions(-)

diff --git a/bin/tests/test_render_smoke.py b/bin/tests/test_render_smoke.py
index dbf4f935..5677e29b 100644
--- a/bin/tests/test_render_smoke.py
+++ b/bin/tests/test_render_smoke.py
@@ -152,6 +152,13 @@ class RenderSmoke(unittest.TestCase):
         )
         self.assertLess(key, first_table)

+    def test_codex_hooks_json_registers_the_four_events(self):
+        hooks = json.loads((self.out / ".codex/hooks.json").read_text())["hooks"]
+        self.assertEqual(
+            sorted(hooks),
+            ["PreCompact", "SessionEnd", "SessionStart", "Stop"],
+        )
+
     def test_each_hook_runs_and_exits_zero(self):
         hooks = sorted((self.out / ".claude/hooks").glob("*.sh"))
         self.assertTrue(hooks, "no hooks rendered")
diff --git a/docs/BOOTSTRAP.md b/docs/BOOTSTRAP.md
index e1836272..1c17e613 100644
--- a/docs/BOOTSTRAP.md
+++ b/docs/BOOTSTRAP.md
@@ -18,7 +18,7 @@ Copier asks three questions: `project_name`, `github_repo` (blank skips GitHub s
 - `CLAUDE.md` importing `AGENTS.md` (the one prose home), both with fill-in placeholders.
 - `.claude/`: Claude Code settings (deny list, sandbox) and the lifecycle hook scripts: the Fable session brief and post-compaction reminder, plus the zero-model memory layer (`mem-capture.sh` on SessionEnd/PreCompact/Stop copies each transcript to the per-user store; `mem-recall.sh` on SessionStart injects the last few sessions). Companion tools `bin/memsearch` and `bin/mem-weekly.sh` search the store and report recurring errors. See `docs/HARNESS.md`.
 - `.agents/skills/`: three skills shared by Claude Code (via symlink) and Codex: `catchup` (session bootstrap), `fable-prompting` (index over the Fable 5.1 guide), `hypothesis-tree` (persistent investigation tree).
-- `.codex/`: Codex configuration and execution rules (`rules/loam.rules`, the same deny families). No hooks ship; `features.hooks` is off. Inert until you trust the project in Codex.
+- `.codex/`: Codex configuration and execution rules (`rules/loam.rules`, the same deny families), plus `.codex/hooks.json`, which registers the memory hooks; `features.hooks` is on. All of it is inert until you trust the project in Codex.
 - `.loam/runtime/`: the qualification runtime; see `docs/runtime/SETUP.md`.

 ## After bootstrap
diff --git a/docs/architecture-working/asset-intake/loam-inventory.json b/docs/architecture-working/asset-intake/loam-inventory.json
index 40c6cebd..91a5e887 100644
--- a/docs/architecture-working/asset-intake/loam-inventory.json
+++ b/docs/architecture-working/asset-intake/loam-inventory.json
@@ -3198,8 +3198,8 @@
       "resolved_path": "/Users/samyakjhaveri/Desktop/loam/seed/.codex/config.toml",
       "kind": "support_or_config",
       "name": "config",
-      "sha256": "64f5d0069afd8c9372a08c0478ac3a24da7509289699fbb3546822f737ca5b15",
-      "bytes": 921,
+      "sha256": "c874a9599f28af31ab6077ca31c4b0f53a53ff4b5b814ce8bcf8e8fa6a0670a2",
+      "bytes": 920,
       "layer": "active_seed",
       "baseline_decision": "include_curated_source_pending_adaptation",
       "runtime_enabled_by_audit": false,
diff --git a/seed/.claude/hooks/mem-capture.sh b/seed/.claude/hooks/mem-capture.sh
index 90486077..b9dd0a24 100755
--- a/seed/.claude/hooks/mem-capture.sh
+++ b/seed/.claude/hooks/mem-capture.sh
@@ -63,6 +63,42 @@ tp = payload.get("transcript_path") or ""
 sid = payload.get("session_id") or ""
 cwd = payload.get("cwd") or ""

+def user_text(rec):
+    # Return the user-message text for a transcript record, or None when the
+    # record is not a user message. Two transcript shapes:
+    #   Claude  - {"type":"user","message":{"content": str | [text blocks]}}
+    #   Codex   - {"type":"event_msg","payload": ...}, the rollout JSONL line, with
+    #             a "user_message" event or an "item_completed" wrapping a user item.
+    if not isinstance(rec, dict):
+        return None
+    kind = rec.get("type")
+    if kind == "user":
+        msg = rec.get("message", rec)
+        content = msg.get("content") if isinstance(msg, dict) else msg
+        if isinstance(content, list):
+            parts = []
+            for block in content:
+                if isinstance(block, dict):
+                    parts.append(str(block.get("text", "")))
+                else:
+                    parts.append(str(block))
+            content = " ".join(parts)
+        return str(content)
+    if kind == "event_msg":
+        payload = rec.get("payload")
+        if isinstance(payload, dict):
+            ptype = payload.get("type")
+            if ptype == "user_message":
+                return str(payload.get("message", ""))
+            if ptype == "item_completed":
+                item = payload.get("item")
+                if isinstance(item, dict) and item.get("type") == "user_message":
+                    text = item.get("text")
+                    if text is None:
+                        text = item.get("message")
+                    return str(text if text is not None else "")
+    return None
+
 first = ""
 if tp:
     try:
@@ -75,19 +111,14 @@ if tp:
                     rec = json.loads(line)
                 except Exception:
                     continue
-                if not isinstance(rec, dict) or rec.get("type") != "user":
+                text = user_text(rec)
+                if text is None:
+                    continue
+                text = text.strip()
+                # Skip injected context (Claude wraps it in <...> tags) and empty turns.
+                if not text or text.startswith("<"):
                     continue
-                msg = rec.get("message", rec)
-                content = msg.get("content") if isinstance(msg, dict) else msg
-                if isinstance(content, list):
-                    parts = []
-                    for block in content:
-                        if isinstance(block, dict):
-                            parts.append(str(block.get("text", "")))
-                        else:
-                            parts.append(str(block))
-                    content = " ".join(parts)
-                first = str(content)
+                first = text
                 break
     except Exception:
         first = ""
@@ -105,7 +136,24 @@ CWD="${REST%%$'\t'*}"; FIRST="${REST#*$'\t'}"
 [ -f "$TP" ] || exit 0
 [ -n "$SID" ] || exit 0

-REPO="$(basename "$(git -C "$CWD" rev-parse --show-toplevel 2>/dev/null || echo "$CWD")")"
+# Key a session's traces by the origin remote, not the checkout directory: the
+# factory renders many worktrees (loam-154, loam-161, ...) of one repo, and a
+# per-directory key would scatter their memory. Fall back to the toplevel
+# basename with no origin, then to the cwd basename with no git.
+repo_key() {
+  local dir="$1" url top
+  url="$(git -C "$dir" remote get-url origin 2>/dev/null)"
+  if [ -n "$url" ]; then
+    url="${url%/}"; url="${url%.git}"
+    basename "$url"
+    return
+  fi
+  top="$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null)"
+  [ -n "$top" ] && { basename "$top"; return; }
+  basename "$dir"
+}
+
+REPO="$(repo_key "$CWD")"
 DST="$STORE/traces/$REPO"
 mkdir -p "$DST" 2>/dev/null || exit 0

diff --git a/seed/.claude/hooks/mem-recall.sh b/seed/.claude/hooks/mem-recall.sh
index af1d9566..fc3402e4 100755
--- a/seed/.claude/hooks/mem-recall.sh
+++ b/seed/.claude/hooks/mem-recall.sh
@@ -24,7 +24,24 @@ if isinstance(payload, dict):
 ' 2>/dev/null)"

 [ -n "$CWD" ] || CWD="$PWD"
-REPO="$(basename "$(git -C "$CWD" rev-parse --show-toplevel 2>/dev/null || echo "$CWD")")"
+
+# Key by the origin remote so recall reads the same directory mem-capture writes
+# across the factory's per-worktree checkouts. Fall back to the toplevel basename
+# with no origin, then to the cwd basename with no git.
+repo_key() {
+  local dir="$1" url top
+  url="$(git -C "$dir" remote get-url origin 2>/dev/null)"
+  if [ -n "$url" ]; then
+    url="${url%/}"; url="${url%.git}"
+    basename "$url"
+    return
+  fi
+  top="$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null)"
+  [ -n "$top" ] && { basename "$top"; return; }
+  basename "$dir"
+}
+
+REPO="$(repo_key "$CWD")"
 INDEX="$STORE/traces/$REPO/INDEX.md"
 [ -f "$INDEX" ] || exit 0

diff --git a/seed/.codex/config.toml b/seed/.codex/config.toml
index af51f47a..af516a91 100644
--- a/seed/.codex/config.toml
+++ b/seed/.codex/config.toml
@@ -5,7 +5,7 @@ approval_policy = "never"
 default_permissions = "loam"

 [features]
-hooks = false
+hooks = true
 multi_agent = true

 [agents]
diff --git a/seed/.codex/hooks.json b/seed/.codex/hooks.json
new file mode 100644
index 00000000..1553c9e2
--- /dev/null
+++ b/seed/.codex/hooks.json
@@ -0,0 +1,49 @@
+{
+  "hooks": {
+    "SessionEnd": [
+      {
+        "hooks": [
+          {
+            "type": "command",
+            "command": ".claude/hooks/mem-capture.sh",
+            "timeout": 10
+          }
+        ]
+      }
+    ],
+    "PreCompact": [
+      {
+        "hooks": [
+          {
+            "type": "command",
+            "command": ".claude/hooks/mem-capture.sh",
+            "timeout": 10
+          }
+        ]
+      }
+    ],
+    "Stop": [
+      {
+        "hooks": [
+          {
+            "type": "command",
+            "command": ".claude/hooks/mem-capture.sh --throttle 600",
+            "timeout": 10
+          }
+        ]
+      }
+    ],
+    "SessionStart": [
+      {
+        "matcher": "startup|resume|clear",
+        "hooks": [
+          {
+            "type": "command",
+            "command": ".claude/hooks/mem-recall.sh",
+            "timeout": 5
+          }
+        ]
+      }
+    ]
+  }
+}
diff --git a/seed/.loam/runtime/assets/curated-catalog.json b/seed/.loam/runtime/assets/curated-catalog.json
index 9acd8d51..98abca7c 100644
--- a/seed/.loam/runtime/assets/curated-catalog.json
+++ b/seed/.loam/runtime/assets/curated-catalog.json
@@ -32252,7 +32252,7 @@
       "source": {
         "type": "regular-file",
         "path": "seed/.codex/config.toml",
-        "sha256": "64f5d0069afd8c9372a08c0478ac3a24da7509289699fbb3546822f737ca5b15"
+        "sha256": "c874a9599f28af31ab6077ca31c4b0f53a53ff4b5b814ce8bcf8e8fa6a0670a2"
       },
       "attribution": {
         "author": "Samyak Jhaveri",
@@ -32281,7 +32281,7 @@
           "role": "body",
           "start": 1,
           "end": 28,
-          "sha256": "64f5d0069afd8c9372a08c0478ac3a24da7509289699fbb3546822f737ca5b15"
+          "sha256": "c874a9599f28af31ab6077ca31c4b0f53a53ff4b5b814ce8bcf8e8fa6a0670a2"
         }
       ],
       "preservation": {
@@ -32333,7 +32333,7 @@
         "owner": null
       },
       "consumers": [],
-      "notes": "Shipped Codex repo-scoped harness config: approval never, default_permissions loam, hooks off, multi_agent on with 6 concurrent threads, loam profile (extends :workspace) with network enabled and .env denied under workspace roots, glob_scan_max_depth cap (noted for codex 0.153.4). Codex-only; local-only already-distributed seed policy (the Codex side of the same runtime policy as seed/.claude/settings.json). Paired with loam.rules by Codex convention (not named in-body); no curated-skill consumers found by grep. Prior reading proposed 'retained', corrected to local-only. Digest matches the input."
+      "notes": "Shipped Codex repo-scoped harness config: approval never, default_permissions loam, hooks on (the memory hooks are registered in the sibling .codex/hooks.json), multi_agent on with 6 concurrent threads, loam profile (extends :workspace) with network enabled and .env denied under workspace roots, glob_scan_max_depth cap (noted for codex 0.153.4). Codex-only; local-only already-distributed seed policy (the Codex side of the same runtime policy as seed/.claude/settings.json). Paired with loam.rules by Codex convention (not named in-body); no curated-skill consumers found by grep. Prior reading proposed 'retained', corrected to local-only. Digest matches the input."
     },
     {
       "id": "support:seed/.codex/rules/loam.rules",
diff --git a/seed/.loam/runtime/release-manifest.json b/seed/.loam/runtime/release-manifest.json
index 77860276..2ff1bcca 100644
--- a/seed/.loam/runtime/release-manifest.json
+++ b/seed/.loam/runtime/release-manifest.json
@@ -8,7 +8,7 @@
     "assets/admission-fixtures/loam-dep-mutating-1.0.0.tgz": "622574d716f11c86305574c0c8604fa60b87ca0e9ce8a785c6db66d62a1c6362",
     "assets/admission-fixtures/loam-dep-plain-1.0.0.tgz": "28937d8437f6c08ea71fe281c47ab75a070a8d23befd4fccc0726f81dde324f0",
     "assets/admission-fixtures/loam-dep-scripted-1.0.0.tgz": "1e2c031e8a15a2cd7750ff73fb0ea298e99ec47b8b3657ba8cbd615afde83732",
-    "assets/curated-catalog.json": "e9ad044e3c2d28fad69905daf07cca4010704e7bd22ce13fdb2521328bfeb22d",
+    "assets/curated-catalog.json": "ff611c917dca5223a33d4ec1b03bfbd7e8ff84b8ca251ea6782c2db231d3d27e",
     "assets/curated-catalog.schema.json": "1f2ffac55fbd67ff9b79310b4cb33620c2060438ae078fb72a2cbd0518ed7a04",
     "assets/runtime-manifest.json": "2fb47dbf5e125b8010d052e6f2b9f8d460001fa92b7f1bf2d0c8597b1244077c",
     "dist/src/assets/catalog.js": "0ac6baf995d266f1c53af9b300cdcf5a9e4ffb0f82760adb7693a8ca86b04591",
@@ -108,7 +108,7 @@
     "tests/platform/qualification.test.ts": "56c88da007715cff74d0d618cef3f1a6e26e14510f79a66254a0591eb674c3ab",
     "tsconfig.json": "89445fad719e12b5b787db90dc85fc652b925c094f32f0a165d89ad96b1b914c"
   },
-  "sourceDigest": "7071d0c1870bff60cba96064afaab1ae45fe79fe2e5d1eedfd940160f7aec92c",
+  "sourceDigest": "ce78146463cfb230f1511b8cf691c51aa3952643e0d38d821fafa620b0f6a8ae",
   "outputDigest": "e04335a82896c899d1a873a5d754d84c8b1e4f54250e87aa4dcded7fda148273",
   "dependencyDigest": "4ef2138ee7efdc09605ce4a042fdfb64bdca4789fc611ba99e30f5e584884f8b"
 }
diff --git a/seed/bin/mem-weekly.sh b/seed/bin/mem-weekly.sh
index 4a2efb24..8cfd9ce0 100755
--- a/seed/bin/mem-weekly.sh
+++ b/seed/bin/mem-weekly.sh
@@ -26,4 +26,24 @@ git add -A 2>/dev/null \
 mkdir -p reports
 grep -rohE 'Error: .{0,60}|RuntimeError.{0,60}|Traceback.{0,60}' traces/ 2>/dev/null \
   | sort | uniq -c | sort -rn | head -20 > reports/recurring-errors.md
+
+# Capture, retrieval, and application counts, so the weekly report says whether
+# the memory layer is used, not only which errors recur. Plain grep over traces/.
+traces=$(ls traces/*/*.jsonl 2>/dev/null | wc -l | tr -d ' ')
+sessions="n/a"
+CLAUDE_PROJECTS="${CLAUDE_CONFIG_DIR:-$HOME/.claude}/projects"
+CODEX_SESSIONS="${CODEX_HOME:-$HOME/.codex}/sessions"
+if [ -d "$CLAUDE_PROJECTS" ] || [ -d "$CODEX_SESSIONS" ]; then
+  claude_n=0; codex_n=0
+  [ -d "$CLAUDE_PROJECTS" ] && claude_n=$(ls "$CLAUDE_PROJECTS"/*/*.jsonl 2>/dev/null | wc -l | tr -d ' ')
+  [ -d "$CODEX_SESSIONS" ] && codex_n=$(find "$CODEX_SESSIONS" -type f -name 'rollout-*.jsonl' 2>/dev/null | wc -l | tr -d ' ')
+  sessions=$((claude_n + codex_n))
+fi
+retrieval=$(grep -rc -e memsearch traces/ 2>/dev/null | awk -F: '{s+=$NF} END{print s+0}')
+application=$(grep -rcE 'APPLICABLE|STALE|UNVERIFIED' traces/ 2>/dev/null | awk -F: '{s+=$NF} END{print s+0}')
+{
+  printf 'capture %s traces, %s sessions seen\n' "$traces" "$sessions"
+  printf 'retrieval %s\n' "$retrieval"
+  printf 'application %s\n' "$application"
+} > reports/counts.md
 exit 0
diff --git a/seed/bin/memsearch b/seed/bin/memsearch
index 43121341..9115c394 100755
--- a/seed/bin/memsearch
+++ b/seed/bin/memsearch
@@ -12,8 +12,25 @@
 set -uo pipefail

 STORE="${LOAM_MEMSTORE:-$HOME/memstore}"
+
+# Key by the origin remote so a search reads the same store directory mem-capture
+# writes across the factory's per-worktree checkouts. Fall back to the toplevel
+# basename with no origin, then to the cwd basename with no git.
+repo_key() {
+  local dir="$1" url top
+  url="$(git -C "$dir" remote get-url origin 2>/dev/null)"
+  if [ -n "$url" ]; then
+    url="${url%/}"; url="${url%.git}"
+    basename "$url"
+    return
+  fi
+  top="$(git -C "$dir" rev-parse --show-toplevel 2>/dev/null)"
+  [ -n "$top" ] && { basename "$top"; return; }
+  basename "$dir"
+}
+
 ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
-REPO="$(basename "${ROOT:-$PWD}")"
+REPO="$(repo_key "$PWD")"

 PATTERN="${1:-}"; [ -n "$PATTERN" ] || exit 0; shift
 TARGETS=()
diff --git a/seed/docs/HARNESS.md b/seed/docs/HARNESS.md
index 625cff79..1a8ec18c 100644
--- a/seed/docs/HARNESS.md
+++ b/seed/docs/HARNESS.md
@@ -59,10 +59,17 @@ per-tool latency.
   Claude Code adds to the context; capped at 4000 bytes, silent when the store
   has no index for the repo.

+Codex runs the same two scripts through `.codex/hooks.json`, which registers
+`mem-capture.sh` on SessionEnd, PreCompact, and Stop (the Stop entry throttled)
+and `mem-recall.sh` on SessionStart. The entries point at the `.claude/hooks/`
+scripts; each reads `cwd` from the hook payload, so one copy serves both
+harnesses and a session lands under the same repository key whichever one ran it.
+
 `bin/memsearch` and `bin/mem-weekly.sh` are companion tools, not hooks.
 `memsearch PATTERN` greps the trace store and the repo's `docs/` with ripgrep
 (or `grep`) and cuts the output at 80 lines. `mem-weekly.sh` commits the store as
-a git baseline and rewrites `reports/recurring-errors.md`; add its cron line by
+a git baseline and rewrites `reports/recurring-errors.md` and `reports/counts.md`
+(capture, retrieval, and application counts); add its cron line by
 hand, it is not installed:

     0 9 * * 0 <project>/bin/mem-weekly.sh
@@ -105,6 +112,10 @@ removing it would cause a mistake.
   delete a trace file to forget it. The weekly baseline commit in the store covers
   reports and native-memory caches only; `traces/` is gitignored there, so a
   deleted transcript leaves no copy in git history.
+- Codex runs a repository hook only after the user trusts the project's `.codex`
+  layer and reviews the hook definition once (Codex keeps a hash of it in its
+  hooks state, and an edit to `hooks.json` asks again), so a Codex session before
+  that step captures nothing.
 - Test tampering and mutation coverage have no gate. Pull-request review owns
   test integrity.
 - Editing any file under `.claude/` needs bypassPermissions mode. An unattended
~~~~~~~~~~~~ evidence
