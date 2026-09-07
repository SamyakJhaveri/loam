# CI and agent efficiency changes

The main CI cost came from a recursion fixture that repeatedly quoted an
already quoted shell command. This change keeps the neighboring depth-10 allow
and depth-11 deny cases, adds a mutation control, and rejects commands larger
than 400,000 UTF-8 bytes before expensive policy parsing. The outer command is
tokenized once. Security decisions remain synchronous.

The earlier local diagnosis measured the original test at 262.133 seconds and
the reduced fixture at 1.230 seconds. Those are individual local test timings,
not a measured hosted CI speedup. The focused policy suite on the integrated
implementation passed in 3.073 seconds. A size limit bounds accepted bytes; it
does not prove every accepted parser input finishes before the host timeout.

## One validation owner and reusable evidence

`seed/.agents/lib/validation.py` supplies the shared `run`, `check`,
`fingerprint`, and `pre-commit` commands. Generated projects use
`.agents/lib/validation.py`. The existing Claude runner and both agents' commit
adapters call that implementation. Loam runs `bin/verify-template.sh` once;
workers use focused checks while editing.

The receipt binds required command results to HEAD, staged entries, nonignored
tracked and untracked contents, deletions, executable modes, symlink targets,
and runtime identity. A fresh `run` executes checks; `check` reuses a matching
receipt. Missing tools, missing required tests, failed checks, and incomplete
receipts block. Non-Python projects declare commands in `.agents/validation.json`;
a project with no executable tests needs an explicit justified `not_applicable`.
These are local provenance checks, not signatures against a malicious owner.

Loam receipts also bind the known tools behind the shell gate, including native
Claude/Codex implementations and the selected Copier environment. Reusable
evidence requires a directly installed Copier executable; a dynamically resolved
`uvx copier` run can still use the public gate but cannot supply this receipt.
Unrecognized native launch wrappers fail closed. The missing-native-CLI
diagnostic override cannot mint or reuse production evidence.
Configured shell checks declare `runtime_dependencies` for external tools;
an empty declaration means the check intentionally uses shell builtins only.
This explicit declaration avoids pretending to discover arbitrary shell or
program dependencies automatically.

Stage intended inputs before validation. A plain commit in a separate command
requires a valid receipt, staged/worktree byte equality, and no omitted
nonignored untracked dependency. Unsupported compound commit forms are rejected.

The shared Stop engine scans a transcript once, checks changed filenames safely,
and accepts matching local evidence across turns. A local receipt cannot prove
remote CI passed. Explicit verification claims still need evidence without a
transcript; a delegated success summary alone does not supply it.

## Frozen checks and bounded work

The public verification and smoke wrappers create a fresh source snapshot,
preserve the caller's HEAD and index, and check both the caller and scratch
source for changes during the run. Generation checks also catch writes restored
before completion. Explicit ignored build outputs stay outside that boundary;
these checks are not an operating-system event journal.
The command deadline defaults to 840 seconds. Timeout returns failure and
bounded process-group cleanup terminates attached descendants. A deliberately
detached process is outside that portable cleanup guarantee.

Copier 9.16.0 can include dirty local files with `--vcs-ref=HEAD`. The snapshot
keeps every stage on one input state; it is not a workaround for Copier
discarding dirty files. Only the public wrapper emits final
`verify-template: PASSED` after validating the source state.

CI now reports slow tests and stage durations, cancels obsolete runs for the
same pull request, and limits jobs to 15 minutes. Release runs remain
independent. Download caches use direct dependency pins: Copier 9.16.0,
Ruff 0.15.20, Claude CLI 2.1.258, and Codex CLI 0.153.2. These pins are not a
complete transitive dependency lock.

## Agent cost and evidence limits

Team and review guidance assigns one integration owner and one validation owner,
uses bounded work reports, and retains independent final review for risky
changes. The parity inventory distinguishes unwritten adapters from missing
host features and checks the shared validation entry points.

The repository's listing scorer reports 10,817 → 10,455 plugin characters and
2,704 → 2,613 estimated listing tokens against upstream `e6c41ba`: 91 fewer
estimated tokens (about 3.4%). The seed listing is unchanged. This character-based
estimate is not a measurement of billed model tokens or whole-session savings.
No hosted after-change CI timing or comparable after-session token usage is
claimed without an actual run.

Hooks supplement the filesystem policy and execution rules. A host may continue
after a command hook times out or returns malformed output; a successful direct
handler fixture does not establish host enforcement. Live probes record those
outcomes separately and use harmless fake Git operations.

## Verification record

Reproduce focused policy, receipt, snapshot, Stop, and parity tests through
`python3 -m unittest` using their modules under `bin/tests`. The complete gate is
`bin/verify-template.sh`; do not also run an unchanged copy of its suite or
deterministic smoke stages. Use a matching receipt for unchanged-state reuse.

This session's exact commands, exits, independent findings and fixes, live host
dispatch observations, negative controls, and final gate timing are recorded in
the task evidence directory `/private/tmp/loam-efficiency-runtime`. The final
result must be read from that evidence; focused checks alone do not certify the
integrated branch. Original repositories and previous worktrees are preserved.
