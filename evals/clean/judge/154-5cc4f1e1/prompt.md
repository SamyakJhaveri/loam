## Ticket

~~~~~~~~~~~~ evidence
Brief:
Give every rendered project a memory layer that costs zero model calls: copy each session transcript into a per-user store, inject the last five sessions at start, search the store with ripgrep, and report recurring errors weekly.
Where: seed/.claude/hooks/ (two new scripts), seed/bin/ (two new scripts), seed/.claude/settings.json (hooks), seed/docs/HARNESS.md (The hooks, Accepted risks, Always-on budget), docs/ASSET-LAYERS.md (the two-hook sentence), docs/BOOTSTRAP.md (the .claude/ bullet), seed/.loam/runtime/assets/curated-catalog.json (the one support entry that pins seed/.claude/settings.json).
Done means: the done-checks block prints no FAIL line: four scripts, four hook events wired, capture proven idempotent on a fake payload, recall under 4000 bytes, memsearch and the weekly report working, a fresh render carrying all of it, HARNESS.md updated.
Out of scope: Codex hooks (features.hooks is off in the shipped config); CARDS.md, GOTCHAS.md, HOSTS.md; any model call; any SQLite; any change to the factory or to NATIVE-09.
Blocked by: nothing on main fad17cb. Relaunched 2026-09-21 after runs 1 and 2 found that the catalog, the asset-intake inventory, and the release manifest all pin seed/.claude/settings.json; the branch factory/154 already carries the four scripts, the hook wiring, the docs, and the test update.

## Goal and why
A rendered project keeps nothing across sessions today, and the campaign's memory tickets (NATIVE-09, 10, 11) build a SQLite store and model assessment before anything measures whether a worker gains from memory at all (docs/research/curation-2026-09-20.md, "The memory design, verified and placed").
Levels 1 and 2 of docs/research/memory-design-2026-09-03.md cost about 120 lines of shell and zero model calls; the weekly recurring-errors report they produce is the measurement that decides NATIVE-09.
Every claim the design rests on was verified against its source on 2026-09-20; the one caveat is that a Stop-time transcript may lag the last turn, which is why SessionEnd and PreCompact also capture.

## Do not touch
The standing list. Also: seed/AGENTS.md.jinja, seed/CLAUDE.md.jinja, seed/.codex/, seed/.loam/, seed/.agents/, bin/factory, docs/architecture-working/.
Except: seed/.claude/settings.json, seed/.claude/hooks/mem-capture.sh, seed/.claude/hooks/mem-recall.sh, seed/bin/memsearch, seed/bin/mem-weekly.sh, seed/.loam/runtime/assets/curated-catalog.json (only the entry with id support:seed/.claude/settings.json), docs/architecture-working/asset-intake/loam-inventory.json (only the row whose source_path is seed/.claude/settings.json), seed/.loam/runtime/release-manifest.json and any tracked file under seed/.loam/runtime/ that the build regenerates, bin/tests/test_render_smoke.py (its two-hook assertions become the four-script set). This ticket creates the four scripts and edits settings.json; the rest is provenance bookkeeping for that one edit.

## Out of scope
Codex hooks; CARDS.md, GOTCHAS.md, HOSTS.md, `.claude/rules/`; embeddings, SQLite, any index beyond ripgrep; any model call; the cron install itself (documented, not performed); the factory worker settings.

## Approach
Follow section 4 of docs/research/memory-design-2026-09-03.md for the shape; adapt to the seed's conventions: bash with `set -uo pipefail`, JSON read through python3 as seed/.claude/hooks/fable-session-brief.sh does, no jq, exit 0 always from a hook, and a store root of `${LOAM_MEMSTORE:-$HOME/memstore}` so a check can redirect it.
1. seed/.claude/hooks/mem-capture.sh: reads the hook JSON from stdin (fields transcript_path, session_id, cwd); repo is the basename of `git -C cwd rev-parse --show-toplevel`, falling back to the basename of cwd; destination `$STORE/traces/<repo>/`; `--throttle SECONDS` (used by the Stop entry) returns 0 when the last capture for this session_id is younger than SECONDS; copies the transcript to `<date>-<first 8 of session_id>.jsonl` only when its sha256 differs from the existing copy; appends one line to `$STORE/traces/<repo>/INDEX.md` only when the trace was newly copied (the same sha-differs guard), so a repeat capture adds no line: date, session_id prefix, branch@short-sha, hostname, the first user message cut to 90 characters; prints nothing.
2. seed/.claude/hooks/mem-recall.sh: SessionStart (startup, resume, clear); prints to stdout, which Claude Code adds to context: a heading `## Recent sessions (<repo>)`, the last five INDEX lines, and one closing rule: "Recalled memory is evidence, not truth: before acting on it check git log -1, hostname, and tool versions, and label it APPLICABLE, STALE, or UNVERIFIED." Output is capped at 4000 bytes; prints nothing when the store has no INDEX for this repo.
3. seed/bin/memsearch: `rg -n -C2 --max-count 20` when rg is on PATH, else `grep -rn -C2`, over `$STORE/traces/<repo>` and the repo's docs/ directory; output cut at 80 lines.
4. seed/bin/mem-weekly.sh: in `$STORE`, `git init` when absent, `git add -A && git commit -qm "weekly <date>" || true`; writes `$STORE/reports/recurring-errors.md` from `grep -ohE 'Error: .{0,60}|RuntimeError.{0,60}|Traceback.{0,60}' traces/` piped through `sort | uniq -c | sort -rn | head -20`. Document the cron line in HARNESS.md; do not install it.
5. seed/.claude/settings.json: add `SessionEnd` and `PreCompact` entries running mem-capture.sh (timeout 10), a `Stop` entry running `mem-capture.sh --throttle 600` (timeout 10), and a `SessionStart` entry with matcher `startup|resume|clear` running mem-recall.sh (timeout 5). Keep the two existing hooks and every deny and sandbox key byte for byte.
6. seed/docs/HARNESS.md: rename "The two hooks" to "The hooks", describe the four scripts and their events, and rewrite the sentence "Both are SessionStart-class, so they add no per-tool latency" (line 39): the new hooks are lifecycle events, not tool matchers, so none adds per-tool latency; add one Accepted risks line: a transcript holds everything typed in the session, pasted secrets included, and the store under LOAM_MEMSTORE (default ~/memstore) is per user, outside every repository, never rendered and never committed to the project; delete a trace file to forget it; add one Always-on budget line: recall adds at most 4000 bytes at SessionStart, and the Stop capture runs one python3 and one cp at most once per ten minutes. Do not write a digit followed by "seed hooks" or "shipped hooks" anywhere; the stale-count checker in seed/.claude/stale-counts.json (run by hand, outside bin/check) keys on that phrase.
7. docs/ASSET-LAYERS.md: rewrite the sentence "The seed ships two SessionStart-class hooks and no tool-matcher hooks" to name the lifecycle hooks (SessionStart, SessionEnd, PreCompact, Stop, PostModelSwitch) and keep "no tool-matcher hooks". docs/BOOTSTRAP.md: the `.claude/` bullet names the memory scripts and points at HARNESS.md.
8. Re-pin the catalog. seed/.loam/runtime/assets/curated-catalog.json records seed/.claude/settings.json as the support entry support:seed/.claude/settings.json with source.sha256 over the whole file and sourceUnits with start, end, and sha256 per unit; bin/factory-catalog-provenance.mjs, inside bin/check, fails when they differ from the tree. After settings.json is final, recompute them with the same rule the runtime uses: import extractUnits and sha256 from seed/.loam/runtime/dist/src/assets/units.js in a node one-liner over the file, write the new source.sha256 and unit list into that one entry, change nothing else in the catalog, and prove it with node bin/factory-catalog-provenance.mjs and node seed/.loam/runtime/launcher.mjs qualify catalog, both printing passed (LOAM_FACTORY_TOOLCHAIN and LOAM_FACTORY_COPIER are exported in the runner's login shell). Then the two layers above the catalog: in docs/architecture-working/asset-intake/loam-inventory.json set sha256 and bytes on the row whose source_path is seed/.claude/settings.json to the new file's values; then regenerate the runtime release manifest, which records the catalog's digest, with `npm --prefix seed/.loam/runtime ci --ignore-scripts && npm --prefix seed/.loam/runtime run build`, and commit every tracked file that changed under seed/.loam/runtime/ together with the catalog and the inventory. Prove the whole stack with node seed/.loam/runtime/launcher.mjs qualify package, then bin/check. Record the new digests in decisions.md.
9. Mark each new script executable and commit as you go; render_into needs the commits.

## Done checks
```done-checks
bash -n seed/.claude/hooks/mem-capture.sh seed/.claude/hooks/mem-recall.sh seed/bin/memsearch seed/bin/mem-weekly.sh 2>/dev/null && [ -x seed/.claude/hooks/mem-capture.sh ] && [ -x seed/bin/memsearch ] && pass scripts-present || fail scripts-present "a script is missing, fails bash -n, or is not executable"
python3 -c 'import json,sys;h=json.load(open("seed/.claude/settings.json"))["hooks"];c=" ".join(x["command"] for e in h.values() for g in e for x in g["hooks"]);sys.exit(0 if all(e in h for e in ("SessionEnd","PreCompact","Stop")) and "mem-recall.sh" in c and "mem-capture.sh --throttle" in c and "fable-session-brief.sh" in c and "post-compact-reinject.sh" in c else 1)' && pass hooks-wired || fail hooks-wired "settings.json lacks an event, a script, or dropped an existing hook"
tmp=$(mktemp -d); printf '{"type":"user","message":{"content":"hello memstore probe"}}\n' > "$tmp/t.jsonl"; for i in 1 2; do printf '{"session_id":"abcdef1234","transcript_path":"%s/t.jsonl","cwd":"%s"}' "$tmp" "$PWD" | LOAM_MEMSTORE="$tmp/store" seed/.claude/hooks/mem-capture.sh >/dev/null 2>&1; done; n=$(ls "$tmp/store/traces"/*/*.jsonl 2>/dev/null | wc -l | tr -d ' '); [ "$n" = 1 ] && [ "$(cat "$tmp/store/traces"/*/INDEX.md 2>/dev/null | grep -c abcdef12)" = 1 ] && pass capture-idempotent || fail capture-idempotent "trace files: $n"
out=$(printf '{"session_id":"x","cwd":"%s"}' "$PWD" | LOAM_MEMSTORE="$tmp/store" seed/.claude/hooks/mem-recall.sh 2>/dev/null); printf '%s' "$out" | grep -q 'abcdef12' && printf '%s' "$out" | grep -q 'APPLICABLE' && [ "${#out}" -lt 4000 ] && pass recall || fail recall "recall printed ${#out} bytes without the session line or the rule"
LOAM_MEMSTORE="$tmp/store" seed/bin/memsearch 'memstore probe' 2>/dev/null | grep -q 'memstore probe' && pass memsearch || fail memsearch "memsearch did not find the probe"
LOAM_MEMSTORE="$tmp/store" seed/bin/mem-weekly.sh >/dev/null 2>&1; [ -f "$tmp/store/reports/recurring-errors.md" ] && [ -d "$tmp/store/.git" ] && pass weekly || fail weekly "no report or no store repo after mem-weekly.sh"
grep -q 'LOAM_MEMSTORE' seed/docs/HARNESS.md && grep -qi 'pasted secrets' seed/docs/HARNESS.md && pass harness-doc || fail harness-doc "HARNESS.md does not name the store or the transcript risk"
grep -q 'mem-capture' docs/BOOTSTRAP.md && ! grep -q 'two SessionStart-class hooks' docs/ASSET-LAYERS.md && grep -q 'no tool-matcher hooks' docs/ASSET-LAYERS.md && pass docs-updated || fail docs-updated "BOOTSTRAP.md or ASSET-LAYERS.md still describe two hooks"
render_into; [ -n "$render_dir" ] || fail render "$render_err"; [ -x "$render_dir/.claude/hooks/mem-capture.sh" ] && [ -x "$render_dir/bin/memsearch" ] && grep -q 'mem-capture.sh' "$render_dir/.claude/settings.json" && pass in-render || fail in-render "the render lacks a script or the hook entries"
[ -n "${LOAM_HOOK:-}" ] && pass check-green || { guard bin/check >/dev/null && pass check-green || fail check-green "bin/check"; }
```

## Merge checklist
- Run one real session in a fresh render, end it, and confirm ~/memstore/traces/<project>/INDEX.md gained a line.
- Note in the PR body that the Loam repo's own sessions now capture too, since .claude points at seed/.claude.

## Worker
worker: claude
codex-review: no
effort: xhigh
MAX_ROUNDS=3
ROUND_BUDGET_USD=25
goal: the done-checks block prints no FAIL line, or stop after 100 turns

## Decisions
docs/research/curation-2026-09-20.md (pick 1), docs/research/memory-design-2026-09-03.md (sections 4, 5, 6), docs/architecture-working/tickets/README.md (Curation verdicts)

~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS scripts-present
PASS hooks-wired
PASS capture-idempotent
PASS recall
PASS memsearch
PASS weekly
PASS harness-doc
PASS docs-updated
PASS in-render
PASS check-green

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
# Ticket #154 - worker decisions (round 3, run 5cc4f1e1)

Branch `factory/154` arrived carrying runs 1-2: the four scripts, the hook wiring,
the docs, the test update, and the catalog re-pin (commit `41efe454`).
The ticket now grants the two exceptions runs 1-2 asked for
(loam-inventory.json row and the runtime release manifest), so this round finished
Approach step 8's upper two provenance layers.

## Digests (settings.json is the pinned file)

- seed/.claude/settings.json: sha256 `97669841e857bfa093305c6cce547359f1ac73d1f2e89676ee6f6eb19bd123fa`, 2622 bytes.
- curated-catalog.json entry `support:seed/.claude/settings.json`: source.sha256 and u1.sha256 both `97669841...` (committed in run 2 as `41efe454`; unchanged this round, not re-committed).
- curated-catalog.json file digest: `e9ad044e3c2d28fad69905daf07cca4010704e7bd22ce13fdb2521328bfeb22d`.
- release-manifest.json now records `assets/curated-catalog.json => e9ad044e...` (was `f0d7af58...`) and the rolled-up `sourceDigest => 7071d0c1870bff60cba96064afaab1ae45fe79fe2e5d1eedfd940160f7aec92c` (was `3823e441...`). `outputDigest`/`dependencyDigest` unchanged (dist and deps untouched).

## What this round changed

1. docs/architecture-working/asset-intake/loam-inventory.json, the one row whose `source_path` is `seed/.claude/settings.json` (files[92]): `sha256` -> `97669841...`, `bytes` -> `2622`. Edited with the Edit tool (two adjacent lines), not a JSON round-trip, so the diff is exactly two lines. Left `static_flags.host_binding` line refs (47/57/63/68) and `bytes`-adjacent metadata otherwise untouched: the ticket's Approach step 8 says only "set sha256 and bytes", and the provenance check (`provenance.inventory-dispositions`) keys only on the sha, so a wider rewrite of that row would be out of the stated scope. Did NOT touch the archived copy under docs/archive/... (same old sha lives there; not excepted).
2. Regenerated seed/.loam/runtime/release-manifest.json with `npm --prefix seed/.loam/runtime ci --ignore-scripts && npm --prefix seed/.loam/runtime run build`. Only release-manifest.json changed under seed/.loam/runtime/ (the committed dist/ already matched a fresh build with this toolchain, so `rebuild.exact` stays green).
3. Committed both as `6fc3fd4b` "Provenance: re-pin settings.json in the intake inventory and regenerate the release manifest".

## Carry-forward note from run 2

The runtime export used to recompute the catalog units is `extractSourceUnits` (not `extractUnits` as the brief named it) from seed/.loam/runtime/dist/src/assets/units.js. Run 2 already applied this to the catalog; no catalog edit was needed this round.

## Proofs

### Frozen done-checks (the block the supervisor reruns)

`bash frozen/checks.sh` from the worktree root, `LOAM_HOOK` unset -> exit 0, no FAIL line:

```
PASS scripts-present
PASS hooks-wired
PASS capture-idempotent
PASS recall
PASS memsearch
PASS weekly
PASS harness-doc
PASS docs-updated
PASS in-render
PASS check-green
```

### Provenance proofs

All three commands below run inside `bin/check`: `qualify package` at `bin/check:95`,
`qualify catalog` at `bin/check:106`, and `factory-catalog-provenance.mjs` at `bin/check:107`.
So `PASS check-green` in the block above already covers all three.
The verbatim outputs below are the worker's own direct runs of the same commands, pasted for the record;
they are not separate lines in the done-checks block.
All three were re-run after the code-fix commit `1ce116dc` and the output was byte-identical.

`node seed/.loam/runtime/launcher.mjs qualify catalog` (exit 0):

```
{"kind":"catalog-qualification","status":"passed","expected":5,"passed":5,"cases":["catalog.schema-and-payload","catalog.conservation-rejections","catalog.activation-honesty","catalog.selected-dependencies-mapped","catalog.pocock-collection"],"environment":{"execPath":"/home/samyak/.local/state/loam/toolchains/node-v24.21.0-linux-x64/bin/node","version":"v24.21.0","platform":"linux","arch":"x64"}}
```

`node seed/.loam/runtime/launcher.mjs qualify package` (exit 0):

```
{"kind":"package-qualification","status":"passed","expected":14,"passed":14,"cases":["package.valid-payload","package.changed-source","package.missing-output","package.extra-output","package.changed-map","package.unsafe-path","package.symlink","package.manifest-boundaries","package.registry-obligations","package.unknown-group","package.unavailable-groups","package.case-accounting","package.compiler-free-recipient","package.import-closure"],"environment":{"execPath":"/home/samyak/.local/state/loam/toolchains/node-v24.21.0-linux-x64/bin/node","version":"v24.21.0","platform":"linux","arch":"x64"}}
```

`node bin/factory-catalog-provenance.mjs` (exit 0):

```
{"kind":"catalog-provenance-qualification","status":"passed","expected":3,"passed":3,"cases":["provenance.sources-match-tree","provenance.baseline-map-agreement","provenance.inventory-dispositions"],"toolchain":{"execPath":"/home/samyak/.local/state/loam/toolchains/node-v24.21.0-linux-x64/bin/node","version":"v24.21.0","npm":"11.19.0","platform":"linux","arch":"x64"}}
```

## Supervisor gate checks (verified with the frozen factory's own logic)

- Do-not-touch gate: `do_not_touch_hits()` (frozen/factory:880) uses the merge-base diff `base.sha...HEAD`, not a two-dot diff. base.sha is `a4597919` (current main tip, ahead of the branch's fork point `fad17cbf`), so the three-dot diff lists only the 12 branch-changed files; ran the exact `under`/protected/exempt logic and it returns zero hits. frozen/exempt.txt contains both `loam-inventory.json` and `release-manifest.json` (and `seed/.loam/runtime/`), so the relaunch's exceptions are in the frozen copy.
- Commit hygiene: all branch commits authored by SamyakJhaveri; no `Co-Authored-By` trailer and no agent name on any of them, including this round's `6fc3fd4b` and `1ce116dc`.

## Round-1 review fixes applied (commit `1ce116dc`)

Applied the four low-severity reviewer findings to the two scripts I own. settings.json is untouched, so no re-pin was needed. Frozen done-checks stay 10/10 PASS after these edits.

1. Throttle mark: added `case "$PREV" in ''|*[!0-9]*) PREV=0;; esac`, so an empty or non-numeric mark file no longer makes `$((NOW - PREV))` an arithmetic error that suppresses every later Stop capture. Took only this guard. Declined the reviewer's second half (move `echo "$NOW" > "$MARK"` to after a successful `cp`): an unchanged transcript exits before `cp` (its sha matches), so a post-cp mark write would never refresh, and the next Stop would re-run python3 and sha256 - which breaks the HARNESS.md budget sentence ("one python3 and one cp at most once per ten minutes") that Approach step 6 dictates verbatim. Deliberate decline.
2. One trace file per session across days: choose OUT by globbing an existing `*-<sid8>.jsonl` in the repo dir first, else name a fresh file with today's date. A session resumed on a later day now reuses its file - no duplicate copy, no second INDEX line. Verified: a cross-day recapture leaves 1 trace file and 1 INDEX line. Deliberate departure from Approach step 1's literal `<date>-<sid8>.jsonl`: a reused file keeps its first-capture date, not the resume day's, which is what makes one session map to one file.
3. Empty cwd: added `[ -n "$CWD" ] || CWD="$PWD"` (matching mem-recall.sh), so a payload with no cwd lands under `traces/<repo>/`, not the traces root. Verified: an empty-cwd capture landed under `traces/loam-154/` with 0 files at the traces root.
4. mem-weekly.sh: commit with explicit identity `git -c user.name=memstore -c user.email=memstore@localhost`, so the weekly baseline commit succeeds even with no global git config.

Left the reviewer's fifth note (HARNESS.md "one python3 and one cp" wording) as-is: Approach step 6 dictates that exact sentence.

## Merge checklist (for the PR body)

The worker writes no PR text; the supervisor lifts these two notes from here.

- The Loam repo's own sessions now capture too. VERIFIED: `ls -la .claude` in the worktree shows `.claude -> seed/.claude` (a symlink), so a real Claude Code session in the Loam repo runs the shipped `seed/.claude/settings.json` hooks and captures into `$LOAM_MEMSTORE/traces/<repo>/`. Caveat: the factory worker's own session runs under `frozen/worker-settings.json` (a single Stop hook that runs the checks with `LOAM_HOOK=1`), not the memory hooks, so this worker session did not itself capture.
- Real-session INDEX.md check: UNVERIFIED. No interactive Claude Code session was run in a fresh render this round, and `~/memstore` does not exist in this environment (`LOAM_MEMSTORE` unset), so no `traces/<project>/INDEX.md` line could be observed from a live session. The capture mechanism is proven on a fake payload by the `capture-idempotent` done-check, and the render carries the scripts and hook wiring (the `in-render` done-check). To verify at merge time: run one real session in a fresh render, end it, and confirm `~/memstore/traces/<project>/INDEX.md` gained a line.

~~~~~~~~~~~~ evidence

## Diff (a4597919...HEAD)

~~~~~~~~~~~~ evidence
 bin/tests/test_render_smoke.py                             |  30 ++++++++++++++++++++++-------
 docs/ASSET-LAYERS.md                                       |   4 ++--
 docs/BOOTSTRAP.md                                          |   2 +-
 docs/architecture-working/asset-intake/loam-inventory.json |   4 ++--
 seed/.claude/hooks/mem-capture.sh                          | 141 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 seed/.claude/hooks/mem-recall.sh                           |  36 ++++++++++++++++++++++++++++++++++
 seed/.claude/settings.json                                 |  43 +++++++++++++++++++++++++++++++++++++++++
 seed/.loam/runtime/assets/curated-catalog.json             |   6 +++---
 seed/.loam/runtime/release-manifest.json                   |   4 ++--
 seed/bin/mem-weekly.sh                                     |  25 ++++++++++++++++++++++++
 seed/bin/memsearch                                         |  26 +++++++++++++++++++++++++
 seed/docs/HARNESS.md                                       |  30 +++++++++++++++++++++++++++--
 12 files changed, 332 insertions(+), 19 deletions(-)

diff --git a/bin/tests/test_render_smoke.py b/bin/tests/test_render_smoke.py
index 2832f2e0..dbf4f935 100644
--- a/bin/tests/test_render_smoke.py
+++ b/bin/tests/test_render_smoke.py
@@ -95,7 +95,7 @@ class RenderSmoke(unittest.TestCase):
     def settings(self) -> dict:
         return json.loads((self.out / ".claude/settings.json").read_text())

-    def test_settings_parse_and_two_hooks(self):
+    def test_settings_parse_and_hooks(self):
         s = self.settings()
         cmds = [
             h["command"]
@@ -103,8 +103,17 @@ class RenderSmoke(unittest.TestCase):
             for entry in block
             for h in entry["hooks"]
         ]
-        names = sorted({c.rsplit("/", 1)[-1] for c in cmds})
-        self.assertEqual(names, ["fable-session-brief.sh", "post-compact-reinject.sh"])
+        # split()[0] drops the Stop entry's `--throttle 600` argument.
+        names = sorted({c.rsplit("/", 1)[-1].split()[0] for c in cmds})
+        self.assertEqual(
+            names,
+            [
+                "fable-session-brief.sh",
+                "mem-capture.sh",
+                "mem-recall.sh",
+                "post-compact-reinject.sh",
+            ],
+        )
         self.assertNotIn("allow", s["permissions"])
         self.assertNotIn("ask", s["permissions"])
         self.assertNotIn("defaultMode", s["permissions"])
@@ -112,10 +121,16 @@ class RenderSmoke(unittest.TestCase):
         self.assertIs(s["sandbox"]["enabled"], True)
         self.assertIn(".env", s["sandbox"]["filesystem"]["denyRead"])

-    def test_only_the_two_hooks_ship(self):
+    def test_only_the_expected_hooks_ship(self):
         shipped = sorted(p.name for p in (self.out / ".claude/hooks").glob("*"))
         self.assertEqual(
-            shipped, ["fable-session-brief.sh", "post-compact-reinject.sh"]
+            shipped,
+            [
+                "fable-session-brief.sh",
+                "mem-capture.sh",
+                "mem-recall.sh",
+                "post-compact-reinject.sh",
+            ],
         )

     def test_codex_config_parses(self):
@@ -218,8 +233,9 @@ class UpdateSmoke(unittest.TestCase):
                 for entry in block:
                     for h in entry["hooks"]:
                         # removeprefix, not lstrip: lstrip("./") would eat
-                        # the leading dot of ".claude/..." as well.
-                        rel = h["command"].removeprefix("./")
+                        # the leading dot of ".claude/..." as well. split()[0]
+                        # drops any argument (the Stop entry's `--throttle 600`).
+                        rel = h["command"].removeprefix("./").split()[0]
                         script = proj / rel
                         self.assertTrue(
                             script.exists(), f"orphan hook wiring: {h['command']}"
diff --git a/docs/ASSET-LAYERS.md b/docs/ASSET-LAYERS.md
index a95febaa..d2ac36a5 100644
--- a/docs/ASSET-LAYERS.md
+++ b/docs/ASSET-LAYERS.md
@@ -6,7 +6,7 @@ A duplicate across layers is a bug unless it is an explicit distribution mirror

 | Layer | Lives in | Reaches a project | Context cost |
 |-------|----------|-------------------|--------------|
-| Always-on seed harness | `seed/` (shared guidance and skills, Claude settings and the two hooks, Codex config and rules) | Rendered by Copier at bootstrap; updated by `copier update` on new tags | Paid in every session; priced highest |
+| Always-on seed harness | `seed/` (shared guidance and skills, Claude settings and the lifecycle hooks, Codex config and rules) | Rendered by Copier at bootstrap; updated by `copier update` on new tags | Paid in every session; priced highest |
 | Plugin layer | `cultivation/marketplace/sam-cc-setup/` (agents + optional skills + the plan-review workflow) | Installed as a plugin; updates in place | Skill descriptions only, until invoked |
 | Marketplace bundles | `cultivation/marketplace/<name>/` | Install-on-demand | Zero until enabled |

@@ -22,5 +22,5 @@ Rules of thumb:
 - Anything that must hold every time is a hook in the seed, not prose anywhere.
 - The shared skill location for both harnesses is `seed/.agents/skills/` (Codex reads it directly; Claude Code reads it through a checked-in symlink in `.claude/skills/`).
 - A seed skill may be pure reference material when the owner requires it in every generated project; keep its description near 40 tokens, because the listing is paid in every session.
-- The seed ships two SessionStart-class hooks and no tool-matcher hooks. Command policy is native: `.claude/settings.json` deny rules and `.codex/rules/loam.rules`. See `seed/docs/HARNESS.md`.
+- The seed ships lifecycle hooks (SessionStart, SessionEnd, PreCompact, Stop, PostModelSwitch) and no tool-matcher hooks. Command policy is native: `.claude/settings.json` deny rules and `.codex/rules/loam.rules`. See `seed/docs/HARNESS.md`.
 - `cultivation/parked/` holds assets removed from the shipped plugin. Nothing installs from it.
diff --git a/docs/BOOTSTRAP.md b/docs/BOOTSTRAP.md
index be89b09b..e1836272 100644
--- a/docs/BOOTSTRAP.md
+++ b/docs/BOOTSTRAP.md
@@ -16,7 +16,7 @@ Copier asks three questions: `project_name`, `github_repo` (blank skips GitHub s
 ## What you get

 - `CLAUDE.md` importing `AGENTS.md` (the one prose home), both with fill-in placeholders.
-- `.claude/`: Claude Code settings (deny list, sandbox) and two hook scripts, registered on SessionStart and PostModelSwitch: the Fable session brief and the post-compaction reminder. See `docs/HARNESS.md`.
+- `.claude/`: Claude Code settings (deny list, sandbox) and the lifecycle hook scripts: the Fable session brief and post-compaction reminder, plus the zero-model memory layer (`mem-capture.sh` on SessionEnd/PreCompact/Stop copies each transcript to the per-user store; `mem-recall.sh` on SessionStart injects the last few sessions). Companion tools `bin/memsearch` and `bin/mem-weekly.sh` search the store and report recurring errors. See `docs/HARNESS.md`.
 - `.agents/skills/`: three skills shared by Claude Code (via symlink) and Codex: `catchup` (session bootstrap), `fable-prompting` (index over the Fable 5.1 guide), `hypothesis-tree` (persistent investigation tree).
 - `.codex/`: Codex configuration and execution rules (`rules/loam.rules`, the same deny families). No hooks ship; `features.hooks` is off. Inert until you trust the project in Codex.
 - `.loam/runtime/`: the qualification runtime; see `docs/runtime/SETUP.md`.
diff --git a/docs/architecture-working/asset-intake/loam-inventory.json b/docs/architecture-working/asset-intake/loam-inventory.json
index 2a4db54a..40c6cebd 100644
--- a/docs/architecture-working/asset-intake/loam-inventory.json
+++ b/docs/architecture-working/asset-intake/loam-inventory.json
@@ -3104,8 +3104,8 @@
       "resolved_path": "/Users/samyakjhaveri/Desktop/loam/seed/.claude/settings.json",
       "kind": "support_or_config",
       "name": "settings",
-      "sha256": "7ba9133a80275f1c72fdede99307d6b39ec5380408ca0851356711ebaca163ee",
-      "bytes": 1766,
+      "sha256": "97669841e857bfa093305c6cce547359f1ac73d1f2e89676ee6f6eb19bd123fa",
+      "bytes": 2622,
       "layer": "active_seed",
       "baseline_decision": "include_curated_source_pending_adaptation",
       "runtime_enabled_by_audit": false,
diff --git a/seed/.claude/hooks/mem-capture.sh b/seed/.claude/hooks/mem-capture.sh
new file mode 100755
index 00000000..38f8d995
--- /dev/null
+++ b/seed/.claude/hooks/mem-capture.sh
@@ -0,0 +1,141 @@
+#!/usr/bin/env bash
+# mem-capture.sh - copy the session transcript into the per-user memory store.
+#
+# Hook events: SessionEnd, PreCompact, and Stop (Stop is throttled). Reads the
+# hook JSON on stdin (transcript_path, session_id, cwd), copies the transcript
+# verbatim into $STORE/traces/<repo>/ and appends one INDEX.md line. Zero model
+# calls. Idempotent: a re-copy of the same transcript (same sha256) adds no file
+# and no INDEX line. Prints nothing.
+#
+# Usage: mem-capture.sh [--throttle SECONDS]
+#   --throttle SECONDS  exit 0 without copying when this session_id was captured
+#                       less than SECONDS ago (used by the Stop entry). The gate
+#                       runs before python3 and cp, so a throttled Stop spawns
+#                       neither.
+#
+# Store root: $LOAM_MEMSTORE, default ~/memstore.
+# Exit codes: 0 = always (advisory hook, never blocks).
+
+set -uo pipefail
+
+STORE="${LOAM_MEMSTORE:-$HOME/memstore}"
+
+THROTTLE=0
+if [ "${1:-}" = "--throttle" ]; then
+  THROTTLE="${2:-600}"
+fi
+
+PAYLOAD="$(cat)"
+
+# Throttle gate first, so a burst of Stop events copies at most once per THROTTLE
+# seconds for a session. The session_id is read with pure bash (no subprocess),
+# so a throttled Stop runs no python3 and no cp.
+if [ "$THROTTLE" -gt 0 ] 2>/dev/null; then
+  sid_tail="${PAYLOAD#*\"session_id\"}"
+  if [ "$sid_tail" != "$PAYLOAD" ]; then
+    sid_tail="${sid_tail#*:}"; sid_tail="${sid_tail#*\"}"
+    SID_CHEAP="${sid_tail%%\"*}"
+    if [ -n "$SID_CHEAP" ]; then
+      MARK="$STORE/.throttle/$SID_CHEAP"
+      NOW="$(date +%s)"
+      if [ -f "$MARK" ]; then
+        PREV="$(cat "$MARK" 2>/dev/null || echo 0)"
+        case "$PREV" in ''|*[!0-9]*) PREV=0;; esac
+        [ $((NOW - PREV)) -lt "$THROTTLE" ] && exit 0
+      fi
+      mkdir -p "$STORE/.throttle" 2>/dev/null || true
+      echo "$NOW" > "$MARK" 2>/dev/null || true
+    fi
+  fi
+fi
+
+# One python3 read: emit transcript_path, session_id, cwd, and the first user
+# message (whitespace collapsed, cut to 90 chars) as four tab-separated fields.
+FIELDS="$(printf '%s' "$PAYLOAD" | python3 -c '
+import json, sys
+try:
+    payload = json.load(sys.stdin)
+except Exception:
+    sys.exit(0)
+if not isinstance(payload, dict):
+    sys.exit(0)
+tp = payload.get("transcript_path") or ""
+sid = payload.get("session_id") or ""
+cwd = payload.get("cwd") or ""
+
+first = ""
+if tp:
+    try:
+        with open(tp, encoding="utf-8", errors="replace") as fh:
+            for line in fh:
+                line = line.strip()
+                if not line:
+                    continue
+                try:
+                    rec = json.loads(line)
+                except Exception:
+                    continue
+                if not isinstance(rec, dict) or rec.get("type") != "user":
+                    continue
+                msg = rec.get("message", rec)
+                content = msg.get("content") if isinstance(msg, dict) else msg
+                if isinstance(content, list):
+                    parts = []
+                    for block in content:
+                        if isinstance(block, dict):
+                            parts.append(str(block.get("text", "")))
+                        else:
+                            parts.append(str(block))
+                    content = " ".join(parts)
+                first = str(content)
+                break
+    except Exception:
+        first = ""
+first = " ".join(first.split())[:90]
+sys.stdout.write("\t".join((tp, sid, cwd, first)))
+' 2>/dev/null)"
+
+# Split the four tab-separated fields.
+TP="${FIELDS%%$'\t'*}"; REST="${FIELDS#*$'\t'}"
+SID="${REST%%$'\t'*}"; REST="${REST#*$'\t'}"
+CWD="${REST%%$'\t'*}"; FIRST="${REST#*$'\t'}"
+[ -n "$CWD" ] || CWD="$PWD"
+
+[ -n "$TP" ] || exit 0
+[ -f "$TP" ] || exit 0
+[ -n "$SID" ] || exit 0
+
+REPO="$(basename "$(git -C "$CWD" rev-parse --show-toplevel 2>/dev/null || echo "$CWD")")"
+DST="$STORE/traces/$REPO"
+mkdir -p "$DST" 2>/dev/null || exit 0
+
+sha() {
+  if command -v sha256sum >/dev/null 2>&1; then
+    sha256sum "$1" | cut -d' ' -f1
+  else
+    shasum -a 256 "$1" | cut -d' ' -f1
+  fi
+}
+
+SID8="$(printf '%s' "$SID" | cut -c1-8)"
+# One session maps to one trace file no matter which calendar day it resumes on:
+# reuse an existing *-<sid8>.jsonl if this session was captured before, else name
+# a fresh file with today's date.
+OUT=""
+for existing in "$DST"/*-"$SID8".jsonl; do
+  [ -f "$existing" ] && { OUT="$existing"; break; }
+done
+[ -n "$OUT" ] || OUT="$DST/$(date +%F)-$SID8.jsonl"
+
+# Copy and index only when the transcript differs from the existing copy.
+if [ -f "$OUT" ] && [ "$(sha "$OUT")" = "$(sha "$TP")" ]; then
+  exit 0
+fi
+cp "$TP" "$OUT" 2>/dev/null || exit 0
+
+BRANCH="$(git -C "$CWD" rev-parse --abbrev-ref HEAD 2>/dev/null)"
+SHORT="$(git -C "$CWD" rev-parse --short HEAD 2>/dev/null)"
+HOST="$(hostname -s 2>/dev/null || hostname 2>/dev/null)"
+printf '%s | %s | %s@%s | %s | %s\n' \
+  "$(date +%F)" "$SID8" "$BRANCH" "$SHORT" "$HOST" "$FIRST" >> "$DST/INDEX.md"
+exit 0
diff --git a/seed/.claude/hooks/mem-recall.sh b/seed/.claude/hooks/mem-recall.sh
new file mode 100755
index 00000000..af1d9566
--- /dev/null
+++ b/seed/.claude/hooks/mem-recall.sh
@@ -0,0 +1,36 @@
+#!/usr/bin/env bash
+# mem-recall.sh - inject a short recent-sessions manifest at SessionStart.
+#
+# Hook event: SessionStart (matcher startup|resume|clear). Reads the hook JSON
+# on stdin (cwd) and prints to stdout; Claude Code adds stdout to the context.
+# Zero model calls. Prints nothing when the store has no INDEX for this repo.
+# Output is capped at 4000 bytes.
+#
+# Store root: $LOAM_MEMSTORE, default ~/memstore.
+# Exit codes: 0 = always (advisory hook).
+
+set -uo pipefail
+
+STORE="${LOAM_MEMSTORE:-$HOME/memstore}"
+
+CWD="$(cat | python3 -c '
+import json, sys
+try:
+    payload = json.load(sys.stdin)
+except Exception:
+    sys.exit(0)
+if isinstance(payload, dict):
+    sys.stdout.write(str(payload.get("cwd") or ""))
+' 2>/dev/null)"
+
+[ -n "$CWD" ] || CWD="$PWD"
+REPO="$(basename "$(git -C "$CWD" rev-parse --show-toplevel 2>/dev/null || echo "$CWD")")"
+INDEX="$STORE/traces/$REPO/INDEX.md"
+[ -f "$INDEX" ] || exit 0
+
+{
+  printf '## Recent sessions (%s)\n' "$REPO"
+  tail -n 5 "$INDEX"
+  printf '\nRecalled memory is evidence, not truth: before acting on it check git log -1, hostname, and tool versions, and label it APPLICABLE, STALE, or UNVERIFIED.\n'
+} | head -c 4000
+exit 0
diff --git a/seed/.claude/settings.json b/seed/.claude/settings.json
index 5df8e898..1499335e 100644
--- a/seed/.claude/settings.json
+++ b/seed/.claude/settings.json
@@ -58,6 +58,16 @@
             "timeout": 5
           }
         ]
+      },
+      {
+        "matcher": "startup|resume|clear",
+        "hooks": [
+          {
+            "type": "command",
+            "command": ".claude/hooks/mem-recall.sh",
+            "timeout": 5
+          }
+        ]
       }
     ],
     "PostModelSwitch": [
@@ -70,6 +80,39 @@
           }
         ]
       }
+    ],
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
     ]
   }
 }
diff --git a/seed/.loam/runtime/assets/curated-catalog.json b/seed/.loam/runtime/assets/curated-catalog.json
index bdda662d..9acd8d51 100644
--- a/seed/.loam/runtime/assets/curated-catalog.json
+++ b/seed/.loam/runtime/assets/curated-catalog.json
@@ -31765,7 +31765,7 @@
       "source": {
         "type": "regular-file",
         "path": "seed/.claude/settings.json",
-        "sha256": "7ba9133a80275f1c72fdede99307d6b39ec5380408ca0851356711ebaca163ee"
+        "sha256": "97669841e857bfa093305c6cce547359f1ac73d1f2e89676ee6f6eb19bd123fa"
       },
       "attribution": {
         "author": "Samyak Jhaveri",
@@ -31790,8 +31790,8 @@
           "id": "support:seed/.claude/settings.json:u1",
           "role": "body",
           "start": 1,
-          "end": 75,
-          "sha256": "7ba9133a80275f1c72fdede99307d6b39ec5380408ca0851356711ebaca163ee"
+          "end": 118,
+          "sha256": "97669841e857bfa093305c6cce547359f1ac73d1f2e89676ee6f6eb19bd123fa"
         }
       ],
       "preservation": {
diff --git a/seed/.loam/runtime/release-manifest.json b/seed/.loam/runtime/release-manifest.json
index 786d09c3..77860276 100644
--- a/seed/.loam/runtime/release-manifest.json
+++ b/seed/.loam/runtime/release-manifest.json
@@ -8,7 +8,7 @@
     "assets/admission-fixtures/loam-dep-mutating-1.0.0.tgz": "622574d716f11c86305574c0c8604fa60b87ca0e9ce8a785c6db66d62a1c6362",
     "assets/admission-fixtures/loam-dep-plain-1.0.0.tgz": "28937d8437f6c08ea71fe281c47ab75a070a8d23befd4fccc0726f81dde324f0",
     "assets/admission-fixtures/loam-dep-scripted-1.0.0.tgz": "1e2c031e8a15a2cd7750ff73fb0ea298e99ec47b8b3657ba8cbd615afde83732",
-    "assets/curated-catalog.json": "f0d7af58ec3e54bd6527881d89bc8fef0558f790a8822fd254740c8d3f411301",
+    "assets/curated-catalog.json": "e9ad044e3c2d28fad69905daf07cca4010704e7bd22ce13fdb2521328bfeb22d",
     "assets/curated-catalog.schema.json": "1f2ffac55fbd67ff9b79310b4cb33620c2060438ae078fb72a2cbd0518ed7a04",
     "assets/runtime-manifest.json": "2fb47dbf5e125b8010d052e6f2b9f8d460001fa92b7f1bf2d0c8597b1244077c",
     "dist/src/assets/catalog.js": "0ac6baf995d266f1c53af9b300cdcf5a9e4ffb0f82760adb7693a8ca86b04591",
@@ -108,7 +108,7 @@
     "tests/platform/qualification.test.ts": "56c88da007715cff74d0d618cef3f1a6e26e14510f79a66254a0591eb674c3ab",
     "tsconfig.json": "89445fad719e12b5b787db90dc85fc652b925c094f32f0a165d89ad96b1b914c"
   },
-  "sourceDigest": "3823e44142104d47121f9b436187d53aafd8e8a010f2e59bebee371a99a81369",
+  "sourceDigest": "7071d0c1870bff60cba96064afaab1ae45fe79fe2e5d1eedfd940160f7aec92c",
   "outputDigest": "e04335a82896c899d1a873a5d754d84c8b1e4f54250e87aa4dcded7fda148273",
   "dependencyDigest": "4ef2138ee7efdc09605ce4a042fdfb64bdca4789fc611ba99e30f5e584884f8b"
 }
diff --git a/seed/bin/mem-weekly.sh b/seed/bin/mem-weekly.sh
new file mode 100755
index 00000000..345bf8a4
--- /dev/null
+++ b/seed/bin/mem-weekly.sh
@@ -0,0 +1,25 @@
+#!/usr/bin/env bash
+# mem-weekly.sh - weekly maintenance for the memory store (run from cron).
+#
+# Commits the store as a git baseline, then regenerates a recurring-errors
+# report from the captured traces. Zero model calls. The cron line is documented
+# in seed/docs/HARNESS.md; this ticket does not install it.
+#
+# Store root: $LOAM_MEMSTORE, default ~/memstore.
+# Usage: mem-weekly.sh
+
+set -uo pipefail
+
+STORE="${LOAM_MEMSTORE:-$HOME/memstore}"
+mkdir -p "$STORE" || exit 0
+cd "$STORE" || exit 0
+
+[ -d .git ] || git init -q 2>/dev/null
+git add -A 2>/dev/null \
+  && git -c user.name=memstore -c user.email=memstore@localhost \
+       commit -qm "weekly $(date +%F)" 2>/dev/null || true
+
+mkdir -p reports
+grep -rohE 'Error: .{0,60}|RuntimeError.{0,60}|Traceback.{0,60}' traces/ 2>/dev/null \
+  | sort | uniq -c | sort -rn | head -20 > reports/recurring-errors.md
+exit 0
diff --git a/seed/bin/memsearch b/seed/bin/memsearch
new file mode 100755
index 00000000..0281a396
--- /dev/null
+++ b/seed/bin/memsearch
@@ -0,0 +1,26 @@
+#!/usr/bin/env bash
+# memsearch - grep the memory store and the repo's docs for a pattern.
+#
+# Searches $STORE/traces/<repo> and <repo>/docs with ripgrep when it is on PATH,
+# else with grep. Zero model calls. Output cut at 80 lines.
+#
+# Store root: $LOAM_MEMSTORE, default ~/memstore.
+# Usage: memsearch PATTERN [extra rg/grep args]
+
+set -uo pipefail
+
+STORE="${LOAM_MEMSTORE:-$HOME/memstore}"
+ROOT="$(git rev-parse --show-toplevel 2>/dev/null)"
+REPO="$(basename "${ROOT:-$PWD}")"
+
+TARGETS=()
+[ -d "$STORE/traces/$REPO" ] && TARGETS+=("$STORE/traces/$REPO")
+[ -n "$ROOT" ] && [ -d "$ROOT/docs" ] && TARGETS+=("$ROOT/docs")
+[ "${#TARGETS[@]}" -gt 0 ] || exit 0
+
+if command -v rg >/dev/null 2>&1; then
+  rg -n -C2 --max-count 20 "$@" "${TARGETS[@]}" 2>/dev/null | head -80
+else
+  grep -rn -C2 "$@" "${TARGETS[@]}" 2>/dev/null | head -80
+fi
+exit 0
diff --git a/seed/docs/HARNESS.md b/seed/docs/HARNESS.md
index defe0f44..05480edc 100644
--- a/seed/docs/HARNESS.md
+++ b/seed/docs/HARNESS.md
@@ -34,9 +34,11 @@ actors. Three cases, and the setup output says which one you got:
 There is no `ask` rule on `git push`, on purpose: an unattended run must not stop
 on a prompt.

-## The two hooks
+## The hooks

-Both are SessionStart-class, so they add no per-tool latency.
+None runs on a tool matcher; every hook fires on a lifecycle event
+(SessionStart, SessionEnd, PreCompact, Stop, PostModelSwitch), so none adds
+per-tool latency.

 - `fable-session-brief.sh` (SessionStart, PostModelSwitch): prints the Fable
   judgment rules Claude Code does not inject, when the event names a Fable
@@ -46,6 +48,24 @@ Both are SessionStart-class, so they add no per-tool latency.
   fire there.
 - `post-compact-reinject.sh` (SessionStart `compact`): re-injects the task after
   a compaction.
+- `mem-capture.sh` (SessionEnd, PreCompact, Stop): copies the session transcript
+  into `$LOAM_MEMSTORE/traces/<repo>/` and appends one `INDEX.md` line, reading
+  the hook JSON with a single `python3` and no model call. It is idempotent on
+  the transcript's sha256, so a repeat capture adds no file and no line. The
+  `Stop` entry passes `--throttle 600`, so a burst of stops copies at most once
+  per ten minutes.
+- `mem-recall.sh` (SessionStart `startup|resume|clear`): prints the last five
+  `INDEX.md` lines for this repo and the applicability rule to stdout, which
+  Claude Code adds to the context; capped at 4000 bytes, silent when the store
+  has no index for the repo.
+
+`bin/memsearch` and `bin/mem-weekly.sh` are companion tools, not hooks.
+`memsearch PATTERN` greps the trace store and the repo's `docs/` with ripgrep
+(or `grep`) and cuts the output at 80 lines. `mem-weekly.sh` commits the store as
+a git baseline and rewrites `reports/recurring-errors.md`; add its cron line by
+hand, it is not installed:
+
+    0 9 * * 0 <project>/bin/mem-weekly.sh

 ## The one check

@@ -69,6 +89,8 @@ removing it would cause a mistake.
   listing shrinks; never raise it without saying why. Raised from 448 on
   2026-09-09 when `plan-review` became model-invocable, so its description
   now sits in the listing.
+- Memory hooks: recall adds at most 4000 bytes at SessionStart, and the Stop
+  capture runs one `python3` and one `cp` at most once per ten minutes.

 ## Accepted risks, stated rather than hidden

@@ -77,6 +99,10 @@ removing it would cause a mistake.
 - The `.env` deny rules do not stop a Python or Node subprocess opening the file.
   The sandbox filesystem deny is the real containment, where the host supports it.
 - Secrets typed into an ordinary source file are not caught locally.
+- A captured transcript holds everything typed in the session, pasted secrets
+  included. The store under `LOAM_MEMSTORE` (default `~/memstore`) is per user,
+  outside every repository, never rendered and never committed to the project;
+  delete a trace file to forget it.
 - Test tampering and mutation coverage have no gate. Pull-request review owns
   test integrity.
 - Editing any file under `.claude/` needs bypassPermissions mode. An unattended
~~~~~~~~~~~~ evidence
