# Maintenance and remote work: design sequence

Critical point: an SSH disconnect must not duplicate a remote GPU run or lose the identity of surviving native work.

1. Preserve the current snapshot and inspect existing maintenance/remote mechanisms. Check: Python comparison against `two-host-checkpoint.json`, current Git status and targeted source/remote-tool inspection. Expected: preserved records and actual observations, with no jobs launched or configuration changed. Baseline comparison completed with `Maintenance baseline preservation: PASSED`.
2. Specify one maintenance model and an SSH execution-host extension for Mac-led Linux work. Include input identity, launch recovery, offline behavior, upgrades and replacement machines. Check: `python3 /private/tmp/loam-maintenance-check.py design`. Expected: `Maintenance design checks: PASSED`, valid links, explicit one-owner/remote-ledger boundaries and required failure cases.
3. Update current host scope, first complete proof, module map and handoff; add bounded implementation tickets. Check: `python3 /private/tmp/loam-maintenance-check.py final`. Expected: `Maintenance final checks: PASSED`, current navigation and remote proof requirements, with unchanged prior snapshots/intake and tracked source.
4. Obtain fresh-context correctness review, repair confirmed gaps and record the self-attack. Checks: repeat final document check, independent `git diff --check`, new preservation checkpoint. Expected: PASS and exit 0. Native/GPU jobs, runtime code, package changes and recurring maintenance automation remain deferred.

The user has expanded the required workflow to local Mac supervision of Linux agents/GPU runs and future replacement Mac/Linux machines. Preserve that requirement without introducing a general cluster scheduler or automatic cross-machine authority takeover.
