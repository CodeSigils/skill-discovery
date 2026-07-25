#!/usr/bin/env python3
"""Validate repository documentation and the shipped Agent Skills payload."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))
from _common import (
    ROOT,
    check_fences,
    check_relative_links,
    parse_expiry_date,
    parse_frontmatter,
    validate_skill,
)

DOCS_DIR = ROOT / "docs"
SKILLS_DIR = ROOT / "skills"
README_PATH = ROOT / "README.md"


def check_expiry(frontmatter: dict, label: str) -> list[str]:
    """Require a valid, non-expired expiry date for dated research docs."""
    value = frontmatter.get("expires")
    if value is None:
        return [f"{label}: missing required field 'expires'"]
    expiry = parse_expiry_date(value)
    if expiry is None:
        return [f"{label}: 'expires' is not a valid date"]
    if expiry < date.today():
        return [f"{label}: expired on {expiry.isoformat()}"]
    return []


def validate_research_doc(path: Path) -> list[str]:
    """Validate one dated repository-only research document."""
    label = str(path.relative_to(ROOT))
    content = path.read_text(encoding="utf-8")
    frontmatter = parse_frontmatter(content)
    if frontmatter is None:
        return [f"{label}: missing or invalid YAML frontmatter"]
    errors = [
        f"{label}: missing required field '{field}'"
        for field in ("status", "date", "purpose")
        if field not in frontmatter
    ]
    errors.extend(check_expiry(frontmatter, label))
    errors.extend(check_fences(content, label))
    errors.extend(check_relative_links(path, content, ROOT))
    return errors


def validate_skill_reference(path: Path) -> list[str]:
    """Validate one supporting Markdown file in a shipped skill payload."""
    label = str(path.relative_to(ROOT))
    content = path.read_text(encoding="utf-8")
    errors = check_fences(content, label)
    errors.extend(check_relative_links(path, content, ROOT))
    return errors


def main() -> int:
    """Run all deterministic Markdown and payload checks."""
    errors: list[str] = []
    paths = sorted(DOCS_DIR.glob("*.md"))
    skills = sorted(SKILLS_DIR.glob("*/SKILL.md"))
    skill_references = sorted(
        path for path in SKILLS_DIR.rglob("*.md") if path.name != "SKILL.md"
    )
    if not paths:
        errors.append("docs: no Markdown research documents found")
    if not skills:
        errors.append("skills: no SKILL.md payload found")

    for path in paths:
        errors.extend(validate_research_doc(path))
        print(f"CHECK {path.relative_to(ROOT)}")
    for path in skills:
        errors.extend(validate_skill(path, ROOT))
        print(f"CHECK {path.relative_to(ROOT)}")
    for path in skill_references:
        errors.extend(validate_skill_reference(path))
        print(f"CHECK {path.relative_to(ROOT)}")

    if not README_PATH.exists():
        errors.append("README.md: missing")
    else:
        readme = README_PATH.read_text(encoding="utf-8")
        errors.extend(check_fences(readme, "README.md"))
        errors.extend(check_relative_links(README_PATH, readme, ROOT))
        print("CHECK README.md")

    if errors:
        print("\nFAIL: documentation or payload validation failed")
        for error in errors:
            print(f"  {error}")
        return 1
    print("\nPASS: documentation and shipped payload are valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
