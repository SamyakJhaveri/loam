#!/usr/bin/env bash
# spike-probes.sh — re-runnable regression guard for the mechanism spike.
#
# Turns the one-off manual probes from the 2026-07-19 mechanism spike into a
# reproducible, version-pinned end-to-end check. It recreates the spike's probe
# chain in a disposable scratch dir and asserts each finding, so a future
# Copier/Loam change that alters the behavior fails loudly here.
#
# Spec:     docs/specs/mechanism-spike-regression-test.md
# Evidence: ~/.claude/plans/2026-07-19-mechanism-spike-findings.md (Appendix verdict table)
#
# WIRING (spec D1 — standalone only): NOT in the /validate gate, NOT a
# verify-template.sh flag, NOT in release.sh. It clones + runs Copier several
# times (slow), so run it MANUALLY on Copier/Loam version bumps and pre-release.
# Pointer lives in docs/COPIER.md §Versioning.
#
# CHANGE-DETECTOR (spec acceptance #6): assertion #2 asserts the promote PR
# target is `samyakjhaveri/loam`. When template-sync-promote-generic-user reworks
# targeting, the single line to update is the grep in ASSERTION 2 below
# (search for "CHANGE HERE"); its source of truth is bin/template-sync.sh:295.
#
# RED/GREEN CONTRACT: #8 is expected RED only when validating the pre-fix
# timestamp baseline. Once copier-update-timestamp-conflict lands, any #8
# failure is a regression. The fix flips #8 green with no other edit to this
# script (spec acceptance #5), and the whole script then exits 0.
#
# Version pins (findings were Verified against these; drift warns, never fails):
#   copier 9.17.0, git 2.55.0
#
# Guardrails: clones canonical into a scratch dir, removes each clone's origin,
# and asserts ~/Desktop/loam's HEAD + working tree are unchanged before/after.
# Never pushes, never opens a PR, always cleans its scratch dir on exit.

set -euo pipefail

PIN_COPIER="9.17.0"
PIN_GIT="2.55.0"

# shellcheck disable=SC2034
LIB_PREFIX="spike"
# shellcheck source=bin/lib.sh
source "$(dirname "$0")/lib.sh"

LOAM="$(cd "$(dirname "$0")/.." && pwd)"
CANONICAL_HEAD="$(git -C "$LOAM" rev-parse HEAD)"
STATUS_BEFORE="$(git -C "$LOAM" status --porcelain)"
[[ -z "$STATUS_BEFORE" ]] || die "canonical working tree must be clean before running probes"
BRANCHES_BEFORE="$(git -C "$LOAM" for-each-ref --format='%(objectname) %(refname)' refs/heads/)"

# Copier can install as a bare command or via uvx; mirror verify-template.sh.
if command -v copier >/dev/null 2>&1; then
  COPIER="copier"
elif command -v uvx >/dev/null 2>&1; then
  COPIER="uvx copier"
else
  die "copier not installed (need 'copier' or 'uvx'); this probe drives Copier directly"
fi

# LFS-tracked hero art (~20MB) would smudge on every clone; the probes never read
# image bytes, so keep pointers and stay fast (same trick as verify-template.sh).
export GIT_LFS_SKIP_SMUDGE=1

SCRATCH="$(mktemp -d 2>/dev/null || mktemp -d -t spike-probes)"

# Cleanup + canonical-untouched assertion run on EVERY exit (success or failure),
# and must preserve the original exit code (spec acceptance #2, #3).
on_exit() {
  local rc=$?
  local head_after status_after branches_after problems=""
  if ! rm -rf "$SCRATCH" 2>/dev/null; then
    problems="$problems scratch-cleanup-failed"
  fi
  if [[ -d "$SCRATCH" ]]; then
    problems="$problems scratch-survived($SCRATCH)"
  fi
  head_after="$(git -C "$LOAM" rev-parse HEAD 2>/dev/null || echo UNKNOWN)"
  status_after="$(git -C "$LOAM" status --porcelain 2>/dev/null || echo UNKNOWN)"
  branches_after="$(git -C "$LOAM" for-each-ref --format='%(objectname) %(refname)' refs/heads/ 2>/dev/null || echo UNKNOWN)"
  if [[ "$head_after" != "$CANONICAL_HEAD" ]]; then problems="$problems HEAD($CANONICAL_HEAD->$head_after)"; fi
  if [[ "$status_after" != "$STATUS_BEFORE" ]]; then problems="$problems working-tree"; fi
  if [[ "$branches_after" != "$BRANCHES_BEFORE" ]]; then problems="$problems branches-changed"; fi
  if [[ -n "$problems" ]]; then
    echo "FAIL: canonical repo at $LOAM was modified by this run:$problems" >&2
    [[ $rc -eq 0 ]] && rc=1
  else
    echo "OK: canonical untouched ($LOAM HEAD $CANONICAL_HEAD, tree and branches unchanged)"
  fi
  exit "$rc"
}
trap on_exit EXIT

# git with a fixed identity so commits never depend on ambient config.
gitc() { git -C "$1" -c user.email=spike@local -c user.name=spike-probes -c commit.gpgsign=false "${@:2}"; }

# fresh_tpl <name> — a pristine template clone with a local `main` pinned to the
# canonical committed HEAD, origin removed (no push can reach the real repo).
# Echoes the clone path. A clone captures only the committed HEAD, never the
# uncommitted working tree — so an un-tagged fix on a feature branch is seen only
# once committed (bears on spec acceptance #5: commit the timestamp fix before
# expecting #8 to flip green).
fresh_tpl() {
  local dst="$SCRATCH/$1"
  git clone -q "$LOAM" "$dst"
  git -C "$dst" remote remove origin 2>/dev/null \
    || fail "scratch isolation: could not remove origin from $dst"
  if git -C "$dst" remote get-url origin >/dev/null 2>&1; then
    fail "scratch isolation: origin still present in $dst"
  fi
  git -C "$dst" checkout -q -B main "$CANONICAL_HEAD"
  echo "$dst"
}

copier_copy() { # <src> <dst> <project_name>
  # shellcheck disable=SC2086
  $COPIER copy --trust --defaults --vcs-ref "$CANONICAL_HEAD" \
    --data "project_name=$3" "$1" "$2" >/dev/null 2>&1
}

copier_commit_sha() { # <template-repo> <answers-file>
  local ref
  ref="$(sed -n 's/^_commit: //p' "$2")"
  [[ -n "$ref" ]] || return 1
  git -C "$1" rev-parse "${ref}^{commit}" 2>/dev/null
}

# ---------------------------------------------------------------------------
info "copier: $($COPIER --version 2>&1 | head -1) | git: $(git --version)"
COPIER_VER="$($COPIER --version 2>&1 | awk '{print $NF}')"
GIT_VER="$(git --version | awk '{print $3}')"
[[ "$COPIER_VER" == "$PIN_COPIER" ]] || warn "copier $COPIER_VER != pinned $PIN_COPIER — findings pinned to $PIN_COPIER; behavior drift is signal, not failure"
[[ "$GIT_VER" == "$PIN_GIT" ]]       || warn "git $GIT_VER != pinned $PIN_GIT — findings pinned to $PIN_GIT"
info "scratch: $SCRATCH"
info "canonical HEAD: $CANONICAL_HEAD"

# ===========================================================================
# ASSERTION 1 — Bootstrap metadata
# After copier copy: .copier-answers.yml exists, no template-manifest.json, no bin/.
# ===========================================================================
T1="$(fresh_tpl a1)"
PROJ1="$SCRATCH/proj1"
copier_copy "$T1" "$PROJ1" spikeproj
test -f "$PROJ1/.copier-answers.yml"    || fail "#1: .copier-answers.yml missing after copier copy"
test ! -f "$PROJ1/template-manifest.json" || fail "#1: template-manifest.json unexpectedly present in project"
test ! -d "$PROJ1/bin"                  || fail "#1: project unexpectedly ships bin/ (only seed/ should render)"
pass "#1 bootstrap metadata (.copier-answers.yml present, no manifest, no bin/)"

# ===========================================================================
# ASSERTION 2 — Upward promote via the script path
# template-sync.sh promote from the project → sync/* branch + committed asset,
# exit 0, printed PR command targets samyakjhaveri/loam. CHANGE-DETECTOR.
# ===========================================================================
mkdir -p "$PROJ1/.claude/rules"
printf '# spike probe asset\n' > "$PROJ1/.claude/rules/spike-probe.md"
PROMOTE_OUT="$(cd "$PROJ1" && bash "$T1/bin/template-sync.sh" promote --layer generic .claude/rules/spike-probe.md 2>&1)" \
  || fail "#2: promote exited non-zero:"$'\n'"$PROMOTE_OUT"
# CHANGE HERE when template-sync-promote-generic-user reworks PR targeting
# (source of truth: bin/template-sync.sh:295, the no-manifest else branch).
grep -q -- '--repo samyakjhaveri/loam' <<<"$PROMOTE_OUT" \
  || fail "#2: promote PR command no longer targets samyakjhaveri/loam:"$'\n'"$PROMOTE_OUT"
SYNC_BRANCH="$(git -C "$T1" for-each-ref --format='%(refname:short)' refs/heads/ | grep '^sync/' | head -1 || true)"
[[ -n "$SYNC_BRANCH" ]] || fail "#2: no sync/* branch created in template clone (branches: $(git -C "$T1" for-each-ref --format='%(refname:short)' refs/heads/ | tr '\n' ' '))"
git -C "$T1" cat-file -e "$SYNC_BRANCH:seed/.claude/rules/spike-probe.md" 2>/dev/null \
  || fail "#2: asset not committed at seed/.claude/rules/spike-probe.md on $SYNC_BRANCH"
pass "#2 upward promote (script) — $SYNC_BRANCH + asset committed, PR target samyakjhaveri/loam"

# ===========================================================================
# ASSERTION 3 — Skill precondition (static)
# The SKILL.md pre-flight refuses without template-manifest.json, so a copier
# project (which has none) can never satisfy the documented skill path.
# Updated/removed once template-sync-promote-generic-user aligns the skill.
# ===========================================================================
SKILL="$T1/seed/.claude/skills/template-sync/SKILL.md"
grep -q 'template-manifest.json' "$SKILL" || fail "#3: SKILL.md no longer references the template-manifest.json precondition"
# Require the refusal ('cannot operate') and the manifest token on the SAME line,
# so a reword that keeps both substrings but severs the tie is caught (harder to
# false-pass than two independent whole-file greps). Known-weak static proxy per
# spec; updated/removed when template-sync-promote-generic-user aligns the skill.
grep -i 'cannot operate' "$SKILL" | grep -qi 'template-manifest' \
  || fail "#3: SKILL.md pre-flight no longer ties 'cannot operate' to a missing template-manifest.json"
pass "#3 skill pre-flight still refuses without template-manifest.json (static)"

# ===========================================================================
# ASSERTION 4 — Edge A broken: copier update on a fork
# A forked "personal Loam" has no .copier-answers.yml, so copier update cannot
# find a template baseline and errors. The findings observed "Cannot obtain old
# template references from .copier-answers.yml"; copier 9.17.0 on a pristine
# fork actually raises "Template not found" (it fails even earlier, at template
# resolution). Both confirm the same verdict — a fork has no Copier baseline, so
# the canonical→personal edge structurally cannot use copier update.
# ===========================================================================
UP="$(fresh_tpl a4up)"
PERSONAL="$SCRATCH/personal"
git clone -q "$UP" "$PERSONAL"
git -C "$PERSONAL" remote remove origin 2>/dev/null \
  || fail "#4: could not remove origin from personal scratch clone"
if git -C "$PERSONAL" remote get-url origin >/dev/null 2>&1; then
  fail "#4: origin still present in personal scratch clone"
fi
git -C "$PERSONAL" remote add upstream "$UP"
test ! -f "$PERSONAL/.copier-answers.yml" || fail "#4: personal fork unexpectedly has .copier-answers.yml"
# shellcheck disable=SC2086
if EDGEA_ERR="$(cd "$PERSONAL" && $COPIER update --defaults 2>&1)"; then
  fail "#4: copier update on a fork unexpectedly succeeded (expected structural failure)"
fi
grep -qiE 'Cannot obtain old template references|Template not found' <<<"$EDGEA_ERR" \
  || fail "#4: copier update on fork failed with an unexpected error:"$'\n'"$EDGEA_ERR"
pass "#4 Edge A broken — copier update on a fork errors (no .copier-answers baseline)"

# ===========================================================================
# ASSERTION 5 — Edge A fallback: git merge upstream (non-overlapping) is clean
# ===========================================================================
printf 'canonical addition\n' > "$UP/seed/.claude/rules/canonical-new.md"
gitc "$UP" add seed/.claude/rules/canonical-new.md
gitc "$UP" commit -q -m "canonical: add canonical-new.md"
printf 'personal divergence\n' > "$PERSONAL/seed/.claude/rules/personal-note.md"
gitc "$PERSONAL" add seed/.claude/rules/personal-note.md
gitc "$PERSONAL" commit -q -m "personal: add personal-note.md"
gitc "$PERSONAL" fetch -q upstream
gitc "$PERSONAL" merge -q --no-edit upstream/main || fail "#5: git merge upstream/main was not clean"
test -f "$PERSONAL/seed/.claude/rules/personal-note.md"  || fail "#5: personal divergence lost after merge"
test -f "$PERSONAL/seed/.claude/rules/canonical-new.md"  || fail "#5: canonical change not pulled by merge"
pass "#5 Edge A fallback — clean git merge preserves divergence + pulls canonical change"

# ===========================================================================
# ASSERTION 6 — Edge B: copier update on a project made from the personal Loam
# advances _commit, pulls the new template file, preserves project divergence.
# (copier update returns exit 0 even with the unrelated timestamp conflict.)
# ===========================================================================
PROJ2="$SCRATCH/proj2"
PERSONAL_HEAD1="$(git -C "$PERSONAL" rev-parse HEAD)"
# shellcheck disable=SC2086
$COPIER copy --trust --defaults --vcs-ref "$PERSONAL_HEAD1" --data project_name=proj2 "$PERSONAL" "$PROJ2" >/dev/null 2>&1
COMMIT_BEFORE_SHA="$(copier_commit_sha "$PERSONAL" "$PROJ2/.copier-answers.yml")" \
  || fail "#6: cannot resolve initial _commit in proj2 .copier-answers.yml"
[[ "$COMMIT_BEFORE_SHA" == "$PERSONAL_HEAD1" ]] \
  || fail "#6: initial _commit resolves to $COMMIT_BEFORE_SHA, expected $PERSONAL_HEAD1"
grep -qx 'personal divergence' "$PROJ2/.claude/rules/personal-note.md" \
  || fail "#6: personal template divergence missing before update"
test ! -e "$PROJ2/.claude/rules/edge-b-new.md" \
  || fail "#6: edge-b-new.md unexpectedly present before template update"
printf 'proj2 local divergence\n' > "$PROJ2/proj2-local.md"
gitc "$PROJ2" add -A
gitc "$PROJ2" commit -q -m "proj2: local divergence"
printf 'edge-b new template file\n' > "$PERSONAL/seed/.claude/rules/edge-b-new.md"
gitc "$PERSONAL" add seed/.claude/rules/edge-b-new.md
gitc "$PERSONAL" commit -q -m "personal: add edge-b-new.md"
PERSONAL_HEAD2="$(git -C "$PERSONAL" rev-parse HEAD)"
# shellcheck disable=SC2086
(cd "$PROJ2" && $COPIER update --trust --defaults --vcs-ref "$PERSONAL_HEAD2" >/dev/null 2>&1) \
  || fail "#6: copier update exited non-zero"
COMMIT_AFTER_SHA="$(copier_commit_sha "$PERSONAL" "$PROJ2/.copier-answers.yml")" \
  || fail "#6: cannot resolve updated _commit in proj2 .copier-answers.yml"
[[ "$COMMIT_AFTER_SHA" == "$PERSONAL_HEAD2" ]] \
  || fail "#6: updated _commit resolves to $COMMIT_AFTER_SHA, expected $PERSONAL_HEAD2"
grep -qx 'personal divergence' "$PROJ2/.claude/rules/personal-note.md" \
  || fail "#6: personal template divergence lost after update"
grep -qx 'edge-b new template file' "$PROJ2/.claude/rules/edge-b-new.md" \
  || fail "#6: new template file missing or changed after update"
grep -qx 'proj2 local divergence' "$PROJ2/proj2-local.md" \
  || fail "#6: project-local divergence lost after update"
pass "#6 Edge B — copier update advances _commit, pulls new file, preserves divergence"

# ===========================================================================
# ASSERTION 7 — Conflict shapes
#   7a same-line git merge → UU
#   7b modify/delete git merge → UD
#   7c copier update overlap → in-file "before/after updating" markers
#   7d template file deletion propagates to the project on update
# ===========================================================================
# 7a: same-line UU
M1="$(fresh_tpl a7a)"
printf 'base\n' > "$M1/seed/.claude/rules/conflict-probe.md"
gitc "$M1" add seed/.claude/rules/conflict-probe.md
gitc "$M1" commit -q -m "conflict base"
gitc "$M1" checkout -q -b sideX
printf 'sideX heading\n' > "$M1/seed/.claude/rules/conflict-probe.md"
gitc "$M1" commit -q -am "sideX edit"
gitc "$M1" checkout -q main
printf 'main heading\n' > "$M1/seed/.claude/rules/conflict-probe.md"
gitc "$M1" commit -q -am "main edit"
if gitc "$M1" merge --no-edit sideX >/dev/null 2>&1; then
  fail "#7a: same-line merge unexpectedly clean"
fi
git -C "$M1" status --porcelain | grep -q '^UU seed/.claude/rules/conflict-probe.md' \
  || fail "#7a: expected UU on same-line merge, got:"$'\n'"$(git -C "$M1" status --porcelain)"
pass "#7a same-line git merge → UU"

# 7b: modify/delete UD (HEAD modifies, merged-in branch deletes → 'deleted by them')
M2="$(fresh_tpl a7b)"
printf 'base\n' > "$M2/seed/.claude/rules/md-probe.md"
gitc "$M2" add seed/.claude/rules/md-probe.md
gitc "$M2" commit -q -m "md base"
gitc "$M2" checkout -q -b sideDel
gitc "$M2" rm -q seed/.claude/rules/md-probe.md
gitc "$M2" commit -q -m "sideDel removes md-probe"
gitc "$M2" checkout -q main
printf 'main modifies\n' > "$M2/seed/.claude/rules/md-probe.md"
gitc "$M2" commit -q -am "main modifies md-probe"
if gitc "$M2" merge --no-edit sideDel >/dev/null 2>&1; then
  fail "#7b: modify/delete merge unexpectedly clean"
fi
git -C "$M2" status --porcelain | grep -q '^UD seed/.claude/rules/md-probe.md' \
  || fail "#7b: expected UD (modify/delete), got:"$'\n'"$(git -C "$M2" status --porcelain)"
pass "#7b modify/delete git merge → UD"

# 7c + 7d: copier update overlap markers + template-deletion propagation
TC="$(fresh_tpl a7c)"
printf 'overlap v1\n' > "$TC/seed/.claude/rules/overlap-probe.md"
printf 'delete me\n'  > "$TC/seed/.claude/rules/delete-probe.md"
gitc "$TC" add seed/.claude/rules/overlap-probe.md seed/.claude/rules/delete-probe.md
gitc "$TC" commit -q -m "tc: add overlap + delete probes"
TC_BASE="$(git -C "$TC" rev-parse HEAD)"
PROJ3="$SCRATCH/proj3"
# shellcheck disable=SC2086
$COPIER copy --trust --defaults --vcs-ref "$TC_BASE" --data project_name=proj3 "$TC" "$PROJ3" >/dev/null 2>&1
test -f "$PROJ3/.claude/rules/delete-probe.md" || fail "#7d: delete-probe.md did not render into project"
printf 'overlap PROJECT edit\n' > "$PROJ3/.claude/rules/overlap-probe.md"
gitc "$PROJ3" commit -q -am "proj3: local overlap edit"
printf 'overlap TEMPLATE edit\n' > "$TC/seed/.claude/rules/overlap-probe.md"
gitc "$TC" rm -q seed/.claude/rules/delete-probe.md
gitc "$TC" commit -q -am "tc: change overlap-probe, delete delete-probe"
TC_NEXT="$(git -C "$TC" rev-parse HEAD)"
# shellcheck disable=SC2086
(cd "$PROJ3" && $COPIER update --trust --defaults --vcs-ref "$TC_NEXT" >/dev/null 2>&1) \
  || fail "#7c: copier update exited non-zero"
if ! grep -q 'before updating' "$PROJ3/.claude/rules/overlap-probe.md" \
   || ! grep -q 'after updating' "$PROJ3/.claude/rules/overlap-probe.md"; then
  fail "#7c: expected copier before/after-updating markers in overlap-probe.md"
fi
pass "#7c copier update overlap → before/after-updating markers"
test ! -f "$PROJ3/.claude/rules/delete-probe.md" \
  || fail "#7d: template deletion did not propagate (delete-probe.md still present)"
pass "#7d template file deletion propagates to project on update"

# ===========================================================================
# ASSERTION 8 — Render reproducibility (THE RED ONE)
# ROOT CAUSE of the timestamp papercut: strftime makes the rendered CLAUDE.md /
# README.md NON-REPRODUCIBLE — rendering the SAME template version at two
# different wall-clock times yields different bytes. That non-reproducibility is
# exactly why `copier update` spuriously conflicts on those two files.
#
# We test the root cause directly first because the downstream conflict is a
# sub-second RACE: copier update conflicts only when its two internal re-renders
# (old + new) straddle a %S boundary, so a fast update can false-green against
# buggy main. Two renders + a >=2s gap make the strftime difference deterministic.
# Once that oracle is green, an empty template commit forces a real no-content
# update and guards the end-to-end zero-conflict behavior too.
#
# Pre-fix: the two renders differ (RED). Post-fix (strftime removed): byte-
# identical (GREEN) — with no other edit to this script (spec acceptance #5).
# The literal "copier update -> zero conflicts" check follows the render oracle.
# ===========================================================================
TS="$(fresh_tpl a8)"
TS_A="$(git -C "$TS" rev-parse HEAD)"
R1="$SCRATCH/ts-r1"; R2="$SCRATCH/ts-r2"
# shellcheck disable=SC2086
$COPIER copy --trust --defaults --vcs-ref "$TS_A" --data project_name=tsproj "$TS" "$R1" >/dev/null 2>&1
sleep 2  # guarantee the wall clock crosses a %S boundary so any strftime differs
# shellcheck disable=SC2086
$COPIER copy --trust --defaults --vcs-ref "$TS_A" --data project_name=tsproj "$TS" "$R2" >/dev/null 2>&1
TS_UNSTABLE=""
for f in CLAUDE.md README.md; do
  cmp -s "$R1/$f" "$R2/$f" || TS_UNSTABLE="$TS_UNSTABLE $f"
done
if [[ -n "$TS_UNSTABLE" ]]; then
  warn "#8 RED (expected only on the pre-fix baseline): non-reproducible render in:$TS_UNSTABLE"
  diff "$R1/CLAUDE.md" "$R2/CLAUDE.md" >&2 || true
  fail "#8: rendered$TS_UNSTABLE differ across two renders of the same version (volatile strftime timestamp)"
fi

# Force Copier to execute its update path without changing any rendered
# template content. Copier requires a clean destination, so commit any cleanup
# that its post-generation tasks performed after the bootstrap commit first.
# This complements the deterministic red/green oracle above.
gitc "$R1" add -A
if ! gitc "$R1" diff --cached --quiet; then
  gitc "$R1" commit -q -m "a8: commit post-bootstrap cleanup"
fi
gitc "$TS" commit --allow-empty -q -m "a8: no-content template revision"
TS_NEXT="$(git -C "$TS" rev-parse HEAD)"
# shellcheck disable=SC2086
if ! TS_UPDATE_OUT="$(cd "$R1" && $COPIER update --trust --defaults --vcs-ref "$TS_NEXT" 2>&1)"; then
  fail "#8: no-content copier update exited non-zero:"$'\n'"$TS_UPDATE_OUT"
fi
TS_COMMIT_AFTER_SHA="$(copier_commit_sha "$TS" "$R1/.copier-answers.yml")" \
  || fail "#8: cannot resolve _commit after no-content update"
[[ "$TS_COMMIT_AFTER_SHA" == "$TS_NEXT" ]] \
  || fail "#8: no-content update _commit resolves to $TS_COMMIT_AFTER_SHA, expected $TS_NEXT"
TS_STATUS="$(git -C "$R1" status --porcelain)"
if grep -Eq '^(DD|AU|UD|UA|DU|AA|UU) ' <<<"$TS_STATUS"; then
  fail "#8: no-content copier update left unmerged files:"$'\n'"$TS_STATUS"
fi
for f in CLAUDE.md README.md; do
  if grep -Eq '^(<<<<<<<|>>>>>>>)' "$R1/$f"; then
    fail "#8: no-content copier update left conflict markers in $f"
  fi
done
pass "#8 render reproducible + no-content copier update conflict-free"

echo "ALL PROBES PASSED"
