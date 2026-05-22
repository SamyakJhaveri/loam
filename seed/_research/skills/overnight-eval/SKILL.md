---
name: overnight-eval
description: >
  Long-running evaluation campaign with tmux isolation. Use when running any eval batch
  exceeding ~30 minutes, canonical benchmark runs, or when the user will be away during
  execution. Pre-flight verification, tmux launch, monitoring, post-flight analysis.
  NOT for: short interactive runs (use eval-run instead).
auto-activate: false
---

# Overnight Eval Campaign

Use when launching a long-running evaluation batch that needs tmux deployment
or should run unattended (overnight, weekend).

**Trigger:** When user types `/overnight-eval` with optional arguments.

## Arguments

- `$ARGUMENTS` — shorthand or explicit flags for the eval script.
  If omitted, prompt interactively.
- `--dry-run` — run pre-flight only, do not launch
- `--session-name <name>` — tmux session name (default: `eval-campaign`)
- `--alert-threshold <N>` — error rate % that triggers alert (default: 50)

## Iron Law

```
NO EVAL CAMPAIGN WITHOUT PRE-FLIGHT VERIFICATION.
Every API key, environment dependency, dataset, and eligibility check MUST pass
before the batch command is issued. No exceptions.
```

## Anti-Rationalization Table

| Excuse | Reality |
|--------|---------|
| "I'll check the API keys later" | A failed key means wasted hours and zero results |
| "The environment is probably fine" | 2 seconds to verify. Hours to re-run |
| "I can run it in the foreground" | Terminal disconnect = killed process. Always tmux |
| "Resume will catch anything I miss" | Resume perpetuates pre-flight errors |
| "I'll analyze tomorrow" | Tomorrow you won't remember the parameters. Log now |

## Workflow

### Phase 1: Pre-Flight Verification

Run ALL checks. Every check must pass before proceeding.

1. **Environment**: Verify venv/dependencies, Python version, key packages
2. **Hardware** (if applicable): GPU availability, memory, utilization
3. **API Keys**: Check only for selected models
4. **Dataset/Source**: Verify benchmark data exists and is accessible
5. **Eligibility**: Verify task list, apply exclusions

Display pre-flight summary and **wait for user confirmation**.

If `--dry-run`, stop after displaying summary.

### Phase 2: Launch in tmux

```bash
tmux new-session -d -s <session-name> -c <project-root>
tmux send-keys -t <session-name> "<eval-command> 2>&1 | tee results/campaign_$(date +%Y%m%d_%H%M%S).log" Enter
```

Verify tmux session is running before proceeding.

### Phase 3: Monitor (Periodic)

The user can check progress at any time:
- Is the tmux session still alive?
- How many results completed?
- Current pass/fail rates
- Error spike detection (alert if error rate exceeds threshold)

### Phase 4: Post-Flight Analysis

After completion:
1. Run analysis scripts
2. Write structured campaign log
3. Generate summary with results table
4. Alert user (desktop notification if available)

### Phase 5: Handoff

Present results summary and recommended next steps:
1. Review campaign log for anomalies
2. Refresh dashboard if applicable
3. Commit results
4. Update paper sections if relevant
