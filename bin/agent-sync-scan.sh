#!/usr/bin/env bash
# sync.sh — sync project's .claude/ INTO the loam repo's cultivation/marketplace/sam-cc-setup/.
# Invoked by the /sync-to-hub skill (or directly for testing).
#
# Direction: project → hub, ADDITIVE ONLY.
# The hub is the curated master set. Files that exist in hub but not in the
# project are NEVER touched — projects are allowed to be a subset of hub.
# Only NEW or CHANGED files are candidates for sync, and each one is presented
# to the user with a 3-way prompt: y=sync now, d=defer (default), n=never.
#
# State persistence: <hub>/.sync-state tracks decisions per file across runs.
# - "defer" remembers an ask_again_at session number; the file is skipped
#   silently until that session is reached.
# - "never" suppresses prompts forever (until state cleared manually).
# - "synced" records when a file was promoted into the hub.
# Threshold for defer expiration: env SAM_CC_DEFER_SESSIONS, default 4.
set -euo pipefail

PROJECT_ROOT="$(git rev-parse --show-toplevel 2>/dev/null)" || {
  echo "Error: run from inside the project's git repo." >&2
  exit 1
}
HUB_REPO="${SAM_CC_HUB_REPO:-$HOME/Desktop/loam}"
DEFER_SESSIONS="${SAM_CC_DEFER_SESSIONS:-4}"
# H5 (Codex pass 2 High): the defer counter feeds Bash arithmetic; bound it to a
# 1-9 digit decimal (<= 999999999) so it can never overflow or inject.
[[ "$DEFER_SESSIONS" =~ ^[0-9]{1,9}$ ]] || {
  echo "Error: SAM_CC_DEFER_SESSIONS must be a decimal number of 1 to 9 digits (got '$DEFER_SESSIONS')" >&2
  exit 1
}
STATE_FILE="$HUB_REPO/.sync-state"

# --bootstrap-bases (R5): a one-time, non-interactive pass that records a merge
# base for every path already shared by project and hub. It never prompts, never
# copies, and touches only .sync-state, so it skips the hub-dirty prompt and the
# rsync diff below and short-circuits before the main scan flow.
BOOTSTRAP_BASES=0
[ "${1:-}" = "--bootstrap-bases" ] && BOOTSTRAP_BASES=1

# 1. Verify hub repo exists and is a git repo
if [ ! -d "$HUB_REPO/.git" ]; then
  echo "Error: Hub repo not found at $HUB_REPO. Set SAM_CC_HUB_REPO to point at it." >&2
  exit 1
fi

# 2. Verify project's .claude/ is committed
if [ -n "$(git -C "$PROJECT_ROOT" status --porcelain .claude 2>/dev/null)" ]; then
  echo "Error: Project's .claude/ has uncommitted changes. Commit or stash before syncing." >&2
  exit 1
fi

# 3. Verify the hub is safe to commit into.
# 3a. C2 (Codex Critical): refuse a non-empty hub index. The final `git commit`
#     has no pathspec, so anything already staged in the hub index would be swept
#     into the sync/prune commit and could be pushed to the public repo. Fail
#     closed here, BEFORE the unstaged-WIP prompt below and with no prompt of its
#     own. Bootstrap never commits, so it stays exempt.
if [ "$BOOTSTRAP_BASES" -eq 0 ] && ! git -C "$HUB_REPO" diff --cached --quiet 2>/dev/null; then
  echo "Error: hub index has staged changes; commit or unstage them before syncing:" >&2
  git -C "$HUB_REPO" diff --cached --name-only >&2
  exit 1
fi

# 3b. Verify hub working tree is clean (warn if not).
#    .sync-state is sync.sh's own state file and is excluded from the cleanliness
#    check (it is expected to be untracked and is added to the hub's .gitignore).
HUB_DIRTY=$(git -C "$HUB_REPO" status --porcelain 2>/dev/null \
  | grep -v -E ' \.sync-state$' || true)
if [ "$BOOTSTRAP_BASES" -eq 0 ] && [ -n "$HUB_DIRTY" ]; then
  echo "Warning: Hub has uncommitted changes — sync may overwrite WIP." >&2
  printf "Continue? [y/N] " >&2
  read -r response || response=""
  case "$response" in
    [yY]|[yY][eE][sS]) ;;
    *) echo "Aborted." >&2; exit 1 ;;
  esac
fi

# Load state file (associative array path → decision-string).
# STATE_BASES holds the three-way merge base: base:<path>:<sha> records the
# blob sha of the PROJECT content at the last sync or bootstrap (Wave 1, R1).
# It is a SEPARATE record from synced: because the legacy synced: parser splits
# on the last colon for the session number; a 4-field record would break it.
declare -A STATE_DECISIONS
declare -A STATE_BASES
PRIOR_SESSION=0

# H1 (Codex High): reject a crafted .sync-state key before it can drive any
# filesystem or git operation. A key like ../../../README.md escapes the plugin
# root - consider_prune resolves it to a file OUTSIDE the tree and an approved
# prune git-rm's it there. Reject empty, absolute (leading /), any . or ..
# path component, and an embedded newline/carriage-return. Returns 0 if safe.
state_path_ok() {
  local p="$1"
  [ -n "$p" ] || return 1
  case "$p" in
    /*) return 1 ;;
  esac
  case "/$p/" in
    *"/../"*|*"/./"*) return 1 ;;
  esac
  case "$p" in
    *$'\n'*|*$'\r'*) return 1 ;;
  esac
  return 0
}

if [ -f "$STATE_FILE" ]; then
  while IFS= read -r line; do
    [ -z "$line" ] && continue
    case "$line" in
      session=*)
        sess="${line#session=}"
        # C3 (Codex Critical): the session value feeds `$((PRIOR_SESSION + 1))`,
        # where a crafted `a[$(cmd)]` runs the command on older bash. Accept only
        # a decimal count; anything else warns and leaves PRIOR_SESSION=0.
        if [[ "$sess" =~ ^[0-9]{1,9}$ ]]; then
          PRIOR_SESSION="$sess"
        else
          echo "warning: ignoring malformed .sync-state session: $sess" >&2
        fi
        ;;
      never:*)
        path="${line#never:}"
        state_path_ok "$path" || { echo "warning: ignoring malformed .sync-state key: $path" >&2; continue; }
        STATE_DECISIONS["$path"]="never"
        ;;
      defer:*)
        rest="${line#defer:}"
        path="${rest%:*}"
        ask_at="${rest##*:}"
        state_path_ok "$path" || { echo "warning: ignoring malformed .sync-state key: $path" >&2; continue; }
        # C3: ask_at feeds `[ "$CURRENT_SESSION" -lt "$ask_at" ]` (arithmetic), so
        # a non-decimal counter is malformed and could smuggle a subscript on
        # older bash; drop the whole defer record.
        [[ "$ask_at" =~ ^[0-9]{1,9}$ ]] || { echo "warning: ignoring malformed .sync-state key: $path" >&2; continue; }
        STATE_DECISIONS["$path"]="defer:$ask_at"
        ;;
      base:*)
        rest="${line#base:}"
        path="${rest%:*}"
        base_sha="${rest##*:}"
        state_path_ok "$path" || { echo "warning: ignoring malformed .sync-state key: $path" >&2; continue; }
        # Ignore a malformed base: line with an empty sha (defensive).
        [ -n "$base_sha" ] && STATE_BASES["$path"]="$base_sha"
        ;;
      synced:*)
        rest="${line#synced:}"
        path="${rest%:*}"
        at_session="${rest##*:}"
        state_path_ok "$path" || { echo "warning: ignoring malformed .sync-state key: $path" >&2; continue; }
        STATE_DECISIONS["$path"]="synced:$at_session"
        ;;
    esac
  done < "$STATE_FILE"
fi
# The ledger is now loaded; the EXIT trap below may persist it. Guarding on this
# flag means an early abort BEFORE the parse never overwrites .sync-state with an
# empty state (High 1, Codex).
STATE_LOADED=1
# 10# forces base-10 so a validated leading-zero count (e.g. 08) never trips the
# octal parser; PRIOR_SESSION is guaranteed decimal by the session=* guard above.
CURRENT_SESSION=$((10#$PRIOR_SESSION + 1))

# Resolve the project and hub trees (shared by bootstrap and the scan below).
PROJECT_CLAUDE="$PROJECT_ROOT/.claude/"
HUB_PLUGIN="$HUB_REPO/cultivation/marketplace/sam-cc-setup/"

RSYNC_EXCLUDES=(
  --exclude=audit.log
  --exclude=.validation_passed
  --exclude=settings.local.json
  --exclude='*.local.*'
)

# Helper: write current state back to disk.
write_state() {
  # C4 (Codex pass 2 Critical): return 1 on a genuine failure to persist the
  # ledger or the base ref, so the normal-path callers can abort BEFORE the
  # commit; a normal run returns 0. The EXIT-trap caller uses `|| true`.
  local rc=0
  # Explicit if/else, NOT `if ! group > tmp && mv` (that binds as
  # `(! group>tmp) && mv`, so mv never runs on the success path).
  if { echo "session=$CURRENT_SESSION"
    for p in "${!STATE_DECISIONS[@]}"; do
      local dec="${STATE_DECISIONS[$p]}"
      case "$dec" in
        never) echo "never:$p" ;;
        defer:*) echo "defer:$p:${dec#defer:}" ;;
        synced:*) echo "synced:$p:${dec#synced:}" ;;
      esac
    done
    for p in "${!STATE_BASES[@]}"; do
      echo "base:$p:${STATE_BASES[$p]}"
    done
     } > "${STATE_FILE}.tmp" && mv "${STATE_FILE}.tmp" "$STATE_FILE"; then
    :   # state written
  else
    echo "  warning: could not write $STATE_FILE" >&2
    rm -f "${STATE_FILE}.tmp" 2>/dev/null || true
    rc=1
  fi

  # C1 (Codex Critical): keep every base blob reachable so `git gc --prune=now`
  # cannot delete it and drop the changed path back to the legacy overwrite
  # prompt (which can erase a hub-only generalization). Rebuild ONE ref
  # refs/agent-sync/bases pointing at a tree of the STATE_BASES blobs.
  # refs/agent-sync/* lives outside refs/heads and refs/tags, so a plain
  # `git push` never sends it to the public hub remote; it exists only to keep
  # the base blobs reachable for gc. Every step warns and sets rc=1 on failure.
  # STATE_BASES is `declare -A` but never assigned, so `${#STATE_BASES[@]}` trips
  # `set -u` when empty; the `[*]+x` alternate form is the set-u-safe emptiness
  # test (yields "x" only when at least one key is set).
  if [ -n "${STATE_BASES[*]+x}" ]; then
    local base_index base_tree
    # A fresh, NON-existent index path: git creates it. An empty pre-created file
    # (e.g. from mktemp) is rejected as a corrupt index ("index file smaller than
    # expected"). WORKDIR is a private mktemp -d, so a fixed name is safe here.
    base_index="$WORKDIR/base-index"
    rm -f "$base_index"
    if ! { for p in "${!STATE_BASES[@]}"; do
             printf '100644 %s\t%s\n' "${STATE_BASES[$p]}" "$p"
           done; } | GIT_INDEX_FILE="$base_index" \
             git -C "$HUB_REPO" update-index --index-info 2>/dev/null; then
      echo "  warning: could not stage base blobs for refs/agent-sync/bases" >&2
      rc=1
    # --missing-ok: a stale STATE_BASES sha whose blob is gone must not abort the
    # tree write (test_base_missing_blob.sh seeds exactly such a sha).
    elif base_tree=$(GIT_INDEX_FILE="$base_index" \
         git -C "$HUB_REPO" write-tree --missing-ok 2>/dev/null); then
      if ! git -C "$HUB_REPO" update-ref refs/agent-sync/bases "$base_tree" 2>/dev/null; then
        echo "  warning: could not update refs/agent-sync/bases" >&2
        rc=1
      fi
    else
      echo "  warning: could not write base tree for refs/agent-sync/bases" >&2
      rc=1
    fi
    rm -f "$base_index"
  else
    # No bases recorded: drop the ref so gc can reclaim any orphaned blobs.
    # Best-effort: a missing ref is the desired end state, so never fail on it.
    git -C "$HUB_REPO" update-ref -d refs/agent-sync/bases 2>/dev/null || true
  fi
  return "$rc"
}

# Record the PROJECT content of $1 as the merge base for next time (R2): write
# its blob into the hub object store and remember the sha. Content-addressed, so
# the value is the same whether computed before or after the file is installed.
record_base() {
  local sha
  if ! sha=$(git -C "$HUB_REPO" hash-object -w "$PROJECT_CLAUDE$1" 2>/dev/null); then
    echo "  warning: hash-object failed for $1; base left unchanged" >&2
    return 0
  fi
  # Only store a real 40-hex blob sha; never let an empty/garbled value become a
  # `base:<path>:` line that the EXIT trap would persist (Codex High).
  # loam is a SHA-1 repository; a SHA-256 hub (64-hex) is out of scope (Codex M2, declined 2026-08-22).
  if [[ "$sha" =~ ^[0-9a-f]{40}$ ]]; then
    STATE_BASES["$1"]="$sha"
  else
    echo "  warning: hash-object gave no valid sha for $1; base left unchanged" >&2
  fi
}

# Is $1 a base sha that resolves to a BLOB in the hub object store? cat-file -e
# accepts any object type, but the merge needs a blob; a commit/tree sha (or a
# pruned blob) must be treated as no-base (Codex Medium).
base_blob_present() {
  [ "$(git -C "$HUB_REPO" cat-file -t "$1" 2>/dev/null)" = blob ]
}

# Should the relative path be skipped for bootstrap? Honors the same RSYNC_EXCLUDES
# patterns and always skips the state file itself.
bootstrap_excluded() {
  local rel="$1" base
  base=$(basename "$rel")
  [ "$rel" = ".sync-state" ] && return 0
  case "$base" in
    audit.log|.validation_passed|settings.local.json) return 0 ;;
    *.local.*) return 0 ;;
  esac
  return 1
}

# One EXIT trap covers both concerns: it persists the ledger (so per-item
# records survive even a mid-batch cp/git rm abort) and removes all temp files
# (base/merge/file-list) so none leak on an error or signal. The write_state is
# guarded by STATE_LOADED so an abort before the parse cannot clobber .sync-state
# with an empty state. Registered here, after write_state is defined.
WORKDIR=$(mktemp -d)
cleanup() {
  [ "${STATE_LOADED:-0}" -eq 1 ] && { write_state || true; }   # cleanup must never abort
  rm -rf "$WORKDIR"
}
trap cleanup EXIT

# --bootstrap-bases (R5): record a base for every regular file present in BOTH
# trees at the same relative path, using the PROJECT blob sha, skipping paths
# that already have one. Never prompts, never copies, touches only .sync-state,
# and does not bump the session counter.
if [ "$BOOTSTRAP_BASES" -eq 1 ]; then
  # R5 is a state-only pass: it must not create the hub tree (Codex Medium).
  [ -d "$HUB_PLUGIN" ] || {
    echo "Error: hub plugin tree not found at $HUB_PLUGIN; nothing to bootstrap." >&2
    # R5 no-bump holds even on this error path: the EXIT trap's write_state must
    # not advance the session, so pin it to PRIOR before exiting.
    CURRENT_SESSION="$PRIOR_SESSION"
    exit 1
  }
  bs_recorded=0
  bs_present=0
  while IFS= read -r pf; do
    rel="${pf#"$PROJECT_CLAUDE"}"
    bootstrap_excluded "$rel" && continue
    [ -f "$HUB_PLUGIN$rel" ] || continue
    # A recorded base whose blob is still present counts as already present; a
    # base whose blob is missing (pruned by gc, or a stale/crafted sha) is
    # RE-RECORDED so bootstrap repairs it instead of trusting the dead value (C1).
    if [ -n "${STATE_BASES[$rel]:-}" ] && base_blob_present "${STATE_BASES[$rel]}"; then
      bs_present=$((bs_present + 1))
      continue
    fi
    record_base "$rel"
    bs_recorded=$((bs_recorded + 1))
  done < <(find "$PROJECT_CLAUDE" -type f)
  CURRENT_SESSION="$PRIOR_SESSION"   # never bump the session on a bootstrap
  write_state || { echo "Error: could not persist .sync-state or refs/agent-sync/bases; hub left uncommitted" >&2; exit 1; }
  echo "bootstrap: $bs_recorded bases recorded, $bs_present already present"
  exit 0
fi

# The normal scan may create the hub plugin dir on a first sync; bootstrap must
# not (see above), so the mkdir lives below the bootstrap exit path.
mkdir -p "$HUB_PLUGIN"

# Helper: should we prompt for this path? Returns 0 (prompt) or 1 (skip silently).
should_prompt() {
  local path="$1"
  local prior="${STATE_DECISIONS[$path]:-}"
  case "$prior" in
    never) return 1 ;;
    defer:*)
      local ask_at="${prior#defer:}"
      [ "$CURRENT_SESSION" -lt "$ask_at" ] && return 1
      return 0
      ;;
    *) return 0 ;;
  esac
}

# Critical-1 (Codex): a changed candidate whose project content still equals its
# recorded base has NOT changed since the last sync - the hub-vs-project delta is
# only the hub's own generalization, so it must not be re-offered. Returns 0
# (suppress) only when a valid base blob is present AND the project blob matches
# it; otherwise 1 (let normal handling proceed).
project_unchanged_since_base() {
  local path="$1" base_sha
  base_sha="${STATE_BASES[$path]:-}"
  [ -n "$base_sha" ] || return 1
  base_blob_present "$base_sha" || return 1
  [ "$(git hash-object "$PROJECT_CLAUDE$path")" = "$base_sha" ]
}

# Portability manifest guard (2026-08-02). The manifest classifies every asset
# as travels/stays/rework; anything marked "stays" must never be offered to the
# hub — the hub is a curated subset, and an additive project→hub sync is
# otherwise a one-way ratchet toward the project's dialect.
MANIFEST_TSV="$PROJECT_ROOT/.claude/reference/portability-manifest.tsv"
manifest_verdict() {
  # Longest-prefix match: "skills/codex-review/SKILL.md" matches row "skills/codex-review".
  local path="$1" probe
  [ -f "$MANIFEST_TSV" ] || { echo ""; return; }
  probe="$path"
  while [ -n "$probe" ] && [ "$probe" != "." ]; do
    local v
    v=$(awk -F'\t' -v p="$probe" '$1 == p { print $3; exit }' "$MANIFEST_TSV")
    if [ -n "$v" ]; then echo "$v"; return; fi
    probe="$(dirname "$probe")"
  done
  echo ""
}

# Filter to paths that need prompting (not silently-skipped by state or manifest).
# Fail-closed when a manifest exists (Codex review 2026-08-02): only 'travels'
# paths may be offered. 'stays' is project-local by declaration; 'rework' is
# project-hardcoded and must be generalized before it may enter the hub; a
# path with NO verdict is unclassified (plans, transcripts, __pycache__, ...)
# and is exactly the noise an additive sync must not offer. Without a manifest
# (other projects), behavior is unchanged: everything is offered.
SKIPPED_STAYS=0; SKIPPED_REWORK=0; SKIPPED_UNKNOWN=0
manifest_allows() {
  [ -f "$MANIFEST_TSV" ] || return 0
  case "$(manifest_verdict "$1")" in
    travels) return 0 ;;
    stays)   SKIPPED_STAYS=$((SKIPPED_STAYS+1));   return 1 ;;
    rework)  SKIPPED_REWORK=$((SKIPPED_REWORK+1)); return 1 ;;
    *)       SKIPPED_UNKNOWN=$((SKIPPED_UNKNOWN+1)); return 1 ;;
  esac
}

# R6 prune fold-in: collect hub files whose project source is gone. A candidate
# has a synced: OR base: ledger record, its hub copy still exists, its project
# source does not, and it is not suppressed by a prior never/defer. Collected
# BEFORE the no-changes early-exit so a retired-file-only run still offers the
# deletion (lead-approved refinement inside R6).
PRUNE_CANDIDATES=()
declare -A _prune_seen
consider_prune() {
  local p="$1"
  [ -n "${_prune_seen[$p]:-}" ] && return
  _prune_seen[$p]=1
  [ -f "$HUB_PLUGIN$p" ] || return          # nothing in the hub to prune
  [ -e "$PROJECT_CLAUDE$p" ] && return       # project source still exists
  should_prompt "$p" || return               # suppressed by a prior never/defer
  # H2 (Codex High): a folded prune must carry an explicit 'travels' verdict,
  # matching bin/agent-sync-prune.sh's manifest gate. A retired stays/rework/
  # unclassified path - or ANY path when there is no manifest at all - is
  # withheld (fail closed), so a curated hub-only generalization is never
  # offered for deletion. Not counted in the SKIPPED_* adds/changes tallies.
  local prune_verdict
  prune_verdict="$(manifest_verdict "$p")"
  if [ "$prune_verdict" != travels ]; then
    echo "  prune withheld (manifest verdict '${prune_verdict:-unclassified}', not travels): $p" >&2
    return
  fi
  PRUNE_CANDIDATES+=("$p")
}
for p in "${!STATE_DECISIONS[@]}"; do
  case "${STATE_DECISIONS[$p]}" in synced:*) consider_prune "$p" ;; esac
done
for p in "${!STATE_BASES[@]}"; do
  consider_prune "$p"
done

# 4. Compute additive diff via rsync --dry-run (no --delete).
# --checksum forces content comparison (slower but accurate). Without it,
# rsync uses size+mtime, which produces false-positive prompts for files
# touched but unchanged (common after a fresh git clone).
set +e
RSYNC_DIFF=$(rsync --dry-run -a --checksum --itemize-changes \
  "${RSYNC_EXCLUDES[@]}" \
  "$PROJECT_CLAUDE" "$HUB_PLUGIN" 2>&1)
RSYNC_STATUS=$?
set -e
if [ "$RSYNC_STATUS" -ne 0 ]; then
  echo "Error: rsync dry-run failed (exit $RSYNC_STATUS); refusing to report 'no changes'." >&2
  echo "$RSYNC_DIFF" >&2
  exit 1
fi

CHANGES=$(echo "$RSYNC_DIFF" | grep -E '^(>f|<f|cf|hf)' || true)

# Exit early only when there is genuinely nothing to do: no adds/changes AND no
# retired files to prune. The message and behavior here are unchanged.
if [ -z "$CHANGES" ] && [ "${#PRUNE_CANDIDATES[@]}" -eq 0 ]; then
  echo "No changes — hub is in sync with project."
  write_state || { echo "Error: could not persist .sync-state or refs/agent-sync/bases; hub left uncommitted" >&2; exit 1; }
  exit 0
fi

# 5. Categorize.
# The itemize-changes attribute field is NOT a fixed 9 chars everywhere:
# GNU rsync emits 9 attribute chars (11 total incl. YX), but macOS ships
# BSD openrsync, which emits only 7 (9 total) - a `{9}` literal count matched
# zero lines there, silently reporting "0 new files" on every run. Match by
# shape instead: an all-'+' run after ">f" is a brand-new file; any other
# non-space run is a changed file. Width-independent, so it works under
# either rsync implementation.
ADDED_PATHS=()
CHANGED_PATHS=()
while IFS= read -r line; do
  [ -z "$line" ] && continue
  if [[ "$line" =~ ^\>f\++\ (.*)$ ]]; then
    ADDED_PATHS+=("${BASH_REMATCH[1]}")
  elif [[ "$line" =~ ^\>f[^+\ ][^\ ]*\ (.*)$ ]]; then
    CHANGED_PATHS+=("${BASH_REMATCH[1]}")
  fi
done <<< "$CHANGES"

PROJ_NAME=$(basename "$PROJECT_ROOT")

# Helper: prompt user, record the NEGATIVE decision into state, return 0 if
# approved. A y approval is NOT recorded here: synced:/base: are written only
# after the file is successfully installed (High 1, Codex), so a failed install
# never leaves a synced ledger entry. defer/never persist regardless.
prompt_for() {
  local action="$1" path="$2"
  printf "%s %s to hub? [y=sync now / d=defer (default) / n=never] " "$action" "$path" >&2
  local resp; read -r resp || resp=""
  case "$resp" in
    y|Y|yes|YES|sync)
      return 0
      ;;
    n|N|never|NEVER)
      STATE_DECISIONS["$path"]="never"
      return 1
      ;;
    *)
      local ask_at=$((CURRENT_SESSION + DEFER_SESSIONS))
      STATE_DECISIONS["$path"]="defer:$ask_at"
      return 1
      ;;
  esac
}

# Dependency-integrity guard (added for the Phase-1A tiered gate; made
# transitive + hub-presence-aware 2026-08-05). A 'travels' consumer whose
# `requires` graph reaches a helper that is not itself 'travels', has no
# manifest row, or is not yet PRESENT in the hub would ship a half-broken
# gate to the hub (e.g. pre-commit-gate.sh without gate_tier.py). The guard
# resolves the COMPLETE transitive closure of column-5 `requires` cells, so
# requires cells only need to name direct deps. Fail-closed on every gap:
# missing manifest row, dependency cycle (diagnosed, never looped), non-
# 'travels' verdict, and hub absence. Hub presence is EXISTENCE ONLY, never
# byte identity - hub copies intentionally diverge after de-projectization.
# When a portable dep is merely absent from the hub, the consumer is withheld
# with a sync-the-dependency-first message; the user syncs the dep and reruns.
# Column 5 is optional; 4-column rows leave it empty and manifest_verdict
# (reads $3 only) is unaffected.
SKIPPED_DEPS=0

# Resolve a path to its manifest row key via the same longest-prefix walk as
# manifest_verdict: a file under a directory row (skills/validate/SKILL.md ->
# row skills/validate) inherits that row, including its `requires` cell
# (exact-match-only here was a fail-open hole, Codex review 2026-08-05 High).
manifest_rowkey() {
  local path="$1" probe="$1"
  [ -f "$MANIFEST_TSV" ] || { echo ""; return; }
  while [ -n "$probe" ] && [ "$probe" != "." ]; do
    if [ -n "$(awk -F'\t' -v p="$probe" '$1 == p { print "1"; exit }' "$MANIFEST_TSV")" ]; then
      echo "$probe"; return
    fi
    probe="$(dirname "$probe")"
  done
  echo ""
}

manifest_field() { # $1=row key, $2=column number
  awk -F'\t' -v p="$1" -v c="$2" '$1 == p { print $c; exit }' "$MANIFEST_TSV"
}

# DFS over the requires graph, run in two modes (Codex review 2026-08-05
# Medium: graph structure must validate BEFORE presence, or an absent cycle
# member masks the cycle diagnostic):
#   graph    - manifest rows, non-'travels' verdicts, cycles, malformed paths
#   presence - every closure dep must exist in the hub's committed HEAD
# Presence means hub HEAD, not the working tree (Codex High: `-e` accepted an
# untracked/dirty hub file that the scoped sync commit would not include).
# $1 = current path, $2 = space-separated row keys on the current DFS chain
# (cycle detector), $3 = mode. On failure sets DEP_FAIL_REASON, returns 1.
HUB_PLUGIN_REL="cultivation/marketplace/sam-cc-setup/"
check_dep_closure() {
  local path="$1" chain="$2" mode="$3" rowkey requires dep dep_row dep_verdict
  rowkey="$(manifest_rowkey "$path")"
  [ -z "$rowkey" ] && return 0   # entry paths without a row never get here (manifest_allows)
  chain="$chain $rowkey"
  requires="$(manifest_field "$rowkey" 5)"
  [ -z "$requires" ] && return 0
  for dep in $requires; do
    # Reject non-normalized dep paths before any lookup (Codex High: an
    # absolute path loops the dirname walk forever, and `..` segments could
    # escape the plugin root at the presence check).
    case "/$dep/" in
      *"/../"*|*"/./"*|//*)
        DEP_FAIL_REASON="requires $dep - malformed dependency path (fail closed)"
        return 1 ;;
    esac
    dep_row="$(manifest_rowkey "$dep")"
    if [ -z "$dep_row" ]; then
      DEP_FAIL_REASON="requires $dep, which has no manifest row (fail closed)"
      return 1
    fi
    case " $chain " in *" $dep_row "*)
      if [ "$mode" = graph ]; then
        DEP_FAIL_REASON="requires $dep - dependency cycle detected (${chain# } -> $dep_row)"
        return 1
      fi
      continue ;;  # presence mode: graph mode already proved acyclicity
    esac
    if [ "$mode" = graph ]; then
      dep_verdict="$(manifest_field "$dep_row" 3)"
      if [ "$dep_verdict" != "travels" ]; then
        DEP_FAIL_REASON="requires $dep (${dep_verdict:-unclassified}, not travels)"
        return 1
      fi
    elif ! git -C "$HUB_REPO" cat-file -e "HEAD:${HUB_PLUGIN_REL}${dep}" 2>/dev/null; then
      DEP_FAIL_REASON="requires $dep, which is not yet in the hub's committed HEAD - sync the dependency first, then rerun"
      return 1
    fi
    check_dep_closure "$dep" "$chain" "$mode" || return 1
  done
  return 0
}

deps_satisfied() {
  local path="$1"
  [ -f "$MANIFEST_TSV" ] || return 0
  DEP_FAIL_REASON=""
  if ! check_dep_closure "$path" "" graph || ! check_dep_closure "$path" "" presence; then
    echo "  withheld: $path $DEP_FAIL_REASON" >&2
    SKIPPED_DEPS=$((SKIPPED_DEPS+1))
    return 1
  fi
  return 0
}

PROMPT_ADDS=()
for path in "${ADDED_PATHS[@]:-}"; do
  [ -z "${path:-}" ] && continue
  manifest_allows "$path" || continue
  deps_satisfied "$path" || continue
  should_prompt "$path" && PROMPT_ADDS+=("$path")
done
PROMPT_CHANGES=()
for path in "${CHANGED_PATHS[@]:-}"; do
  [ -z "${path:-}" ] && continue
  manifest_allows "$path" || continue
  deps_satisfied "$path" || continue
  should_prompt "$path" || continue
  project_unchanged_since_base "$path" && continue   # Critical-1: no-op, suppress
  PROMPT_CHANGES+=("$path")
done
if [ -f "$MANIFEST_TSV" ]; then
  echo "  manifest guard: $SKIPPED_STAYS 'stays', $SKIPPED_REWORK 'rework' (generalize first), $SKIPPED_UNKNOWN unclassified, $SKIPPED_DEPS dep-withheld paths"
fi

echo "Sync from $PROJ_NAME (session $CURRENT_SESSION):"
echo "  ${#PROMPT_ADDS[@]} new files to ask about (${#ADDED_PATHS[@]} total — others suppressed by prior decisions)"
echo "  ${#PROMPT_CHANGES[@]} changed files to ask about (${#CHANGED_PATHS[@]} total — others suppressed by prior decisions)"

# 6. Prompt only the non-suppressed entries.
APPROVED_ADDS=()
for path in "${PROMPT_ADDS[@]:-}"; do
  [ -z "${path:-}" ] && continue
  if prompt_for "Add" "$path"; then
    APPROVED_ADDS+=("$path")
  fi
done

APPROVED_CHANGES=()
MERGED_PATHS=()
declare -A MERGED_TMP
if [ "${#PROMPT_CHANGES[@]}" -gt 0 ]; then
  echo "CAUTION: hub copies in this plugin are GENERALIZED variants (de-projectized" >&2
  echo "paths, different gate thresholds). Overwriting one reverts that generalization." >&2
  echo "Answer y only if you intend to re-generalize the hub copy afterwards." >&2
fi
for path in "${PROMPT_CHANGES[@]:-}"; do
  [ -z "${path:-}" ] && continue
  base_sha="${STATE_BASES[$path]:-}"
  handled=0
  # Clean-merge regime (R3): the path has a recorded base, the base blob still
  # exists in the hub object store, AND the three-way merge is clean. Every
  # other outcome (no base, pruned blob, or a non-clean merge) falls through to
  # the legacy overwrite prompt below.
  if [ -n "$base_sha" ] && base_blob_present "$base_sha"; then
    base_tmp=$(mktemp "$WORKDIR/base.XXXXXX")
    git -C "$HUB_REPO" cat-file blob "$base_sha" > "$base_tmp"
    merged_tmp=$(mktemp "$WORKDIR/merged.XXXXXX")
    set +e
    git merge-file --stdout -L hub -L base -L project \
      "$HUB_PLUGIN$path" "$base_tmp" "$PROJECT_CLAUDE$path" > "$merged_tmp"
    mrc=$?
    set -e
    rm -f "$base_tmp"
    if [ "$mrc" -eq 0 ]; then
      handled=1
      # Critical-2 (Codex): a clean merge whose output equals the hub copy is a
      # no-op (the project independently made the same edit the hub already had).
      # State-only base advance: record the base so the next scan sees
      # project==base and Critical 1 suppresses it; do NOT offer, install, set
      # synced:, or commit.
      if cmp -s "$merged_tmp" "$HUB_PLUGIN$path"; then
        rm -f "$merged_tmp"
        record_base "$path"
        continue
      fi
      # Clean three-way merge: hub generalization and project edit coexist.
      printf 'Merge %s: clean three-way merge (hub generalization kept, project edit applied)\n' "$path" >&2
      diff -u "$HUB_PLUGIN$path" "$merged_tmp" >&2 || true
      if prompt_for "Merge" "$path"; then
        MERGED_PATHS+=("$path")
        MERGED_TMP["$path"]="$merged_tmp"
      else
        rm -f "$merged_tmp"
      fi
    elif [ "$mrc" -eq 255 ]; then
      # Operational error (High 2, Codex): git merge-file returns 255 when it
      # cannot complete - e.g. an unreadable input file - which is NOT a content
      # conflict and must never be offered a destructive overwrite. Skip the path
      # safely: warn and continue, with no prompt and no state change.
      handled=1
      rm -f "$merged_tmp"
      printf 'Merge error %s: git merge-file failed (exit %s); skipped\n' "$path" "$mrc" >&2
      continue
    else
      # Conflict (mrc in 1..254): base present, but hub and project diverge on the
      # same lines. Never auto-install; surface both versions, then take the
      # overwrite prompt (default defer). On y the rsync overwrite applies and the
      # base is re-recorded per R2.
      handled=1
      rm -f "$merged_tmp"
      printf 'Conflict %s: base, hub, and project all differ on the same lines; showing both versions\n' "$path" >&2
      diff -u "$HUB_PLUGIN$path" "$PROJECT_CLAUDE$path" >&2 || true
      if prompt_for "Update" "$path"; then
        APPROVED_CHANGES+=("$path")
      fi
    fi
  fi
  # Legacy overwrite fallthrough (default defer): no base or a pruned base blob.
  if [ "$handled" -eq 0 ]; then
    if prompt_for "Update" "$path"; then
      APPROVED_CHANGES+=("$path")
    fi
  fi
done

# R6 prune fold-in: offer to delete each retired hub file (project source gone).
# Reads from STDIN like the other prompts (prune.sh reads /dev/tty, which is why
# it cannot be tested and is not reused verbatim). Only the y/d/n DECISION is
# collected here; the git rm is applied later, after a preflight, so a mid-loop
# failure cannot leave some deletions staged with their records still present
# (High 3, Codex). d/n record defer/never exactly as prompt_for does.
PRUNE_APPROVED=()
for p in "${PRUNE_CANDIDATES[@]:-}"; do
  [ -z "${p:-}" ] && continue
  printf "Delete %s from hub? [y=delete now / d=defer (default) / n=never] " "$p" >&2
  read -r presp || presp=""
  case "$presp" in
    y|Y|yes|YES) PRUNE_APPROVED+=("$p") ;;
    n|N|never|NEVER) STATE_DECISIONS["$p"]="never" ;;
    *) STATE_DECISIONS["$p"]="defer:$((CURRENT_SESSION + DEFER_SESSIONS))" ;;
  esac
done

TOTAL_APPROVED=$(( ${#APPROVED_ADDS[@]} + ${#APPROVED_CHANGES[@]} + ${#MERGED_PATHS[@]} + ${#PRUNE_APPROVED[@]} ))
if [ "$TOTAL_APPROVED" -eq 0 ]; then
  # Persist defer/never decisions and any no-op base advances, then stop.
  write_state || { echo "Error: could not persist .sync-state or refs/agent-sync/bases; hub left uncommitted" >&2; exit 1; }
  echo "Nothing approved — exiting."
  exit 0
fi

# reject_symlink_path <rel>: C5 (Codex pass 2 Critical). install_file's mkdir -p,
# mktemp and cp would FOLLOW a committed hub symlink ancestor (e.g. a symlink
# `skills -> ../../../outside`) and write OUTSIDE the plugin tree. Walk every
# cumulative component of $rel under HUB_PLUGIN and refuse if any EXISTING one is
# a symlink (`[ -L ]` tests the link itself, never follows it). A fresh path,
# whose components do not exist yet, passes cleanly.
reject_symlink_path() {
  local rel="$1" prefix="" remainder="$1" component
  while [ -n "$remainder" ]; do
    component="${remainder%%/*}"
    if [ "$component" = "$remainder" ]; then remainder=""; else remainder="${remainder#*/}"; fi
    [ -z "$component" ] && continue
    prefix="${prefix:+$prefix/}$component"
    if [ -L "$HUB_PLUGIN$prefix" ]; then
      echo "Error: install failed for $rel (symlink in destination path: $prefix)" >&2
      exit 1
    fi
  done
}

# install_file <src> <dst> <rel>: install one file atomically. H3 (Codex High):
# a bulk rsync could leave earlier files installed with no ledger record when a
# later one fails, and a direct cp can truncate the destination on an I/O error.
# Copy to a temp file in the SAME directory as the destination (so the rename is
# atomic on one filesystem), preserving the mode with cp -p (hook scripts must
# stay +x), then mv -f into place. Each step is guarded so any failure removes
# the temp file, reports the path, and exits 1 - never relying on set -e, which
# would skip the cleanup and message. The EXIT trap then persists the ledger with
# only the items recorded so far. The temp name starts with .sync-install. so a
# leftover can never collide with a real path (none is left on success).
install_file() {
  local src="$1" dst="$2" rel="$3" dstdir tmp
  reject_symlink_path "$rel"   # C5: no symlink ancestor may redirect the write
  # H4 (Codex High): refuse to install over a directory. `mv -f "$tmp" "$dst"`
  # would move the temp file INTO an existing directory and return 0, so the scan
  # would record a phantom synced:/base: and could commit a stray .sync-install.*
  # file. Fail closed before the copy.
  if [ -d "$dst" ]; then
    echo "Error: install failed for $rel (destination is a directory)" >&2
    exit 1
  fi
  dstdir="$(dirname "$dst")"
  mkdir -p "$dstdir" || { echo "Error: install failed for $rel" >&2; exit 1; }
  tmp="$(mktemp "$dstdir/.sync-install.XXXXXX")" || { echo "Error: install failed for $rel" >&2; exit 1; }
  if ! cp -p "$src" "$tmp" || ! mv -f "$tmp" "$dst"; then
    rm -f "$tmp"
    echo "Error: install failed for $rel" >&2
    exit 1
  fi
  # H4 belt-and-suspenders: a TOCTOU race could make $dst a directory after the
  # pre-check, so the mv would land inside it; require a regular file at $dst.
  # On that race the temp was moved to $dst/<tempname>, so clean up there too -
  # never leave a stray .sync-install.* the sync commit could sweep up.
  if [ ! -f "$dst" ]; then
    rm -f "$tmp" "$dst/$(basename "$tmp")"
    echo "Error: install failed for $rel (destination is a directory)" >&2
    exit 1
  fi
}

# 7. Apply approved adds + overwrite-changes, one file at a time.
NONEMPTY=()
for p in "${APPROVED_ADDS[@]:-}" "${APPROVED_CHANGES[@]:-}"; do
  [ -n "$p" ] && NONEMPTY+=("$p")
done

# High 1 (Codex): record synced:/base: per item, IMMEDIATELY after that item is
# installed - never in a single deferred pass - so a mid-batch install/git rm
# abort leaves every earlier success already recorded. H3 closes OD-13c: each
# item installs atomically via install_file, so a later failure can never leave
# an earlier item installed-but-unrecorded. Merged and pruned items are recorded
# one at a time inside their own loops. The EXIT trap then persists the ledger
# even on an abort.
for p in "${NONEMPTY[@]:-}"; do
  [ -z "${p:-}" ] && continue
  install_file "$PROJECT_CLAUDE$p" "$HUB_PLUGIN$p" "$p"
  STATE_DECISIONS["$p"]="synced:$CURRENT_SESSION"
  record_base "$p"
done

# Merged results are installed via install_file too (never rsync, which would
# re-overwrite the hub copy with the raw project file and discard the merge).
# install_file's cp -p would otherwise carry the mktemp temp's 0600 mode, so
# first match the merged result's mode to the PROJECT file's (portable across
# BSD/GNU stat). Record each right after its own install succeeds.
for p in "${MERGED_PATHS[@]:-}"; do
  [ -z "${p:-}" ] && continue
  # GNU stat treats -f as --file-system (it prints a multi-line dump, not the
  # mode), so -f must run AFTER -c; BSD stat has no -c and falls through to -f.
  merged_mode=$(stat -c '%a' "$PROJECT_CLAUDE$p" 2>/dev/null \
    || stat -f '%Lp' "$PROJECT_CLAUDE$p" 2>/dev/null || echo 644)
  chmod "$merged_mode" "${MERGED_TMP[$p]}" 2>/dev/null || true
  install_file "${MERGED_TMP[$p]}" "$HUB_PLUGIN$p" "$p"
  STATE_DECISIONS["$p"]="synced:$CURRENT_SESSION"
  record_base "$p"
  rm -f "${MERGED_TMP[$p]}"
done

# High 3 (Codex): apply prune deletions now, each preflighted so git rm cannot
# fail mid-loop. A candidate whose hub copy is not tracked (e.g. never committed)
# is skipped, not aborted. Each successful deletion drops its records right away.
PRUNED_PATHS=()
for p in "${PRUNE_APPROVED[@]:-}"; do
  [ -z "${p:-}" ] && continue
  # H1 second line of defense: a crafted key cannot reach here after the parser
  # guard drops it, but the git-rm is destructive so re-check before it.
  state_path_ok "$p" || { echo "  prune skipped (malformed state key): $p" >&2; continue; }
  reject_symlink_path "$p"   # C5: no symlink ancestor may redirect the git rm
  hub_rel="cultivation/marketplace/sam-cc-setup/$p"
  if git -C "$HUB_REPO" ls-files --error-unmatch -- "$hub_rel" >/dev/null 2>&1; then
    git -C "$HUB_REPO" rm -r --quiet "$hub_rel"
    unset 'STATE_DECISIONS[$p]'
    unset 'STATE_BASES[$p]'
    PRUNED_PATHS+=("$p")
  else
    echo "  prune skipped (not tracked in hub): $p" >&2
  fi
done

# Persist the ledger now that installs and prunes have happened (the EXIT trap
# also persists it, so a mid-batch abort still records the completed items).
write_state || { echo "Error: could not persist .sync-state or refs/agent-sync/bases; hub left uncommitted" >&2; exit 1; }

# 8. Show resulting git status in hub
echo "---"
echo "Hub status after apply:"
git -C "$HUB_REPO" status --short

# Nothing actually reached the hub (e.g. every approved prune was untracked).
if [ "${#APPROVED_ADDS[@]}" -eq 0 ] && [ "${#APPROVED_CHANGES[@]}" -eq 0 ] \
   && [ "${#MERGED_PATHS[@]}" -eq 0 ] && [ "${#PRUNED_PATHS[@]}" -eq 0 ]; then
  echo "Nothing was applied to the hub — nothing to commit."
  exit 0
fi

# 9. Prompt commit + push (default Y).
printf "Commit synced files? [Y/n] " >&2
read -r commit_resp || commit_resp=""
case "$commit_resp" in
  n|N|no|NO)
    echo "Skipped commit. Hub working tree has changes you can review."
    exit 0
    ;;
esac

# 10. Commit + push.
#     SCOPED: only the approved synced files are added. Pre-existing dirty
#     hub WIP (if user continued through the warning) and runtime artifacts
#     (.sync-state) MUST NOT be swept into the sync commit.
DATE=$(date -u +%Y-%m-%d)
HUB_RELPATHS=()
for p in "${APPROVED_ADDS[@]:-}" "${APPROVED_CHANGES[@]:-}" "${MERGED_PATHS[@]:-}"; do
  [ -n "$p" ] && HUB_RELPATHS+=("cultivation/marketplace/sam-cc-setup/$p")
done

# Stage adds/changes/merges (scoped). Pruned paths are already staged as
# deletions by git rm, so they need no add (git add on a removed path errors).
if [ "${#HUB_RELPATHS[@]}" -gt 0 ]; then
  git -C "$HUB_REPO" add -- "${HUB_RELPATHS[@]}"
fi
git -C "$HUB_REPO" commit -m "sync: from $PROJ_NAME on $DATE"
# Push is outward-facing and the hub is a general-purpose repo — separate confirm.
printf "Push %s to its origin now? [y/N] " "$HUB_REPO" >&2
read -r push_resp || push_resp=""
case "$push_resp" in
  y|Y|yes|YES) ;;
  *) echo "Commit kept local. Push later with: cd $HUB_REPO && git push"; exit 0 ;;
esac
if ! git -C "$HUB_REPO" push 2>&1; then
  echo "Push failed. Run: cd $HUB_REPO && git pull --rebase && git push" >&2
  exit 1
fi
