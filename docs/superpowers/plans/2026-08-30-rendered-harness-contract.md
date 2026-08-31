# Rendered Harness Contract Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use
> `superpowers:subagent-driven-development` to implement this plan task by task.
> Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Make `bin/verify-template.sh` prove that a rendered Loam project has a
complete and enforceable Claude Code and Codex harness.

**Architecture:** Keep `bin/verify-template.sh` as the only public release gate.
Put semantic validation behind one standard-library Python interface. Exercise
the Codex policy hook through its process boundary instead of importing parser
internals.

**Tech Stack:** Bash, Python 3.11 or newer, `unittest`, Copier, Claude Code CLI,
and Codex CLI.

## Global Constraints

- Keep this branch limited to the Rendered Harness Contract.
- Use only the Python standard library in the core checker.
- Expose only `verify_contract(source_root, rendered_root)` as Python policy API.
- Collect all independent failures in one run.
- Render every failure as `FAIL [contract-area]: explanation`.
- Keep native Claude and Codex checks supplemental.
- Treat a present native CLI validation failure as a gate failure.
- Do not push, merge, tag, publish, release, or delete repository data.
- Follow test-driven development. Observe each new test fail before production code.
- Run `bin/verify-template.sh` before every commit.
- The wrapper renders committed `HEAD`. Commit task code before its rendered check.

## File map

| File | Responsibility |
|---|---|
| `bin/rendered_harness_contract.py` | One semantic contract and CLI adapter |
| `bin/tests/test_rendered_harness_contract.py` | Fixtures and all contract regressions |
| `bin/verify-template.sh` | Public release gate and optional native checks |
| `seed/.claude/hooks/ruff-after-edit.sh` | Tested Ruff adapter for Claude hook JSON |
| `seed/.claude/settings.json` | Claude hook wiring |
| `seed/.codex/hooks/pre-tool-policy.py` | Literal force-push process policy |
| `seed/.codex/hooks.json` | Anchored synchronous Codex hook wiring |
| `seed/.codex/config.toml` | Explicit hooks feature and permission profile |
| `seed/.codex/rules/default.rules` | Prefix-rule defense in depth |
| `seed/CLAUDE.md.jinja` | Active shipped routes only |

---

### Task 1: Contract kernel, topology, and release callers

**Files:**

- Create: `bin/rendered_harness_contract.py`
- Create: `bin/tests/test_rendered_harness_contract.py`
- Inspect: `copier.yml`
- Inspect: `.github/workflows/test.yml`
- Inspect: `.github/workflows/release.yml`
- Inspect: `bin/release.sh`

**Interfaces:**

- Produces: `Violation(area: str, detail: str)`
- Produces: `verify_contract(source_root: Path, rendered_root: Path) -> tuple[Violation, ...]`
- Produces: `main(argv: Sequence[str] | None = None) -> int`
- Later tasks extend private checks without changing the public interface.

- [ ] **Step 1: Write the fixture and failing topology tests.**

Create a `unittest.TestCase` that gives every test separate `source` and
`rendered` temporary directories. Add `write()`, `make_executable()`, and
`build_good_fixture()` helpers. The good fixture must create every required
source and rendered path named in the design specification.

Add these tests:

```text
test_known_good_fixture_has_no_violations
test_missing_required_rendered_paths_are_reported
test_missing_required_source_paths_are_reported
test_forbidden_rendered_paths_are_reported
test_multiple_areas_are_reported_in_one_run
```

The missing-path tests must assert both `FAIL [topology]` and the exact path.

- [ ] **Step 2: Write failing release-caller tests.**

Add these tests:

```text
test_pull_request_workflow_calls_public_gate
test_release_workflow_runs_gate_before_publish
test_release_script_runs_gate_before_version_write
test_release_caller_failures_accumulate
```

Use these exact ordering markers:

```text
bin/verify-template.sh
softprops/action-gh-release
bash "$SELF_DIR/verify-template.sh"
echo "$VERSION" > VERSION
```

- [ ] **Step 3: Run the red phase.**

Run:

```bash
python3 -m unittest discover -s bin/tests -p 'test_rendered_harness_contract.py' -v
```

Expected: import failure because `rendered_harness_contract` does not exist.

- [ ] **Step 4: Implement the minimum kernel.**

Use this public shape:

```python
@dataclasses.dataclass(frozen=True, order=True)
class Violation:
    area: str
    detail: str

    def render(self) -> str:
        return f"FAIL [{self.area}]: {self.detail}"


def verify_contract(
    source_root: pathlib.Path,
    rendered_root: pathlib.Path,
) -> tuple[Violation, ...]:
    violations: list[Violation] = []
    _check_topology(source_root, rendered_root, violations)
    _check_release_callers(source_root, violations)
    return tuple(sorted(violations))
```

Define `REQUIRED_SOURCE_PATHS`, `REQUIRED_RENDERED_PATHS`, and
`FORBIDDEN_RENDERED_PATHS` exactly from the design specification. Do not infer
requirements from the fixture.

The CLI must require `--source-root` and `--rendered-root`. It prints every
rendered violation. It returns `1` when violations exist and `0` otherwise.

- [ ] **Step 5: Run the green checks.**

Run:

```bash
python3 -m unittest discover -s bin/tests -p 'test_rendered_harness_contract.py' -v
python3 -m py_compile bin/rendered_harness_contract.py bin/tests/test_rendered_harness_contract.py
git diff --check
```

Expected: every Task 1 test passes. Both syntax checks exit `0`.

- [ ] **Step 6: Commit Task 1.**

Run `bin/verify-template.sh`. Require `verify-template: PASSED`.

Commit only the two Task 1 files with:

```text
test: define rendered harness contract
```

---

### Task 2: Claude hooks, symlink, prose routes, and modes

**Files:**

- Modify: `bin/rendered_harness_contract.py`
- Modify: `bin/tests/test_rendered_harness_contract.py`
- Modify: `seed/.claude/settings.json`
- Create: `seed/.claude/hooks/ruff-after-edit.sh`
- Modify: `seed/CLAUDE.md.jinja`
- Modify only after a failing route test: `seed/AGENTS.md.jinja`

**Interfaces:**

- Consumes: `verify_contract(...)`
- Produces private checks for `symlinks`, `claude-hooks`, `prose-routes`, and
  `executable-modes`.

- [ ] **Step 1: Add failing symlink and settings tests.**

Add these test groups:

```text
catchup is a symlink
catchup resolves to .agents/skills/catchup
catchup target contains SKILL.md
settings JSON is an object
only PreToolUse, PostToolUse, and Stop are owned events
owned matchers equal the design values
every owned handler is a command handler
every repository script target exists
inline Ruff command is rejected
Ruff route reads tool_input.file_path
```

The good settings fixture must route `PostToolUse` `Edit|Write` to
`.claude/hooks/ruff-after-edit.sh`.

- [ ] **Step 2: Add failing Ruff process tests.**

Create a temporary `ruff/__main__.py` under a temporary `PYTHONPATH`. It writes
its received arguments to `RUFF_CAPTURE`.

Test these payloads and outcomes:

| Payload | Expected outcome |
|---|---|
| `tool_input.file_path = "src/example.py"` | Capture `check --fix -- src/example.py` |
| Non-Python path | No capture |
| Missing path | No capture |
| Non-string path | No capture |
| Malformed JSON | Exit `0`, no capture |
| Fake Ruff exits nonzero | Hook still exits `0` |

- [ ] **Step 3: Add failing route and mode tests.**

Test every prose route table entry in the design. Reject the unresolved `docs/`
placeholder. Do not require targets for rows containing `if installed`.

Remove executable bits from each rendered hook script in a table-driven test.
Each case must produce `FAIL [executable-modes]` with the exact path.

- [ ] **Step 4: Run the red phase.**

Run the targeted unittest command. Expected failures must name all four new
contract areas.

- [ ] **Step 5: Implement and wire the Ruff adapter.**

The script must:

```text
read one JSON object from stdin
extract only tool_input.file_path when it is a string
run python3 -m ruff check --fix -- "$FILE" only for *.py
ignore malformed or irrelevant input
return 0 even when Ruff fails
```

Set the script executable. Replace the inline settings command with the script
route. Add `ruff-after-edit.sh` to the shipped hook sentence. Remove the `docs/`
placeholder route.

- [ ] **Step 6: Implement the four private contract checks.**

Use `Path.is_symlink()`, `os.readlink()`, and `Path.resolve()` for the symlink.
Reject resolved paths outside the rendered root. Validate the exact owned event
and matcher map. Extract repository script routes without executing settings
commands. Check executable mode with user, group, or other execute bits.

- [ ] **Step 7: Run the green checks and commit.**

Run:

```bash
python3 -m unittest discover -s bin/tests -p 'test_rendered_harness_contract.py' -v
bash -n seed/.claude/hooks/ruff-after-edit.sh
python3 -m json.tool seed/.claude/settings.json
git diff --check
bin/verify-template.sh
```

Expected: all commands exit `0`. The final line is `verify-template: PASSED`.

Commit the Task 2 files with:

```text
feat: enforce rendered Claude harness
```

---

### Task 3: Codex policy process, wiring, config, and rules

**Files:**

- Create: `seed/.codex/hooks/pre-tool-policy.py`
- Create: `seed/.codex/hooks.json`
- Modify: `seed/.codex/config.toml`
- Modify only after a failing policy test: `seed/.codex/rules/default.rules`
- Modify: `bin/rendered_harness_contract.py`
- Modify: `bin/tests/test_rendered_harness_contract.py`

**Interfaces:**

- Consumes: the `verify_contract(...)` public interface.
- Produces: a policy process with `stdin JSON -> stdout JSON` or
  `stderr reason + exit 2`.
- Keeps all policy parser functions private and unimported by tests.

- [ ] **Step 1: Add failing policy-process tests.**

For every valid envelope, require `hook_event_name = "PreToolUse"`,
`tool_name = "Bash"`, and `tool_input.command` as a string.

Denied commands must cover:

```text
--force before and after refspecs
--force=<value>
--force-with-lease and assigned form
-f and short clusters containing f
plus-prefixed refspecs
git -C, git -c, --git-dir, --work-tree, --namespace, and --no-pager
command --, env assignments, /usr/bin/env -i, and bare assignments
;, &, &&, ||, |, and unquoted newline separators
backslash-LF and backslash-CRLF continuations
concatenated quoted git, push, and force tokens
literal Git sequences in control flow, brace groups, compact case arms,
functions, and heredoc text
literal Git sequences after any environment-name syntax
```

Allowed commands must cover normal push, dry-run push, Git help, unrelated
commands, quoted force text, commented force text, quoted separators, and a
single quoted data argument such as `git push --force`. Safe `git --version`
analogs must remain allowed. Aliases, expansions, `eval`, nested shells, and
command substitution remain outside the guarantee.

Malformed envelopes must cover empty input, invalid JSON, every non-object JSON
type, wrong event, wrong tool, missing or non-object `tool_input`, and missing or
non-string command. Require exit `2`, empty stdout, and a short stderr reason.

An empty string command is valid and silent.

- [ ] **Step 2: Add failing wiring tests.**

Require this exact handler contract:

```json
{
  "matcher": "^Bash$",
  "hooks": [{
    "type": "command",
    "command": "python3 \"$(git rev-parse --show-toplevel)/.codex/hooks/pre-tool-policy.py\"",
    "timeout": 10,
    "statusMessage": "Checking Git push policy"
  }]
}
```

Reject `async: true`. Initialize a temporary Git repository. Execute the exact
configured command from a nested directory. Prove both allowed and denied
payloads reach the hook.

- [ ] **Step 3: Add failing configuration and rule tests.**

Parse config with `tomllib`. Require only these root keys:

```text
default_permissions, features, agents, permissions
```

Require `features.hooks = true`, `features.multi_agent = true`, a positive
non-Boolean agent limit, the exact `project-workspace` profile, and every current
`.env` and `.envrc` deny pattern. Reject unknown owned keys and inline hooks.

Parse `.rules` with `ast.parse` and `ast.literal_eval`. Reject imports,
assignments, positional arguments, duplicate keywords, unknown keywords,
nonliteral values, and calls other than `prefix_rule`. Require literal
`pattern`, `decision`, `justification`, and `match`. Require the existing allow,
normal-push prompt, recursive-delete forbids, hard-reset forbid, and direct
force-push forbids.

- [ ] **Step 4: Run the red phase.**

Run the targeted unittest command. Expected: failures because the policy hook,
wiring, explicit hooks feature, and checker behavior are absent.

- [ ] **Step 5: Implement the policy process.**

Implementation order:

```text
use one lexical pass for continuations, comments, and Bash ANSI-C and locale quoted words
lex once with POSIX quoting and shell punctuation
scan every literal `git` token as a possible command start
skip recognized shell redirection spans before the Git subcommand
classify Git global options by argument count
locate only the push subcommand
classify force flags and plus refspecs with one long-option arity map
```

Do not emulate function depth, heredoc delimiter decoding, case grammar, or
brace structure. Do not search every token for force-related words. Search only
for literal `git` starts, then use the bounded Git and push classifiers.
Unsupported compound or heredoc forms that expose separate `git`, `push`, and
force tokens deny conservatively. Unparseable shell text blocks with exit `2`.
A recognized force push emits only the design denial JSON and exits `0`.

- [ ] **Step 6: Implement wiring and contract checks.**

Create `.codex/hooks.json` with the exact Step 2 handler. Add `hooks = true` to
`[features]`. Execute the shipped hook as a subprocess for a normal push and a
direct force push. Never import it. Implement the bounded TOML and AST checks.

- [ ] **Step 7: Run green and native checks.**

Run:

```bash
python3 -m unittest discover -s bin/tests -p 'test_rendered_harness_contract.py' -v
python3 -m py_compile seed/.codex/hooks/pre-tool-policy.py
python3 -m json.tool seed/.codex/hooks.json
codex execpolicy check --pretty --rules seed/.codex/rules/default.rules -- git push origin main
codex execpolicy check --pretty --rules seed/.codex/rules/default.rules -- git push --force origin main
codex execpolicy check --pretty --rules seed/.codex/rules/default.rules -- git push --force-with-lease origin main
git diff --check
bin/verify-template.sh
```

Parse the policy JSON. Expected decisions are `prompt`, `forbidden`, and
`forbidden`. Do not infer success from the command exit status.

Commit the Task 3 files with:

```text
feat: wire rendered Codex policy
```

---

### Task 4: Public wrapper and native supplemental checks

**Files:**

- Modify: `bin/verify-template.sh`
- Modify: `bin/rendered_harness_contract.py`
- Modify: `bin/tests/test_rendered_harness_contract.py`

**Interfaces:**

- Consumes: checker CLI and committed rendered seed.
- Produces: marketplace discovery and native validation stages.

- [ ] **Step 1: Add failing marketplace tests.**

Parse `cultivation/marketplace/.claude-plugin/marketplace.json`. Discover only
string `source` entries. Ignore remote object sources. Reject local sources that
escape the marketplace root. Report missing local roots. Parse every declared
local plugin `hooks/hooks.json` when present.

- [ ] **Step 2: Add failing wrapper-order tests.**

Require this stage order:

```text
contract unit tests
Copier scratch render from HEAD
rendered harness contract
Claude native validation
Codex native policy probes
skill frontmatter names
final summary
```

Require visible skips for missing Claude and Codex. Require present native
failures to set the shared failure state. Keep the summary text
`verify-template: PASSED` or `verify-template: FAILED`.

- [ ] **Step 3: Run the red phase.**

Run the targeted unittest command. Expected: marketplace and wrapper-stage tests
fail against the old wrapper.

- [ ] **Step 4: Implement the wrapper stages.**

Run every fallible independent command inside an `if` block. Record its failure
and continue. Invoke the checker with the repository root and scratch render.
Do not duplicate old symlink or JSON checks in shell.

When Claude exists, validate:

```text
seed/.claude without --strict, because Claude validation does not follow its deliberate symlink
seed/.agents/skills with --strict
cultivation/marketplace with --strict
each declared local plugin root with --strict
each present agents, skills, or commands component directory with --strict
```

Do not pass a raw hooks directory to `claude plugin validate`. Parse plugin hook
JSON with the core checker and `python3 -m json.tool`.

When Codex exists, run the three native rule probes from Task 3. Parse each JSON
decision. Do not run `codex doctor`.

- [ ] **Step 5: Run green checks and commit.**

Run:

```bash
python3 -m unittest discover -s bin/tests -p 'test_rendered_harness_contract.py' -v
bash -n bin/verify-template.sh
python3 -m py_compile bin/rendered_harness_contract.py bin/tests/test_rendered_harness_contract.py
git diff --check
bin/verify-template.sh
```

Expected: all commands exit `0`. The final line is `verify-template: PASSED`.

Commit the Task 4 files with:

```text
feat: deepen template release gate
```

---

### Task 5: Critical-point negative control and final verification

**Files:** No planned source edits.

**Interfaces:** Consumes the complete committed release gate.

- [ ] **Step 1: Run the complete unit suite.**

Run the targeted unittest discovery command. Record its exact `Ran N tests` and
`OK` lines. Do not predict the count.

- [ ] **Step 2: Run direct syntax and hook suites.**

Run:

```bash
bash -n bin/verify-template.sh
bash -n seed/.claude/hooks/ruff-after-edit.sh
bash -n seed/.claude/hooks/bash-audit-log.sh
bash -n seed/.claude/hooks/concurrent-checkout-guard.sh
bash -n seed/.claude/hooks/stop-verify-gate.sh
python3 -m py_compile bin/rendered_harness_contract.py bin/tests/test_rendered_harness_contract.py seed/.codex/hooks/pre-tool-policy.py
python3 -m json.tool seed/.claude/settings.json
python3 -m json.tool seed/.codex/hooks.json
python3 cultivation/marketplace/sam-cc-setup/hooks/test_check_stale_counts.py
python3 cultivation/marketplace/sam-cc-setup/hooks/test_protect_paths.py
```

Record every exit code and explicit test summary.

- [ ] **Step 3: Run the positive release gate.**

Run `bin/verify-template.sh`. Require exit `0` and final line
`verify-template: PASSED`.

- [ ] **Step 4: Run the independent negative control.**

Render committed `HEAD` into a temporary directory. Print the Ruff hook path and
mode. Remove only that temporary file's executable bit. Run the checker. Require
nonzero exit and `FAIL [executable-modes]` naming the Ruff hook.

- [ ] **Step 5: Run completion checks.**

Run:

```bash
git diff --check
git status --short
git diff --name-only main...HEAD
```

Require no uncommitted implementation files. Require every changed path to stay
inside the approved design and plan scope.

- [ ] **Step 6: Dispatch the final Sol correctness review.**

Use a fresh Codex Sol worker at high effort. Give it the design, branch diff
package, and verification transcript. Require correctness findings only. Fix
confirmed defects with one fix worker. Rerun affected tests and the complete
release gate.

- [ ] **Step 7: Perform the final self-attack.**

Answer:

```text
What input breaks the checker or either new hook?
Which generated route or release caller was not checked?
What changed code has no test?
Which completion claim lacks command evidence?
```

Fix concrete defects. Record untestable doubts as residual risks. Do not push or
merge.
