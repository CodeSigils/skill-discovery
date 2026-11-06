#!/usr/bin/env python3
"""Monitor evidence URLs, redirects, JSON syntax, and minimal response shapes."""

from __future__ import annotations

import argparse
import os
import sys
from concurrent.futures import ThreadPoolExecutor
from datetime import date
from typing import Any

from _expiry import check_research_expiry, create_expiry_issue
from _manifest import ROOT, apply_fixes, load_manifest, save_manifest
from _url_contract import (
    CheckResult,
    check_url,
    contract_drift_reasons,
    validate_entry,
)


def can_auto_fix(entry: dict[str, Any], result: CheckResult, reasons: list[str]) -> bool:
    """Allow only a canonical URL correction with an otherwise valid response."""
    max_redirects = entry.get("max_redirects")
    return (
        len(reasons) == 1
        and reasons[0].startswith("final_url=")
        and result.status in entry["expected_statuses"]
        and (max_redirects is None or result.redirects <= max_redirects)
        and result.content in {"-", "VALID_JSON", "VALID_SCHEMA"}
    )


def check_indexed(item: tuple[int, dict[str, Any]]) -> tuple[int, dict[str, Any], CheckResult]:
    """Check one manifest entry for threaded execution."""
    index, entry = item
    return index, entry, check_url(entry)


def write_workflow_output(name: str, value: int) -> None:
    """Expose monitor evidence to a GitHub Actions step when available."""
    output_path = os.environ.get("GITHUB_OUTPUT")
    if output_path:
        with open(output_path, "a", encoding="utf-8") as output:
            output.write(f"{name}={value}\n")


def build_summary(
    *,
    checked_count: int,
    drift_names: list[str],
    timestamp_refresh_count: int,
    canonical_fix_count: int,
    validation_errors: bool,
) -> list[str]:
    """Build a compact Markdown summary for the workflow run."""
    lines = [
        "## External contract monitor",
        "",
        f"- Checked: {checked_count}",
        f"- Drift detected: {len(drift_names)}",
        f"- Timestamp refreshes: {timestamp_refresh_count}",
        f"- Canonical fixes: {canonical_fix_count}",
    ]
    if validation_errors:
        lines.append("- Manifest validation errors: yes")
    if drift_names:
        lines.extend(["", "### Drift", *[f"- {name}" for name in drift_names]])
    return lines


def write_step_summary(lines: list[str]) -> None:
    """Append the monitor summary to the GitHub Actions step summary."""
    summary_path = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as summary:
            summary.write("\n".join(lines) + "\n")


def check_and_create_expiry_issues() -> None:
    """Report research files nearing expiry and open one issue per file."""
    docs_dir = ROOT / "docs"
    expiring = check_research_expiry(docs_dir)
    if expiring:
        print(f"\nEXPIRING: {len(expiring)} research file(s) nearing expiry:")
        for info in expiring:
            print(f"  - {info['file']}: expires {info['expires']} ({info['days_until']} days)")
            create_expiry_issue(info)
    else:
        print("\nEXPIRY: no research files nearing expiry")


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description="Monitor evidence URLs, redirects, JSON syntax, and minimal response shapes."
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Auto-fix drift by updating evidence-urls.json in place",
    )
    parser.add_argument(
        "--check-expiry",
        action="store_true",
        help="Check research files for upcoming expiry and create issues",
    )
    parser.add_argument(
        "--expiry-only",
        action="store_true",
        help="Skip URL checks and only check research expiry",
    )
    return parser.parse_args()


def main() -> int:
    """Run scheduled external contract monitoring."""
    args = parse_args()
    if args.expiry_only:
        check_and_create_expiry_issues()
        return 0
    document, entries = load_manifest()
    validation_errors = False
    drift_count = 0
    fixes: list[tuple[int, str]] = []
    drift_names: list[str] = []
    timestamp_refresh_count = 0
    print(f"{'Name':<44} {'Status':<8} {'Redirects':<10} {'Content':<28} Result")
    print("-" * 105)
    checked: list[tuple[int, dict[str, Any], CheckResult]] = []
    valid_entries: list[tuple[int, dict[str, Any]]] = []
    for index, entry in enumerate(entries):
        try:
            validate_entry(entry)
        except ValueError as exc:
            print(f"{entry.get('name', '<unnamed>'):<44} {'-':<8} {'-':<10} {'-':<28} MANIFEST: {exc}")
            validation_errors = True
            continue
        valid_entries.append((index, entry))
    if valid_entries:
        workers = min(8, len(valid_entries))
        with ThreadPoolExecutor(max_workers=workers) as executor:
            ordered_entries = sorted(valid_entries, key=lambda item: str(item[1].get("name", "")).casefold())
            checked = list(executor.map(check_indexed, ordered_entries))
    for original_idx, entry, result in checked:
        reasons = contract_drift_reasons(entry, result)
        valid = not reasons
        if not valid:
            drift_count += 1
            drift_names.append(str(entry.get("name", "<unnamed>")))
            if args.fix and can_auto_fix(entry, result, reasons):
                fixes.append((original_idx, reasons[0]))
        # Update last_verified on success
        if valid:
            today = date.today().isoformat()
            if entry.get("last_verified") != today:
                timestamp_refresh_count += 1
            entry["last_verified"] = today
        print(
            f"{entry['name']:<44} {str(result.status):<8} {result.redirects:<10} "
            f"{result.content[:28]:<28} {'OK' if valid else 'DRIFT:' + ';'.join(reasons)}"
        )
    if args.fix:
        apply_fixes(document, entries, fixes)
        save_manifest(document)
        if fixes:
            print(f"\nFIXED: updated {len(fixes)} entries in evidence-urls.json")
        else:
            print("\nUPDATED: last_verified timestamps in evidence-urls.json")
        drift_count -= len(fixes)
    write_workflow_output("checked_count", len(checked))
    write_workflow_output("timestamp_refresh_count", timestamp_refresh_count)
    write_workflow_output("canonical_url_fix_count", len(fixes))
    write_step_summary(
        build_summary(
            checked_count=len(checked),
            drift_names=drift_names,
            timestamp_refresh_count=timestamp_refresh_count,
            canonical_fix_count=len(fixes),
            validation_errors=validation_errors,
        )
    )
    if args.check_expiry:
        check_and_create_expiry_issues()
    if validation_errors or drift_count:
        print("\nFAIL: one or more external contracts drifted")
        return 1
    print("\nPASS: external status and minimal response contracts match")
    return 0


if __name__ == "__main__":
    sys.exit(main())
