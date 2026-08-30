# Rendered Harness Contract Design

**Date:** 2026-08-30
**Status:** Approved design, pending implementation plan

## Purpose

Loam renders a Claude Code and Codex harness into each generated project. The
current release gate proves that Copier can render the template, the catchup
symlink resolves, and selected configuration files parse. It does not prove
that the complete generated harness is connected or enforceable.

This change introduces one deep verification interface. It checks the rendered
project as a complete harness instead of checking isolated files.

The domain term for this interface is **Rendered Harness Contract**. Its
canonical definition lives in `CONTEXT.md`.

## Goals

1. Make `bin/verify-template.sh` the single public verification command.
2. Verify the core generated-project contract without requiring Claude or Codex.
3. Detect missing files, broken links, inert hooks, weak Codex policy, stale
   active routes, and non-executable hook scripts.
4. Keep native Claude and Codex checks as supplemental checks when their command
   line tools are installed.
5. Report all contract failures in one run with enough detail to repair them.

## Non-goals

This change does not repair unrelated review findings. Those changes remain
separate because Loam permits one behavior change per session.

The deferred findings are:

1. The `sam-superpowers` dependency on the removed `writing-plans` skill.
2. Stale public, plugin, root, and release-loop documentation.
3. Intellectual-property sweep coverage for tracked cultivation content.
4. The machine-local path in `docs/specs/cliefnotes-wisdom.md`.
5. Duplicate ownership of the concurrent-checkout hook.

## Chosen architecture

`bin/verify-template.sh` remains the public entry point. A new Python module,
`bin/rendered_harness_contract.py`, owns the semantic checks. It uses only the
Python standard library.

The shell wrapper performs these stages:

1. Run the contract unit tests.
2. Render a normal project with Copier into a temporary directory.
3. Run the contract checker against the source and rendered roots.
4. Run native Claude and Codex checks when their tools are installed.
5. Run the existing repository naming checks and print the final summary.

The core checks do not depend on either agent command line tool. A missing tool
may skip only its native supplemental checks.

The checker accumulates failures. Each failure uses this form:

```text
FAIL [contract-area]: explanation
```

It exits nonzero when any failure exists.

## Contract areas

### Copier topology

The checker has an explicit list of required generated harness paths. It also
has an explicit list of retired paths that must remain absent.

The required set covers the rendered Claude configuration, Claude hook scripts,
the shared catchup skill, Codex configuration, Codex rules, Codex hook wiring,
and rendered agent instructions.

This is a product contract, not a generic directory scan. Adding or removing a
required harness component therefore requires an intentional contract update.

### Symlinks

The checker proves that `.claude/skills/catchup` is a symlink. It proves that
the link resolves to `.agents/skills/catchup`. It also proves that the target
contains `SKILL.md`.

### Claude hooks

The checker parses `.claude/settings.json`. It validates supported event names,
known matcher values, and command-backed hook definitions.

For every command that invokes a repository script, the checker proves that the
script exists inside the rendered project. It also proves that the Ruff hook
reads `tool_input.file_path`.

The inline Ruff command moves to `.claude/hooks/ruff-after-edit.sh`. The script
reads the hook envelope from standard input. It ignores non-Python files. It
runs `python3 -m ruff check --fix` only for a Python file. Ruff remains
non-blocking, which preserves the current behavior.

### Codex policy

The generated project gains `.codex/hooks.json` and
`.codex/hooks/pre-tool-policy.py`.

The hook runs on `PreToolUse` for shell commands. It reads the command from
`tool_input.command`. It denies a recognized force push with the current Codex
hook result:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Force pushes are blocked by repository policy."
  }
}
```

The policy parser recognizes Git global options and common wrappers before the
`push` subcommand. It denies long force flags, assigned long force flags, short
`-f`, clustered short flags containing `f`, and plus-prefixed refspecs. It does
not deny a normal push.

The hook fails closed when it recognizes a Git push but cannot safely classify
a force-related argument. Malformed or unrelated hook input exits without a
decision so it cannot disable unrelated tools.

`default.rules` remains as defense in depth. It prompts for ordinary pushes and
forbids the direct force forms that its prefix matcher can express. The hook is
the argument-aware enforcement layer.

### Prose routes

The checker validates a small, explicit set of active harness references in the
rendered `AGENTS.md` and `CLAUDE.md`. Each referenced repository path must
exist. Each required command route must point at the active interface.

The checker does not scan every Markdown link. Historical specifications,
examples, and external URLs are outside this contract. This avoids false
failures from non-runtime documentation.

### Executable modes

Every repository script invoked by a Claude or Codex hook must exist and have an
executable mode bit. The checker validates the rendered files, not only their
source copies.

## Native supplemental checks

When Claude Code is installed, the wrapper validates the main Claude directory,
the shared skill directory, and each shipped plugin component directory. It does
not treat a successful plugin manifest check as proof that nested agents and
skills are valid.

When Codex is installed, the wrapper runs representative execution-policy probes
against `seed/.codex/rules/default.rules`. These probes confirm the native
decision for a normal push and direct force-push forms.

Native checks strengthen the contract. They do not define the minimum continuous
integration environment.

## Test design

The implementation follows test-driven development. The first implementation
change creates failing tests in
`bin/tests/test_rendered_harness_contract.py`.

Each contract area receives a known-good fixture and at least one deliberately
broken fixture. Tests assert the contract-area label and the important evidence
in each failure message. A separate test proves that one run reports failures
from more than one area.

The force-push hook receives a table of allowed and denied command strings. The
table covers direct flags, assigned flags, clustered short flags, plus-prefixed
refspecs, Git global options, wrappers, quoted arguments, command chains, and
malformed input.

The Ruff hook receives realistic Claude hook JSON. A temporary executable on
`PATH` records whether Ruff was invoked. The test does not require Ruff itself.

The release gate receives two independent checks at the critical point:

1. A normal rendered project passes the complete verifier.
2. A temporary broken rendered fixture fails for its expected contract area.

## Error behavior

The checker does not stop after the first defect. It reports every independent
contract violation it can assess safely.

File-read, JSON-parse, symlink, and permission errors are contract failures.
Optional native-tool absence is a visible skip. Native-tool presence followed
by validation failure is a release-gate failure.

Temporary fixtures are created outside the repository and removed by the test
framework or the existing shell cleanup trap.

## Files in scope

The expected implementation may create or modify:

- `bin/rendered_harness_contract.py`
- `bin/tests/test_rendered_harness_contract.py`
- `bin/verify-template.sh`
- `seed/.claude/settings.json`
- `seed/.claude/hooks/ruff-after-edit.sh`
- `seed/.codex/hooks.json`
- `seed/.codex/hooks/pre-tool-policy.py`
- `seed/.codex/rules/default.rules`
- `seed/AGENTS.md.jinja`
- `seed/CLAUDE.md.jinja`

Only files required by a failing contract test may change during implementation.

## Rollout and completion gate

The change is complete only after all targeted unit tests pass, the hook test
suites pass, `bin/verify-template.sh` passes, `git diff --check` passes, and an
independent correctness review finds no unresolved blocking defect.

The branch will not be pushed or merged without explicit user confirmation.
