"""macOS shapes of `ps` and `date` for factory tests, so a Linux host exercises the Mac paths too.

The fake `ps` pads `lstart` with four trailing spaces as macOS ps does. The fake `date` rejects `-d` as BSD date does
and answers `-j [-u] -f <format> <value> +%s` like it, taking the fields a format lacks from now; any other call runs
the real `date`. Put path(dir) first on PATH.
"""

from __future__ import annotations

import os
import pathlib
import shutil
import sys

PS = """#!/bin/bash
out=$('{ps}' "$@"); rc=$?
case " $* " in *lstart=*) end='    ' ;; *) end= ;; esac
[ -z "$out" ] || printf '%s%s\\n' "$out" "$end"
exit $rc
"""

DATE = """#!{python}
import calendar, datetime, os, sys, time
a = sys.argv[1:]
if "-d" in a:
    sys.exit("date: illegal option -- d")
if "-j" not in a:
    os.execv({date!r}, [{date!r}] + a)
i = a.index("-f")
fmt, val, out = a[i + 1], a[i + 2], a[i + 3:]
try:
    t = datetime.datetime.strptime(val, fmt.replace("%T", "%H:%M:%S"))
except ValueError:
    sys.exit("date: illegal time format")
if out != ["+%s"]:
    sys.exit("date: this stub prints only +%s")
if "%Y" not in fmt:
    n = datetime.datetime.now()
    t = t.replace(year=n.year, month=n.month, day=n.day)
print(calendar.timegm(t.timetuple()) if "-u" in a else int(time.mktime(t.timetuple())))
"""


def path(d: pathlib.Path) -> str:
    """Write the fake ps and date into d; return a PATH that finds them first."""
    d.mkdir(parents=True, exist_ok=True)
    for name, body in (("ps", PS.format(ps=shutil.which("ps"))),
                       ("date", DATE.format(python=sys.executable, date=shutil.which("date")))):
        (d / name).write_text(body)
        (d / name).chmod(0o755)
    return f"{d}{os.pathsep}{os.environ['PATH']}"
