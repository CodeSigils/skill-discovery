#!/usr/bin/env python3
"""Validate repository documentation and the shipped Agent Skills payload."""

from __future__ import annotations

import re
import sys
from datetime import date, datetime
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[2]
DOCS_DIR = ROOT / "docs"
SKILLS_DIR = ROOT / "skills"
README_PATH = ROOT / "README.md"
FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", re.DOTALL)
FENCE_RE = re.compile(r"^```([^`]*)$")
MARKDOWN_LINK_RE = re.compile(r"\[[^]]+\]\(([^)]+)\)")
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def parse_frontmatter(content: str) -> dict | None:
    """Return parsed leading YAML frontmatter, or None."""
    match = FRONTMATTER_RE.search(content)
    if not match:
        return None
    try:
        frontmatter = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None
    return frontmatter if isinstance(frontmatter, dict) else None


def check_expiry(frontmatter: dict, label: str) -> list[str]:
    """Require a valid, non-expired expiry date for dated research docs."""
    value = frontmatter.get("expires")
    if value is None:
        return [f"{label}: missing required field 'expires'"]
    if isinstance(value, datetime):
        expiry = value.date()
    elif isinstance(value, date):
        expiry = value
    elif isinstance(value, str):
        try:
            expiry = date.fromisoformat(value)
        except ValueError:
            return [f"{label}: 'expires' is not YYYY-MM-DD"]
    else:
        return [f"{label}: 'expires' is not a date or string"]
    if expiry < date.today():
        return [f"{label}: expired on {expiry.isoformat()}"]
    return []


def check_fences(content: str, label: str) -> list[str]:
    """Require matched fences and a language on opening fences."""
    errors: list[str] = []
    opening: tuple[int, str] | None = None
    for line_number, line in enumerate(content.splitlines(), start=1):
        match = FENCE_RE.match(line)
        if not match:
            continue
        if opening is None:
            language = match.group(1).strip()
            opening = (line_number, language)
            if not language:
                errors.append(f"{label}:{line_number}: opening code fence has no language")
        else:
            opening = None
    if opening is not None:
        errors.append(f"{label}:{opening[0]}: unmatched code fence")
    return errors


def check_relative_links(path: Path, content: str) -> list[str]:
    """Ensure relative Markdown links resolve inside the repository."""
    errors: list[str] = []
    for target in MARKDOWN_LINK_RE.findall(content):
        target = target.split("#", 1)[0].strip()
        if not target or "://" in target or target.startswith(("#", "mailto:")):
            continue
        resolved = (path.parent / target).resolve()
        try:
            resolved.relative_to(ROOT.resolve())
        except ValueError:
            errors.append(f"{path.relative_to(ROOT)}: link escapes repository: {target}")
            continue
        if not resolved.exists():
            errors.append(f"{path.relative_to(ROOT)}: missing link target: {target}")
    return errors


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
    errors.extend(check_relative_links(path, content))
    return errors


def validate_skill(path: Path) -> list[str]:
    """Validate Agent Skills frontmatter, size, references, and fences."""
    label = str(path.relative_to(ROOT))
    content = path.read_text(encoding="utf-8")
    frontmatter = parse_frontmatter(content)
    if frontmatter is None:
        return [f"{label}: missing or invalid YAML frontmatter"]

    errors: list[str] = []
    name = frontmatter.get("name")
    description = frontmatter.get("description")
    if not isinstance(name, str) or not SKILL_NAME_RE.fullmatch(name):
        errors.append(f"{label}: invalid or missing skill name")
    elif name != path.parent.name:
        errors.append(f"{label}: name '{name}' does not match directory '{path.parent.name}'")
    if not isinstance(description, str) or not description.strip():
        errors.append(f"{label}: missing non-empty description")
    elif len(description) > 1024:
        errors.append(f"{label}: description exceeds 1024 characters")
    line_count = len(content.splitlines())
    if line_count > 500:
        errors.append(f"{label}: {line_count} lines exceeds the 500-line payload budget")
    errors.extend(check_fences(content, label))
    errors.extend(check_relative_links(path, content))
    return errors


def validate_skill_reference(path: Path) -> list[str]:
    """Validate one supporting Markdown file in a shipped skill payload."""
    label = str(path.relative_to(ROOT))
    content = path.read_text(encoding="utf-8")
    errors = check_fences(content, label)
    errors.extend(check_relative_links(path, content))
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
        errors.extend(validate_skill(path))
        print(f"CHECK {path.relative_to(ROOT)}")
    for path in skill_references:
        errors.extend(validate_skill_reference(path))
        print(f"CHECK {path.relative_to(ROOT)}")

    if not README_PATH.exists():
        errors.append("README.md: missing")
    else:
        readme = README_PATH.read_text(encoding="utf-8")
        errors.extend(check_fences(readme, "README.md"))
        errors.extend(check_relative_links(README_PATH, readme))
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
