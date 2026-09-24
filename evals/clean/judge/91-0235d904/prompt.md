## Ticket

~~~~~~~~~~~~ evidence
Brief:
Make `grader_file` resolve a grader prompt from the newest installed plugin version, the way `skill_file` already does, so a plugin bump that leaves the old version in the cache does not keep the loop and the eval on the old prompt.
Where: bin/factory (grader_file)
Done means: with two cached versions that both carry `reviewer.md`, `grader_file reviewer` prints the path under the higher version; the checkout fallback and the `GRADERS_DIR` override are unchanged.
Out of scope: pruning the cache; any grader prompt; `skill_file`.
Track: B    Risk: high    Mode: build    Open question: none
Blocked by: none

## Goal and why
`grader_file` globs `~/.claude/plugins/cache/*/sam-cc-setup/*/agents` and returns the first directory that holds `<grader>.md`. A bash glob expands in lexical order, so `0.9.0` comes before `0.9.1`, and `claude plugin update` leaves old versions in place (the Mac cache holds 0.8.0, 0.8.1, 0.8.2, and 0.9.0 side by side; the runner holds 0.1.0, 0.8.2, and 0.9.0). Today only 0.9.0 carries `judge.md` and `reviewer.md`, so the defect is latent. F23 bumps the plugin to 0.9.1 with an edited `reviewer.md`; after that update every run and every `bin/factory eval` would read the 0.9.0 prompt while the new `verdict_consistent` refutes its replies, three times per round, ending in the synthetic "reviewer output unparseable" high finding (found by the F23 plan review, 2026-09-11).
`skill_file` solves the same problem for plugin skills with `sort -rV | head -1`. `grader_file` takes the same rule.

## Do not touch
The standing list. Except: bin/factory (grader_file only).
Also: bin/factory.d/; the judge, reviewer, and Codex review prompts and schemas; seed/.

## Out of scope
- removing old versions from the plugin cache
- `skill_file`, which already picks the newest version
- the checkout fallback (`$ROOT/cultivation/marketplace/sam-cc-setup/agents`), which stays the last resort, and `GRADERS_DIR`, which stays the override

## Approach
Executor: `bin/factory run` as merged in F1, with F21 merged.

Facts pinned: `grader_file` in `bin/factory` builds `dirs` from `$GRADERS_DIR` or from the glob `"$HOME"/.claude/plugins/cache/*/sam-cc-setup/*/agents` followed by `"$ROOT/cultivation/marketplace/sam-cc-setup/agents"`, and returns the first `$d/$1.md` that exists; `skill_file` resolves a plugin skill with `find ... | sort -rV | head -1`; `precondition_lines` and `freeze` call `grader_file`, and `freeze` records the chosen path in the ledger's `grader` event; `run_eval` calls `grader_file` too.

Change: in `grader_file`, when `GRADERS_DIR` is empty, order the cache directories newest version first (`sort -rV` on the expanded glob, or `find -maxdepth 3 -name agents` piped through it) before the checkout fallback. The search loop, the override, and the error line stay as they are; the comment above the search says the cache is searched newest version first (the `skill_file` comment already claims that of `grader_file`).

## Done checks
```done-checks
h=$(mktemp -d "${TMPDIR:-/tmp}/f26.XXXXXX"); for v in 0.9.0 0.10.0 0.11.0; do mkdir -p "$h/.claude/plugins/cache/seed-skills/sam-cc-setup/$v/agents"; echo "# $v" > "$h/.claude/plugins/cache/seed-skills/sam-cc-setup/$v/agents/reviewer.md"; done; out=$(HOME="$h" FACTORY_SOURCED=1 bash -c '. "$0"; grader_file reviewer' bin/factory 2>/dev/null); rm -r "$h"; case "$out" in */0.11.0/agents/reviewer.md) pass newest-version ;; *) fail newest-version "grader_file returned '$out', not the 0.11.0 copy (lexical order puts 0.10.0 first, plain reverse order puts 0.9.0 first)" ;; esac
h=$(mktemp -d "${TMPDIR:-/tmp}/f26b.XXXXXX"); mkdir -p "$h/.claude/plugins/cache/seed-skills/sam-cc-setup/0.9.0/agents"; out=$(HOME="$h" FACTORY_SOURCED=1 bash -c '. "$0"; grader_file reviewer' bin/factory 2>/dev/null); rm -r "$h"; case "$out" in *cultivation/marketplace/sam-cc-setup/agents/reviewer.md) pass checkout-fallback ;; *) fail checkout-fallback "with no cached reviewer.md grader_file returned '$out', not the checkout copy" ;; esac   # guard: the fallback works on main and must keep working
guard bash -n bin/factory && pass syntax || fail syntax "bash -n bin/factory"
[ -n "${LOAM_HOOK:-}" ] && pass check-green || { guard bin/check >/dev/null && pass check-green || fail check-green "bin/check"; }
```

## Merge checklist
- after the F23 plugin update, the next run's ledger `grader` event names the 0.9.1 `reviewer.md` while 0.9.0 is still in the cache
- human diff read before merge (Risk high)

## Worker
worker: claude
codex-review: no
effort: xhigh
goal: the Done checks block, sourced after bin/factory.d/lib.sh and run from the worktree root with its output shown, prints no FAIL line and one PASS line per named check, or stop after 30 turns

## Decisions
the F23 plan review of 2026-09-11 (finding 1), docs/factory/LOOP.md (Preconditions: the plugin cache holds the grader files at the version the ledger records)

~~~~~~~~~~~~ evidence

## Checks output

~~~~~~~~~~~~ evidence
PASS newest-version
PASS checkout-fallback
PASS syntax
PASS check-green

~~~~~~~~~~~~ evidence

## Rows measured

~~~~~~~~~~~~ evidence

~~~~~~~~~~~~ evidence

## decisions.md (worker-authored)

~~~~~~~~~~~~ evidence
grader_file: when GRADERS_DIR is empty, sort the expanded cache glob with `printf | sort -rV | mapfile` so the newest plugin version wins, then append the checkout fallback last. Chose the ticket's first option (sort the expanded glob) over `find`, keeping the exact existing search glob `*/sam-cc-setup/*/agents`; mirrors skill_file's `sort -rV`.
Scope note (not a fix): sort runs on the full path, so like skill_file, with two different cache-name dirs the cache-name component sorts before the version. In practice sam-cc-setup has one cache-name dir, so version wins; the done-check uses one cache-name dir.
Comment above the search now says the cache is searched newest version first; the override (GRADERS_DIR) and the checkout fallback are unchanged.
Round 2 (blocking finding from round 1): `mapfile` is a bash 4 builtin and does not exist in macOS /bin/bash 3.2, but the loop also runs on the Mac cache. Replaced the `mapfile -t dirs` line with a bash-3.2-safe read loop: `dirs=(); while IFS= read -r d; do dirs+=("$d"); done < <(printf ... | sort -rV)`, then append the checkout fallback. `sort -rV` and the glob are unchanged. Uses only bash 3.1-era features (empty-array assign, process substitution, `+=`). All four done-checks PASS, no FAIL (LOAM_HOOK unset, so check-green ran the real bin/check).
Observed, not fixed (out of scope, and grader_file only per Where): `bin/factory:911` also uses `mapfile`; the same bash-3.2 concern applies if that code path runs on the Mac.

~~~~~~~~~~~~ evidence

## Diff (f9666778...HEAD)

~~~~~~~~~~~~ evidence
 bin/factory | 12 ++++++++----
 1 file changed, 8 insertions(+), 4 deletions(-)

diff --git a/bin/factory b/bin/factory
index e83f0aa..7d9991e 100755
--- a/bin/factory
+++ b/bin/factory
@@ -196,10 +196,14 @@ GRADERS_DIR=""
 # so both grade with the version the ledger records. --graders-dir replaces the search.
 grader_file() {
   local dirs=("$GRADERS_DIR") d f
-  # The installed plugin first; the checkout's own marketplace copy is the fallback, so a run works
-  # from a branch whose grader edits are not installed yet.
-  [ -n "$GRADERS_DIR" ] || dirs=("$HOME"/.claude/plugins/cache/*/sam-cc-setup/*/agents \
-                                 "$ROOT/cultivation/marketplace/sam-cc-setup/agents")
+  # The installed plugin cache is searched newest version first; the checkout's own marketplace copy
+  # is the last-resort fallback, so a run works from a branch whose grader edits are not installed yet.
+  # `claude plugin update` leaves old versions in the cache, so sort by version, not by glob order.
+  if [ -z "$GRADERS_DIR" ]; then
+    dirs=() # bash 3.2 (macOS) has no mapfile, so read the sorted glob in a plain loop, like skill_file
+    while IFS= read -r d; do dirs+=("$d"); done < <(printf '%s\n' "$HOME"/.claude/plugins/cache/*/sam-cc-setup/*/agents | sort -rV)
+    dirs+=("$ROOT/cultivation/marketplace/sam-cc-setup/agents")
+  fi
   for d in "${dirs[@]}"; do
     f="$d/$1.md"
     [ -f "$f" ] && { printf '%s\n' "$f"; return 0; }
~~~~~~~~~~~~ evidence
