# Accepted mixed policy: design continuation

Critical point: reconnecting or recovering must not restart an existing job, renew an expired execution budget or bypass an interrupted native worker's authority check.

1. Verify preservation before changing records. Check: compare every `maintenance-checkpoint.json` hash with the current files and save a before-copy. Expected: `Offline policy baseline: PASSED`. Completed before edits; Git status contains only the untracked architecture directory.
2. Record accepted D-OFFLINE and specify the job record and operator sequence. Check: `python3 /private/tmp/loam-offline-check.py`. Expected: `Offline policy documentation: PASSED`, accepted status in current records, working links, unchanged historical files/intake and no tracked changes.
3. Review the authority/disconnect boundary independently, fix confirmed gaps and record the self-attack. Check: repeat the documentation check, changed-document whitespace scan and `git diff --check`; create and verify `offline-policy-checkpoint.json`. Expected: PASS. No runtime, native job, service or package changes.

The user's answer settles the mixed offline default. It does not select numerical limits, permit general autonomous native work or authorize runtime implementation. The following job-record and setup details remain mechanism recommendations.
