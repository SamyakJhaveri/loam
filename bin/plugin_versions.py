#!/usr/bin/env python3
"""Check the versions of the marketplace plugins that live in this repo.

Rule 1: each plugin with a local source declares the same version in
cultivation/marketplace/.claude-plugin/marketplace.json and in its own
.claude-plugin/plugin.json.

Rule 2: a plugin whose files differ from the merge base with origin/main (or
main) carries a higher MAJOR.MINOR.PATCH version than it had there. Installed
copies update only when the version changes, and CI checks a pull request
merged onto main, so a branch that reuses a version main already took fails.

Exit status: 0 pass, 1 fail, 3 rule 1 passed but rule 2 was skipped because
no merge base exists.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import posixpath
import re
import subprocess

MARKETPLACE = "cultivation/marketplace"
MANIFEST = f"{MARKETPLACE}/.claude-plugin/marketplace.json"
BASES = ("origin/main", "main")
SEMVER = re.compile(r"(\d+)\.(\d+)\.(\d+)")
SKIPPED = 3


def git(root: pathlib.Path, *args: str, check: bool = False) -> subprocess.CompletedProcess:
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, check=check)


def merge_base(root: pathlib.Path) -> tuple[str, str] | None:
    for ref in BASES:
        r = git(root, "merge-base", "HEAD", ref)
        if r.returncode == 0:
            return ref, r.stdout.strip()
    return None


def semver(version: object) -> tuple[int, ...] | None:
    m = SEMVER.fullmatch(version) if isinstance(version, str) else None
    return tuple(map(int, m.groups())) if m else None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", default=".")
    root = pathlib.Path(parser.parse_args().root)

    manifest = json.loads((root / MANIFEST).read_text(encoding="utf-8"))
    # A git-subdir source has no plugin.json in this repo to compare against.
    plugins = [p for p in manifest["plugins"] if isinstance(p.get("source"), str)]
    base = merge_base(root)
    errors = []
    for p in plugins:
        name, listed = p["name"], p.get("version")
        source = posixpath.normpath(posixpath.join(MARKETPLACE, p["source"]))
        plugin_json = f"{source}/.claude-plugin/plugin.json"
        version = json.loads((root / plugin_json).read_text(encoding="utf-8")).get("version")
        if listed != version:
            errors.append(f"{name}: marketplace.json says {listed} but {plugin_json} says {version}")
            continue
        if base is None:
            print(f"{name}: {version}")
            continue
        ref, sha = base
        if not git(root, "diff", "--name-only", sha, "--", source, check=True).stdout.strip():
            print(f"{name}: {version}, unchanged since {ref} ({sha[:8]})")
            continue
        old = git(root, "show", f"{sha}:{plugin_json}")
        if old.returncode != 0:
            print(f"{name}: {version}, new since {ref} ({sha[:8]})")
            continue
        was = json.loads(old.stdout).get("version")
        if semver(version) is None or semver(was) is None:
            errors.append(f"{name}: versions must be MAJOR.MINOR.PATCH, got {version} (was {was} at {ref})")
        elif semver(version) <= semver(was):
            errors.append(
                f"{name}: files under {source} changed since {ref} ({sha[:8]}) but version "
                f"{version} is not above {was}; bump it in plugin.json and marketplace.json"
            )
        else:
            print(f"{name}: {version}, up from {was} at {ref} ({sha[:8]})")
    for e in errors:
        print("FAIL:", e)
    if errors:
        return 1
    if base is None:
        print(f"NOTE: no merge base with {' or '.join(BASES)}; skipped the version-bump rule")
        return SKIPPED
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
