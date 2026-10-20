# Harness notes for Loam only

`seed/docs/HARNESS.md.jinja` ships to every generated project, so facts that hold only for the Loam repository or its owner's machines live here.
Token figures are byte counts divided by four, not a tokenizer result.

## Skill-listing budget

Loam's `bin/check` asserts the `sam-cc-setup` plugin listing weight against the `LISTING_BUDGET` default in its skill-listing step; that default is the one home for the number.
Lower it when the listing shrinks; never raise it without saying why.
It rose from 448 to 565 on 2026-09-09 (a4f61fa) when `plan-review` became model-invocable, and to 634 the same day (5af0946) when the judge and reviewer became plugin agents.
A rendered project's `bin/check` asserts no listing budget.

## The owner's memory-store remote

On the owner's machines the store remote uses the ssh alias `jhaveris`, the same alias `bin/runner` uses:

    git -C ~/memstore remote add origin jhaveris:memstore.git

## Measured cost, v2.3.0 to v3.0.0

A record of the v3.0.0 cut, not maintained.
Rendered-project rows were measured in a `copier copy` render of each version; repo-side rows in the repo itself.

| Row | Before (v2.3.0) | After (v3.0.0) |
|---|---|---|
| Hooks shipped in `.claude/hooks/` | 15 | 2 |
| `PreToolUse` hook entries matching Bash | 7 | 0 |
| Hook runs per Edit or Write | 1 ruff run | 0 |
| Always-on prose bytes (`CLAUDE.md` + `AGENTS.md`) | 7862 | 1125 |
| Check wall time, one script | 207 s (`bin/verify-template.sh`) | 5 s local, 7 s in CI |
| Seed hook and lib lines | 2309 | 71 |
| `bin/` plus `bin/tests/` lines | 11377 | 1525 |
| Marketplace skills shipped | 26 | 3 |

## Daily verify-loam upkeep

`bin/verify-loam-daily` clones origin/main and runs `/pstack:maintain-verification-skill` on verify-loam with `claude -p` on `claude-opus-5-5` at effort `xhigh`, in auto permission mode.
It never pushes.
Each run writes `result.json`, `report.md` and the stream-json transcript `claude.jsonl` under `~/.local/state/loam/evidence/verify-daily/<stamp>/`.
Only `clean`, or `changed` with a commit on the run's local `verify/maintain-<stamp>` branch beyond origin/main, counts as ok; `blocked`, a missing report and any other word exit non-zero.
A `changed` run keeps its clone in `<stamp>/loam` for the owner to review; every other run, and every `--probe`, deletes it.
`VERIFY_DAILY_TIMEOUT` (default 14400 seconds) kills a hung `claude`, so a stuck run cannot block the next day's run.
`--probe` checks claude, login and an enabled pstack plugin at $0.

The daily schedule is a launchd job the owner installs after merge; nothing in the repo installs it.
macOS privacy rules refuse a launchd job any read under `~/Desktop` ("Operation not permitted", checked 2026-10-18), so the job runs an installed copy and clones from GitHub:

    install -m 755 bin/verify-loam-daily ~/.local/bin/verify-loam-daily

Reinstall the copy after the script changes. Save this as `~/Library/LaunchAgents/com.samyakjhaveri.verify-loam-daily.plist`.
Its PATH must name the directories that hold the toolchain `claude`, `uvx` (`~/.local/bin`), `jq` (Homebrew), and `git` and `perl` (`/usr/bin`); change the node directory when the toolchain moves to a new node version.

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
  <key>Label</key>
  <string>com.samyakjhaveri.verify-loam-daily</string>
  <key>ProgramArguments</key>
  <array>
    <string>/Users/samyakjhaveri/.local/bin/verify-loam-daily</string>
  </array>
  <key>StartCalendarInterval</key>
  <dict>
    <key>Hour</key>
    <integer>6</integer>
    <key>Minute</key>
    <integer>0</integer>
  </dict>
  <key>EnvironmentVariables</key>
  <dict>
    <key>PATH</key>
    <string>/Users/samyakjhaveri/.local/state/loam/toolchains/node-v24.21.0-darwin-arm64/bin:/Users/samyakjhaveri/.local/bin:/opt/homebrew/bin:/usr/bin:/bin:/usr/sbin:/sbin</string>
    <key>VERIFY_DAILY_ORIGIN</key>
    <string>https://github.com/SamyakJhaveri/loam.git</string>
  </dict>
  <key>StandardOutPath</key>
  <string>/Users/samyakjhaveri/Library/Logs/verify-loam-daily.log</string>
  <key>StandardErrorPath</key>
  <string>/Users/samyakjhaveri/Library/Logs/verify-loam-daily.log</string>
</dict>
</plist>
```

Load it with `launchctl bootstrap gui/$(id -u) ~/Library/LaunchAgents/com.samyakjhaveri.verify-loam-daily.plist`.
`launchctl kickstart -k gui/$(id -u)/com.samyakjhaveri.verify-loam-daily` starts a paid run at once; read the last run with `launchctl print gui/$(id -u)/com.samyakjhaveri.verify-loam-daily | grep 'last exit'`.
