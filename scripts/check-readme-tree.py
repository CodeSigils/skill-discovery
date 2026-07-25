#!/usr/bin/env python3
"""Validate that files listed in README's repository tree actually exist.

Extracts the file tree from README.md (between ```text markers), parses
the file paths with directory context, and verifies each one exists on disk.
Does NOT check for completeness — the tree is curated, not exhaustive.
Uses the LAST ```text block (the full repo tree), not the skills payload tree.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
README = ROOT / "README.md"


def extract_tree_files(readme: Path) -> list[str]:
    """Extract file paths from the last ```text tree block in README.md."""
    if not readme.exists():
        return []
    text = readme.read_text(encoding="utf-8")
    # Find ALL ```text blocks, use the last one (full repo tree)
    matches = list(re.finditer(r"```text\n(.*?)```", text, re.DOTALL))
    if not matches:
        return []
    tree_block = matches[-1].group(1)

    # Stack of (depth, path) for tracking directory context
    stack: list[tuple[int, str]] = []
    files: list[str] = []
    root_prefix = ""

    for line in tree_block.splitlines():
        if not line.strip():
            continue

        match_branch = re.search(r"[├└]──\s*(.+)$", line)
        if not match_branch:
            # This is the root line (e.g., "skill-discovery/")
            name = line.strip().rstrip("/")
            root_prefix = name
            stack = [(0, name)]
            continue

        name = match_branch.group(1).strip()
        # Calculate depth from the position of the branch character
        branch_pos = line.index("├") if "├" in line else line.index("└")
        depth = branch_pos // 4 + 1

        # Pop stack to find parent
        while stack and stack[-1][0] >= depth:
            stack.pop()

        if name.endswith("/"):
            # Directory — push onto stack
            parent_path = stack[-1][1] if stack else ""
            full_path = f"{parent_path}/{name.rstrip('/')}" if parent_path else name.rstrip("/")
            stack.append((depth, full_path))
        else:
            # File — record it
            clean_name = re.split(r"\s+#", name)[0].strip()
            parent_path = stack[-1][1] if stack else ""
            full_path = f"{parent_path}/{clean_name}" if parent_path else clean_name
            # Strip root prefix (e.g., "skill-discovery/")
            if root_prefix and full_path.startswith(root_prefix + "/"):
                full_path = full_path[len(root_prefix) + 1 :]
            files.append(full_path)

    return sorted(files)


def main() -> int:
    errors: list[str] = []

    tree_files = extract_tree_files(README)

    if not tree_files:
        errors.append("check-readme-tree: no ```text tree block found in README.md")
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    # Check each listed file exists
    for filepath in tree_files:
        # Skip special entries
        if filepath == ".agents/skills/skill-discovery":
            continue  # Symlink, checked separately by validate-ci.py
        full_path = ROOT / filepath
        if not full_path.exists():
            errors.append(f"stale-tree-entry: {filepath} is in README tree but does not exist on disk")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print(f"PASS: all {len(tree_files)} files in README tree exist on disk")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
