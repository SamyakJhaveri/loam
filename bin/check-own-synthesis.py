#!/usr/bin/env python3
"""Local dev guard: flag verbatim runs shared between seed/ text and the private
course backup, so 'own-synthesis' rewrites don't leave lifted expression behind.

Why this exists: the marker greps (`\\bICM\\b`, `jvc`, module names) only catch
LABELED references. Uncited derivation is by definition unmarked and sails past
them (see the scaling-vs-automating.md BLOCK). This guard compares actual prose.

Needs the private course backup (default ~/loam-soil-backup). If absent it prints
SKIP and exits 0 — so CI and other clones (which never have the private course)
are never blocked. It is a LOCAL author aid, not a shippable CI gate.

ponytail: word-level N-gram shingle intersection; stdlib only (no pyyaml).
Usage: bin/check-own-synthesis.py [backup_dir] [--n N]
"""
import os
import re
import sys
import glob
import pathlib

N = 8  # minimum shared consecutive-word run to flag (8 identical words in a row is rarely coincidental)
BACKUP = os.path.expanduser("~/loam-soil-backup")
SEED = "seed/.claude"

# Consciously accepted shared runs. These are short FUNCTIONAL schemas, not prose: a
# blank-form document template and a kept-by-decision framework table. A blank form /
# table layout is uncopyrightable method (idea-expression merger), so these are waived by
# design and recorded here as an explicit, auditable decision — every OTHER shared run
# must be original. Each entry is the exact space-joined run the guard would print.
ACCEPTED_RUNS = {
    # CONTEXT.md six-section template header ("Task | Load These | Skip These") —
    # context-md-anatomy.md documents it; scaffold-context/SKILL.md generates it.
    "what to load task load these skip these",
    "to load task load these skip these task",
    "load task load these skip these task a",
    "what to load table task load these skip",
    "to load table task load these skip these",
    # L0/L1/L2 layer comparison table — the context-routing framework kept by explicit
    # decision (the ICM->context-routing rename preserved the L0/L1/L2 layer names). L0-budget.md.
    "on entry 300 tokens l2 stage contract what",
    "entry 300 tokens l2 stage contract what do",
    "300 tokens l2 stage contract what do i",
    "tokens l2 stage contract what do i do",
}

args = [a for a in sys.argv[1:]]
if "--n" in args:
    i = args.index("--n")
    N = int(args[i + 1])
    del args[i:i + 2]
if args:
    BACKUP = os.path.expanduser(args[0])


def words(text):
    return re.findall(r"[A-Za-z0-9']+", text.lower())


def shingles(ws, n):
    return {tuple(ws[i:i + n]) for i in range(len(ws) - n + 1)}


def main():
    if not os.path.isdir(BACKUP):
        print(f"SKIP: course backup {BACKUP} not present — own-synthesis guard is a local-only aid.")
        return 0

    course = set()
    for f in glob.glob(f"{BACKUP}/**/*.md", recursive=True):
        course |= shingles(words(pathlib.Path(f).read_text(errors="ignore")), N)
    if not course:
        print(f"SKIP: no course text found under {BACKUP}.")
        return 0

    seed_files = (
        glob.glob(f"{SEED}/**/*.md", recursive=True)
        + glob.glob(f"{SEED}/**/*.sh", recursive=True)
    )
    flagged = []
    for f in sorted(seed_files):
        ws = words(pathlib.Path(f).read_text(errors="ignore"))
        hits = {h for h in (shingles(ws, N) & course) if " ".join(h) not in ACCEPTED_RUNS}
        if hits:
            flagged.append((f, hits))

    if not flagged:
        print(f"OWN-SYNTHESIS OK: no shared >={N}-word verbatim run between seed/ and the course backup.")
        return 0

    print(f"OWN-SYNTHESIS FAIL: {len(flagged)} seed file(s) share >={N}-word verbatim runs with the course.\n")
    for f, hits in flagged:
        print(f"{f}  ({len(hits)} run(s)):")
        for h in sorted(hits):
            print("   … " + " ".join(h) + " …")
        print()
    return 1


if __name__ == "__main__":
    sys.exit(main())
