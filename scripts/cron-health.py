#!/usr/bin/env python3
"""Weekly repo health checks (detect-only).

Checks:
  1. internal-link-rot   – relative markdown links that don't resolve
  2. reference-integrity  – references/*.md paths in SKILL.md that don't exist
  3. skill-budget         – SKILL.md line count against 350-line warning threshold

Exit code 0 = all checks passed, 1 = at least one issue found.
"""
from __future__ import annotations

import re
import sys

from _common import ROOT, find_markdown_files

RELATIVE_LINK_RE = re.compile(r"\[.*?\]\(((?!https?://|mailto:|#)[^)]+)\)")
SKILL_REF_RE = re.compile(r"\]\((references/[^)\s]+\.md)\)")


def check_link_rot() -> list[str]:
    errors: list[str] = []
    for md in find_markdown_files(ROOT):
        rel = md.relative_to(ROOT)
        text = md.read_text(encoding="utf-8", errors="replace")
        for match in RELATIVE_LINK_RE.finditer(text):
            target = match.group(1)
            target_path = target.split("#", 1)[0]
            if not target_path:
                continue
            resolved = (md.parent / target_path).resolve()
            if not resolved.exists():
                errors.append(f"{rel}: broken link → {target_path}")
    return errors


# ── check 2: reference file integrity ───────────────────────────────────

def check_reference_integrity() -> list[str]:
    errors: list[str] = []
    for skill_md in sorted(ROOT.glob("skills/*/SKILL.md")):
        rel = skill_md.relative_to(ROOT)
        text = skill_md.read_text(encoding="utf-8", errors="replace")
        seen: set[str] = set()
        for match in SKILL_REF_RE.finditer(text):
            ref_path = (skill_md.parent / match.group(1)).resolve()
            key = str(ref_path)
            if key in seen:
                continue
            seen.add(key)
            if not ref_path.exists():
                errors.append(f"{rel}: missing reference → {match.group(1)}")
    return errors


# ── check 3: SKILL.md budget ───────────────────────────────────────────

BUDGET_WARN_LINES = 350


def check_skill_budget() -> list[str]:
    warnings: list[str] = []
    for skill_md in sorted(ROOT.glob("skills/*/SKILL.md")):
        rel = skill_md.relative_to(ROOT)
        lines = len(skill_md.read_text(encoding="utf-8", errors="replace").splitlines())
        if lines > BUDGET_WARN_LINES:
            warnings.append(f"{rel}: {lines} lines (budget {BUDGET_WARN_LINES})")
    return warnings


# ── main ─────────────────────────────────────────────────────────────────

CHECKS = {
    "internal-link-rot": check_link_rot,
    "reference-integrity": check_reference_integrity,
    "skill-budget": check_skill_budget,
}


def main(check: str | None = None) -> int:
    checks_to_run = {check: CHECKS[check]} if check else CHECKS
    all_ok = True
    for name, fn in checks_to_run.items():
        issues = fn()
        if issues:
            all_ok = False
            for issue in issues:
                print(f"⚠️  {name}: {issue}", file=sys.stderr)
        else:
            print(f"✅ {name}: OK")
    return 0 if all_ok else 1


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        choices=list(CHECKS),
        default=None,
        help="Run a single check (default: all)",
    )
    args = parser.parse_args()
    sys.exit(main(check=args.check))
