# release-ip-gate-inert

> Spec for a gap found during the mechanism-spike follow-up (2026-07-19), while reference-checking the other specs.
> Not part of the three-tier mechanism itself — a release-hygiene defect surfaced by the retrospective.
> Generated via `/gen-spec`, 2026-07-19. **Status: ready (grilled 2026-07-19).**

## Identity

- **Name:** release-ip-gate-inert
- **Owner:** Sam
- **Status:** ready (grilled 2026-07-19)
- **Scope:** Restore or rewire the release-time IP/secret sweep so that a release cut from the canonical `~/Desktop/loam` repo actually runs an IP gate, instead of silently skipping it. Touches `bin/release.sh` and possibly adds/adapts a sweep script. Does NOT change what gets published beyond re-enabling the gate.

## Inputs (Verified 2026-07-19)

- `bin/release.sh:35-42` — the IP gate is conditional:
  ```bash
  # IP gate (defense-in-depth): if the private-dev sweep is present, it must pass
  # in strict mode before we publish. Absent (e.g. public clone) → skip loudly.
  if [[ -x "$(dirname "$0")/ip-sweep.sh" ]]; then
    IP_SWEEP_STRICT=1 bash "$(dirname "$0")/ip-sweep.sh" || die "ip-sweep failed — refusing to release"
  else
    warn "bin/ip-sweep.sh not present — skipping IP gate"
  fi
  ```
- **`bin/ip-sweep.sh` is absent from the public repo** and was **never in its history** (`git log --all -- bin/ip-sweep.sh` empty). It is **not** gitignored.
- The script **does** exist, tracked, in the private archive: `~/Desktop/loam-dev-archive/bin/ip-sweep.sh` (3.4 KB) — the fresh-repo cutover (2026-07-02) left it behind.
- `bin/check-own-synthesis.py` **is** present in the public repo but is **not wired into `release.sh`** (a standalone local dev guard).
- **Consequence:** the canonical `~/Desktop/loam` *is* Sam's release machine (canonical = his personal instance). Because `ip-sweep.sh` is not present there, every `bin/release.sh` run takes the `else` branch → **the IP gate is skipped with only a warning.** The design's "skip loudly on public clones" is correct for strangers, but it also silently disables the gate on Sam's own releases.
- Prior belief was wrong: memory `project_ip_remediation_live` claimed both `ip-sweep.sh` + `check-own-synthesis.py` were "live guards … green in the public tree." Corrected 2026-07-19.

## Behavior

**Grill decision D4 (Sam, 2026-07-19): Option 1a — restore the archive `ip-sweep.sh` after read-first review. Keep it byte-identical unless the review proves its missing-terms failure lacks the required actionable message; in that one case, permit only that message patch.**

- Copy `~/Desktop/loam-dev-archive/bin/ip-sweep.sh` to `bin/ip-sweep.sh` (executable) after reading it in full for private paths/leaks (the constraint below stands). Preserve it byte-for-byte unless the missing-terms message patch described above is necessary.
- The blocklist of IP terms lives **outside** the script in `bin/.ip-terms`, which is **gitignored** (never committed).
- Commit `bin/.ip-terms.example` (a redacted template) — read it in full first to confirm it leaks no real terms.
- Sam copies the real `.ip-terms` from the archive to his local `bin/.ip-terms` (gitignored, never committed).
- **Missing-terms behavior:** in strict mode, an absent `bin/.ip-terms` is a **hard FAIL**, not a silent skip — the honest gate. (This is the archive script's existing behavior; Session 2 confirms it when reading the script in full, and adds only the actionable "copy `.ip-terms.example`" message if the archive script does not already emit one.)
- **No `bin/release.sh` edit needed:** the existing `if [[ -x …/ip-sweep.sh ]]` conditional already runs the sweep in strict mode once the script is present.

**Rationale:** the script embeds no IP terms itself (they are external + gitignored), so restoring the reviewed script leaks nothing; the strict hard-fail on missing terms is the honest behavior for maintainer tooling; the author/LFS checks already pass today (Verified 2026-07-19: all public-repo commit identities are the single noreply address, and `git lfs ls-files` count is 0).

**Original options (historical — superseded by D4 = Option 1a):**

- **Option 1 (recommended) — restore an IP sweep into the public repo.** Review `~/Desktop/loam-dev-archive/bin/ip-sweep.sh` for any private-only assumptions (paths, the `~/loam-soil-backup` dependency), generalize it to skip-clean when its private inputs are absent, and commit it to `bin/`. Then Sam's releases run it; strangers without the private backup still skip cleanly. Keep the `release.sh` conditional (it already handles "present → run strict, absent → skip loud").
- **Option 2 — wire the existing public guard.** Make `release.sh` invoke `bin/check-own-synthesis.py` (already public) as the IP gate, in addition to / instead of `ip-sweep.sh`. Cheaper (no new file) but only covers the prose-synthesis check, not the grep/author/LFS checks the archived `ip-sweep.sh` did — confirm coverage before choosing this.
- **Option 3 — remove the dead call.** Only if Sam decides no release-time IP gate is wanted (unlikely, since releases publish to a public repo). If chosen, delete the `if/else` block so `release.sh` doesn't reference a non-existent script.

Whichever: `release.sh` must not end in a state where it *appears* to gate but silently doesn't on the maintainer's own machine.

## Outputs (D4 — Option 1a)

- **Added:** `bin/ip-sweep.sh` — restored from the archive, executable, read-first, and unchanged except for the single permitted missing-terms message patch if required.
- **Added:** `bin/.ip-terms.example` — redacted template, committed after a full leak-check read.
- **Modified:** `.gitignore` — add `bin/.ip-terms`.
- **Not modified:** `bin/release.sh` — its existing `if [[ -x …/ip-sweep.sh ]]` conditional already gates strict once the script is present.
- **Local, never committed:** `bin/.ip-terms` — Sam copies the real terms from the archive.
- **Updated docs:** mark the `docs/plans/2026-07-19-spike-followup-handoff.md` §3 gap resolved.
- **Updated memory:** `project_ip_remediation_live` reflects the resolution.

## Constraints (must NOT)

- MUST NOT copy `~/Desktop/loam-dev-archive/bin/ip-sweep.sh` into the public repo **without** reading it in full first for private paths, machine-local assumptions, or references to the private backup — it comes from the quarantined dirty-history repo.
- A clean public clone that lacks the private `bin/.ip-terms` gets a **clear, actionable failure** in strict mode (message: copy `bin/.ip-terms.example` → `bin/.ip-terms`), **never a silent skip**. `release.sh` is maintainer tooling, so the honest failure is correct — this **supersedes** the earlier "must skip cleanly for strangers" constraint (D4; strangers are not the release audience).
- MUST NOT weaken the existing `check-own-synthesis.py` behavior.
- MUST NOT leave `release.sh` referencing a script that does not exist in the repo (the current defect).
- MUST NOT expand this into the broader IP-remediation work (that is closed per `project_ip_remediation_live`) — scope is only re-enabling the release gate.

## Acceptance Criteria

1. Run `IP_SWEEP_STRICT=1 bash bin/ip-sweep.sh` directly in a disposable clone configured with test terms; the transcript shows the actual strict sweep ran. Separately inspect `bin/release.sh` and prove its existing executable check invokes that script with `IP_SWEEP_STRICT=1`. **Do not run `bin/release.sh` as verification:** it commits, tags, and pushes after the gate.
2. `grep -n 'ip-sweep' bin/release.sh` resolves to a script that exists in the repo, OR the block is removed (no dangling reference).
3. (Option 1a) `bin/ip-sweep.sh` exists in the public repo, is executable, and in **strict** mode **hard-fails with an actionable message** (copy `bin/.ip-terms.example` → `bin/.ip-terms`) when `bin/.ip-terms` is absent — verified by running it without the terms file. (Supersedes the original "skips cleanly" criterion: the honest gate fails loudly for the maintainer.)
4. `bin/verify-template.sh` → `ALL OK` (release.sh change did not break the template).
5. The chosen approach and rationale are recorded (grill decision), and `project_ip_remediation_live` memory reflects the resolution.
