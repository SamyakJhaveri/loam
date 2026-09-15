# Contributing to Loam

Thanks for your interest! Loam is a Copier template; the things it ships live under
`seed/`, and the repo runs on its own config via the `.claude -> seed/.claude` symlink.

## Development setup

```bash
git clone https://github.com/samyakjhaveri/loam && cd loam
# Select a Node 24.21.0 distribution with its bundled npm 11.19.0.
export LOAM_FACTORY_TOOLCHAIN="/absolute/path/to/node-v24.21.0-distribution"
export PATH="$LOAM_FACTORY_TOOLCHAIN/bin:$PATH"
# Install the pinned Python tools in an environment you control.
python3 -m pip install -r .github/ci/python-requirements.txt
export LOAM_FACTORY_COPIER="$(command -v copier)"
bin/check   # expect "check: PASSED"
```

Requirements: [Copier](https://copier.readthedocs.io/) 9.16.0 for release verification,
Node 24.21.0 with bundled npm 11.19.0, `python3`, `bash`, the Claude Code and Codex
CLIs, and the pinned Python check dependencies. Node and npm are package qualification
candidates. This does not declare the future factory runtime supported.

`bin/check` requires the two explicit tool exports above. The rebuild gate downloads
the locked development dependencies into fresh scratch, so it needs access to the npm
registry. It compares against the supplied `dist` files without changing them. It also
checks that the factory payload exactly matches Git's index. Stage intended factory
changes before running it. Build source changes explicitly with
`npm --prefix seed/.loam/factory run build`, then stage the source, compiled output and
release manifest together. A stale or missing compiled file fails the check.
`bin/check` also runs `qualify platform` (storage, lifetime locks, runtime identity);
candidate containment (`qualify native-boundary`) is a host-only gate run from a plain
terminal, not by `bin/check` or CI. See [factory setup](seed/docs/factory/SETUP.md).

The factory's dependencies stay under `seed/.loam/factory/node_modules`. Project-root
packages cannot supply a missing compiler or Node type package. Recipient package
checks execute supplied JavaScript without installing the compiler; see
[factory setup](seed/docs/factory/SETUP.md).
Missing agent CLIs fail the gate; `LOAM_ALLOW_MISSING_AGENT_CLIS=1` permits a reduced local run (CI never sets it).

**Windows note:** template *development* relies on the `.claude -> seed/.claude` symlink.
Use WSL, or enable Developer Mode and `git config core.symlinks true` before cloning.
Rendered projects are unaffected: Copier writes real directories.

## Making changes

- **Docs, content, small fixes**: commit directly to `main` (or open a PR if you're external).
- **Behavior changes** (`seed/` guidance, skills, hooks, policy, `copier.yml`, or release tooling): branch and PR, always.
- Run `bin/check` before every PR. CI runs the same script; a red run blocks merge.
- Before merging any PR, run `bin/check && bash bin/ip-sweep.sh`.
  Without `bin/.ip-terms`, the non-strict IP sweep warns that it skips the content
  sweep and can still pass.
- Skills follow the [agentskills.io](https://agentskills.io/specification) SKILL.md format.
  A skill that must reach every rendered project goes in `seed/.agents/skills/`.
  Reusable optional skills go in the appropriate marketplace plugin.
- **Vet every external skill before it enters the repo.** Any skill or bundle from a
  third-party source must pass `bin/vet-skill.sh <path-or-url>` first. It wraps
  [NVIDIA SkillSpector](https://github.com/nvidia/skillspector): exit 0 (LOW/NONE) adopts,
  exit 2 (HIGH/CRITICAL) rejects, exit 1 (MEDIUM) needs a recorded human decision in the PR.
  Keep the scanner current with `uv tool upgrade skillspector`.
- Read `CLAUDE.md` for current repository gotchas. Read `docs/ASSET-LAYERS.md` before placing a new asset.

## Promoting a skill from your project

If you built a broadly useful skill in a Loam-bootstrapped project, you can promote it
by hand into the plugin marketplace. See `docs/SYNC.md` for the current route.
Promotion PRs should state which project battle-tested the skill and what it was used for.

## Releases (maintainers)

Copier resolves from **git tags**, not HEAD. After merging significant changes:

```bash
bin/release.sh <version>   # needs a green CI run on HEAD; runs the IP sweep, bumps VERSION, tags, pushes
```

## Reporting issues

Open a GitHub issue with your Copier version and the output of `bin/check`
if the template fails to render.
