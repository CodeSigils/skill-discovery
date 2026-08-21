#!/usr/bin/env python3
"""Check version consistency across pyproject.toml and CITATION.cff."""

from __future__ import annotations

import re
import sys

from _common import ROOT

# Version source files — single source of truth
CITATION_CFF = "CITATION.cff"
PYPROJECT_TOML = "pyproject.toml"


def get_citation_version() -> str | None:
    """Extract version from CITATION.cff."""
    citation = ROOT / CITATION_CFF
    if not citation.exists():
        return None
    text = citation.read_text(encoding="utf-8")
    match = re.search(r'^version:\s*["\']?([^"\'\s]+)["\']?\s*$', text, re.MULTILINE)
    return match.group(1) if match else None


def get_pyproject_version() -> str | None:
    """Extract version from pyproject.toml [project] section.

    Uses a line-by-line parser that respects section boundaries —
    avoids matching version fields in unrelated sections like [tool.ruff].
    """
    pyproject = ROOT / PYPROJECT_TOML
    if not pyproject.exists():
        return None
    text = pyproject.read_text(encoding="utf-8")
    in_project = False
    for line in text.splitlines():
        stripped = line.strip()
        if stripped.startswith("[project]"):
            in_project = True
        elif stripped.startswith("["):
            in_project = False
        elif in_project:
            m = re.match(r'^version\s*=\s*["\']([^"\']+)["\']', line.lstrip())
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
        sources[CITATION_CFF] = citation_version
    if pyproject_version:
        sources[PYPROJECT_TOML] = pyproject_version

    if len(sources) < 2:
        if not sources:
            print("WARN: no version sources found (CITATION.cff, pyproject.toml)")
        elif CITATION_CFF not in sources:
            print("WARN: CITATION.cff missing or has no version field")
        elif PYPROJECT_TOML not in sources:
            print("WARN: pyproject.toml missing or has no version field")
        # Still OK if at least one source exists
        return 0

    # Check consistency
    citation_ver = sources.get(CITATION_CFF)
    pyproject_ver = sources.get(PYPROJECT_TOML)
    if citation_ver != pyproject_ver:
        for source, ver in sorted(sources.items()):
            errors.append(f"version-mismatch: {source} has version {ver!r}")
        expected = citation_ver or pyproject_ver
        errors.append(f"version-mismatch: expected all sources to use {expected!r}")
    else:
        print(f"PASS: all version sources agree on {citation_ver!r}")

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
