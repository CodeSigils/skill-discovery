#!/usr/bin/env python3
"""Monitor evidence URLs, redirects, JSON syntax, and minimal response shapes."""

from __future__ import annotations

import argparse
import sys
from datetime import date

from _expiry import check_research_expiry, create_expiry_issue
from _manifest import ROOT, apply_fixes, load_manifest, save_manifest
from _url_contract import (
    check_url,
    contract_drift_reasons,
    validate_entry,
)


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
    return parser.parse_args()


def main() -> int:
    """Run scheduled external contract monitoring."""
    args = parse_args()
    document, entries = load_manifest()
    validation_errors = False
    drift_count = 0
    fixes: list[tuple[int, str]] = []
    print(f"{'Name':<44} {'Status':<8} {'Redirects':<10} {'Content':<28} Result")
    print("-" * 105)
    name_to_idx = {e.get("name", ""): i for i, e in enumerate(entries)}
    for entry in sorted(entries, key=lambda value: str(value.get("name", "")).casefold()):
        original_idx = name_to_idx.get(entry.get("name", ""), -1)
        try:
            validate_entry(entry)
        except ValueError as exc:
            print(f"{entry.get('name', '<unnamed>'):<44} {'-':<8} {'-':<10} {'-':<28} MANIFEST: {exc}")
            validation_errors = True
            continue
        result = check_url(entry)
        reasons = contract_drift_reasons(entry, result)
        valid = not reasons
        if not valid:
            drift_count += 1
            fixes.append((original_idx, ";".join(reasons)))
        # Update last_verified on success
        if valid:
            entry["last_verified"] = date.today().isoformat()
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
        drift_count = 0  # Drift resolved by auto-fix
    if args.check_expiry:
        docs_dir = ROOT / "docs"
        expiring = check_research_expiry(docs_dir)
        if expiring:
            print(f"\nEXPIRING: {len(expiring)} research file(s) nearing expiry:")
            for info in expiring:
                print(f"  - {info['file']}: expires {info['expires']} ({info['days_until']} days)")
                create_expiry_issue(info)
        else:
            print("\nEXPIRY: no research files nearing expiry")
    if validation_errors or drift_count:
        print("\nFAIL: one or more external contracts drifted")
        return 1
    print("\nPASS: external status and minimal response contracts match")
    return 0


if __name__ == "__main__":
    sys.exit(main())
