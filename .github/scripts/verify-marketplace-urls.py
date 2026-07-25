#!/usr/bin/env python3
"""Monitor evidence URLs, redirects, JSON syntax, and minimal response shapes."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import urllib.error
import urllib.request
from dataclasses import dataclass
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "docs" / "evidence-urls.json"


class RedirectTracker(urllib.request.HTTPRedirectHandler):
    """Count redirects followed by one opener invocation."""

    def __init__(self) -> None:
        super().__init__()
        self.count = 0

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        self.count += 1
        return super().redirect_request(req, fp, code, msg, headers, newurl)


@dataclass(frozen=True)
class CheckResult:
    status: int | str
    redirects: int
    content: str
    final_url: str


def load_manifest(path: Path = MANIFEST_PATH) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    """Load and validate the manifest envelope. Returns (document, entries)."""
    try:
        document = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise SystemExit(f"FAIL: could not load {path}: {exc}") from exc
    entries = document.get("urls") if isinstance(document, dict) else None
    if not isinstance(entries, list):
        raise SystemExit(f"FAIL: {path} must contain a top-level 'urls' list")
    return document, entries


def validate_entry(entry: dict[str, Any]) -> None:
    """Validate one manifest entry before network access."""
    for field in ("name", "url", "expected_statuses", "source_section"):
        if field not in entry:
            raise ValueError(f"missing required field '{field}'")
    if not isinstance(entry["name"], str) or not isinstance(entry["url"], str):
        raise ValueError("name and url must be strings")
    statuses = entry["expected_statuses"]
    if not isinstance(statuses, list) or not statuses or not all(isinstance(value, int) for value in statuses):
        raise ValueError("expected_statuses must be a non-empty integer list")
    max_redirects = entry.get("max_redirects")
    if max_redirects is not None and (not isinstance(max_redirects, int) or max_redirects < 0):
        raise ValueError("max_redirects must be a non-negative integer")
    canonical_url = entry.get("canonical_url")
    if canonical_url is not None and not isinstance(canonical_url, str):
        raise ValueError("canonical_url must be a string")
    schema = entry.get("json_schema")
    if schema is not None:
        if entry.get("content_type") != "json" or not isinstance(schema, dict):
            raise ValueError("json_schema requires content_type=json and an object schema")
        if schema.get("type") not in {"array", "object"}:
            raise ValueError("json_schema.type must be 'array' or 'object'")
        required = schema.get("required_keys", [])
        if not isinstance(required, list) or not all(isinstance(key, str) for key in required):
            raise ValueError("json_schema.required_keys must be a string list")


def validate_json_shape(value: Any, schema: dict[str, Any] | None) -> str:
    """Return a compact semantic validation result."""
    if schema is None:
        return "VALID_JSON"
    expected = schema["type"]
    if expected == "array" and not isinstance(value, list):
        return "SCHEMA:expected-array"
    if expected == "object" and not isinstance(value, dict):
        return "SCHEMA:expected-object"
    if isinstance(value, dict):
        missing = [key for key in schema.get("required_keys", []) if key not in value]
        if missing:
            return f"SCHEMA:missing-{','.join(missing)}"
    return "VALID_SCHEMA"


def check_url(entry: dict[str, Any], timeout: int = 15) -> CheckResult:
    """Fetch one URL and validate JSON when requested."""
    tracker = RedirectTracker()
    opener = urllib.request.build_opener(tracker)
    request = urllib.request.Request(
        entry["url"],
        method="GET",
        headers={"User-Agent": "skill-discovery-contract-monitor/2"},
    )
    try:
        with opener.open(request, timeout=timeout) as response:
            if entry.get("content_type") != "json":
                return CheckResult(response.status, tracker.count, "-", response.geturl())
            body = response.read()
            try:
                value = json.loads(body.decode("utf-8"))
            except (UnicodeDecodeError, json.JSONDecodeError):
                return CheckResult(response.status, tracker.count, "INVALID_JSON", response.geturl())
            return CheckResult(
                response.status,
                tracker.count,
                validate_json_shape(value, entry.get("json_schema")),
                response.geturl(),
            )
    except urllib.error.HTTPError as exc:
        return CheckResult(exc.code, tracker.count, f"HTTP_{exc.code}", exc.geturl())
    except (urllib.error.URLError, TimeoutError, ValueError) as exc:
        return CheckResult("ERROR", tracker.count, str(exc), entry["url"])


def contract_drift_reasons(entry: dict[str, Any], result: CheckResult) -> list[str]:
    """Return concrete reasons why a response differs from its manifest contract."""
    reasons: list[str] = []
    if result.status not in entry["expected_statuses"]:
        reasons.append(f"status={result.status}")
    if result.redirects > entry.get("max_redirects", result.redirects):
        reasons.append(f"redirects={result.redirects}")
    canonical_url = entry.get("canonical_url")
    if canonical_url is not None and result.final_url != canonical_url:
        reasons.append(f"final_url={result.final_url}")
    if entry.get("content_type") == "json" and result.content not in {"VALID_JSON", "VALID_SCHEMA"}:
        reasons.append(result.content)
    return reasons


def parse_frontmatter(content: str) -> dict[str, Any]:
    """Extract YAML frontmatter from markdown content."""
    if not content.startswith("---"):
        return {}
    end = content.find("---", 3)
    if end == -1:
        return {}
    frontmatter = content[3:end].strip()
    result: dict[str, Any] = {}
    for line in frontmatter.split("\n"):
        if ":" in line:
            key, value = line.split(":", 1)
            result[key.strip()] = value.strip().strip('"').strip("'")
    return result


def check_research_expiry(docs_dir: Path, warning_days: int = 14) -> list[dict[str, Any]]:
    """Check research files for upcoming expiry and return files needing attention."""
    expiring: list[dict[str, Any]] = []
    today = date.today()
    for md_file in docs_dir.glob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
        except OSError:
            continue
        frontmatter = parse_frontmatter(content)
        expires_str = frontmatter.get("expires")
        if not expires_str:
            continue
        try:
            expires = date.fromisoformat(expires_str)
        except ValueError:
            continue
        days_until = (expires - today).days
        if days_until <= warning_days:
            expiring.append({
                "file": md_file.name,
                "expires": expires_str,
                "days_until": days_until,
                "status": frontmatter.get("status", "unknown"),
                "purpose": frontmatter.get("purpose", "").strip(),
            })
    return expiring


def has_existing_expiry_issue(file_info: dict[str, Any]) -> bool:
    """Check if an open issue already exists for this expiring file."""
    try:
        result = subprocess.run(
            [
                "gh", "issue", "list",
                "--state", "open",
                "--search", f"Research expiry: {file_info['file']}",
                "--json", "number",
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        issues = json.loads(result.stdout)
        return len(issues) > 0
    except (subprocess.CalledProcessError, FileNotFoundError, json.JSONDecodeError):
        return False


def create_expiry_issue(file_info: dict[str, Any]) -> bool:
    """Create a GitHub issue for an expiring research file. Returns True on success."""
    if has_existing_expiry_issue(file_info):
        print(f"SKIP: open issue already exists for {file_info['file']}")
        return True
    title = f"Research expiry: {file_info['file']} expires in {file_info['days_until']} days"
    body = (
        f"## Research file expiring soon\n\n"
        f"**File:** `docs/{file_info['file']}`\n"
        f"**Expires:** {file_info['expires']} ({file_info['days_until']} days)\n"
        f"**Status:** {file_info['status']}\n\n"
        f"### Purpose\n\n{file_info['purpose']}\n\n"
        f"### Action required\n\n"
        f"This research document is approaching its expiry date. Please review and either:\n"
        f"1. **Update** the research with fresh data and extend the expiry\n"
        f"2. **Archive** if the research is no longer relevant\n"
        f"3. **Close** this issue if the document has been updated\n"
    )
    try:
        result = subprocess.run(
            ["gh", "issue", "create", "--title", title, "--body", body, "--label", "research-expiry"],
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"ISSUE: created for {file_info['file']}: {result.stdout.strip()}")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError) as exc:
        print(f"WARNING: could not create issue for {file_info['file']}: {exc}")
        return False


def apply_fixes(document: dict[str, Any], entries: list[dict[str, Any]], fixes: list[tuple[int, str]]) -> None:
    """Apply auto-fixes to the manifest document in place."""
    today = date.today().isoformat()
    for index, reason in fixes:
        entry = entries[index]
        if "final_url=" in reason:
            new_url = reason.split("final_url=", 1)[1]
            entry["url"] = new_url
            if "canonical_url" in entry:
                entry["canonical_url"] = new_url
        entry["last_verified"] = today


def save_manifest(document: dict[str, Any], path: Path = MANIFEST_PATH) -> None:
    """Write the updated manifest back to disk."""
    path.write_text(json.dumps(document, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


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
            print(f"\nFIXED: updated {len(fixes)} entries in {MANIFEST_PATH}")
        else:
            print(f"\nUPDATED: last_verified timestamps in {MANIFEST_PATH}")
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
