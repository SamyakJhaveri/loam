# First-run design work and checks

Status: design work only. Runtime implementation remains deferred. Root owns integration and the repository check; independent agents supply bounded source investigation and correctness review.

Critical point: ownership recovery must preserve unknown execution and cannot create a replacement empty authority store.

1. Verify the saved baseline and current main before designing. Checks: `git rev-parse HEAD main origin/main`, `git ls-remote origin refs/heads/main`, and Python SHA-256 comparisons against `pause-checkpoint.json` and `snapshot-manifest.json`. Expected: the recorded commit and matching saved files. Completed. `PATH="$PWD/.venv/check/bin:$PATH" bin/check` completed with `31 passed in 8.95s` and `check: PASSED`, exit 0. The existing environment was used; no dependencies were installed.
2. Write the first-run, ownership, storage and recovery specification, with alternatives and failure cases. Check: `python3 /private/tmp/loam-first-run-doc-check.py design`. Expected: `First-run design checks: PASSED`, including local links, required boundaries and preservation of historical snapshots. Run before updating the navigation and current records.
3. Update the living decision record, runtime overview, proving-slice commands and restart handoff. Check: `python3 /private/tmp/loam-first-run-doc-check.py final`. Expected: `First-run final checks: PASSED`, including current Node command mappings and documentation-only changes against the saved session baseline.
4. Obtain a fresh-context correctness review, repair confirmed gaps and complete the written self-attack. Check: rerun the final document checker and `git diff --check`; expected PASS and exit 0. Confirm `git status --short --branch` still contains only the architecture directory. Do not repeat the full repository suite for prose changes alone.

The temporary document checker and before-edit copies are session validation artifacts. They implement no factory behavior. The saved pause checkpoint remains historical; the new validation record identifies intentional changes separately. No commit or publication is part of this task.

Verified outcome: the design and final document checks passed. The fresh-context review found bootstrap-authority and interrupted-restore gaps; both were repaired and the bounded rereview confirmed the repairs. The written self-attack and requirement mapping are in [first-run-validation.md](first-run-validation.md). Exact runtime probes and file-level tickets remain subsequent work.
