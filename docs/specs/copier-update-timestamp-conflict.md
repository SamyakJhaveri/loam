# copier-update-timestamp-conflict

> Spec derived from the mechanism spike (Part 0.5 of the Phase-1 campaign, `~/.claude/plans/so-i-want-to-dazzling-manatee.md`).
> Evidence: `~/.claude/plans/2026-07-19-mechanism-spike-findings.md` §3 ("The perpetual timestamp conflict").
> Generated via `/gen-spec`, 2026-07-19. **Status: ready (grilled 2026-07-19).**
> Decided (a bug, no architecture dependency). Safe to implement independently of the Part 2 debate.

## Identity

- **Name:** copier-update-timestamp-conflict
- **Owner:** Sam
- **Status:** ready (grilled 2026-07-19)
- **Scope:** Eliminate the spurious merge conflict that `copier update` can produce because the rendered `CLAUDE.md` and `README.md` embed a render-time timestamp. Touches only two seed jinja files (and possibly `copier.yml`). No change to any other bootstrapped content.
- **Related:** `mechanism-spike-regression-test.md` (its acceptance test #5 is the red→green proof for this fix).

## Inputs

- **The defect, Verified in the spike (findings §3):** three lines embed a volatile render timestamp:
  - `seed/CLAUDE.md.jinja:3` — `> Bootstrapped from Loam on {{ "%Y-%m-%dT%H:%M:%SZ" | strftime }}. …`
  - `seed/CLAUDE.md.jinja:70` — `Today's date is {{ "%Y-%m-%dT%H:%M:%SZ" | strftime }}.`
  - `seed/README.md.jinja:3` — `> Created from [loam](…) on {{ "%Y-%m-%dT%H:%M:%SZ" | strftime }}. …`
- **Why it conflicts:** Copier's `.copier-answers.yml` persists *answers* across updates, but a `strftime` call re-evaluates on every render. Copier internally renders the old and new template revisions during update; when those renders cross a one-second boundary, the timestamps differ and its three-way merge marks those lines as conflicts (`UU`). Fast runs can therefore false-green, while two same-version renders separated by ≥2 seconds expose the root non-determinism reliably. The downstream conflict was observed twice in the spike (verbatim):
  ```
  <<<<<<< before updating
  > Bootstrapped from Loam on 2026-07-19T11:20:02Z …
  =======
  > Bootstrapped from Loam on 2026-07-19T11:21:05Z …
  >>>>>>> after updating
  ```
- **Copier facts that constrain the fix (must be re-Verified during implementation, not assumed):**
  - Answers stored in `.copier-answers.yml` are reused on `copier update` without prompting.
  - Whether a **computed answer** (`when: false` question with a `strftime` default) is *persisted once and reused* — versus re-computed each update — is **UNCERTAIN** and is the load-bearing unknown for Option B below. Implementation MUST verify this empirically before committing to Option B.

## Behavior

The bootstrap timestamp must be **stable across `copier update`** so no spurious conflict appears, while preserving the "bootstrapped on" provenance if Sam wants it. Two distinct lines, two sub-decisions:

### Sub-decision 1 — the provenance line (`CLAUDE.md.jinja:3`, `README.md.jinja:3`)

**Grill decision D2 (Sam, 2026-07-19): Option A — drop the date, keep the phrase.** Render `> Bootstrapped from Loam.` (`CLAUDE.md.jinja:3`) and `> Created from loam.` (`README.md.jinja:3`) with no `strftime` and no date. No `copier.yml` change and no persistence probe needed. Options B and C below are retained only as historical alternatives.

- **Option A (CHOSEN) — drop the timestamp.** Replace `on {{ … | strftime }}` with a static phrase (e.g. "Bootstrapped from Loam."). Simplest; zero merge surface; loses the date provenance.
- **Option B (recommended) — freeze the date in a persisted answer.** Add a hidden `copier.yml` question, e.g.
  ```yaml
  _bootstrap_date:
    type: str
    when: false
    default: "{{ '%Y-%m-%d' | strftime }}"
  ```
  and render `{{ _bootstrap_date }}` instead of `strftime` in the two files. If Copier persists the computed default into `.copier-answers.yml`, the value is identical on re-render → no conflict, provenance kept. **Gate:** verify persistence first; if it re-computes, use Option A.
- **Option C — exclude from update merge.** Move the provenance into a file Copier does not re-merge (`_exclude` or a skip-if-exists pattern). More machinery than the papercut warrants; documented only as a fallback.

### Sub-decision 2 — the "Today's date" line (`CLAUDE.md.jinja:70`)

**Grill decision D3 (Sam, 2026-07-19): remove the line entirely** — not converted to guidance. The session already knows the real current date from its own environment/system context, so the line adds only a stale-date hazard.

This line is **independently wrong**: a static render date frozen at copy time is read by every future session as "today", but it never updates. It cannot self-refresh from a template file.

## Outputs

- **Modified:** `seed/CLAUDE.md.jinja`, `seed/README.md.jinja` (and `seed/../copier.yml` if Option B).
- **Unchanged:** all other rendered content of those two files (byte-identical except the timestamp lines).
- The fix is proven by `mechanism-spike-regression-test.md` acceptance #5 and by this spec's criteria below.

## Constraints (must NOT)

- MUST NOT change any content in `CLAUDE.md.jinja` / `README.md.jinja` other than the two timestamp constructs and (for line 70) its surrounding line.
- MUST NOT introduce a new **interactive** Copier question — the fix must not add a prompt (`when: false` only).
- MUST NOT break either flavor's render: `bin/verify-template.sh` must stay `ALL OK` for default and research.
- MUST NOT silently delete the "bootstrapped from Loam" provenance without Sam's decision in the grill — present Option A vs B, let Sam pick.
- MUST NOT adopt Option B without first Verifying that Copier persists the computed answer across an actual `copier update` (else the fix does nothing).

## Acceptance Criteria

1. Bootstrap a project and commit it; create an empty template commit so the template revision advances with **no rendered content change**; then run `copier update --defaults` to that revision. The persisted `_commit` advances, `git status --porcelain` shows zero unmerged files, and neither `CLAUDE.md` nor `README.md` contains conflict markers.
2. `bin/verify-template.sh` prints `ALL OK` for both the default and research flavors.
3. `grep -nE '%Y-%m-%dT%H:%M:%SZ" \| strftime' seed/CLAUDE.md.jinja seed/README.md.jinja` returns **no** match inside a Copier-merged region (either removed, or replaced by a persisted answer).
4. **N/A — Option A chosen (D2).** No persisted bootstrap-date answer exists, so there is nothing to prove. (Original Option-B persistence criterion retained for history.)
5. The `CLAUDE.md.jinja:70` "Today's date is …" line is **removed** (D3), and no static frozen date remains that a session would misread as "today".
