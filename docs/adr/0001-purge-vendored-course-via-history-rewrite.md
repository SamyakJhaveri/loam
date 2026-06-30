# ADR-0001 — Purge vendored third-party course from git history via rewrite

- Status: Accepted
- Date: 2026-06-30

## Context

Loam's repository has been public on GitHub (`samyakjhaveri/loam`) since ~2026-05-23.
For that window, a vendored third-party paid course lived in the tree and history under
`soil/jvc/` (5.4M) and `soil/foundation/` (1.7M) — copyrighted third-party material that
must not ship with, or remain recoverable from, a public MIT-licensed template. Removing
the files at HEAD (`git rm`) leaves them fully intact in history, reachable by any prior
commit SHA.

## Decision

Purge `soil/jvc/` and `soil/foundation/` from **every** commit with
`git filter-repo --invert-paths` on a fresh clone, then force-push the rewritten `main`
and re-push all tags. The rewrite runs **once**, after the working-tree removal and the
own-synthesis content rewrite are already on `main`, so a single force-push yields both a
clean HEAD and clean history. Tags are preserved (re-pointed automatically by
filter-repo) so `copier update` keeps working for existing adopters — Copier resolves
from tags, not HEAD.

## Consequences

- **History is intentionally discontinuous.** Commit SHAs before the rewrite no longer
  exist on the canonical remote. Collaborators and CI must re-clone or
  `git fetch && git reset --hard origin/main` — never `merge`, which would reintroduce
  the purged blobs.
- **A force-push is not complete remediation.** Forks, open PR refs, and GitHub's cached
  commit views can retain the material until server-side gc. Given the ~5-week public
  window, the material is treated as already-distributed; a GitHub Support
  sensitive-data-removal request is optional, not required.
- The copyrighted bulk is removed; borrowed framing in `seed/` rule files was separately
  reworded into own-synthesis in the same release.

## Alternatives considered

- **`git rm` only (no history rewrite).** Rejected: leaves the course fully recoverable
  by SHA — does not remediate the exposure.
- **Nuke and recreate the repo.** Rejected: destroys all release tags and breaks
  `copier update` for every existing adopter.
