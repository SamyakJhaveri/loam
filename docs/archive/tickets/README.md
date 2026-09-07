# Audit session tickets

One ticket per remaining audit session.
Run them in order or independently; each ticket is self-contained for dispatch.
The full item detail for every session lives in `docs/HANDOFF-2026-09-03-audit-sessions.md`;
each ticket points to its section there and carries the goal, branch, and checks you need to start.

## Status

| Ticket | Session | Branch | Status |
|--------|---------|--------|--------|
| [session-1](../HANDOFF-2026-09-03-audit-sessions.md) | 1: stop the bleeding | `fix/audit-s1-stop-the-bleeding` | DONE (merged, PR #5) |
| [session-2.md](session-2.md) | 2: prompts to Fable 5.1 | `fix/audit-s2-prompts` | DONE (review SHIP, merged, PR #6) |
| [session-3.md](session-3.md) | 3: review consolidation | `fix/audit-s3-reviews` | DONE (review SHIP, merged, PR #7) |
| [session-4.md](session-4.md) | 4: new hooks | `fix/audit-s4-hooks` | DONE (review FIX applied, merged, PR #8) |
| [session-5.md](session-5.md) | 5: repair sync, promote inventions | `fix/audit-s5-sync` | next |
| [session-6.md](session-6.md) | 6: research and autonomy layer | `fix/audit-s6-research` | not started |

Mark a ticket DONE here after its End-of-session review passes.

## How to run any ticket (same five steps)

1. Open a new Claude Code session in the session's own worktree, created from `main`.
   `main` now lives in the primary checkout `~/Desktop/loam`, updated through session 4.
   Create the worktree from `main`, never from a stale branch:
   `git fetch origin && git worktree add /private/tmp/loam-<name> -b <branch> origin/main`.
   Never check out `main` in two places.
2. Set the model to Fable 5.1 at `high` effort. Never higher for Fable.
3. Turn on auto mode, so `/goal` turns run unattended.
4. Paste the ticket's "Run" block.
5. When it commits and stops, open another fresh session and run that ticket's "Review" block.

## Rules every ticket inherits

- Lead is Fable 5.1 (decides, commissions, assesses, gives feedback; does not write code).
- Workers are Opus 4.8 at `xhigh`. Allowed models: Opus and Fable only.
- Workers never commit; the lead commits on the branch. Do not push, do not open a PR.
- Before commit: `bin/verify-template.sh` prints "verify-template: PASSED", `uvx pytest -q bin/tests` is green, and `bin/harness-smoke.sh` prints PASS.
- Each session also owns the rows in `docs/findings/FINDINGS.md` whose Status names it; close them and fill the closing commit.
