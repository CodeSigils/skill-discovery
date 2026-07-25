#!/usr/bin/env python3
"""Check that version numbers are consistent across project metadata files.

Verifies CITATION.cff and pyproject.toml contain the same version.
Optionally checks SKILL.md frontmatter if a version field is added later.
"""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def get_citation_version() -> str | None:
    """Extract version from CITATION.cff."""
    citation = ROOT / "CITATION.cff"
    if not citation.exists():
        return None
    text = citation.read_text(encoding="utf-8")
    match = re.search(r'^version:\s*["\']?([^"\'\s]+)["\']?\s*$', text, re.MULTILINE)
    return match.group(1) if match else None


def get_pyproject_version() -> str | None:
    """Extract version from pyproject.toml [project] section."""
    pyproject = ROOT / "pyproject.toml"
    if not pyproject.exists():
        return None
    text = pyproject.read_text(encoding="utf-8")
    match = re.search(r'^(?:\[project\].*?)?version\s*=\s*["\']([^"\']+)["\']', text, re.MULTILINE | re.DOTALL)
    if match:
        return match.group(1)
    # Simpler pattern: find version = "x.y.z" under [project]
    in_project = False
    for line in text.splitlines():
        if line.strip().startswith("[project]"):
            in_project = True
        elif line.strip().startswith("["):
            in_project = False
        elif in_project:
            m = re.match(r'^version\s*=\s*["\']([^"\']+)["\']', line)
            if m:
                return m.group(1)
    return None


def main() -> int:
    errors: list[str] = []

    citation_version = get_citation_version()
    pyproject_version = get_pyproject_version()

    # Collect all available sources
    sources: dict[str, str] = {}
    if citation_version:
        sources["CITATION.cff"] = citation_version
    if pyproject_version:
        sources["pyproject.toml"] = pyproject_version

    if len(sources) < 2:
        if not sources:
            print("WARN: no version sources found (CITATION.cff, pyproject.toml)")
        elif "CITATION.cff" not in sources:
            print("WARN: CITATION.cff missing or has no version field")
        elif "pyproject.toml" not in sources:
            print("WARN: pyproject.toml missing or has no version field")
        # Still OK if at least one source exists
        return 0

    # Check consistency
    versions = set(sources.values())
    if len(versions) > 1:
        for source, ver in sorted(sources.items()):
            errors.append(f"version-mismatch: {source} has version {ver!r}")
        # Show what they should be
        most_common = max(versions, key=lambda v: sum(1 for sv in sources.values() if sv == v))
        errors.append(f"version-mismatch: expected all sources to use {most_common!r}")
    else:
        ver = versions.pop()
        print(f"PASS: all version sources agree on {ver!r}")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
