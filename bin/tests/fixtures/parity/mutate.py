#!/usr/bin/env python3
"""Mutation check for bin/factory-parity: break each rule in a copy and show which test turns red.

  python3 bin/tests/fixtures/parity/mutate.py

Each row is (rule, text in bin/factory-parity, its broken replacement). Prints KILLED (some test went red) or ALIVE
per rule and exits 1 if any mutation stays alive, so a rule no test guards shows here. Add a row with each new rule.
"""
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[4]
MUTATIONS = [  # (rule, old, new): each old must occur exactly once
    ("full read only", 'def full_reads(t: Transcript, j: int) -> set[tuple[str, str]]:\n    """',
     'def full_reads(t: Transcript, j: int) -> set[tuple[str, str]]:\n    return skill_reads(*t.calls[j][1:])\n    """'),
    ("713 reviewer only a plain cat is a full Bash read", 'return words[1] if len(words) == 2 and words[0] == "cat" and',
     'return words[-1] if words[0] in ("cat", "head", "sed") or'),
    ("713 Codex 1 a call with no result proves nothing", "return self.result(i) is not None and self.ran(i)",
     "return self.ran(i)"),
    ("713 Codex 2 each named agent's transcript", "    if missing:\n        raise Unusable", "    if False:\n        raise Unusable"),
    ("713 Codex 3 a $VAR before its assignment stays", "values[r.group(1)][0] <= at + r.start()", "True"),
    ("713 Codex 3 a conditional assignment stays", r're.search(r"(?:\A|[;\n])[ \t]*\Z", before)', "True"),
    ("713 Codex 4 cd - ends the scratch exemption", '        elif not (m.group(1) == "cd" and target and',
     '        elif False and (m.group(1) == "cd" and target and'),
    ("a blocked or denied call never ran",
     "return self.ids[i] not in self.denied and not (res and NOT_RUN.search(res[1]))", "return True"),
    ("audit3 C2 a failed read reads nothing", "and self.ran(i) and self.ids[i] not in self.errors", "and self.ran(i)"),
    ("a failed read reads nothing", "    if not res or not t.ok(j):\n        return set()", "    if not res:\n        return set()"),
    ("a cat counts only when its result shows the file", "return {f for f in skill_paths(read, {}) if shows(res[1], f[1])}",
     "return set(skill_paths(read, {}))"),
    ("a Read counts only when its result shows the file", "return {f for f in skill_reads(name, inp) if shows(res[1], f[1])}",
     "return skill_reads(name, inp)"),
    ("a compound SKILL.md read is UNSURE", '    return READ_DOUBT if "SKILL.md" in bare and compound(cmd) else None', "    return None"),
    ("P4 no record is UNSURE", "        elif not checks.is_file():", "        elif False:"),
    ("P4 needs the check-green line", r'r"(?:PASS|FAIL) check-green\b"', r'r"(?:PASS|FAIL) "'),
    ("audit4 F2 P8 a no-result row is no review", ' and e.get("subtype") != "no-result"]', ']'),
    ("audit3 C4 a failed proof call proves nothing", 'in text and t.ok(j):', 'in text and t.ran(j):'),
    ("audit3 F2 a Round N: prefix", r"(?:Round \d+:\s*)?pstack:", "pstack:"),
    ("C4 brief-named read", "    names = named_skills(f\"{t.brief}\\n{run.ticket}\", run.pstack)\n",
     "    names = set()\n"),
    ("F5 notes are no change", 'NOTES = re.compile(r"/[0-9a-f]{8}/worker/|', 'NOTES = re.compile(r"(?!x)x/[0-9a-f]{8}/worker/|'),
    ("cd into scratch", "            where = bool(NOTES.search(target))", "            where = False"),
    ("VAR=value expansion", "    return expand(text, 0) if values else text", "    return text"),
    ("cat heredoc body is data", r'''if not re.search(r"\b(?:cat|tee)\b[^\n]*$", m.string[:m.start()])''',
     r'''if True or not re.search(r"\b(?:cat|tee)\b[^\n]*$", m.string[:m.start()])'''),
    ("quoted ; ends no write", '''        bare = re.sub(''', '''        bare = cmd or re.sub('''),
    ("P3 method anywhere before the change", "if (m := pstack_methods(full_reads(t, j), pstack))), None)",
     "if j >= (router_index(t, i) or 0) and (m := pstack_methods(full_reads(t, j), pstack))), None)"),
    ("P3 needs a pstack: line (F3)", "        if changed and not run.attended and not logged:", "        if False:"),
    ("P3 pstack: line read (713 Codex 5: that same file)", "            elif any(same_path(path, p) for p in read_paths):",
     "            elif name in read:"),
    ("P1 plugin-dir", "        elif paths != [want]:", "        elif False:"),
    ("P1 memory view", "        if MEMORY_VIEW in lines:", "        if True:"),
    ("P7 init auto", 'rows.append(("PASS" if mode == "auto"', 'rows.append(("PASS" if True'),
    ("P7 sandbox off", '("PASS" if enabled is False else "FAIL"', '("PASS" if True else "FAIL"'),
    ("P7 digests equal", "        elif differ:", "        elif False:"),
    ("P7 git digests present", "        elif lacking:", "        elif False:"),
    ("P7 synced ignored", '''        a, b = ({k: v for k, v in d.items() if "/.claude/skills/synced/" not in k} for d in (a, b))\n''', ""),
    ("P7 lists denials", "            for line, tid, reason in t.denials:", "            for line, tid, reason in []:"),
    ("P8 served Fable", 'for k, e in reviewers if e.get("served_models") != [FABLE]]', 'for k, e in reviewers if False]'),
    ("P8 both reviews present", '                bad.append(f"no readable {name}")\n', '                pass\n'),
    ("P8 ids = blocking ids", "            if sorted(ids) != sorted(blocking):", "            if False:"),
    ("P8 Codex blocking severities", 'BLOCKING = {"reviewer": {"high", "medium"}, "codex": {"critical", "high"}}',
     'BLOCKING = {"reviewer": {"high", "medium"}, "codex": {"critical", "high", "medium"}}'),
    ("P8 REJECTED evidence", '                elif verdict == "REJECTED" and not all(', '                elif False and all('),
    ("P8 UNVERIFIED fails", 'VERDICTS = {"CONFIRMED", "PARTLY", "REJECTED"}', 'VERDICTS = {"CONFIRMED", "PARTLY", "REJECTED", "UNVERIFIED"}'),
    ("audit3 C6 P8 verify.json sha", '            if verify.get("sha") != graded_sha:', '            if False:'),
    ("audit3 F8 P8 unparseable review", '            if data.get("unparseable") is True:', '            if False:'),
    ("attended subagents", '[path.with_suffix("") / "subagents"]', '[]'),
    ("attended P6 touched files", 'and "/.claude/" not in (p := str(inp.get("file_path") or "")) and COVERED_PATH.search(p)})',
     'and "/.claude/" not in (p := str(inp.get("file_path") or "")) and False})'),
]
src = (ROOT / "bin/factory-parity").read_text()
alive = 0
for rule, old, new in MUTATIONS:
    assert src.count(old) == 1, (rule, src.count(old))
    with tempfile.TemporaryDirectory() as d:
        tests = Path(d) / "bin/tests"
        shutil.copytree(ROOT / "bin/tests/fixtures/parity", tests / "fixtures/parity")
        shutil.copy(ROOT / "bin/tests/test_factory_parity.py", tests)
        (Path(d) / "bin/factory-parity").write_text(src.replace(old, new))
        r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", str(tests / "test_factory_parity.py")],
                           capture_output=True, text=True, cwd=d)
        failed = [x.split("::", 1)[1].split(" ")[0] for x in r.stdout.splitlines() if x.startswith("FAILED")]
        alive += not failed
        print(f"{'KILLED' if failed else 'ALIVE '} {rule}: {len(failed)} red: {', '.join(failed)[:200]}")
print(f"{len(MUTATIONS) - alive}/{len(MUTATIONS)} mutations turn a test red")
sys.exit(1 if alive else 0)
