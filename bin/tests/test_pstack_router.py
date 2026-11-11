"""The sam-cc-setup pstack router names only skills the installed pstack has (docs/PSTACK.md, post-update check).

The router (cultivation/marketplace/sam-cc-setup/skills/pstack/SKILL.md) is a table of situations and the pstack
skills to read for each, then a list of every principle card. A pstack update can rename or drop a skill, and the
router would then send agents to a missing file; a new principle card would go unlisted. The drift test reads the
pstack folder from the real user's ~/.claude/plugins/installed_plugins.json (conftest points HOME at a scratch dir)
and skips when pstack is not installed, as on CI.
"""

from __future__ import annotations

import json
import os
import pathlib
import pwd
import re
import unittest

ROOT = pathlib.Path(__file__).resolve().parents[2]
ROUTER = ROOT / "cultivation/marketplace/sam-cc-setup/skills/pstack/SKILL.md"


def router_names() -> tuple[set[str], list[str]]:
    """(skill names in the table, principle names in the list) as the router's text gives them."""
    table, principles, in_list = set(), [], False
    for line in ROUTER.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if line.startswith("|") and len(cells) == 2 and not set(cells[1]) <= set("-") and cells[1] != "Skill":
            # Each `;` or `,` piece starts with a skill name: "tdd for a cheap local test", "how, why (spawns)".
            table |= {piece.split()[0] for piece in re.split(r"[;,]", cells[1]) if piece.strip()}
        if line == "Principles:":
            in_list = True
        elif in_list and line.startswith("- "):
            principles.append(line[2:].split(":", 1)[0])
    return table, principles


def installed_pstack() -> pathlib.Path | None:
    home = pathlib.Path(pwd.getpwuid(os.getuid()).pw_dir)
    try:
        registry = json.loads((home / ".claude/plugins/installed_plugins.json").read_text(encoding="utf-8"))
        path = pathlib.Path(registry["plugins"]["pstack@cursor-plugins"][0]["installPath"])
    except (OSError, ValueError, KeyError, IndexError, TypeError):
        return None
    return path if (path / "skills").is_dir() else None


class PstackRouterTests(unittest.TestCase):
    def test_router_parses_to_a_table_and_a_principle_list(self) -> None:
        # Guards the drift test: a parse that found nothing would pass it vacuously.
        table, principles = router_names()
        self.assertIn("principle-prove-it-works", table)
        self.assertIn("interrogate", table)
        self.assertGreaterEqual(len(principles), 20)
        self.assertEqual(len(principles), len(set(principles)))

    def test_every_router_name_is_an_installed_pstack_skill(self) -> None:
        pstack = installed_pstack()
        if pstack is None:
            self.skipTest("pstack is not installed (no pstack@cursor-plugins installPath in installed_plugins.json)")
        installed = {p.parent.name for p in (pstack / "skills").glob("*/SKILL.md")}
        table, principles = router_names()
        self.assertEqual(sorted((table | set(principles)) - installed), [], f"router names missing from {pstack}")
        cards = sorted(n for n in installed if n.startswith("principle-"))
        self.assertEqual(sorted(principles), cards, f"the router's principle list differs from {pstack}'s cards")


if __name__ == "__main__":
    unittest.main()
