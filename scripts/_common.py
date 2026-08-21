"""Shared validation utilities for repository scripts."""

from __future__ import annotations

import re
from datetime import date, datetime
from pathlib import Path
from typing import Any

import yaml

ROOT = Path(__file__).resolve().parents[1]

FRONTMATTER_RE = re.compile(r"\A---\r?\n(.*?)\r?\n---(?:\r?\n|\Z)", re.DOTALL)
FENCE_RE = re.compile(r"^```([^`]*)$")
MARKDOWN_LINK_RE = re.compile(r"\[[^]]+\]\(([^)]+)\)")
SKILL_NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")


def parse_frontmatter(content: str) -> dict[str, Any] | None:
    """Return parsed leading YAML frontmatter, or None."""
    match = FRONTMATTER_RE.search(content)
    if not match:
        return None
    try:
        frontmatter = yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None
    return frontmatter if isinstance(frontmatter, dict) else None


def parse_expiry_date(value: Any) -> date | None:
    """Parse an expiry value (datetime, date, or ISO string) into a date.

    Returns None if the value is missing, unparseable, or not a date-like type.
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if isinstance(value, str):
        try:
            return date.fromisoformat(value)
        except ValueError:
            return None
    return None


def check_fences(content: str, label: str) -> list[str]:
    """Require matched fences and a language tag on opening fences."""
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
                errors.append(
                    f"{label}:{line_number}: opening code fence has no language"
                )
        else:
            opening = None
    if opening is not None:
        errors.append(f"{label}:{opening[0]}: unmatched code fence")
    return errors


def check_relative_links(path: Path, content: str, root: Path) -> list[str]:
    """Ensure relative Markdown links resolve inside the repository."""
    errors: list[str] = []
    for raw in MARKDOWN_LINK_RE.findall(content):
        target = raw.split("#", 1)[0].split("?", 1)[0].strip()
        if not target or "://" in target or target.startswith(("#", "mailto:")):
            continue
        resolved = (path.parent / target).resolve()
        try:
            resolved.relative_to(root.resolve())
        except ValueError:
            errors.append(
                f"{path.relative_to(root)}: link escapes repository: {target}"
            )
            continue
        if not resolved.exists():
            errors.append(
                f"{path.relative_to(root)}: missing link target: {target}"
            )
    return errors


def find_markdown_files(root: Path) -> list[Path]:
    """Collect all markdown files, skipping .git and node_modules."""
    return sorted(
        p
        for p in root.rglob("*.md")
        if ".git" not in p.parts and "node_modules" not in p.parts and ".omo" not in p.parts
    )


def validate_skill(skill_md: Path, root: Path) -> list[str]:
    """Validate Agent Skills frontmatter, size, references, and fences.

    *skill_md* is the absolute path to a SKILL.md file.  *root* is the
    repository root used for relative path reporting.
    """
    label = str(skill_md.relative_to(root))
    content = skill_md.read_text(encoding="utf-8")
    frontmatter = parse_frontmatter(content)
    if frontmatter is None:
        return [f"{label}: missing or invalid YAML frontmatter"]

    errors: list[str] = []
    name = frontmatter.get("name")
    description = frontmatter.get("description")
    if not isinstance(name, str) or not SKILL_NAME_RE.fullmatch(name):
        errors.append(f"{label}: invalid or missing skill name")
    elif name != skill_md.parent.name:
        errors.append(
            f"{label}: name '{name}' does not match directory "
            f"'{skill_md.parent.name}'"
        )
    if not isinstance(description, str) or not description.strip():
        errors.append(f"{label}: missing non-empty description")
    elif len(description) > 1024:
        errors.append(f"{label}: description exceeds 1024 characters")
    line_count = len(content.splitlines())
    if line_count > 500:
        errors.append(
            f"{label}: {line_count} lines exceeds the 500-line payload budget"
        )
    errors.extend(check_fences(content, label))
    errors.extend(check_relative_links(skill_md, content, root))
    return errors
