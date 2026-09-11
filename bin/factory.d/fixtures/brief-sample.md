# Sample: publish a Track B ticket from one session
Brief:
Add a `bin/factory publish` subcommand that turns a linted ticket file into a GitHub issue.
Where: bin/factory (a new publish subcommand), docs/factory/CONTRACT.md (the Seam with to-tickets section).
Done means: bin/factory publish FILE opens an issue whose body is the file, and bin/factory lint still accepts every committed fixture.
Out of scope: editing an issue after it is opened; any change to the loop, the grader, or to-tickets.
Track: B    Risk: high    Mode: build    Open question: none
Blocked by: none

## Goal and why
A Track B brief should reach GitHub without a second tool.
Today the author copies the linted body into the web UI by hand; a `publish` subcommand closes stage 2 in one session (ROADMAP.md F5).

## Do not touch
The standing list. Except: bin/factory (this ticket adds the publish subcommand).

## Out of scope
Editing an issue after it is opened; any change to the loop, the grader, or to-tickets.

## Done checks
```done-checks
guard bash -n bin/factory && pass syntax || fail syntax "bin/factory does not parse"
out=$(bin/factory 2>&1); grep -q 'publish' <<<"$out" && pass advertised || fail advertised "the usage banner does not name publish"
out=$(bin/factory publish --help 2>&1); grep -q 'issue' <<<"$out" && pass documented || fail documented "publish --help does not mention the issue it opens"
guard bin/factory lint bin/factory.d/fixtures/S1.md >/dev/null && pass lint-still-green || fail lint-still-green "lint regressed on a known-good fixture"
```

## Worker
worker: claude
codex-review: yes
effort: medium
goal: the done-checks block prints no FAIL line, or stop after 60 turns

## Decisions
docs/factory/CONTRACT.md, docs/factory/ROADMAP.md
