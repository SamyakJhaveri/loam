# three-tier-divergence-decision

> **This is a DECISION BRIEF, not an implementation spec.** It frames the one architectural question the mechanism spike leaves open, so Sam's grill / the Part 2 debate can resolve it into an ADR. It does NOT decide the direction — that is the debate's job (Fable = devil's advocate).
> Evidence: `~/.claude/plans/2026-07-19-mechanism-spike-findings.md` §4–§6.
> Campaign context: `~/.claude/plans/so-i-want-to-dazzling-manatee.md` "Part 2 — Direction debate", Agenda Items 0/1/2.
> Generated via `/gen-spec`, 2026-07-19. **Status: decision-required (blocks: `template-sync-promote-generic-user` Part B, and the roadmap).**

## Identity

- **Name:** three-tier-divergence-decision
- **Owner:** Sam (decision); Fable (devil's advocate in the debate)
- **Status:** decision-required — resolve via grill/debate → ADR
- **Scope:** ONLY the mechanically-settled Part 2 items the spike informs — Item 0 (mechanics before governance), Item 1 (what a "personal Loam" IS), Item 2 (fork-based vs data-based divergence). Part 2 Items 3/4/5 (upward-flow automation, cuts, differentiation commitments) need Part 1 ("State of Loam") first and are **out of scope here**.

## Context — what the spike settled (so the debate starts from evidence, not vibes)

All Verified against copier 9.17.0 / git 2.55.0 / loam v1.0.0; an independent read-only agent confirmed all source claims.

- The "seed regrows the seed" three-tier model is **not new machinery**. It is: fork + `upstream` remote + `copier update` (downward) + `git merge upstream` (canonical→personal) + a thin `template-sync promote` helper (upward). Nothing bespoke.
- **The load-bearing constraint:** a personal Loam is a fork of the *template repo itself*, which has no `.copier-answers.yml`/`_commit` baseline, so **Edge A (canonical→personal) cannot `copier update`** (Verified error: "Cannot obtain old template references from `.copier-answers.yml`"). Its only sync mechanism is raw `git merge upstream`, which surfaces every divergence as an ordinary git conflict (`UU` / modify-delete `UD`).
- The two `→ project` edges (canonical→project, personal→project) **do** get Copier's divergence-preserving three-way merge and work cleanly.
- So the asymmetry is the whole story: **data-based divergence (Copier answers/flavors) is what makes the project edges pleasant; the fork-based personal tier pays a permanent git-merge tax and has no Copier baseline.**

## The decision to make

**Is the fork-based "personal Loam" tier worth its cost, or should per-user divergence be data-based on a single canonical instead?** Everything else in Part 2 Item 0/1/2 follows from this.

### Option 1 — Fork-based personal Loam (Sam's current diagram)
Each user forks the canonical template repo; syncs canonical→personal via `git merge upstream`; points `copier copy`/`copier update` at their fork for their projects.
- **For:** Maximum divergence freedom; a personal Loam can restructure `seed/` arbitrarily; matches Sam's mental model exactly; contribute-up is a normal PR.
- **Against (spike evidence):** Edge A has no Copier baseline → every canonical sync is a raw `git merge` with real conflicts; the `template-sync promote` PR target is fork-ambiguous (currently hardcoded to `samyakjhaveri/loam`); chezmoi explicitly rejects fork-based machine divergence for exactly this merge pain; a "personal Loam" provides **no user-visible invariant** beyond "fork + merge upstream + point Copier at the fork" (spike could not name one).
- **If chosen:** adopt a standard scheduled-merge pattern (cruft-style auto-PR) for Edge A; fix `template-sync.sh:295` to retarget the fork's canonical; document the fork convention; STOP inventing personal-tier machinery.

### Option 2 — Data-based divergence on a single canonical (no personal fork)
Per-user customization lives as Copier answers + flavor overlays + marketplace/skill selection on one canonical; there is no `canonical→personal` edge to merge at all.
- **For:** Uses the mechanism that already works cleanly (Copier three-way merge on the project edge); no git-merge tax; no fork-target ambiguity; simplest supply chain.
- **Against:** Caps how far a user can diverge (bounded by what flavors/answers express); heavier customization (restructuring `seed/`) is awkward without a fork; may not match Sam's "each personal Loam is a different shape" intent.
- **If chosen:** the "personal Loam tier" collapses into "flavors + answers"; Part 2 architecture feature-work largely disappears; roadmap focuses on the flavor/answer surface instead.

### The test to apply in the debate (from campaign Item 1)
> Name ≥1 user-visible invariant the personal fork tier provides **beyond** "fork canonical, merge upstream, point Copier at the fork." If none survives the grill, document the fork convention and stop personal-tier architecture work.

## What the decision unblocks / gates

- **Unblocks:** `template-sync-promote-generic-user.md` Part B (the PR-target retargeting shape depends on whether forks exist).
- **Gates:** the campaign roadmap (`so-i-want-to-dazzling-manatee.md` sequencing) and the one-month exit criterion (c): "one ADR chooses documented fork-convention OR explicit personal-overlay."
- **Preserve regardless of direction (campaign Item 5):** the genuine novelty is the **dual-harness (Claude + Codex) seed** and the **regeneration/soil narrative** — "forks + Copier give the rest for free." Do not let the divergence decision erode those.

## Constraints on the decision (must NOT)

- MUST NOT be decided without running the campaign's Part 1 ("State of Loam") for Items 3/4/5 — this brief resolves only Items 0/1/2.
- MUST NOT ignore the **dual-role IP-leak** constraint: canonical is "also Sam's personal instance", and `.claude → seed/.claude` means Sam's session edits mutate the shipped template. The only present guard is `bin/check-own-synthesis.py` (a local dev guard); note that `bin/release.sh:37-41` expects a `bin/ip-sweep.sh` that is **not in the repo**, so the release-time IP gate currently no-ops (see the handoff carry-forward). Any chosen model must keep this leak a first-class "must NOT".
- MUST NOT assume the shipped **Codex** runtime works — the campaign Verified it is broken (session-start hook exits 1; repo skills discovered from the wrong dir; spoofable sentinel). Implementation of any decision happens in **Claude Code (Opus 4.8), not Codex**, until Track 6 fixes land.
- MUST NOT pre-empt the debate here — this document presents evidence + options + a test, and stops. The recommendation below is an input to the grill, not a verdict.

## Recommendation (an input to the grill, not a decision)

The spike evidence leans toward **documenting the fork convention (Option 1) rather than building new personal-tier machinery** — because the fork path already works with standard git, and Copier already handles the project edges — while treating **data-based divergence (Option 2) as the default for users who don't need to restructure `seed/`**. In short: forks are allowed and documented (with cruft-style auto-PR for Edge A and a fixed promote target), but the *recommended* path for most users is flavors + answers, because that is the edge with no merge tax. The grill should try hard to break this and to surface any personal-tier invariant that would justify more machinery.

## Definition of "decided" (acceptance)

1. An ADR exists (proposed `docs/adr/NNNN-divergence-model.md`) recording the chosen model and the **winning argument**, per campaign Part 2 outputs.
2. The ADR answers the Item-1 test explicitly (names an invariant, or states none survived and the fork convention is documented).
3. The ADR states the resolution for `template-sync.sh:295` targeting (or explicitly defers it with a named follow-up).
4. The ADR records the dual-role IP-leak and Codex-runtime constraints as carried-forward must-NOTs.
5. The decision passes `/plan-review-invoke` in a fresh session (campaign Part 2 verification bar).
