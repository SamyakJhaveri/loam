#!/bin/bash
# Prints the absolute pstack folder, or nothing when pstack is not installed; always exits 0.
jq -r '.plugins["pstack@cursor-plugins"][0].installPath // empty' ~/.claude/plugins/installed_plugins.json 2> /dev/null
exit 0
