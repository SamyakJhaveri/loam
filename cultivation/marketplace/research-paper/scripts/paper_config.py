#!/usr/bin/env python3
"""Find, load and fill the project config of the research-paper plugin.

Every script in this folder reads its project settings through this module:

    from paper_config import load

    cfg = load()
    main_tex = args.main if args.main is not None else cfg["paper"]["main_tex"]

load() returns a plain dict of tables (DEFAULTS below shows every key). A path key comes
back as an absolute pathlib.Path: a relative value resolves against the project root, and
"" means none and comes back as None. A path list (literature.notes) comes back as
absolute path strings, each keeping its "::HEADING" suffix. Every other value keeps its
TOML type. cfg["project"]["root"] is the project root and cfg["project"]["config"] the
file that was read (None when there was none).

Where the values come from:
- Project root: PAPER_TOOLS_ROOT when set, else `git rev-parse --show-toplevel` run in
  the current directory, else the current directory.
- Config file: PAPER_TOOLS_CONFIG when set (it must exist), else
  <root>/paper/tools/paper-tools.toml. A missing default file is not an error: every key
  has a default, so a script still runs on its flags alone.
- An unknown table or key, or a value whose type differs from its default, is an error
  (exit 2).

A command-line flag wins over the config. A flag's path is taken as given (relative to
the current directory); only config values resolve against the project root. The scripts
sit side by side, so `import paper_config` works when a script is run by path; tests put
scripts/ on sys.path, or call load(root=..., config=...).

    python3 paper_config.py              # the resolved config as JSON
    python3 paper_config.py build.pdf    # one value, for a shell variable
"""

import argparse
import copy
import json
import os
import subprocess
import sys
from pathlib import Path

try:
    import tomllib
except ModuleNotFoundError:  # Python 3.10 or older
    sys.exit("paper_config: needs Python 3.11 or later (stdlib tomllib)")

DEFAULT_CONFIG = Path("paper/tools/paper-tools.toml")

DEFAULTS = {
    "paper": {
        "main_tex": "paper/main.tex",
        "sections_dir": "paper/sections",
        "sections": [],
        "abstract_tex": "paper/sections/abstract.tex",
        "intro_section": "introduction",
        "discussion_section": "discussion",
        "preamble_tex": "paper/preamble.tex",
        "title_macro": "PaperTitle",
        "bib": "paper/references.bib",
        "figures_dir": "paper/figures",
        "citation_cff": "CITATION.cff",
        "macros": {},
        "smallcaps_names": [],
    },
    "build": {
        "command": [
            "latexmk",
            "-pdf",
            "-interaction=nonstopmode",
            "-outdir=paper/build",
            "paper/main.tex",
        ],
        "pdf": "paper/build/main.pdf",
        "log": "paper/build/main.log",
        "text": "paper/build/main.txt",
    },
    "limits": {
        "max_pages": 10,
        "max_abstract_words": 500,
        "appendix_allowed": False,
    },
    "terms": {
        "banned": "paper/tools/banned_terms.txt",
        "anonymity": "paper/tools/anonymity_terms.txt",
        "anonymity_baseline": "paper/tools/anonymity_baseline.txt",
        "acronym_allow": "paper/tools/acronym_allow.txt",
        "acronym_baseline": "paper/tools/acronym_baseline.txt",
    },
    "literature": {
        "notes": [],
        "self_names": [],
    },
    "cite": {
        "warn_only": [],
    },
    "consistency": {
        "term_groups": {},
    },
}

# Keys whose values are paths; literature.notes is a list of them.
PATH_KEYS = {
    "paper": {
        "main_tex",
        "sections_dir",
        "abstract_tex",
        "preamble_tex",
        "bib",
        "figures_dir",
        "citation_cff",
    },
    "build": {"pdf", "log", "text"},
    "terms": set(DEFAULTS["terms"]),
}


def _fail(message):
    print(f"paper_config: {message}", file=sys.stderr)
    raise SystemExit(2)


def find_root():
    """PAPER_TOOLS_ROOT, else the git top level of the current directory, else it."""
    if os.environ.get("PAPER_TOOLS_ROOT"):
        return Path(os.environ["PAPER_TOOLS_ROOT"]).resolve()
    try:
        git = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"], capture_output=True, text=True
        )
    except OSError:  # no git on PATH
        return Path.cwd()
    top = git.stdout.strip()
    return Path(top) if git.returncode == 0 and top else Path.cwd()


def _resolve(value, root):
    if value == "":
        return None
    path = Path(value)
    return path if path.is_absolute() else root / path


def load(root=None, config=None):
    """The resolved config (see the module docstring); root and config override discovery."""
    root = Path(root).resolve() if root is not None else find_root()
    if config is None and os.environ.get("PAPER_TOOLS_CONFIG"):
        config = os.environ["PAPER_TOOLS_CONFIG"]
    if config is not None:
        config = Path(config)
        if not config.is_file():
            _fail(f"no config file at {config}")
    elif (root / DEFAULT_CONFIG).is_file():
        config = root / DEFAULT_CONFIG

    data = {}
    if config is not None:
        try:
            with open(config, "rb") as handle:
                data = tomllib.load(handle)
        except (OSError, tomllib.TOMLDecodeError) as exc:
            _fail(f"cannot read {config}: {exc}")

    cfg = copy.deepcopy(DEFAULTS)
    for table, values in data.items():
        if table not in DEFAULTS or not isinstance(values, dict):
            _fail(f"{config}: unknown table [{table}]")
        for key, value in values.items():
            if key not in DEFAULTS[table]:
                _fail(f"{config}: unknown key {table}.{key}")
            want = type(DEFAULTS[table][key])
            if type(value) is not want:
                _fail(f"{config}: {table}.{key} must be a TOML {want.__name__}")
            cfg[table][key] = value

    for table, keys in PATH_KEYS.items():
        for key in keys:
            cfg[table][key] = _resolve(cfg[table][key], root)
    notes = []
    for note in cfg["literature"]["notes"]:
        file, sep, heading = note.partition("::")
        notes.append(f"{_resolve(file, root)}{sep}{heading}")
    cfg["literature"]["notes"] = notes
    cfg["project"] = {"root": root, "config": config}
    return cfg


def main(argv=None):
    parser = argparse.ArgumentParser(description="Print the resolved config.")
    parser.add_argument("key", nargs="?", help="one dotted key, such as build.pdf")
    args = parser.parse_args(argv)
    cfg = load()
    if args.key is None:
        print(json.dumps(cfg, indent=2, default=str))
        return 0
    table, _, key = args.key.partition(".")
    if table not in cfg or key not in cfg[table]:
        _fail(f"unknown key {args.key}")
    value = cfg[table][key]
    if value is None:
        print("")
    elif isinstance(value, (bool, list, dict)):
        print(json.dumps(value, default=str))
    else:
        print(value)
    return 0


if __name__ == "__main__":
    sys.exit(main())
