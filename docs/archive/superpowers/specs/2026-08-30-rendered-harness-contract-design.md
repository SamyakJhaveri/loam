# Rendered Harness Contract Design

**Date:** 2026-08-30
**Status:** Complete and independently reviewed

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
Python standard library. The release tooling requires Python 3.11 or newer
because the core TOML parser is `tomllib`. Loam continuous integration uses
Python 3.12.

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

The checker exposes one Python interface:

```python
@dataclass(frozen=True, order=True)
class Violation:
    area: str
    detail: str

def verify_contract(
    source_root: Path,
    rendered_root: Path,
) -> tuple[Violation, ...]:
    ...
```

All area-specific functions remain private. The command-line entry point adapts
this interface to printed failures and an exit status.

## Contract areas

### Copier topology

The checker enforces this exact rendered path set:

| Required rendered path | Kind |
|---|---|
| `AGENTS.md` | Rendered agent instructions |
| `CLAUDE.md` | Rendered Claude instructions |
| `.agents/skills/catchup/SKILL.md` | Shared skill source |
| `.claude/settings.json` | Claude configuration and hook wiring |
| `.claude/settings.local.json.template` | Local settings template |
| `.claude/hooks/bash-audit-log.sh` | Claude hook script |
| `.claude/hooks/concurrent-checkout-guard.sh` | Claude hook script |
| `.claude/hooks/ruff-after-edit.sh` | Claude hook script |
| `.claude/hooks/stop-verify-gate.sh` | Claude hook script |
| `.claude/skills/catchup` | Symlink to the shared skill |
| `.codex/config.toml` | Codex configuration |
| `.codex/hooks.json` | Codex hook wiring |
| `.codex/hooks/pre-tool-policy.py` | Codex policy hook |
| `.codex/rules/default.rules` | Codex execution rules |

Every required rendered path except `.claude/skills/catchup` must be a direct
regular file. It must resolve inside the rendered root. A directory, an
external symlink, or an internal symlink is a contract failure. The catchup
route is the only designed symlink.

The checker enforces this exact source-only path set:

| Required source-only path | Purpose |
|---|---|
| `copier.yml` | Copier topology and symlink behavior |
| `bin/verify-template.sh` | Public verification interface |
| `bin/rendered_harness_contract.py` | Semantic contract checker |
| `bin/tests/test_rendered_harness_contract.py` | Contract regression tests |
| `.github/workflows/test.yml` | Pull-request release-gate wiring |
| `.github/workflows/release.yml` | Tag release-gate wiring |
| `bin/release.sh` | Local release-gate wiring |

All release-gate callers are part of the contract. The checker reads workflow
steps as complete bounded records. Both workflow files must run
`bin/verify-template.sh` in a step with no `if` field and no active
`continue-on-error`. In `.github/workflows/release.yml`, that step must occur
before the first publishing step, currently `softprops/action-gh-release`.
`bin/release.sh` must contain the exact fail-closed gate command as an
unindented, top-level line before its first mutation, currently
`echo "$VERSION" > VERSION`. A conditional body or an uncalled function does
not satisfy this controlled source contract. This is not a general YAML or
Bash interpreter. A conservative line scanner tracks literal condition,
loop, case, brace-group, and subshell boundaries. It fails closed on unmatched
boundaries. A function declaration before the gate disqualifies that gate.
A release-flow refactor must update the bounded contract deliberately.

The checker also requires these retired rendered paths to stay absent:

| Forbidden rendered path | Reason |
|---|---|
| `.mcp.json` | Seed MCP defaults were retired |
| `.claude/agents` | Seed agents were retired |
| `.claude/rules` | Empty always-loaded rule layer was retired |
| `.claude/hooks/post-compact-recovery.sh` | Native context reload replaced it |
| `.claude/skills/reassess-template-sync` | Sync engine was retired |
| `.agents/skills/agent-team` | The seed does not ship an agent-team skill |
| `.codex/reassess-hooks.json` | Old inactive hook file was retired |
| `.codex/agents` | Empty Codex agent layer was retired |
| `.codex/mcp` | Dangling MCP layer was retired |
| `_research` | The research flavor was retired |

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

The hook runs on `PreToolUse` with the anchored `^Bash$` matcher. Its command is
`python3 "$(git rev-parse --show-toplevel)/.codex/hooks/pre-tool-policy.py"`.
Codex runs hook commands from the session directory, so a relative `.codex`
path is not valid wiring when a session starts in a repository subdirectory.
The hook reads the shell command from `tool_input.command`. It denies a
recognized force push with the current Codex hook result:

```json
{
  "hookSpecificOutput": {
    "hookEventName": "PreToolUse",
    "permissionDecision": "deny",
    "permissionDecisionReason": "Force pushes are blocked by repository policy."
  }
}
```

The policy first validates the complete command with `bash -n`. One lexical
preprocessing pass then applies Bash line-continuation and comment rules and
translates Bash ANSI-C and locale quoted words for the small POSIX token
recognizer. Decoded ANSI-C values outside Python Unicode become opaque,
nonmatching token content. Raw NUL input is discarded from the complete command
before lexical-state recognition. Bash control escapes use the first UTF-8 byte;
a non-ASCII nonzero result becomes opaque, nonmatching content. A zero-valued
ANSI-C escape terminates the remaining content in that quoted fragment; source
concatenation resumes after its closing quote. It does not emulate Bash function
depth, heredoc delimiters, case grammar, or brace structure. From every literal
`git` token, it skips recognized shell
redirections, parses Git global options, locates `push`, and applies the bounded
push argument classifier. It denies long force flags, assigned long force
flags, short `-f`, clustered short flags containing `f`, and plus-prefixed
refspecs. It also denies active `--mirror`, including the unique native Git
abbreviation. Later `--no-mirror` cancels it, and later `--mirror` restores it.
Proven help-only and dry-run forms remain allowed.

This recognition is deliberately conservative. Literal Git token sequences in
control flow, brace groups, case arms, functions, heredoc text, and after any
environment-name syntax are classified even when Bash structure would make the
tokens data or defer their execution. A quoted single argument such as
`'git push --force'` remains one data token and is allowed. Other unsupported
compound or heredoc forms that expose separate `git`, `push`, and force tokens
are denied.

The `Bash` matcher keeps unrelated tools outside this hook. Invalid JSON, a
non-object envelope, a missing `tool_input`, or a non-string command exits `2`
with a blocking reason. A wrong or missing `hook_event_name` or `tool_name` also
exits `2`. Unparseable shell text exits `2`. A valid empty or unrelated shell
command exits `0` without a decision. Extra envelope fields are accepted for
forward compatibility.

The hook must remain synchronous. The contract rejects `async: true`, because a
background hook cannot block the triggering command.

This local hook recognizes literal Git token sequences and, since the
2026-09-01 hardening, force pushes reached through common obfuscations: a
path-prefixed or variable head (`/usr/bin/git`, `$GIT`, `${GIT}`), a command
substitution used as the head (`$(command -v git)`), `sh -c`/`bash -c` string
arguments (including interpreter options such as `-O extglob`), and `eval`.
Leading wrapper commands (`command`, `env`) are unwrapped to the real head.
Stacked shells and substitutions past a recursion limit are denied
conservatively rather than allowed. One known residual remains: a force push
whose subcommand is produced only by runtime variable expansion, with no
visible `push` token in the command (`x='git push --force'; eval "$x"`), cannot
be caught by static inspection. Git aliases and other value-dependent
expansions that resolve only at runtime are likewise outside its guarantee.
Absolute force-push prevention belongs at the remote Git trust boundary through
branch protection or a pre-receive hook. The local hook and rules are developer guardrails, not a
replacement for that remote control.

`default.rules` remains as defense in depth. It prompts for ordinary pushes and
forbids the direct force forms that its prefix matcher can express. The hook is
the argument-aware enforcement layer.

### Prose routes

The checker validates these active rendered references:

| Rendered document | Required reference | Required target |
|---|---|---|
| `CLAUDE.md` | `@AGENTS.md` | `AGENTS.md` |
| `AGENTS.md` | `.codex/` | `.codex/` |
| `AGENTS.md` | `.agents/skills/` | `.agents/skills/` |
| `CLAUDE.md` | `.claude/hooks/stop-verify-gate.sh` | The named hook script |
| `CLAUDE.md` | `/catchup` and `.agents/skills/` | `.agents/skills/catchup/SKILL.md` |
| `CLAUDE.md` | `bash-audit-log.sh` | The named hook script |
| `CLAUDE.md` | `concurrent-checkout-guard.sh` | The named hook script |
| `CLAUDE.md` | `ruff-after-edit.sh` | The named hook script |

The current `docs/` placeholder route has no rendered target. The implementation
removes that row from `seed/CLAUDE.md.jinja`. Routes qualified with "if
installed" point to optional plugins and are excluded from required-target
validation.

The checker does not scan every Markdown link. Historical specifications,
examples, and external URLs are outside this contract. This avoids false
failures from non-runtime documentation.

### Executable modes

Every repository script invoked by a Claude or Codex hook must exist and have an
executable mode bit. The checker validates the rendered files, not only their
source copies.

## Native supplemental checks

When Claude Code is installed, the wrapper validates the main Claude directory
without strict mode because the validator does not follow its deliberate
catchup symlink. It validates the real shared skill directory, marketplace,
each plugin root, and supported `agents`, `skills`, and `commands` component
directories in strict mode when present. It does not pass a `hooks` directory
to `claude plugin validate`, because that command requires a plugin or
marketplace manifest. The checker reads local plugin roots from
`cultivation/marketplace/.claude-plugin/marketplace.json` and validates hook
JSON for each declared local plugin. It does not require any plugin by name.

When Codex is installed, the wrapper runs representative execution-policy probes
against `seed/.codex/rules/default.rules`. These probes confirm the native
decision for a normal push and direct force-push forms.

Native checks strengthen the contract. They do not define the minimum continuous
integration environment.

Without Codex, the core checker parses `.codex/config.toml` with `tomllib`. It
parses `default.rules` as the supported Python-like `prefix_rule` call shape
with `ast`. It requires literal `pattern`, `decision`, `justification`, and
`match` values and the expected allow, prompt, and forbidden policies. Native
Codex probes remain the authoritative semantic check when Codex is installed.
The core grammar accepts only the native decisions `allow`, `prompt`, and
`forbidden`. A pattern is a non-empty list of strings or non-empty string
alternative lists. Match examples are strings or non-empty string-token lists.
Invalid appended rules fail the complete file even when every required rule is
also present.

The core Codex configuration schema is bounded to the sections Loam owns:

| Configuration path | Required value contract |
|---|---|
| Root table | Only `default_permissions`, `features`, `agents`, and `permissions` |
| `default_permissions` | String equal to `project-workspace` |
| `features` | Only `hooks` and `multi_agent`, both equal to `true` |
| `agents` | Only `max_concurrent_threads_per_session`, with a positive integer |
| `permissions` | Only the `project-workspace` profile |
| `permissions.project-workspace.description` | Non-empty string |
| `permissions.project-workspace.extends` | String equal to `:workspace` |
| `permissions.project-workspace.filesystem` | Only the `:workspace_roots` table |
| Secret-file deny entries | The current `.env` and `.envrc` patterns, each equal to `deny` |

Unknown keys inside these owned sections are contract failures. The required
keys and types follow the current official Codex configuration reference. The
implementation adds `features.hooks = true` so the policy hook is not dependent
on a default value.

The installed Codex CLI has no deterministic command that strictly validates an
untrusted project configuration without starting an agent. `codex
--strict-config ... doctor` reads the trusted user layer and ignores an
untrusted project layer. The release gate therefore does not claim that command
as evidence. The bounded core schema is the required project-config check.

The wrapper also validates `cultivation/marketplace` as a marketplace root. It
reads local plugin roots from the manifest's string `source` entries. Remote
object sources are not treated as local directories. It validates each local
plugin root and its supported component directories.

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
refspecs, Git global options, bare assignments, supported wrappers, POSIX,
ANSI-C, and locale quoted tokens, redirections, all supported segment
separators, line continuations, shell comments, and malformed hook envelopes.
Visible literal Git sequences inside functions and heredoc text are denied
conservatively. Separate tests record that Git aliases, expansions, `eval`,
nested shells, and command substitution are outside the local guarantee.

Supported wrapper forms include `command --`, `env` with assignments, and
`/usr/bin/env -i` with assignments. Git global options are classified by whether
they consume a following value. Concatenated quoted tokens such as `g''it` and
`p''ush` must be recognized. Quoted or commented force-push text that is only an
argument to another command must not be blocked.

Tests execute the hook as a process. They do not import parser functions. This
proves the interpreter command, envelope handling, exit status, standard output,
standard error, and denial JSON through the same seam Codex uses.

A wiring test initializes a temporary Git repository, places the hook under its
`.codex` directory, changes into a nested directory, and executes the exact
configured hook command. The test proves that both an allowed command and a
denied force push reach the script from that nested working directory.

The Ruff hook receives realistic Claude hook JSON. A temporary executable on
`PATH` records whether Ruff was invoked. The test does not require Ruff itself.

The release gate receives two independent checks at the critical point:

1. A normal rendered project passes the complete verifier.
2. A temporary broken rendered fixture fails for its expected contract area.

## Error behavior

The checker does not stop after the first defect. It reports every independent
contract violation it can assess safely.

File-read, JSON-parse, TOML-parse, rule-parse, symlink, and permission errors are
contract failures. A malformed payload to the Bash policy hook is denied.
Optional native-tool absence is a visible skip. Native-tool presence followed
by validation failure is a release-gate failure.

Temporary fixtures are created outside the repository and removed by the test
framework or the existing shell cleanup trap.

## Authoritative references

- [Codex hooks](https://learn.chatgpt.com/docs/hooks) defines project hook
  discovery, `PreToolUse`, `tool_input.command`, and denial output.
- [Codex configuration reference](https://learn.chatgpt.com/docs/config-file/config-reference)
  defines the project trust gate and the keys in the bounded configuration
  schema.
- [Claude Code hooks reference](https://code.claude.com/docs/en/hooks) defines
  the hook envelope and `tool_input.file_path` for Edit and Write events.

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
