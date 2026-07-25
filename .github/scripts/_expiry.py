"""Research expiry checking and GitHub issue creation."""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import date, datetime
from pathlib import Path
from pathlib import Path as _Path
from typing import Any

sys.path.insert(0, str(_Path(__file__).resolve().parents[2] / "scripts"))
from _common import parse_frontmatter


def check_research_expiry(docs_dir: Path, warning_days: int = 14) -> list[dict[str, Any]]:
    """Check research files for upcoming expiry and return files needing attention."""
    expiring: list[dict[str, Any]] = []
    today = date.today()
    for md_file in docs_dir.glob("*.md"):
        try:
            content = md_file.read_text(encoding="utf-8")
        except OSError:
            continue
        fm = parse_frontmatter(content)
        frontmatter = fm if fm is not None else {}
        expires_raw = frontmatter.get("expires")
        if not expires_raw:
            continue
        if isinstance(expires_raw, datetime):
            expires = expires_raw.date()
            expires_str = expires.isoformat()
        elif isinstance(expires_raw, date):
            expires = expires_raw
            expires_str = expires.isoformat()
        elif isinstance(expires_raw, str):
            try:
                expires = date.fromisoformat(expires_raw)
            except ValueError:
                continue
            expires_str = expires_raw
        else:
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
