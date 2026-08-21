"""Shared validation utilities for repository scripts."""

from __future__ import annotations

import re
import sys
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


def read_text_checked(path: Path) -> str:
    """Read a file's text content with safety checks.

    Rejects symlinks (security), handles missing files, encoding errors,
    and OS errors with clear messages.
    """
    if path.is_symlink() and not path.is_file():
        raise OSError(f"{path}: is a broken symlink")
    if path.is_symlink():
        raise OSError(f"{path}: symlink reading not allowed (security)")
    try:
        return path.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise FileNotFoundError(f"{path}: file not found") from None
    except UnicodeDecodeError:
        raise UnicodeDecodeError(
            "utf-8", b"", 0, 1, f"{path}: file is not valid UTF-8",
        ) from None
    except OSError as exc:
        raise OSError(f"{path}: {exc}") from None


def fail(message: str, hint: str | None = None) -> None:
    """Print a standardized error message to stderr with optional hint."""
    print(f"FAIL: {message}", file=sys.stderr)
    if hint:
        print(f"  HINT: {hint}", file=sys.stderr)


def contains_markdown_phrase(text: str, phrase: str) -> bool:
    """Check if *phrase* exists in *text* with whitespace normalization.

    Collapses runs of whitespace (spaces, tabs, newlines) to single spaces
    before matching, so formatting changes don't cause false negatives.
    """
    import re as _re
    normalized = _re.sub(r"\s+", " ", text)
    phrase_normalized = _re.sub(r"\s+", " ", phrase)
    return phrase_normalized in normalized


# ── unsafe probe detection ────────────────────────────────────────────────

UNSAFE_PROBE_PATTERNS: list[tuple[str, str]] = [
    (r"git\s+log\s+.*%[BH]", "git log with format placeholders can exfiltrate history"),
    (r"cat\s+\.env", "reading .env files exposes secrets"),
    (r"git\s+reset\s+--hard", "git reset --hard can destroy working changes"),
    (r"git\s+push\s+--force", "force push can overwrite remote history"),
    (r"curl\s+.*\|\s*(?:bash|sh)", "piping curl to shell is a supply-chain risk"),
    (r"eval\s*\(", "eval() can execute arbitrary code"),
]


def check_unsafe_probes(content: str, label: str) -> list[str]:
    """Flag dangerous git/code patterns in skill content."""
    errors: list[str] = []
    for line_num, line in enumerate(content.splitlines(), start=1):
        for pattern, reason in UNSAFE_PROBE_PATTERNS:
            if re.search(pattern, line):
                errors.append(f"{label}:L{line_num}: unsafe pattern — {reason}")
    return errors


# ── reference file size budgets ───────────────────────────────────────────

SKILL_REF_RE = re.compile(r"\]\((references/[^)\s]+\.md)\)")
REF_MIN_BYTES = 50
REF_MAX_BYTES = 50_000


def check_reference_sizes(skill_md: Path, root: Path) -> list[str]:
    """Verify referenced files are within size budgets."""
    errors: list[str] = []
    label = str(skill_md.relative_to(root))
    content = skill_md.read_text(encoding="utf-8")
    seen: set[str] = set()
    for match in SKILL_REF_RE.finditer(content):
        ref_path = (skill_md.parent / match.group(1)).resolve()
        key = str(ref_path)
        if key in seen:
            continue
        seen.add(key)
        if not ref_path.exists():
            continue  # already caught by check_relative_links
        size = ref_path.stat().st_size
        if size < REF_MIN_BYTES:
            errors.append(
                f"{label}: {match.group(1)} is {size} bytes (minimum {REF_MIN_BYTES})"
            )
        elif size > REF_MAX_BYTES:
            errors.append(
                f"{label}: {match.group(1)} is {size} bytes (maximum {REF_MAX_BYTES})"
            )
    return errors


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
    errors.extend(check_unsafe_probes(content, label))
    errors.extend(check_reference_sizes(skill_md, root))
    return errors
