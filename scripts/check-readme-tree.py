#!/usr/bin/env python3
"""Check README file tree is in sync with actual repository layout."""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

from _common import ROOT

README = ROOT / "README.md"

# Special entries checked by other scripts
SYMLINK_ENTRY = ".agents/skills/skill-discovery"

# Directories to exclude from reverse drift check
EXCLUDE_DIRS = {".git", "node_modules", ".omo", "__pycache__", ".ruff_cache"}
EXCLUDE_FILES = {".gitignore", "uv.lock", "CITATION.cff", "advisory-baseline.json"}


def git_tracked_files() -> set[str]:
    """Return set of tracked files using git ls-files (excludes ignored)."""
    try:
        result = subprocess.run(
            ["git", "ls-files"],
            cwd=ROOT,
            capture_output=True,
            text=True,
            check=True,
        )
        return {
            line.strip()
            for line in result.stdout.splitlines()
            if line.strip() and (ROOT / line.strip()).exists()
        }
    except (subprocess.CalledProcessError, FileNotFoundError):
        return set()


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
        if filepath == SYMLINK_ENTRY:
            continue
        full_path = ROOT / filepath
        if not full_path.exists():
            errors.append(f"stale-tree-entry: {filepath} is in README tree but does not exist on disk")

    # Reverse check: tracked files not in README tree (stale drift)
    tracked = git_tracked_files()
    tree_set = set(tree_files)
    unlisted = sorted(
        f for f in tracked
        if f not in tree_set
        and not any(part in EXCLUDE_DIRS for part in Path(f).parts)
        and Path(f).name not in EXCLUDE_FILES
        and not f.startswith(".github/")
        and not f.startswith(".agents/")
    )
    for filepath in unlisted:
        errors.append(f"unlisted-file: {filepath} exists on disk but is not in README tree")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print(f"PASS: all {len(tree_files)} files in README tree exist on disk, no unlisted files")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
