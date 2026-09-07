# Ticket: Session 4 - new hooks

- Branch: `fix/audit-s4-hooks`
- Full items: `docs/HANDOFF-2026-09-03-audit-sessions.md`, the "Session 4" block plus every Gap review and Research addition item tagged "session 4". All hooks go under `seed/.claude/hooks/`, each wired in `seed/.claude/settings.json`, added to `CLAUDE_HOOK_ROUTES` in the contract, and covered by a test.
- Also owned by session 4: Research addition B in the handoff (diff-scoped mutation score gate, anti-reward-hacking scan of the test half of a diff, harness hygiene at SessionStart plus the skill-usage log, command capture with exit code and experiment name), and the two `docs/findings/FINDINGS.md` rows with Status "open, owner session 4" (stop-verify-gate ruff probe; plan-review-fanout agents to xhigh). Research addition F says every run-logging hook must read the `cwd` field of the hook JSON, not `CLAUDE_PROJECT_DIR`.
- If the combined scope exceeds one workflow run, split into 4a (the six hook items) and 4b (Research B and the tracker rows) on the same branch and log both.
- Depends on: sessions 1 to 3 merged (main at `d56d008` or later).

## Start here (run before anything else)

```bash
cd ~/Desktop/loam
git fetch origin
git checkout -b fix/audit-s4-hooks origin/main
git log --oneline -1   # must show d56d008 or a later main commit
```

Local `main` is checked out in the worktree `/private/tmp/loam-audit-s3-reviews`. Do not check out `main` in `~/Desktop/loam` while that worktree exists. Docs commits that must go direct to main go through that worktree or through `git push origin HEAD:main` from a detached checkout of `origin/main`.

## Run (paste into a fresh Fable 5.1 session, high effort, auto mode)

```text
You are the Claude Fable 5.1 lead for the Loam harness audit. First run the "Start here"
block in docs/tickets/session-4.md: cd ~/Desktop/loam, git fetch origin, and create the branch
fix/audit-s4-hooks from origin/main. Do not check out main; it lives in a worktree. Confirm HEAD
is d56d008 or later before editing anything. Then read docs/tickets/session-4.md and
docs/HANDOFF-2026-09-03-audit-sessions.md in full, and run SESSION 4 only, then stop.
Session 4 owns its six hook items, Research addition B, and the two FINDINGS.md rows marked
"owner session 4". Split into 4a and 4b on the same branch if one workflow run cannot hold it.
Read "Operating model" first; it defines your loop. Run yourself at high effort, never higher;
Opus 4.8 workers run at xhigh. Orchestrate with dynamic workflows and the ultracode quality
patterns. In auto mode, set /goal to session 4's Goal line (below).
You decide, commission, coordinate, and assess each worker's diff on four axes (correctness,
Samyak's intent, taste, thoroughness); send work back with feedback, capped at two rounds per
worker. You do not write the file edits; Opus 4.8 workers do. A worker cannot read your thinking,
so every brief stands alone. Branch is fix/audit-s4-hooks. You commit; workers never commit; do
not push and do not open a PR. Run a Codex second-opinion round on the diff before you finish,
capped at two rounds; findings are candidates, not verdicts. Update the Execution log when done, then stop so the review can run
in a fresh context. Please remove all mannered prose.
```

## Goal (the lead sets this as `/goal`)

every item tagged for session 4 is implemented and committed on `fix/audit-s4-hooks`, each new hook is wired in `seed/.claude/settings.json`, added to `CLAUDE_HOOK_ROUTES` in the contract, and covered by a test, and this session's transcript shows each new hook run against a synthetic stdin envelope with the expected output, `uvx pytest -q bin/tests` printed 0 failed, `bin/verify-template.sh` printed "verify-template: PASSED", and `bin/harness-smoke.sh` printed PASS. No file outside the session 4 items is changed; do not push or open a PR. Or stop after 30 turns and say what is left.

## Verify

- Each new hook run against a synthetic stdin envelope prints the expected output.
- Each new hook is in `CLAUDE_HOOK_ROUTES` and has a test in `bin/tests/test_seed_claude_hooks.py`.
- The two FINDINGS.md rows owned by session 4 are closed with their closing commit.
- Four checks green.

## Review (paste into another fresh Fable 5.1 session, high effort)

Use the "End-of-session review" prompt in the handoff, with N=4 and branch `fix/audit-s4-hooks`.

## Done when

The review verdict is SHIP, the four checks are green, and this ticket is marked DONE in `README.md`.
