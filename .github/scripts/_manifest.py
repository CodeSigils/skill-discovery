"""Manifest I/O: load, save, and apply fixes to evidence-urls.json."""

from __future__ import annotations

import json
from datetime import date
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
MANIFEST_PATH = ROOT / "docs" / "evidence-urls.json"


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
