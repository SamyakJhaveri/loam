#!/usr/bin/env bash
# sync.sh - sync project's .claude/ INTO the loam repo's cultivation/marketplace/sam-cc-setup/.
# Invoked by the /sync-to-hub skill (or directly for testing).
#
# Direction: project → hub, ADDITIVE ONLY.
# The hub is the curated master set. Files that exist in hub but not in the
# project are NEVER touched - projects are allowed to be a subset of hub.
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
# M7 + TOCTOU (group 12): the symlink-sensitive steps bash cannot do no-follow live
# in this helper, located next to the engine. The sync now hard-depends on python3.
SAFE_IO="$(cd "$(dirname "${BASH_SOURCE[0]:-$0}")" && pwd)/agent-sync-safe-io.py"
command -v python3 >/dev/null 2>&1 || { echo "Error: python3 is required (the no-follow safe-io helper)." >&2; exit 1; }
[ -f "$SAFE_IO" ] || { echo "Error: safe-io helper not found at $SAFE_IO; cannot run safely." >&2; exit 1; }
DEFER_SESSIONS="${SAM_CC_DEFER_SESSIONS:-4}"
# H5 (Codex pass 2 High): the defer counter feeds Bash arithmetic; bound it to a
# 1-9 digit decimal (<= 999999999) so it can never overflow or inject.
[[ "$DEFER_SESSIONS" =~ ^[0-9]{1,6}$ ]] || {
  echo "Error: SAM_CC_DEFER_SESSIONS must be a decimal number of 1 to 6 digits (got '$DEFER_SESSIONS')" >&2
  exit 1
}
# Item 7 (Codex p5 Medium): the regex above accepts leading zeros (08, 000008), but
# bare `$(( ... + DEFER_SESSIONS ))` parses those as invalid octal ("value too great
# for base"). Canonicalize to base-10 ONCE here, before any arithmetic use (the
# ceiling guard below, prompt_for's ask_at, the prune-loop ask_at). The regex
# guarantees a 1-6 digit decimal, so 10# never fails.
DEFER_SESSIONS=$((10#$DEFER_SESSIONS))
# Ledger counters (session=, defer ask_at) must stay strictly below a ceiling so
# every value the scan DERIVES from them next run is still re-readable. counter_ok
# rejects anything >= 900000000. This bounds the STORED value; the DERIVED values
# (CURRENT_SESSION = session + 1, and the next ask_at = CURRENT_SESSION +
# DEFER_SESSIONS) are validated at derivation time (just below the CURRENT_SESSION
# assignment) and the run is REFUSED - never rolled over - if either would cross the
# ceiling (Codex pass 4 Medium: the old code let session 899999999 advance to
# 900000000, which the next run then rejected, silently dropping the ledger).
counter_ok() {
  [[ "$1" =~ ^[0-9]{1,9}$ ]] && [ "$1" -lt 900000000 ]
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

# 2. Verify project's .claude/ is committed.
# M7 (group 12): when .claude is a SYMLINK (loam's own .claude -> seed/.claude
# layout), `git status --porcelain .claude` statuses only the symlink blob, so a
# dirty file under the target is invisible while rsync's trailing-slash source
# follows the link and would promote it. Resolve the symlink and status the TARGET
# (the helper refuses a target that escapes the repo).
if ! CLAUDE_PATHSPEC=$(python3 "$SAFE_IO" resolve-claude "$PROJECT_ROOT"); then
  echo "Error: could not resolve the project's .claude path safely; refusing to sync." >&2
  exit 1
fi
# CX-2 (Codex round 1): status BOTH the literal `.claude` path AND the resolved
# target. Statusing only the resolved target misses an uncommitted RETARGET of the
# .claude symlink to a different, clean, committed in-repo tree - the named target
# is clean, the symlink-blob change is never seen, and rsync then promotes a tree
# the project never committed to. The literal `.claude` pathspec catches the
# retarget (and a dirty real .claude dir); the resolved target still catches a
# dirty file under the symlink target. :(literal) per R1; when .claude is not a
# symlink resolve-claude prints `.claude`, so the two pathspecs coincide (harmless).
# H4 (Codex round 1): capture the status OUTPUT and EXIT CODE separately. The old
# `[ -n "$(git status ... 2>/dev/null)" ]` discarded the exit code, so a FAILED
# git status (e.g. a corrupt index) yielded "" and the -n test read the tree as
# CLEAN - a fail-OPEN on the very guard Item 2's tracked-only safety argument rests
# on (this guard refuses every untracked non-ignored path, so the filter can only
# ever exclude gitignored files). Refuse fail-CLOSED on ANY nonzero status, with a
# message DISTINCT from the dirty-tree one, before the -n refusal (and before the
# Item 2 ls-files guard below). Tripwire: test_claude_status_failure_refused.sh.
set +e
claude_porcelain=$(git -C "$PROJECT_ROOT" status --porcelain -- ":(literal).claude" ":(literal)$CLAUDE_PATHSPEC" 2>/dev/null)
claude_status_rc=$?
set -e
if [ "$claude_status_rc" -ne 0 ]; then
  echo "Error: could not check the project's .claude for uncommitted changes (git status exit $claude_status_rc); refusing to sync." >&2
  exit 1
fi
if [ -n "$claude_porcelain" ]; then
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
  echo "Warning: Hub has uncommitted changes - sync may overwrite WIP." >&2
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
# M2: prune decisions live in their OWN namespace so a prune 'd'/'n' never
# overwrites the sync decision slot (STATE_DECISIONS). Serialized as
# prune-defer:/prune-never: records; read by prune_should_prompt, written by the
# prune prompt loop.
declare -A STATE_PRUNE_DECISIONS
PRIOR_SESSION=0

# M3 (group 11): the ledger is shared by multiple source projects, so records are
# keyed by project identity. PROJ_ID is the project's absolute (symlink-resolved)
# git toplevel; the TAB after it delimits the identity from the path. A TAB in the
# identity would corrupt that split, so refuse one (git toplevel never contains a
# TAB or newline in practice, but fail closed).
TAB=$'\t'
PROJ_ID="$PROJECT_ROOT"
case "$PROJ_ID" in
  *"$TAB"*|*$'\n'*)
    echo "Error: project path contains a tab or newline; cannot key the ledger by it: $PROJ_ID" >&2
    exit 1 ;;
esac
# Records belonging to OTHER projects are loaded into neither STATE_* array; they
# are retained verbatim (RETAINED_LINES) and re-emitted unchanged by write_state,
# and their base blob shas (RETAINED_BASE_SHAS) are staged into refs/agent-sync/bases
# so `git gc` cannot prune another project's base out from under it (M3 + C1).
RETAINED_LINES=()
RETAINED_BASE_SHAS=()

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
  # M3 (group 11): a TAB is the project-identity delimiter in the ledger, so a
  # real path must never contain one - that keeps "keypart has a TAB" an
  # unambiguous "this record is project-prefixed" test in the parser.
  case "$p" in
    *"$TAB"*) return 1 ;;
  esac
  return 0
}

# classify_rest <rest-after-type-prefix> (M3, group 11): decide whether a ledger
# record belongs to THIS project and strip its identity prefix. Sets REC_SCOPE and
# REC_BODY. A prefixed record splits on the FIRST tab into <projid> + <body>;
# projid==PROJ_ID -> mine (REC_BODY = body). A different projid -> other (the
# caller retains the raw line verbatim). No tab -> a legacy un-prefixed record,
# ADOPTED by this project (R5): mine, REC_BODY = the whole rest.
classify_rest() {
  local rest="$1"
  if [[ "$rest" == *"$TAB"* ]]; then
    if [ "${rest%%"$TAB"*}" = "$PROJ_ID" ]; then
      REC_SCOPE=mine; REC_BODY="${rest#*"$TAB"}"
    else
      REC_SCOPE=other; REC_BODY=""
    fi
  else
    REC_SCOPE=mine; REC_BODY="$rest"
  fi
}

# Item 5 (Codex p5 Critical): a .sync-state that is a symlink (the `[ -f ]` read
# below follows it) or a directory is not a valid ledger; refuse both shapes up
# front so no read or write ever touches an unexpected target. This runs before
# STATE_LOADED=1 and before the EXIT trap is registered, so nothing is persisted on
# this abort.
if [ -L "$STATE_FILE" ]; then
  echo "Error: $STATE_FILE is a symlink, not a regular file; refusing to read or write it. Remove it and re-run." >&2
  exit 1
fi
if [ -d "$STATE_FILE" ]; then
  echo "Error: $STATE_FILE is a directory, not a regular file; refusing to read or write it. Remove it and re-run." >&2
  exit 1
fi
if [ -f "$STATE_FILE" ]; then
  # L2: `|| [ -n "$line" ]` processes a final line with no trailing newline (a hand
  # edit) - otherwise read returns non-zero at EOF-without-delimiter, the body never
  # runs for it, and the next write_state rewrites the ledger without it (erased).
  while IFS= read -r line || [ -n "$line" ]; do
    [ -z "$line" ] && continue
    case "$line" in
      session=*)
        # Legacy GLOBAL session counter (pre-M3): adopted as THIS project's on the
        # next write_state (R5). C3 (Codex Critical): the value feeds arithmetic, so
        # accept only a decimal count; anything else warns and leaves PRIOR_SESSION=0.
        sess="${line#session=}"
        if counter_ok "$sess"; then
          PRIOR_SESSION="$sess"
        else
          echo "warning: ignoring malformed .sync-state session: $sess" >&2
        fi
        ;;
      session:*)
        # Per-project session (M3): session:<projid>\t<N>. Mine sets PRIOR_SESSION;
        # another project's counter is retained verbatim, never consumed here.
        classify_rest "${line#session:}"
        if [ "$REC_SCOPE" = other ]; then RETAINED_LINES+=("$line"); continue; fi
        if counter_ok "$REC_BODY"; then
          PRIOR_SESSION="$REC_BODY"
        else
          echo "warning: ignoring malformed .sync-state session: $REC_BODY" >&2
        fi
        ;;
      never:*)
        classify_rest "${line#never:}"
        if [ "$REC_SCOPE" = other ]; then RETAINED_LINES+=("$line"); continue; fi
        path="$REC_BODY"
        state_path_ok "$path" || { echo "warning: ignoring malformed .sync-state key: $path" >&2; continue; }
        STATE_DECISIONS["$path"]="never"
        ;;
      defer:*)
        classify_rest "${line#defer:}"
        if [ "$REC_SCOPE" = other ]; then RETAINED_LINES+=("$line"); continue; fi
        path="${REC_BODY%:*}"
        ask_at="${REC_BODY##*:}"
        state_path_ok "$path" || { echo "warning: ignoring malformed .sync-state key: $path" >&2; continue; }
        # C3: ask_at feeds `[ "$CURRENT_SESSION" -lt "$ask_at" ]` (arithmetic), so
        # a non-decimal counter is malformed and could smuggle a subscript on
        # older bash; drop the whole defer record.
        counter_ok "$ask_at" || { echo "warning: ignoring malformed .sync-state key: $path" >&2; continue; }
        STATE_DECISIONS["$path"]="defer:$ask_at"
        ;;
      base:*)
        classify_rest "${line#base:}"
        if [ "$REC_SCOPE" = other ]; then
          RETAINED_LINES+=("$line")
          # Feed the other project's base blob sha into the bases ref (M3 + C1) so
          # gc cannot prune it; the last colon-field is the sha. L3: only a 40-hex sha
          # may enter the tree (update-index --index-info rejects an abbreviated one,
          # wedging write_state); the LINE is still retained verbatim above, so no
          # other-project record is lost.
          sha="${line##*:}"; [[ "$sha" =~ ^[0-9a-f]{40}$ ]] && RETAINED_BASE_SHAS+=("$sha")
          continue
        fi
        path="${REC_BODY%:*}"
        base_sha="${REC_BODY##*:}"
        state_path_ok "$path" || { echo "warning: ignoring malformed .sync-state key: $path" >&2; continue; }
        # L3: validate 40-hex at parse (mirror compute_base). An abbreviated or
        # non-hex base sha resolves via cat-file (base_blob_present passes) but
        # update-index --index-info rejects it, wedging every write_state; DROP it
        # (warn) so the run proceeds and --bootstrap-bases re-records a valid base
        # via its existing missing-base path (STATE_BASES unset -> compute_base).
        if [[ "$base_sha" =~ ^[0-9a-f]{40}$ ]]; then
          STATE_BASES["$path"]="$base_sha"
        else
          echo "warning: ignoring malformed .sync-state base sha (not 40-hex): $path" >&2
        fi
        ;;
      synced:*)
        classify_rest "${line#synced:}"
        if [ "$REC_SCOPE" = other ]; then RETAINED_LINES+=("$line"); continue; fi
        path="${REC_BODY%:*}"
        at_session="${REC_BODY##*:}"
        state_path_ok "$path" || { echo "warning: ignoring malformed .sync-state key: $path" >&2; continue; }
        STATE_DECISIONS["$path"]="synced:$at_session"
        ;;
      prune-never:*)
        # M2: a namespaced prune decision. Cannot collide with never:* above -
        # that pattern requires the line to START with never:, and this starts
        # with prune-never:.
        classify_rest "${line#prune-never:}"
        if [ "$REC_SCOPE" = other ]; then RETAINED_LINES+=("$line"); continue; fi
        path="$REC_BODY"
        state_path_ok "$path" || { echo "warning: ignoring malformed .sync-state key: $path" >&2; continue; }
        STATE_PRUNE_DECISIONS["$path"]="never"
        ;;
      prune-defer:*)
        classify_rest "${line#prune-defer:}"
        if [ "$REC_SCOPE" = other ]; then RETAINED_LINES+=("$line"); continue; fi
        path="${REC_BODY%:*}"
        ask_at="${REC_BODY##*:}"
        state_path_ok "$path" || { echo "warning: ignoring malformed .sync-state key: $path" >&2; continue; }
        counter_ok "$ask_at" || { echo "warning: ignoring malformed .sync-state key: $path" >&2; continue; }
        STATE_PRUNE_DECISIONS["$path"]="defer:$ask_at"
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
# Ceiling guard (ruling 3 + A1): both CURRENT_SESSION and the largest ask_at a defer
# could derive this run (CURRENT_SESSION + DEFER_SESSIONS) must stay below the
# counter ceiling, or the NEXT run's counter_ok would reject them and silently drop
# the ledger. Refuse at derivation - never roll over. Pin CURRENT_SESSION back to
# PRIOR so the EXIT trap persists the UNCHANGED session, then exit re-runnably. The
# guard is UNGATED (applies to bootstrap too, per lead ruling): a bootstrap at the
# ceiling refuses with the same Error and writes nothing, and the PRIOR pin holds.
if ! counter_ok "$CURRENT_SESSION" || ! counter_ok "$((CURRENT_SESSION + DEFER_SESSIONS))"; then
  echo "Error: session counter at the ceiling: next session $CURRENT_SESSION, a defer would reach ask_at $((CURRENT_SESSION + DEFER_SESSIONS)); both must stay below 900000000. Refusing to advance without rewriting .sync-state; clear it to reset the counter." >&2
  CURRENT_SESSION="$PRIOR_SESSION"
  exit 1
fi

# Resolve the project and hub trees (shared by bootstrap and the scan below).
PROJECT_CLAUDE="$PROJECT_ROOT/.claude/"
HUB_PLUGIN="$HUB_REPO/cultivation/marketplace/sam-cc-setup/"
HUB_PLUGIN_REL="cultivation/marketplace/sam-cc-setup/"

RSYNC_EXCLUDES=(
  --exclude=audit.log
  --exclude=.validation_passed
  --exclude=settings.local.json
  --exclude='*.local.*'
  # H6: never sync a nested .git (a vendored repo under .claude/). Slashless, so
  # it matches a .git file or dir at any depth and rsync does not descend into an
  # excluded dir, so its internals are excluded too. Does not match .gitignore/
  # .gitattributes (those are not named exactly ".git").
  --exclude=.git
)

# Helper: write current state back to disk.
write_state() {
  # C4 (Codex pass 2 Critical): return 1 on a genuine failure to persist the
  # ledger or the base ref, so the normal-path callers can abort BEFORE the
  # commit; a normal run returns 0. The EXIT-trap caller uses `|| true`.
  local rc=0 state_tmp=""
  # Codex pass 3 Critical: a predictable ${STATE_FILE}.tmp could be pre-planted
  # as a symlink and followed; mktemp gives an unpredictable name in the hub
  # root, and the rename onto .sync-state never follows a symlink at the target.
  if ! state_tmp=$(mktemp "$HUB_REPO/.sync-state.XXXXXX" 2>/dev/null); then
    echo "  warning: could not create a temp file for $STATE_FILE" >&2
    state_tmp=""
    rc=1
  fi
  # Explicit if/else, NOT `if ! group > tmp && mv` (that binds as
  # `(! group>tmp) && mv`, so mv never runs on the success path).
  # Item 5 (Codex p5 Critical): `mv -f "$tmp" "$STATE_FILE"` onto a DIRECTORY or a
  # SYMLINK-to-directory moves the temp INTO it (or through it) and returns 0 - no
  # readable ledger, yet a commit could proceed, and a symlink writes OUTSIDE the
  # hub. Refuse both shapes BEFORE the mv (rm temp, rc=1 so the normal path aborts
  # before the commit); after the mv, require a regular, non-symlink file (guards a
  # mid-run TOCTOU plant). The parse-time guard above already refuses a bad shape
  # present at start; this covers one appearing during the run.
  if [ -n "$state_tmp" ] && { [ -L "$STATE_FILE" ] || [ -d "$STATE_FILE" ]; }; then
    local shape=symlink
    [ -L "$STATE_FILE" ] || shape=directory
    echo "  Error: $STATE_FILE is a $shape, not a regular file; refusing to write the ledger" >&2
    rm -f "$state_tmp" 2>/dev/null || true
    rc=1
  elif [ -n "$state_tmp" ] && { echo "session:$PROJ_ID$TAB$CURRENT_SESSION"
    for p in "${!STATE_DECISIONS[@]}"; do
      local dec="${STATE_DECISIONS[$p]}"
      case "$dec" in
        never) echo "never:$PROJ_ID$TAB$p" ;;
        defer:*) echo "defer:$PROJ_ID$TAB$p:${dec#defer:}" ;;
        synced:*) echo "synced:$PROJ_ID$TAB$p:${dec#synced:}" ;;
      esac
    done
    for p in "${!STATE_BASES[@]}"; do
      echo "base:$PROJ_ID$TAB$p:${STATE_BASES[$p]}"
    done
    for p in "${!STATE_PRUNE_DECISIONS[@]}"; do
      local pdec="${STATE_PRUNE_DECISIONS[$p]}"
      case "$pdec" in
        never) echo "prune-never:$PROJ_ID$TAB$p" ;;
        defer:*) echo "prune-defer:$PROJ_ID$TAB$p:${pdec#defer:}" ;;
      esac
    done
    # M3: other projects' records, re-emitted byte-for-byte (never adopted or dropped).
    # `|| continue` (not `&& echo`) so the loop's exit status is 0 even when the
    # array is empty (the `:-` gives one empty iteration) - otherwise the command
    # group returns non-zero and write_state falsely reports a write failure.
    for rl in "${RETAINED_LINES[@]:-}"; do
      [ -n "$rl" ] || continue
      echo "$rl"
    done
     } > "$state_tmp" && mv -f "$state_tmp" "$STATE_FILE" \
       && [ -f "$STATE_FILE" ] && ! [ -L "$STATE_FILE" ]; then
    :   # state written and verified a regular, non-symlink file
  else
    [ -n "$state_tmp" ] && { echo "  warning: could not write $STATE_FILE" >&2; rm -f "$state_tmp" 2>/dev/null || true; }
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
  if [ -n "${STATE_BASES[*]+x}" ] || [ "${#RETAINED_BASE_SHAS[@]}" -gt 0 ]; then
    local base_index base_tree
    # A fresh, NON-existent index path: git creates it. An empty pre-created file
    # (e.g. from mktemp) is rejected as a corrupt index ("index file smaller than
    # expected"). WORKDIR is a private mktemp -d, so a fixed name is safe here.
    base_index="$WORKDIR/base-index"
    rm -f "$base_index"
    # Codex pass 3 High: a base whose blob is gone (stale or pruned sha) must
    # not enter the tree - a reachable tree with a missing blob fails git fsck.
    # The ledger line is kept; --bootstrap-bases re-records it.
    # M3: the tree entry is NAMED BY THE BLOB SHA, not by the path. Two projects
    # can hold DIFFERENT base blobs for the SAME path; keying by path would collide
    # in --index-info (one overwrites the other) and gc would prune the dropped
    # blob. A blob-sha name is TAB-free (never breaks the --index-info format) and
    # unique per distinct blob, so every project's base stays reachable. This
    # stages both this project's bases (STATE_BASES) and other projects' retained
    # base blobs (RETAINED_BASE_SHAS).
    if ! { for p in "${!STATE_BASES[@]}"; do
             base_blob_present "${STATE_BASES[$p]}" || continue
             printf '100644 %s\t%s\n' "${STATE_BASES[$p]}" "${STATE_BASES[$p]}"
           done
           for rsha in "${RETAINED_BASE_SHAS[@]:-}"; do
             [ -n "$rsha" ] || continue
             base_blob_present "$rsha" || continue
             printf '100644 %s\t%s\n' "$rsha" "$rsha"
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

# compute_base <rel>: write the PROJECT content of $1 into the hub object store and
# echo its validated 40-hex blob sha on stdout; return 1 (with an Error) on any
# failure - a hash-object error OR a non-40-hex result. Callers compute the base
# BEFORE install so a failure fails the item (Error + exit 1) instead of recording a
# synced: line with no merge base, which the next scan would resolve by a destructive
# overwrite (ruling 2 / A3, Codex pass-4 High). Content-addressed, so the value is
# the same whether computed before or after the file is installed.
# loam is a SHA-1 repository; a SHA-256 hub (64-hex) is out of scope (Codex M2, declined 2026-08-22).
compute_base() {
  local sha
  if ! sha=$(git -C "$HUB_REPO" hash-object -w "$PROJECT_CLAUDE$1" 2>/dev/null); then
    echo "  Error: hash-object failed for $1; no merge base recorded" >&2
    return 1
  fi
  if [[ "$sha" =~ ^[0-9a-f]{40}$ ]]; then
    printf '%s\n' "$sha"
    return 0
  fi
  echo "  Error: hash-object gave no valid sha for $1; no merge base recorded" >&2
  return 1
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

# candidate_ok <path>: reject a candidate that fails state_path_ok OR carries an
# rsync `\#ooo` control-char escape (three octal digits). Used at two capture points:
# the bootstrap find loop below (item 8, Codex p6) and the rsync categorize loop
# (item 6, Codex p5). rsync escapes a control char in an itemized name as `\#ooo`
# (both GNU and BSD), so an LF cannot split the itemize line but the captured string
# names no real file; a bootstrap `find -print0` name instead carries a REAL newline,
# which state_path_ok's `*$'\n'*` clause rejects. Defined here, above both loops.
candidate_ok() {
  local p="$1"
  state_path_ok "$p" || return 1
  case "$p" in
    *'\#'[0-7][0-7][0-7]*) return 1 ;;
  esac
  # H6: reject any path with a .git component (a nested repo's internals, or a
  # bare .git gitlink file) so it is never enumerated, installed, or based. The
  # /.../ wrap catches a leading (.git/...) or trailing (.../.git) component.
  case "/$p/" in
    */.git/*) return 1 ;;
  esac
  return 0
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

# 8b Item 2: enumerate only git-TRACKED project files. Both enumeration paths
# below walk the filesystem (rsync --dry-run over $PROJECT_CLAUDE, and the
# bootstrap `find`), so a project file that is not committed would be offered as
# an add / recorded as a base. The hub mirrors COMMITTED project state, so build
# the set of tracked paths (relative to the .claude tree) ONCE here and gate both
# loops on it.
#
# Why this is exactly "exclude gitignored" and CANNOT drop a legitimately-new
# uncommitted file: the :86 guard above already REFUSES the whole run when
# `git status --porcelain -- :(literal).claude ...` reports anything, and porcelain
# reports untracked files as `??` - but it OMITS ignored files. So the only
# not-tracked file that can ever reach these loops is a gitignored one; an
# untracked-non-ignored file has already aborted the run upstream. (Guarded by the
# tripwire test test_untracked_nonignored_refused.sh - if :86 is ever loosened,
# that test fails and this safety argument must be revisited.)
#
# CLAUDE_PATHSPEC is the RESOLVED, project-relative .claude prefix from
# resolve-claude (`.claude`, or a symlink target e.g. `seed/.claude`); using it
# (not literal `.claude`) makes ls-files list the REAL tracked files even when
# .claude is a symlink, and stripping "$CLAUDE_PATHSPEC/" yields the same rel form
# both loops produce (no leading slash, relative to the .claude tree). :(literal)
# per 8a R1 so a glob-y dir name is matched literally. ls-files -z is written to a
# temp file and read with `read -r -d ''` because command substitution cannot hold
# NUL. PROJECT_ROOT is a git toplevel (verified at :19), so this never runs against
# a non-repo; an ls-files failure fails CLOSED (pin the session to PRIOR so the
# EXIT trap does not advance the ledger, then exit) rather than enumerating blindly.
declare -A PROJECT_TRACKED
tracked_list="$WORKDIR/tracked.list"
if ! git -C "$PROJECT_ROOT" ls-files -z -- ":(literal)$CLAUDE_PATHSPEC" > "$tracked_list" 2>/dev/null; then
  echo "Error: could not list git-tracked files under $CLAUDE_PATHSPEC; refusing to enumerate untracked project files (re-runnable)." >&2
  CURRENT_SESSION="$PRIOR_SESSION"
  exit 1
fi
while IFS= read -r -d '' _tf; do
  PROJECT_TRACKED["${_tf#"$CLAUDE_PATHSPEC/"}"]=1
done < "$tracked_list"

# project_tracked <rel>: is a candidate path (relative to the .claude tree, no
# leading slash - the form both enumeration loops produce) a COMMITTED project
# file? Fail closed: an untracked/gitignored path is not in the set, so not offered.
project_tracked() {
  [ -n "${PROJECT_TRACKED[$1]:-}" ]
}

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
  # M8-a: a missing project .claude/ (usually the wrong cwd) must abort
  # re-runnably, not fail open with "0 bases recorded" plus a written state file.
  # Mirror the compute_base failure path: pin the session to PRIOR so the EXIT
  # trap does not advance the ledger, then exit non-zero.
  [ -d "$PROJECT_CLAUDE" ] || {
    echo "Error: project .claude tree not found at $PROJECT_CLAUDE; nothing to bootstrap (wrong cwd?)." >&2
    CURRENT_SESSION="$PRIOR_SESSION"
    exit 1
  }
  bs_recorded=0
  bs_present=0
  bs_differing=()
  bs_skipped_untracked=0   # 8b Item 2: gitignored project files not based
  # M8-b: enumerate to a temp file so find's exit status is checkable - a process
  # substitution `done < <(find ...)` hides it, so an unreadable subtree (or any
  # other find error) yielded a partial bootstrap that exited 0. Abort
  # re-runnably instead. -name .git -prune keeps H6 (never walk a nested .git).
  bootstrap_list="$WORKDIR/bootstrap.list"
  if ! find "$PROJECT_CLAUDE" -name .git -prune -o -type f -print0 > "$bootstrap_list"; then
    echo "Error: enumerating $PROJECT_CLAUDE failed (unreadable subtree?); bootstrap aborted (re-runnable)" >&2
    CURRENT_SESSION="$PRIOR_SESSION"
    exit 1
  fi
  while IFS= read -r -d '' pf; do
    rel="${pf#"$PROJECT_CLAUDE"}"
    # Item 8 (Codex p6 High): validate the rel read from `find -print0` before use -
    # a newline-named file is caught by state_path_ok's `*$'\n'*` clause in candidate_ok.
    candidate_ok "$rel" || { echo "warning: ignoring unsafe candidate path: $rel" >&2; continue; }
    # 8b Item 2: base only git-tracked project files (a gitignored file present in
    # both trees would otherwise get a base). Counted for one post-loop summary,
    # never per-file (bootstrap is the bulk unattended path - a per-file line
    # would be spam, but a swallowed skip is exactly 8a's failure class).
    project_tracked "$rel" || { bs_skipped_untracked=$((bs_skipped_untracked + 1)); continue; }
    bootstrap_excluded "$rel" && continue
    [ -f "$HUB_PLUGIN$rel" ] || continue
    # A recorded base whose blob is still present counts as already present; a
    # base whose blob is missing (pruned by gc, or a stale/crafted sha) is
    # RE-RECORDED so bootstrap repairs it instead of trusting the dead value (C1).
    if [ -n "${STATE_BASES[$rel]:-}" ] && base_blob_present "${STATE_BASES[$rel]}"; then
      bs_present=$((bs_present + 1))
      continue
    fi
    # M1: an active synced:/defer: decision is a pending user choice; recording a
    # base here would cancel it (the next scan sees project==base and suppresses
    # the offer forever). Skip + warn, leaving the decision and its route intact.
    # Decision-check ONLY (no content gate): a hub-ahead generalization and a
    # project-ahead drift are content-indistinguishable, so a cmp gate would break
    # the designed generalization bootstrap (lead ruling REVISED, group 8). This
    # runs before compute_base so it blocks both a fresh record and the C1
    # dead-base re-record.
    case "${STATE_DECISIONS[$rel]:-}" in
      synced:*|defer:*)
        echo "  bootstrap skipped ($rel: an active ${STATE_DECISIONS[$rel]%%:*} decision exists; sync it via a scan)" >&2
        continue
        ;;
    esac
    if bsha=$(compute_base "$rel"); then
      STATE_BASES["$rel"]="$bsha"
      bs_recorded=$((bs_recorded + 1))
      # Warning (messaging only - never gates the record): a based path whose hub
      # and project content differ is now treated as intentional hub-side state.
      # Fires on both the fresh record and the C1 dead-base re-record (both reach
      # here). Collected now, named in one loud post-loop summary.
      cmp -s "$PROJECT_CLAUDE$rel" "$HUB_PLUGIN$rel" || bs_differing+=("$rel")
    else
      # A3: fail closed - never count the failed path; pin CURRENT_SESSION to PRIOR
      # so the EXIT trap does not advance the ledger, then exit re-runnably.
      echo "Error: could not record a base for $rel; bootstrap aborted (re-runnable)" >&2
      CURRENT_SESSION="$PRIOR_SESSION"
      exit 1
    fi
  done < "$bootstrap_list"
  CURRENT_SESSION="$PRIOR_SESSION"   # never bump the session on a bootstrap
  write_state || { echo "Error: could not persist .sync-state or refs/agent-sync/bases; hub left uncommitted" >&2; exit 1; }
  if [ "${#bs_differing[@]}" -gt 0 ]; then
    echo "warning: bootstrap recorded a base for ${#bs_differing[@]} path(s) whose hub and project content DIFFER:" >&2
    for dp in "${bs_differing[@]}"; do echo "  differs: $dp" >&2; done
    echo "  These differences are now treated as intentional hub-side state. If a path carries an un-synced project improvement, resolve it by hand (sync it via a scan) before relying on the merge." >&2
  fi
  # 8b Item 2: one stderr summary line for gitignored files skipped by the
  # tracked-only filter. N>0 only, silent at N==0 so bootstrap's quiet-success
  # output is byte-identical for the common case (no bootstrap test churn).
  [ "$bs_skipped_untracked" -gt 0 ] \
    && echo "bootstrap: $bs_skipped_untracked gitignored project file(s) not based (not git-tracked; track it in the project to sync)" >&2
  echo "bootstrap: $bs_recorded bases recorded, $bs_present already present"
  exit 0
fi

# reject_symlink_path <rel>: C5 (Codex pass 2 Critical) + item 1 (Codex pass 4
# Critical). install_file's mkdir -p, mktemp and cp - and the normal scan's
# `mkdir -p "$HUB_PLUGIN"` below - would FOLLOW a committed hub symlink ancestor
# (e.g. `cultivation -> ../outside`) and write OUTSIDE the plugin tree. Walk every
# cumulative component of $rel under HUB_PLUGIN and refuse if any EXISTING one is
# a symlink (`[ -L ]` tests the link itself, never follows it). A fresh path,
# whose components do not exist yet, passes cleanly. Defined here, above the
# plugin-root mkdir, so bash has bound it before the first call (functions bind at
# definition time); install_file and the prune loop below call it too.
reject_symlink_path() {
  # Walk from the HUB ROOT (Codex pass 3 Critical): cultivation/, marketplace/
  # and sam-cc-setup/ themselves could be symlinks, not only the components
  # below the plugin root. The message names the component relative to the
  # plugin root when it lies below it.
  local rel="$1" prefix="" remainder="${HUB_PLUGIN_REL}$1" component shown
  while [ -n "$remainder" ]; do
    component="${remainder%%/*}"
    if [ "$component" = "$remainder" ]; then remainder=""; else remainder="${remainder#*/}"; fi
    [ -z "$component" ] && continue
    prefix="${prefix:+$prefix/}$component"
    if [ -L "$HUB_REPO/$prefix" ]; then
      shown="${prefix#"$HUB_PLUGIN_REL"}"
      echo "Error: install failed for $rel (symlink in destination path: $shown)" >&2
      exit 1
    fi
  done
}

# The normal scan may create the hub plugin dir on a first sync; bootstrap must
# not (see above), so the mkdir lives below the bootstrap exit path.
# Item 1 (Codex pass 4 Critical): check the plugin-root ancestry BEFORE the mkdir,
# or a symlinked ancestor redirects the dir creation outside the hub.
# TOCTOU (group 12): create the plugin root through the no-follow helper too, so a
# component turning into a symlink (e.g. cultivation -> ../outside) between the
# reject_symlink_path check and the mkdir cannot redirect the creation outside.
reject_symlink_path ""   # defense-in-depth pre-check (retained per critic)
if ! python3 "$SAFE_IO" mkdir "$HUB_REPO" "$HUB_PLUGIN_REL"; then
  echo "Error: could not create the hub plugin directory safely." >&2
  exit 1
fi

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

# M2: the prune analogue of should_prompt, reading the SEPARATE prune namespace so
# a prune defer/never never touches the sync decision slot. Returns 0 (offer the
# prune) or 1 (suppressed by a prior prune defer/never).
prune_should_prompt() {
  local path="$1"
  local prior="${STATE_PRUNE_DECISIONS[$path]:-}"
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
# hub - the hub is a curated subset, and an additive project→hub sync is
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

# H3: a hub-gitignored approved path is refused by `git add` at commit time, and
# under set -e that aborts the WHOLE batch - no file commits, the non-ignored ones
# are left staged, and the next scan wedges on the C2 staged-index guard. Detect
# such a path here, BEFORE install, and skip it. The predicate is
# check-ignore-matched AND not already tracked: `git add` never refuses a TRACKED
# file that matches an ignore rule, so only an untracked one is the hazard.
# check-ignore takes a LITERAL pathname (it rejects the :(literal) magic with
# rc=128 and does not glob its arg), so it gets the plain hub-relpath; only rc==0
# counts as matched (rc=1 not-ignored, rc=128 error both fail safe as no-skip).
# The tracked-check reuses the :(literal) prefix used elsewhere.
SKIPPED_HUBIGNORE=0
hub_ignored_untracked() {
  local rel="cultivation/marketplace/sam-cc-setup/$1"
  git -C "$HUB_REPO" check-ignore -q -- "$rel" 2>/dev/null || return 1
  git -C "$HUB_REPO" ls-files --error-unmatch -- ":(literal)$rel" >/dev/null 2>&1 && return 1
  return 0
}
# Returns 0 (skip this path) when the hub would refuse it, printing the reason
# unconditionally (a manifestless consumer still needs the preflight visible).
hub_ignore_skip() {
  hub_ignored_untracked "$1" || return 1
  echo "  skipped (matches a hub .gitignore rule; git add -f in the hub or adjust the hub .gitignore, then re-run): $1" >&2
  SKIPPED_HUBIGNORE=$((SKIPPED_HUBIGNORE+1))
  return 0
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
  [ -n "${_prune_seen[$p]:-}" ] && return 0
  _prune_seen[$p]=1
  # consider_prune is a COLLECTOR (appends to PRUNE_CANDIDATES), not a predicate:
  # every early exit returns 0 so a "no candidate" outcome never propagates a
  # non-zero status that set -e would treat as an abort in the enumeration loop
  # below. (M2 exposed this: a suppressed-but-still-synced path is now enumerated
  # for the first time, so prune_should_prompt's `|| return` must not leak 1.)
  [ -f "$HUB_PLUGIN$p" ] || return 0        # nothing in the hub to prune
  [ -f "$PROJECT_CLAUDE$p" ] && return 0     # M6: a regular project FILE (not a dir) shields the hub file
  prune_should_prompt "$p" || return 0       # M2: suppressed by a prior PRUNE defer/never
  # H2 (Codex High): a folded prune must carry an explicit 'travels' verdict,
  # matching bin/agent-sync-prune.sh's manifest gate. A retired stays/rework/
  # unclassified path - or ANY path when there is no manifest at all - is
  # withheld (fail closed), so a curated hub-only generalization is never
  # offered for deletion. Not counted in the SKIPPED_* adds/changes tallies.
  local prune_verdict
  prune_verdict="$(manifest_verdict "$p")"
  if [ "$prune_verdict" != travels ]; then
    echo "  prune withheld (manifest verdict '${prune_verdict:-unclassified}', not travels): $p" >&2
    return 0
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

# M5: also keep attribute-only mode lines (`.f...p...`: a content-identical file
# whose permissions differ). Both openrsync and GNU rsync emit these for a
# perms-only diff; dropping them left a hub hook dead at 644 AND made the
# early-exit below spuriously report "No changes" when only a mode differed.
CHANGES=$(echo "$RSYNC_DIFF" | grep -E '^(>f|<f|cf|hf)|^\.f[^ ]*p' || true)

# Exit early only when there is genuinely nothing to do: no adds/changes AND no
# retired files to prune. The message and behavior here are unchanged.
if [ -z "$CHANGES" ] && [ "${#PRUNE_CANDIDATES[@]}" -eq 0 ]; then
  echo "No changes - hub is in sync with project."
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
# H4 (ruling R4): parse each itemize line byte-wise. macOS openrsync escapes bytes
# 0x80-0x9F as \#ooo mid-UTF-8, so an itemize line for a non-ASCII name is invalid
# UTF-8; under a UTF-8 locale bash [[ =~ ]] fails BOTH regexes and the line is
# dropped with no output - the file is silently unsyncable on the Mac while it
# syncs on Linux. match_itemize sets a local LC_ALL=C so the match is byte-wise
# (restored on return, so candidate_ok below runs under the normal locale and its
# \#ooo reject still fires); it returns MATCH_KIND (add/change/none) + MATCH_PATH.
match_itemize() {
  local LC_ALL=C line="$1"
  if [[ "$line" =~ ^\>f\++\ (.*)$ ]]; then
    MATCH_KIND=add; MATCH_PATH="${BASH_REMATCH[1]}"
  elif [[ "$line" =~ ^\>f[^+\ ][^\ ]*\ (.*)$ ]]; then
    MATCH_KIND=change; MATCH_PATH="${BASH_REMATCH[1]}"
  elif [[ "$line" =~ ^\.f[^\ ]*p[^\ ]*\ (.*)$ ]]; then
    # M5: a `.f` (content-identical) line carrying a `p` in the attribute field is
    # a mode-only change. Width-independent (openrsync's short field and GNU's
    # YXcstpoguax both work): the `p` is matched anywhere in the non-space attr
    # run, which stops at the space before the path.
    MATCH_KIND=mode; MATCH_PATH="${BASH_REMATCH[1]}"
  else
    MATCH_KIND=none; MATCH_PATH=""
  fi
}

ADDED_PATHS=()
CHANGED_PATHS=()
MODE_PATHS=()
# 8b Item 2: gitignored project files dropped by the tracked-only filter. The
# unsafe-path warning still takes precedence (a bad path is reported, not counted
# here); a safe-but-untracked path is counted for one post-loop summary.
skipped_untracked=0
while IFS= read -r line; do
  [ -z "$line" ] && continue
  match_itemize "$line"
  case "$MATCH_KIND" in
    add)
      if ! candidate_ok "$MATCH_PATH"; then echo "warning: ignoring unsafe candidate path: $MATCH_PATH" >&2
      elif ! project_tracked "$MATCH_PATH"; then skipped_untracked=$((skipped_untracked + 1))
      else ADDED_PATHS+=("$MATCH_PATH"); fi ;;
    change)
      if ! candidate_ok "$MATCH_PATH"; then echo "warning: ignoring unsafe candidate path: $MATCH_PATH" >&2
      elif ! project_tracked "$MATCH_PATH"; then skipped_untracked=$((skipped_untracked + 1))
      else CHANGED_PATHS+=("$MATCH_PATH"); fi ;;
    mode)
      # M5: a mode-only change (content identical, permissions differ).
      if ! candidate_ok "$MATCH_PATH"; then echo "warning: ignoring unsafe candidate path: $MATCH_PATH" >&2
      elif ! project_tracked "$MATCH_PATH"; then skipped_untracked=$((skipped_untracked + 1))
      else MODE_PATHS+=("$MATCH_PATH"); fi ;;
    *)
      # R4 floor: a transfer line this scan cannot categorize (an unexpected
      # itemize shape, or a <f/cf/hf type not handled) is surfaced, never dropped.
      echo "warning: unparsed rsync itemize line (not synced; report if a real file is missing): $line" >&2 ;;
  esac
done <<< "$CHANGES"
# 8b Item 2: one stderr summary line, never per-file (per-path here would be spam;
# 8a's failure history is swallowed skips, so it must stay visible). N>0 only, and
# silent at N==0 - this runs after the "No changes" early-exit above, so the
# no-change path is unaffected either way, but silence-at-zero keeps a
# changes-present run that skips nothing byte-identical too.
[ "$skipped_untracked" -gt 0 ] \
  && echo "Skipped $skipped_untracked gitignored project file(s) (not git-tracked; track it in the project to sync)." >&2

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
  hub_ignore_skip "$path" && continue   # H3: refuse a hub-gitignored path before install
  should_prompt "$path" && PROMPT_ADDS+=("$path")
done
PROMPT_CHANGES=()
for path in "${CHANGED_PATHS[@]:-}"; do
  [ -z "${path:-}" ] && continue
  manifest_allows "$path" || continue
  deps_satisfied "$path" || continue
  hub_ignore_skip "$path" && continue   # H3: refuse a hub-gitignored path before install
  should_prompt "$path" || continue
  project_unchanged_since_base "$path" && continue   # Critical-1: no-op, suppress
  PROMPT_CHANGES+=("$path")
done
# M5: mode-only changes are gated like PROMPT_CHANGES EXCEPT project_unchanged_since_base
# - a mode-only change is content-identical by definition, so that suppression would
# drop every one. should_prompt READS the sync slot (a content never:/defer: suppresses
# the mode too, intentionally) but this pipeline NEVER writes it, so no M2 collision.
PROMPT_MODES=()
for path in "${MODE_PATHS[@]:-}"; do
  [ -z "${path:-}" ] && continue
  manifest_allows "$path" || continue
  deps_satisfied "$path" || continue
  hub_ignore_skip "$path" && continue
  should_prompt "$path" || continue
  PROMPT_MODES+=("$path")
done
if [ -f "$MANIFEST_TSV" ]; then
  echo "  manifest guard: $SKIPPED_STAYS 'stays', $SKIPPED_REWORK 'rework' (generalize first), $SKIPPED_UNKNOWN unclassified, $SKIPPED_DEPS dep-withheld, $SKIPPED_HUBIGNORE hub-gitignored paths"
fi

echo "Sync from $PROJ_NAME (session $CURRENT_SESSION):"
echo "  ${#PROMPT_ADDS[@]} new files to ask about (${#ADDED_PATHS[@]} total - others suppressed by prior decisions)"
echo "  ${#PROMPT_CHANGES[@]} changed files to ask about (${#CHANGED_PATHS[@]} total - others suppressed by prior decisions)"
echo "  ${#PROMPT_MODES[@]} mode-only changes to ask about (${#MODE_PATHS[@]} total - others suppressed by prior decisions)"

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
        # No-op base advance: on a compute failure (A3) warn and record nothing, so
        # the next scan simply re-offers the path (nothing was installed here).
        if nb=$(compute_base "$path"); then
          STATE_BASES["$path"]="$nb"
        else
          echo "  warning: base not advanced for $path; it will be re-offered next scan" >&2
        fi
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
      # git merge-file returns 255 for two distinct reasons: an operational error
      # (an unreadable input) OR binary inputs it cannot three-way. M4: a binary
      # asset with a base record was skipped forever here. Distinguish the two with
      # AFFIRMATIVE binary evidence, not mere readability - a readable non-binary
      # 255 must stay a safe skip (High 2, Codex), so the overwrite needs positive
      # proof. Readability gates FIRST so grep never runs on an unreadable file
      # (grep -Iq exits 2 there, which the `!` would misread as "binary").
      handled=1
      rm -f "$merged_tmp"
      if [ -r "$HUB_PLUGIN$path" ] && [ -r "$PROJECT_CLAUDE$path" ] \
         && { ! LC_ALL=C grep -Iq . "$HUB_PLUGIN$path" || ! LC_ALL=C grep -Iq . "$PROJECT_CLAUDE$path"; }; then
        # Binary: no line merge exists, but the update is still deliverable. Fall
        # through to the legacy overwrite prompt (handled=0), NOT the conflict
        # branch below (whose diff would dump binary). On y the overwrite installs
        # and compute_base re-records the base per R2.
        printf 'Binary %s: cannot three-way merge; offering a full overwrite\n' "$path" >&2
        handled=0
      else
        # Operational error (High 2, Codex): an unreadable input (or an unexpected
        # readable-but-text 255). NOT a content conflict; never offer a destructive
        # overwrite. Skip safely. Message kept BYTE-IDENTICAL - test_merge_error_skips
        # asserts this exact string.
        printf 'Merge error %s: git merge-file failed (exit %s); skipped\n' "$path" "$mrc" >&2
        continue
      fi
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

# M5: mode-only changes. Content is identical, so there is no merge/overwrite - a
# plain y/N (default N) that records NOTHING (advisor8a option a: writing a
# defer/never here would reintroduce the M2 sync-slot collision this ticket just
# fixed). A declined mode change simply re-offers next scan.
APPROVED_MODES=()
for path in "${PROMPT_MODES[@]:-}"; do
  [ -z "${path:-}" ] && continue
  pmode=$(stat -c '%a' "$PROJECT_CLAUDE$path" 2>/dev/null \
    || stat -f '%Lp' "$PROJECT_CLAUDE$path" 2>/dev/null || echo "")
  hmode=$(stat -c '%a' "$HUB_PLUGIN$path" 2>/dev/null \
    || stat -f '%Lp' "$HUB_PLUGIN$path" 2>/dev/null || echo "")
  printf "Sync mode of %s to hub (%s -> %s)? [y/N] " "$path" "$hmode" "$pmode" >&2
  read -r mresp || mresp=""
  case "$mresp" in
    y|Y|yes|YES) APPROVED_MODES+=("$path") ;;
  esac
done

# R6 prune fold-in: offer to delete each retired hub file (project source gone).
# Reads from STDIN like the other prompts (prune.sh reads /dev/tty, which is why
# it cannot be tested and is not reused verbatim). Only the y/d/n DECISION is
# collected here; the git rm is applied later, after a preflight, so a mid-loop
# failure cannot leave some deletions staged with their records still present
# (High 3, Codex). M2: d/n record into the PRUNE namespace (STATE_PRUNE_DECISIONS),
# never the sync slot, so a kept/deferred prune cannot suppress a later sync of the
# same path and a base-less synced record keeps its route into prune candidacy.
PRUNE_APPROVED=()
for p in "${PRUNE_CANDIDATES[@]:-}"; do
  [ -z "${p:-}" ] && continue
  printf "Delete %s from hub? [y=delete now / d=defer (default) / n=never] " "$p" >&2
  read -r presp || presp=""
  case "$presp" in
    y|Y|yes|YES) PRUNE_APPROVED+=("$p") ;;
    n|N|never|NEVER) STATE_PRUNE_DECISIONS["$p"]="never" ;;
    *) STATE_PRUNE_DECISIONS["$p"]="defer:$((CURRENT_SESSION + DEFER_SESSIONS))" ;;
  esac
done

# CX-3 (Codex round 1): refuse an approved path whose hub copy carries PRE-SCAN
# uncommitted edits. If the user continued past the global dirty-hub warning
# (:100), installing over that WIP and then rolling back on decline via
# rollback_path's `git checkout HEAD` would DESTROY the pre-scan WIP while the
# decline message claims "hub restored". Drop such a path HERE - after every
# approval prompt and before anything touches the hub - so it never enters the
# install loops, the rollback set, the commit set, TOTAL_APPROVED, or PENDING_*.
# Mirrors the group-5 modified-prune skip (the prune loop keeps its own guard at
# the tracked-prune branch); this also closes the group-5-noted clobber-on-commit.
# The C2 guard (:89) guarantees a clean index, so unstaged edits are the only
# possible dirtiness. APPROVED_ADDS are NOT filtered: an add's hub path is absent
# (else rsync classifies it a change/mode), so it is always clean and its rollback
# is an rm of the just-installed file - no pre-existing WIP to lose.
drop_dirty_approved() {   # $1 = name of an approved-path array; drop dirty-hub paths in place
  local -n _arr="$1"
  local _kept=() _p
  for _p in "${_arr[@]}"; do
    [ -z "$_p" ] && continue
    if ! git -C "$HUB_REPO" diff --quiet -- ":(literal)${HUB_PLUGIN_REL}$_p"; then
      echo "  skipped ($_p has uncommitted edits in the hub - commit or discard them, then re-run)" >&2
      if [ -n "${MERGED_TMP[$_p]:-}" ]; then rm -f "${MERGED_TMP[$_p]}"; unset 'MERGED_TMP[$_p]'; fi
      continue
    fi
    # Round-2: `git diff` ignores UNTRACKED files, so an existing untracked hub
    # copy at this path is pre-scan work the diff check cannot see - installing
    # over it and later rolling back (checkout misses it; the HEAD-absent branch
    # unlinks it) would destroy it. Refuse it the same way.
    if ! git -C "$HUB_REPO" ls-files --error-unmatch -- ":(literal)${HUB_PLUGIN_REL}$_p" >/dev/null 2>&1 \
       && [ -e "$HUB_PLUGIN$_p" ]; then
      echo "  skipped ($_p exists UNTRACKED in the hub - commit or remove it, then re-run)" >&2
      if [ -n "${MERGED_TMP[$_p]:-}" ]; then rm -f "${MERGED_TMP[$_p]}"; unset 'MERGED_TMP[$_p]'; fi
      continue
    fi
    _kept+=("$_p")
  done
  _arr=("${_kept[@]}")
}
drop_dirty_approved APPROVED_CHANGES
drop_dirty_approved MERGED_PATHS
drop_dirty_approved APPROVED_MODES

TOTAL_APPROVED=$(( ${#APPROVED_ADDS[@]} + ${#APPROVED_CHANGES[@]} + ${#MERGED_PATHS[@]} + ${#APPROVED_MODES[@]} + ${#PRUNE_APPROVED[@]} ))
if [ "$TOTAL_APPROVED" -eq 0 ]; then
  # Persist defer/never decisions and any no-op base advances, then stop.
  write_state || { echo "Error: could not persist .sync-state or refs/agent-sync/bases; hub left uncommitted" >&2; exit 1; }
  echo "Nothing approved - exiting."
  exit 0
fi

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
  local src="$1" dst="$2" rel="$3"
  reject_symlink_path "$rel"   # C5 defense-in-depth pre-check (retained per critic)
  # H4 (Codex High): refuse to install over a directory (defense-in-depth; the
  # helper also refuses this atomically).
  if [ -d "$dst" ]; then
    echo "Error: install failed for $rel (destination is a directory)" >&2
    exit 1
  fi
  # TOCTOU (group 12): the create+write goes through the no-follow helper - it
  # descends each hub component with openat(O_NOFOLLOW), refusing any symlink, then
  # writes a private temp and renames it through the final dir fd. This CLOSES the
  # check-then-act race reject_symlink_path alone cannot (walkthrough OD-10c). It
  # preserves the source mode (cp -p semantics) and leaves no stray temp on failure.
  # The HUB_REPO-relative path is HUB_PLUGIN_REL + rel (dst == HUB_REPO/that).
  if ! python3 "$SAFE_IO" install "$HUB_REPO" "$HUB_PLUGIN_REL$rel" "$src"; then
    echo "Error: install failed for $rel" >&2
    exit 1
  fi
}

# 7. Apply approved adds + overwrite-changes, one file at a time.
NONEMPTY=()
for p in "${APPROVED_ADDS[@]:-}" "${APPROVED_CHANGES[@]:-}"; do
  [ -n "$p" ] && NONEMPTY+=("$p")
done

# H2 (group 3, pending-quarantine - lead A1): prune git-rms and installs happen
# now so the commit prompt shows a real diff, but the ledger records they imply
# are held in PENDING_* and applied to STATE only AFTER the hub commit succeeds.
# A declined commit rolls the hub back and leaves STATE untouched, so the ledger
# is byte-identical for the affected paths and the next scan re-offers them. This
# supersedes the former per-item-record rationale: a mid-batch CRASH (not a
# decline) now leaves installed-but-unrecorded files, surfaced by the dirty-hub
# warning and healed by --bootstrap-bases. Bootstrap and the merge no-op base
# advance stay exempt (state-only by design) and write STATE_BASES directly.
declare -A PENDING_SYNCED PENDING_BASES PENDING_PRUNE_UNSET

# High 3 / H5 / M6 (group 5): apply approved prune deletions BEFORE the installs,
# so a git rm that empties a hub directory frees the path for a file install there
# (M6 dir->file), and a non-clean hub copy is handled before any install runs.
# Three cases:
#   - clean tracked copy: git rm (staged); the record erasure is quarantined in
#     PENDING_PRUNE_UNSET and applied to STATE only after the commit succeeds (H2);
#     rolled back on decline.
#   - modified tracked copy (unstaged local edits): REFUSE and warn, keep it (lead
#     R2(i)). git rm would crash "local modifications" under set -e, and a forced
#     rm would let the decline rollback (checkout HEAD) discard the WIP. Re-offered
#     until the user resolves the hub WIP. Not staged, not recorded.
#   - untracked copy (a stale ledger record with no committed hub blob): rm the
#     leftover and drop its ledger record NOW (state-only, R2(i) amendment) - an
#     untracked rm stages nothing so it can never reach a commit, and quarantining
#     it would strand the cleanup at the "nothing to commit" exit. Kept even on a
#     declined batch; the decline message enumerates these.
PRUNED_PATHS=()
UNTRACKED_PRUNED=()
for p in "${PRUNE_APPROVED[@]:-}"; do
  [ -z "${p:-}" ] && continue
  # H1 second line of defense: re-check the state key before the destructive rm.
  state_path_ok "$p" || { echo "  prune skipped (malformed state key): $p" >&2; continue; }
  reject_symlink_path "$p"   # C5: no symlink ancestor may redirect the git rm
  hub_rel="cultivation/marketplace/sam-cc-setup/$p"
  # H1: :(literal) on every ledger-derived pathspec so a glob metachar in the name
  # (a[1].md) cannot wildmatch a sibling into the ls-files match, the diff check,
  # or the git rm. (`-c core.literalPathspecs` is not a real key; the magic prefix
  # is the fix.)
  if git -C "$HUB_REPO" ls-files --error-unmatch -- ":(literal)$hub_rel" >/dev/null 2>&1; then
    # Tracked. H5: refuse a copy with unstaged local edits. The C2 guard (:75)
    # guarantees a clean index at start, so a non-clean git diff here means
    # unstaged local modifications; git rm would crash and a forced rm would let a
    # declined rollback discard the WIP. Skip per-path (no staged residue); the
    # prune re-offers until the user resolves the hub WIP.
    if ! git -C "$HUB_REPO" diff --quiet -- ":(literal)$hub_rel"; then
      echo "  prune skipped ($p has local edits in the hub - commit or discard them, then re-run)" >&2
      continue
    fi
    git -C "$HUB_REPO" rm -r --quiet -- ":(literal)$hub_rel"
    PENDING_PRUNE_UNSET["$p"]=1   # H2: erase the record only after the commit succeeds
    PRUNED_PATHS+=("$p")
  else
    # Untracked hub copy (H5 + R2(i) amendment): rm the leftover and clear its
    # stale ledger record immediately (state-only). Persisted by write_state below;
    # kept even on a declined batch (nothing committed to roll back).
    # CX-4: no-follow removal via the helper. Round-2: clear the record and report
    # the prune ONLY on a successful unlink - clearing on failure would leave the
    # file in place with its only route into prune candidacy erased, so the same
    # leftover could never be offered again.
    if python3 "$SAFE_IO" unlink "$HUB_REPO" "$HUB_PLUGIN_REL$p"; then
      unset 'STATE_DECISIONS[$p]'
      unset 'STATE_BASES[$p]'
      UNTRACKED_PRUNED+=("$p")
      echo "  pruned untracked hub copy: removed $p and cleared its stale ledger record" >&2
    else
      echo "  warning: could not remove untracked hub copy $p (left in place; ledger record kept so it re-offers)" >&2
    fi
  fi
done

for p in "${NONEMPTY[@]:-}"; do
  [ -z "${p:-}" ] && continue
  # Compute the base BEFORE install (ruling 2): a hash-object failure fails the item
  # here, so no synced: line is ever written without a matching base:.
  if ! base_sha=$(compute_base "$p"); then
    echo "Error: aborting before install of $p (no merge base)" >&2
    exit 1
  fi
  install_file "$PROJECT_CLAUDE$p" "$HUB_PLUGIN$p" "$p"
  # Quarantine synced:/base: (H2); promoted into STATE only after the commit succeeds.
  PENDING_SYNCED["$p"]="$CURRENT_SESSION"
  PENDING_BASES["$p"]="$base_sha"
done

# Merged results are installed via install_file too (never rsync, which would
# re-overwrite the hub copy with the raw project file and discard the merge).
# install_file's cp -p would otherwise carry the mktemp temp's 0600 mode, so
# first match the merged result's mode to the PROJECT file's (portable across
# BSD/GNU stat). Record each right after its own install succeeds.
for p in "${MERGED_PATHS[@]:-}"; do
  [ -z "${p:-}" ] && continue
  # Compute the base BEFORE install (ruling 2); compute_base hashes the PROJECT
  # blob, the same base value as the plain install path.
  if ! base_sha=$(compute_base "$p"); then
    echo "Error: aborting before install of merged $p (no merge base)" >&2
    exit 1
  fi
  # GNU stat treats -f as --file-system (it prints a multi-line dump, not the
  # mode), so -f must run AFTER -c; BSD stat has no -c and falls through to -f.
  merged_mode=$(stat -c '%a' "$PROJECT_CLAUDE$p" 2>/dev/null \
    || stat -f '%Lp' "$PROJECT_CLAUDE$p" 2>/dev/null || echo 644)
  chmod "$merged_mode" "${MERGED_TMP[$p]}" 2>/dev/null || true
  install_file "${MERGED_TMP[$p]}" "$HUB_PLUGIN$p" "$p"
  PENDING_SYNCED["$p"]="$CURRENT_SESSION"   # H2: promoted post-commit
  PENDING_BASES["$p"]="$base_sha"
  rm -f "${MERGED_TMP[$p]}"
done

# M5: apply approved mode-only changes - the content is identical, so chmod the
# hub copy to the project's mode (portable stat, the merged-mode idiom above). No
# base/synced record: content is unchanged, git tracks the mode, and the next
# scan sees hub mode == project mode. Staged/rolled-back/counted below alongside
# the other approved actions; git checkout HEAD on decline restores the old mode.
_kept_modes=()
for p in "${APPROVED_MODES[@]:-}"; do
  [ -z "${p:-}" ] && continue
  reject_symlink_path "$p"   # C5: no symlink ancestor may redirect the chmod
  pmode=$(stat -c '%a' "$PROJECT_CLAUDE$p" 2>/dev/null \
    || stat -f '%Lp' "$PROJECT_CLAUDE$p" 2>/dev/null || echo "")
  # CX-4: no-follow chmod via the helper - a component swapped to a symlink after
  # reject_symlink_path must not let chmod follow it and change an outside file.
  # Round 2: a refused/failed chmod DROPS the path from the approved set - it must
  # not be staged (a raced replacement could be swept in recursively) or rolled
  # back; the mode difference simply re-offers on the next scan.
  if [ -n "$pmode" ] && python3 "$SAFE_IO" chmod "$HUB_REPO" "$HUB_PLUGIN_REL$p" "$pmode"; then
    _kept_modes+=("$p")
  else
    echo "  skipped mode change for $p (safe chmod refused or failed; re-run after fixing)" >&2
  fi
done
APPROVED_MODES=()
[ "${#_kept_modes[@]}" -gt 0 ] && APPROVED_MODES=("${_kept_modes[@]}")

# (Approved prunes were applied BEFORE the installs above - see the prune loop
# just after the PENDING_* declaration. High 3 / H5 / M6 dir->file, group 5.)

# Persist defer/never decisions and any no-op base advances now (the batch's
# synced:/base: records are quarantined in PENDING_* and written only after the
# commit succeeds; the EXIT trap also persists this partial state on an abort).
write_state || { echo "Error: could not persist .sync-state or refs/agent-sync/bases; hub left uncommitted" >&2; exit 1; }

# 8. Show resulting git status in hub
echo "---"
echo "Hub status after apply:"
git -C "$HUB_REPO" status --short

# Nothing actually reached the hub (e.g. every approved prune was untracked).
if [ "${#APPROVED_ADDS[@]}" -eq 0 ] && [ "${#APPROVED_CHANGES[@]}" -eq 0 ] \
   && [ "${#MERGED_PATHS[@]}" -eq 0 ] && [ "${#APPROVED_MODES[@]}" -eq 0 ] \
   && [ "${#PRUNED_PATHS[@]}" -eq 0 ]; then
  if [ "${#UNTRACKED_PRUNED[@]}" -gt 0 ]; then
    echo "Only untracked cleanups were applied (state-only, already persisted); nothing to commit."
  else
    echo "Nothing was applied to the hub - nothing to commit."
  fi
  exit 0
fi

# rollback_path <rel>: on a declined commit, restore one hub path to its pre-scan
# state. A path present in HEAD (a change, a merge, or a just-git-rm'd prune) is
# checked out from HEAD - restoring the worktree AND unstaging any staged deletion;
# a path absent from HEAD (a newly installed add) is removed. :(literal) so a glob
# name cannot wildmatch a sibling; the HEAD:<path> lookup is already a literal path.
rollback_path() {
  local p="$1" hub_rel="cultivation/marketplace/sam-cc-setup/$1"
  if git -C "$HUB_REPO" cat-file -e "HEAD:$hub_rel" 2>/dev/null; then
    # Round 2: a checkout failure must be REPORTED, not swallowed - the callers
    # decide whether to claim a complete restore. Return nonzero on failure
    # (every caller guards the call, so set -e never aborts mid-rollback).
    if ! git -C "$HUB_REPO" checkout HEAD -- ":(literal)$hub_rel" 2>/dev/null; then
      echo "  warning: could not restore $p from HEAD" >&2
      return 1
    fi
  else
    # CX-4: no-follow removal of a HEAD-absent add. A refusal (a symlink swapped
    # into an ancestor) surfaces and is non-fatal - the file is left, not followed.
    if ! python3 "$SAFE_IO" unlink "$HUB_REPO" "$HUB_PLUGIN_REL$p"; then
      echo "  warning: could not remove $p (left in place)" >&2
      return 1
    fi
  fi
  return 0
}

# rollback_batch: restore every path this run touched (shared by the decline path
# and the commit-failure path). Round 2: returns nonzero if ANY per-path rollback
# failed, so the caller can verify residue and report honestly instead of
# unconditionally claiming the hub was restored.
rollback_batch() {
  local _rb_failed=0 rbp
  for rbp in "${APPROVED_ADDS[@]:-}" "${APPROVED_CHANGES[@]:-}" "${MERGED_PATHS[@]:-}" "${APPROVED_MODES[@]:-}" "${PRUNED_PATHS[@]:-}"; do
    [ -z "${rbp:-}" ] && continue
    rollback_path "$rbp" || _rb_failed=1
  done
  return "$_rb_failed"
}

# scoped_residue: porcelain status restricted to the paths this run touched
# (:(literal) pathspecs, all five sets). Empty output = the hub really is back to
# its pre-scan state for this run's paths.
scoped_residue() {
  local _sp=() rbp
  for rbp in "${APPROVED_ADDS[@]:-}" "${APPROVED_CHANGES[@]:-}" "${MERGED_PATHS[@]:-}" "${APPROVED_MODES[@]:-}" "${PRUNED_PATHS[@]:-}"; do
    [ -z "${rbp:-}" ] && continue
    _sp+=(":(literal)cultivation/marketplace/sam-cc-setup/$rbp")
  done
  [ "${#_sp[@]}" -eq 0 ] && return 0
  # Round 3: keep git's stderr visible - a failing probe must be diagnosable. The
  # callers guard this call, so a probe failure reports as unverifiable instead
  # of aborting under set -e before the INCOMPLETE branch.
  git -C "$HUB_REPO" status --porcelain -- "${_sp[@]}"
}

# 9. Prompt commit + push (default Y).
printf "Commit synced files? [Y/n] " >&2
read -r commit_resp || commit_resp=""
case "$commit_resp" in
  n|N|no|NO)
    # H2 decline = surgical rollback (lead R2(iii)): restore exactly the paths this
    # run touched so the hub returns to its pre-scan state; PENDING_* is discarded
    # (never promoted), so the ledger stays byte-identical and the next scan
    # re-offers. Scoped per-path so pre-existing hub WIP is untouched. Round 2:
    # claim a restore only if the rollback really completed - otherwise print the
    # residue and how to finish by hand.
    decline_rb_ok=0
    rollback_batch || decline_rb_ok=1
    # Round 3: a bare $(scoped_residue) assignment aborts under set -e if the
    # status probe itself fails - before the INCOMPLETE branch could report.
    if ! decline_residue=$(scoped_residue); then
      decline_rb_ok=1
      decline_residue="(could not verify scoped residue - inspect the hub by hand)"
    fi
    if [ "$decline_rb_ok" -ne 0 ] || [ -n "$decline_residue" ]; then
      echo "Declined, but the rollback is INCOMPLETE - residue on this run's paths:" >&2
      printf '%s\n' "$decline_residue" >&2
      echo "Finish by hand: cd $HUB_REPO && git reset -- <path> && git checkout HEAD -- <path> (no sync records were added)." >&2
      exit 1
    fi
    echo "Declined - hub restored, nothing kept; re-run to apply."
    if [ "${#UNTRACKED_PRUNED[@]}" -gt 0 ]; then
      echo "Kept (state-only, not part of the declined commit): removed these untracked hub copies and cleared their stale ledger records: ${UNTRACKED_PRUNED[*]}"
    fi
    exit 0
    ;;
esac

# 10. Commit + push.
#     SCOPED: only the approved synced files are added. Pre-existing dirty
#     hub WIP (if user continued through the warning) and runtime artifacts
#     (.sync-state) MUST NOT be swept into the sync commit.
DATE=$(date -u +%Y-%m-%d)
HUB_RELPATHS=()
for p in "${APPROVED_ADDS[@]:-}" "${APPROVED_CHANGES[@]:-}" "${MERGED_PATHS[@]:-}" "${APPROVED_MODES[@]:-}"; do
  # H1: :(literal) so the scoped stage cannot wildmatch a glob-named path onto an
  # unrelated dirty hub WIP sibling and sweep it into the sync commit (defeating
  # the no-contamination guarantee above).
  [ -n "$p" ] && HUB_RELPATHS+=(":(literal)cultivation/marketplace/sam-cc-setup/$p")
done

# Stage adds/changes/merges (scoped). Pruned paths are already staged as
# deletions by git rm, so they need no add (git add on a removed path errors).
if [ "${#HUB_RELPATHS[@]}" -gt 0 ]; then
  git -C "$HUB_REPO" add -- "${HUB_RELPATHS[@]}"
fi
# CX-5: a commit FAILURE (rejecting hook, identity misconfig) is not a decline -
# git add has already staged this run's paths. Left alone, that residue wedges the
# next scan at the C2 staged-index guard with no matching ledger records (the
# synced:/base: promotion below never ran). Unstage the scoped adds first -
# rollback_path's no-follow unlink removes a HEAD-absent add from the worktree but
# cannot unstage it - then run the same scoped rollback the decline path uses.
# The reset is guarded (a prune-only batch has empty HUB_RELPATHS, and a bare
# `git reset --` would mixed-reset the ENTIRE index) and || true so it cannot
# abort the rollback under set -e; prunes are restored by rollback_path itself.

# Wave 3 (8b Item 1): a SOFT provenance reminder. Every promoted change is meant
# to get one line in cultivation/marketplace/UPGRADING.md (WHAT changed and WHY).
# Detect whether this batch touched UPGRADING.md: a non-empty `git status
# --porcelain` for it means it is staged OR unstaged in the hub. UPGRADING.md sits
# OUTSIDE the sam-cc-setup plugin tree, so it is never among this run's approved
# paths - the git-status probe is the only meaningful signal. Captured BEFORE the
# commit as a defensive choice; the realistic signal is an unstaged edit, which a
# no-pathspec `git commit` never consumes, and C2 already refuses a pre-staged hub
# index. The reminder is printed only after a SUCCESSFUL commit below: it never
# gates, never blocks, never changes the exit code, never suppresses the commit.
upgrading_touched=1
[ -z "$(git -C "$HUB_REPO" status --porcelain -- ":(literal)cultivation/marketplace/UPGRADING.md" 2>/dev/null)" ] \
  && upgrading_touched=0
if ! git -C "$HUB_REPO" commit -m "sync: from $PROJ_NAME on $DATE"; then
  cf_rb_ok=0
  if [ "${#HUB_RELPATHS[@]}" -gt 0 ]; then
    git -C "$HUB_REPO" reset -q -- "${HUB_RELPATHS[@]}" || cf_rb_ok=1
  fi
  rollback_batch || cf_rb_ok=1
  # Round 2: verify before claiming success - a failed reset/checkout/unlink can
  # leave staged or worktree residue that would wedge the next scan at C2.
  # Round 3: guard the capture - a failed probe reports as unverifiable, never
  # aborts under set -e before the INCOMPLETE branch.
  if ! cf_residue=$(scoped_residue); then
    cf_rb_ok=1
    cf_residue="(could not verify scoped residue - inspect the hub by hand)"
  fi
  if [ "$cf_rb_ok" -ne 0 ] || [ -n "$cf_residue" ]; then
    echo "Error: hub commit failed and the rollback is INCOMPLETE - residue on this run's paths:" >&2
    printf '%s\n' "$cf_residue" >&2
    echo "Finish by hand: cd $HUB_REPO && git reset -- <path> && git checkout HEAD -- <path>. No sync records were added." >&2
  else
    echo "Error: hub commit failed; rolled back this run's staged changes. Nothing was committed and no sync records were added. Fix the hub commit failure, then re-run to re-offer." >&2
  fi
  exit 1
fi
# Commit succeeded: promote the quarantined records into the ledger, then persist
# (H2). Until here STATE held no synced:/base: for this batch, so a decline or a
# crash before this point could never leave a false-synced record (also removes
# the H6 residue: an empty-index commit failure aborts before this promotion).
if [ -n "${PENDING_SYNCED[*]+x}" ]; then
  for pp in "${!PENDING_SYNCED[@]}"; do
    STATE_DECISIONS["$pp"]="synced:${PENDING_SYNCED[$pp]}"
    STATE_BASES["$pp"]="${PENDING_BASES[$pp]}"
  done
fi
if [ -n "${PENDING_PRUNE_UNSET[*]+x}" ]; then
  for pp in "${!PENDING_PRUNE_UNSET[@]}"; do
    unset 'STATE_DECISIONS[$pp]'
    unset 'STATE_BASES[$pp]'
  done
fi
write_state || { echo "Error: could not persist .sync-state after commit; ledger and hub HEAD may disagree - re-run with --bootstrap-bases" >&2; exit 1; }
# Wave 3 (8b Item 1): the soft provenance reminder fires here - after a real
# commit, before the push prompt - so it always implies a promotion just landed.
# Reminder only (stderr, advisory class): never a gate, never blocks, never
# changes the exit code. Silent when UPGRADING.md was touched in this batch.
if [ "$upgrading_touched" -eq 0 ]; then
  echo "Reminder: cultivation/marketplace/UPGRADING.md was not updated in this batch. Consider adding a provenance line (WHAT changed and WHY) for the promoted change(s)." >&2
fi
# Push is outward-facing and the hub is a general-purpose repo - separate confirm.
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
