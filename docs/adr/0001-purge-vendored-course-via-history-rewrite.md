# ADR-0001 — Purge vendored third-party course from git history via rewrite

- Status: Accepted
- Date: 2026-06-30

## Context

Loam's repository has been public on GitHub (`samyakjhaveri/loam`) since ~2026-05-23.
For that window, a vendored third-party paid course lived in the tree and history —
copyrighted material that must not ship with, or remain recoverable from, a public
MIT-licensed template. At HEAD it sat under `soil/jvc/` (5.4M) and `soil/foundation/`
(1.7M), but **before the v3.0 restructure `git mv`'d it into `soil/`, the same material
lived under earlier top-level paths** — `claude_code_course_files/` (with `jvc_vault/`,
`jvc_foundation/`, "Claude Folder Setup.pdf") and `temp/` — added in commits such as
d487f712 ("…stuff from Jake Van Clief") and 4f6586de ("…Paid 'The Vault' notes"). A
`git mv` preserves the old-path blobs, so the course is recoverable by SHA under **all**
of those paths, not just `soil/`. Removing the files at HEAD (`git rm`) leaves every one
of them intact in history.

## Decision

Purge the course from **every** commit with `git filter-repo --invert-paths` on a fresh
clone, then force-push the rewritten `main` and re-push all tags. The `--path` list must
cover **every** historical home of the material, not just its HEAD location — at minimum
`soil/jvc`, `soil/foundation`, `claude_code_course_files`, and `temp`, plus anything a
full history sweep surfaces
(`git log --all --name-only --pretty= | awk -F/ '{print $1}' | sort -u` enumerates every
top-level directory that ever existed). **Verify with a broad history grep** —
`git log --all --raw --pretty= | grep -iE 'jvc|foundation|vault|full_toolkit'` must be
empty — **not** a `soil/`-scoped path check, which would falsely pass while the old paths
still carry the course (the "verification monoculture" trap in `known-issues.md`). The
rewrite runs **once**, after the working-tree removal and own-synthesis content rewrite
are already on `main`, so a single force-push yields both a clean HEAD and clean history.
Tags are preserved (re-pointed automatically by filter-repo) so `copier update` keeps
working for existing adopters — Copier resolves from tags, not HEAD.

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
  reworded into own-synthesis and is regression-guarded by `bin/check-own-synthesis.py`.
- **Commit *messages* survive `filter-repo`.** Subjects like d487f712 ("…Jake Van Clief")
  keep naming the course/author after the blob purge. Add `--replace-message` to the same
  pass if a fully scrubbed log is wanted; otherwise this residual attribution is accepted.
- The same force-push is the one low-cost window to purge any *other* material that should
  not be public. The historical top-level directory list was audited before the rewrite so
  the `--path` set could be decided in a single pass.

## Alternatives considered

- **`git rm` only (no history rewrite).** Rejected: leaves the course fully recoverable
  by SHA — does not remediate the exposure.
- **Nuke and recreate the repo.** Rejected: destroys all release tags and breaks
  `copier update` for every existing adopter.
