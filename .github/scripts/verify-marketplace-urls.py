#!/usr/bin/env python3
"""Verify evidence URLs against the documented expected state.

The URL list lives in docs/evidence-urls.json so the research evidence base has
one machine-readable source of truth. If the doc adds or removes URLs, update
that manifest instead of editing this script's code.

Usage:
  python3 .github/scripts/verify-marketplace-urls.py
  # Windows: py -3 .github/scripts/verify-marketplace-urls.py
  # Virtualenvs may also support: python .github/scripts/verify-marketplace-urls.py

Outputs a table of URL → final status with drift annotations.
Exit code 0 = all URLs match documented expected state.
Exit code 1 = one or more URLs differs from the manifest.
"""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "docs" / "evidence-urls.json"


def load_manifest(path: Path = MANIFEST_PATH) -> list[dict[str, Any]]:
    """Load URL entries from the evidence manifest."""
    try:
        manifest = json.loads(path.read_text(encoding="utf-8"))
    except OSError as exc:
        raise SystemExit(f"FAIL: could not read {path}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise SystemExit(f"FAIL: invalid JSON in {path}: {exc}") from exc

    urls = manifest.get("urls")
    if not isinstance(urls, list):
        raise SystemExit(f"FAIL: {path} must contain a top-level 'urls' list")
    return urls


def validate_entry(entry: dict[str, Any]) -> None:
    """Validate one manifest entry before using it."""
    required = ("name", "url", "expected_statuses")
    missing = [key for key in required if key not in entry]
    if missing:
        raise ValueError(f"missing required field(s): {', '.join(missing)}")
    if not isinstance(entry["expected_statuses"], list) or not entry["expected_statuses"]:
        raise ValueError("expected_statuses must be a non-empty list")
    for status in entry["expected_statuses"]:
        if not isinstance(status, int):
            raise ValueError("expected_statuses must contain integers")


def check_url(url: str) -> tuple[int | str, int | str]:
    """Return (final_status_code, redirect_count) for one URL."""
    try:
        result = subprocess.run(
            [
                "curl",
                "-s",
                "-o",
                "/dev/null",
                "-w",
                "%{http_code} %{num_redirects}",
                "--max-time",
                "10",
                "-L",
                url,
            ],
            capture_output=True,
            text=True,
            timeout=15,
            check=False,
        )
    except subprocess.TimeoutExpired:
        return "TIMEOUT", "-"
    except OSError as exc:
        return "ERROR", str(exc)

    parts = result.stdout.strip().split()
    if result.returncode != 0 or len(parts) != 2:
        return "ERROR", result.stderr.strip() or f"curl exited {result.returncode}"

    status_text, redirect_text = parts
    try:
        status: int | str = int(status_text)
    except ValueError:
        status = status_text
    try:
        redirects: int | str = int(redirect_text)
    except ValueError:
        redirects = redirect_text
    return status, redirects


def classify_status(status: int | str, expected_statuses: list[int]) -> str:
    """Return OK when status matches the manifest, else DRIFT."""
    if isinstance(status, int) and status in expected_statuses:
        return "OK"
    return "DRIFT"


def main() -> int:
    entries = load_manifest()

    print("=== Evidence URL Re-verification ===")
    print(f"{'Name':<30s} {'Status':<8s} {'Expected':<12s} {'Redirects':<9s} {'Note':<10s}")
    print("-" * 78)

    drift_found = False
    for entry in sorted(entries, key=lambda item: item["name"].lower()):
        try:
            validate_entry(entry)
        except ValueError as exc:
            print(f"  {entry.get('name', '<unnamed>'):<30s} {'-':<8s} {'-':<12s} {'-':<9s} MANIFEST: {exc}")
            drift_found = True
            continue

        status, redirects = check_url(entry["url"])
        expected = entry["expected_statuses"]
        note = classify_status(status, expected)
        if note == "DRIFT":
            drift_found = True

        expected_text = "/".join(str(code) for code in expected)
        marker = "  ← DRIFT" if note == "DRIFT" else ""
        print(
            f"  {entry['name']:<30s} {str(status):<8s} {expected_text:<12s} "
            f"{str(redirects):<9s} {note:<10s}{marker}"
        )

    if drift_found:
        print("\nRESULT: Drift detected — one or more URLs differ from docs/evidence-urls.json.")
        print("Update the manifest and research doc together after investigating the changed URL state.")
        return 1

    print("\nRESULT: All URLs match documented expected state")
    return 0


if __name__ == "__main__":
    sys.exit(main())
