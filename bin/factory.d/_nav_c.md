For any "where is" or "where does" question about this repository, before you open, grep, or guess at any file, first run `semble search "<query>" . --top-k 8 --content all --format json` and open only the files that command returns.
Semble is a semantic code-search tool; put your question in plain words as `<query>` and pass `.` as the repository root.
Use `--top-k 8`, not `-k`, to ask for the eight best matches, and `--content all` so the results include markdown and JSON files, which the default `--content code` leaves out.
Let the search point you at the files, then read them; do not fall back to a blind path search first.
