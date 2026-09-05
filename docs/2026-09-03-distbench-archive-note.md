# distbench: archived, not migrated

> Written 2026-09-03 during Loam harness audit session 5.
> distbench is not edited by this audit; this note only records its state and what session 5 promoted from it.

## State

- distbench lives at `~/Desktop/distbench` and is archived at commit `410c07e` (full `410c07e9baa62a06ecfe3d076ac45c99f2dc52ce`), which is its current HEAD.
- Verified read-only: `git -C ~/Desktop/distbench rev-parse HEAD` returns `410c07e9baa62a06ecfe3d076ac45c99f2dc52ce`.
- Its Loam pin in `~/Desktop/distbench/.copier-answers.yml` is `_commit: v3.6.2`, against `_src_path: gh:samyakjhaveri/loam`.
- That pin is dead: `v3.6.2` no longer exists as a tag on the public repo, because the public `gh:samyakjhaveri/loam` was reset to a fresh history at `v1.0.0` (2026-07-02 cutover).
- Verified: `git ls-remote --tags https://github.com/samyakjhaveri/loam | grep -c v3.6.2` returns `0` (the remote returns 9 tags, none of them `v3.6.2`).
- The current release in this checkout is `VERSION` = `2.1.0`, so `copier update` cannot run against the old pin without re-pinning.

## Inventions session 5 promoted into Loam

- The parity checker moved out: distbench `agent-parity.toml` plus `scripts/agent_parity/parity.py` became `bin/agent_parity/parity.py` plus `seed/agent-parity.toml`, wired check-only.
- The validate-sentinel trio moved out: distbench `.claude/hooks/run-validate-waves.sh`, `sentinel-cleanup.sh`, and `pre-commit-gate.sh` became `seed/.claude/hooks/` copies.
- Those hook copies are generalized: ruff and mypy are guarded on the presence of `pyproject.toml`, so a rendered project without one skips them cleanly.

## Not promoted, and why

- The parity catalog and its report are not promoted, because they are distbench-only assets tied to that project's own agent set.
- The effort policy is not promoted, because it fixes worker effort in a way that contradicts Loam's workers-at-xhigh convention.
- The memory-agent block of `sentinel-cleanup.sh` is not promoted, because the seed ships no agents for it to clean up after.

## Dogfood plan

- distbench stays archived at `410c07e`; it is not updated in place.
- The dogfood target is a NEW distbench rendered fresh from the updated seed, per Samyak's 2026-09-03 answer.
