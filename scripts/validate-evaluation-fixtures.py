#!/usr/bin/env python3
"""Validate evaluation fixtures are well-formed."""

from __future__ import annotations

import json
import sys

from _common import ROOT

FIXTURE = ROOT / "tests" / "discovery-evaluations.json"
RESULTS = {"direct_fit", "conditional_fit", "partial_fit", "inspection_blocked", "reject"}
FRESHNESS = {"known", "stale", "unknown"}
LOADERS = {"verified", "structural_only", "unavailable"}
PRIVACY = {"synthetic-only", "not-applicable"}
BEHAVIOR = {"not-run", "partial", "pass"}
REQUIRED = {
    "id",
    "task",
    "result",
    "catalog_freshness",
    "candidate_revision",
    "loader_status",
    "privacy",
    "behavior_validation",
}


def validate(document: object) -> list[str]:
    """Return schema and value errors for one fixture document."""
    errors: list[str] = []
    if not isinstance(document, dict):
        return ["document must be an object"]
    if document.get("schema_version") != 1:
        errors.append("schema_version must be 1")
    cases = document.get("cases")
    if not isinstance(cases, list) or not cases:
        return errors + ["cases must be a non-empty list"]
    ids: set[str] = set()
    for index, case in enumerate(cases):
        label = f"cases[{index}]"
        if not isinstance(case, dict):
            errors.append(f"{label} must be an object")
            continue
        missing = REQUIRED - case.keys()
        errors.extend(f"{label}: missing {field}" for field in sorted(missing))
        case_id = case.get("id")
        if not isinstance(case_id, str) or not case_id:
            errors.append(f"{label}: id must be non-empty")
        elif case_id in ids:
            errors.append(f"{label}: duplicate id {case_id!r}")
        else:
            ids.add(case_id)
        checks = (
            ("result", RESULTS),
            ("catalog_freshness", FRESHNESS),
            ("loader_status", LOADERS),
            ("privacy", PRIVACY),
            ("behavior_validation", BEHAVIOR),
        )
        for field, allowed in checks:
            value = case.get(field)
            if value not in allowed:
                errors.append(f"{label}: {field} must be one of {sorted(allowed)}")
        if case.get("result") == "inspection_blocked":
            if case.get("candidate_revision") != "unavailable":
                errors.append(f"{label}: blocked candidates require unavailable revision")
            if case.get("loader_status") != "unavailable":
                errors.append(f"{label}: blocked candidates require unavailable loader")
    return errors


def main() -> int:
    try:
        document = json.loads(FIXTURE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        print(f"FAIL: cannot read {FIXTURE}: {exc}", file=sys.stderr)
        return 1
    errors = validate(document)
    if errors:
        print("FAIL: discovery evaluation fixtures are invalid", file=sys.stderr)
        for error in errors:
            print(f"  {error}", file=sys.stderr)
        return 1
    print(f"PASS: {len(document['cases'])} offline discovery evaluation fixtures are valid")
    return 0


if __name__ == "__main__":
    sys.exit(main())
