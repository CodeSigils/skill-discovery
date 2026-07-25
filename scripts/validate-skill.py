#!/usr/bin/env python3
"""Validate a single Agent Skill directory.

Usage:
    python scripts/validate-skill.py skills/skill-discovery
    python scripts/validate-skill.py skills/skill-discovery --root /path/to/repo

The script inspects SKILL.md inside the given directory for frontmatter
correctness, payload budget, description limits, code fence balance,
and relative link integrity.  Exit code 0 means clean, 1 means violations
found (printed to stderr).
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from _common import validate_skill


def find_repo_root(start: Path) -> Path | None:
    """Walk upward from *start* looking for a ``.git`` directory."""
    current = start.resolve()
    while current != current.parent:
        if (current / ".git").is_dir():
            return current
        current = current.parent
    return None


def validate_skill_entry(skill_md: Path, root: Path | None = None) -> list[str]:
    """Validate a skill, auto-detecting root if not provided."""
    if root is None:
        detected = find_repo_root(skill_md)
        root = detected if detected is not None else skill_md.resolve().parent.parent.parent
    return validate_skill(skill_md, root)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("skill_dir", help="Directory containing SKILL.md")
    parser.add_argument(
        "--root",
        help="Repository root for link validation (auto-detected if omitted)",
    )
    args = parser.parse_args()
    skill_path = Path(args.skill_dir).resolve()
    skill_md = skill_path / "SKILL.md"
    if not skill_md.exists():
        print(f"ERROR: {skill_md} not found", file=sys.stderr)
        return 1
    root = Path(args.root).resolve() if args.root else find_repo_root(skill_path)
    errors = validate_skill_entry(skill_md, root)
    for error in errors:
        print(error, file=sys.stderr)
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
