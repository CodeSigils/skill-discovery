#!/usr/bin/env python3
"""Weekly repo health checks (detect-only).

Checks:
  1. internal-link-rot   – relative markdown links that don't resolve
  2. reference-integrity  – references/*.md paths in SKILL.md that don't exist
  3. skill-budget         – SKILL.md line count against 350-line warning threshold

Exit code 0 = all checks passed, 1 = at least one issue found.

Usage:
  cron-health.py                        Run all checks, report vs baseline
  cron-health.py --check internal-link-rot   Run single check
  cron-health.py --update-baseline      Snapshot current warnings as new baseline
"""
from __future__ import annotations

import re
import sys

from _common import (
    ROOT,
    SKILL_REF_RE,
    diff_advisories,
    find_markdown_files,
    load_advisory_baseline,
    save_advisory_baseline,
)

RELATIVE_LINK_RE = re.compile(r"\[.*?\]\(((?!https?://|mailto:|#)[^)]+)\)")


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


def main(check: str | None = None, update_baseline: bool = False) -> int:
    checks_to_run = {check: CHECKS[check]} if check else CHECKS
    all_warnings: list[str] = []
    for name, fn in checks_to_run.items():
        issues = fn()
        for issue in issues:
            all_warnings.append(f"{name}: {issue}")

    if update_baseline:
        save_advisory_baseline(all_warnings)
        print(f"Baseline updated: {len(all_warnings)} warnings saved")
        return 0

    baseline = load_advisory_baseline()
    new, resolved = diff_advisories(all_warnings, baseline)

    if baseline:
        known = len(all_warnings) - len(new)
        if known > 0:
            print(f"ℹ️  {known} known warning(s) suppressed by baseline")
        for w in resolved:
            print(f"✅ RESOLVED (baseline): {w}")
    else:
        new = all_warnings

    all_ok = True
    for w in new:
        all_ok = False
        print(f"⚠️  NEW: {w}", file=sys.stderr)
    for w in all_warnings:
        if w not in new:
            print(f"✅ {w}")
    if not all_warnings:
        print("✅ All checks passed")
        return 0

    n_new = len(new)
    n_known = len(all_warnings) - n_new
    n_resolved = len(resolved)
    parts = []
    if n_new:
        parts.append(f"{n_new} new")
    if n_known:
        parts.append(f"{n_known} known")
    if n_resolved:
        parts.append(f"{n_resolved} resolved")
    print(f"Summary: {', '.join(parts)} warning(s)")
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
    parser.add_argument(
        "--update-baseline",
        action="store_true",
        help="Save current warnings as the new advisory baseline",
    )
    args = parser.parse_args()
    sys.exit(main(check=args.check, update_baseline=args.update_baseline))
