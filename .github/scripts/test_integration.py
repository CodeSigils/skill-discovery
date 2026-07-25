#!/usr/bin/env python3
"""Integration tests for validate-docs.py — runs the real validator on the repo."""

from __future__ import annotations

import re
import subprocess
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
VALIDATE_DOCS = ROOT / ".github" / "scripts" / "validate-docs.py"


class TestValidateDocsIntegration(unittest.TestCase):
    """Run validate-docs.py on the real repo and verify it passes."""

    def test_validate_docs_passes(self):
        """validate-docs.py should pass on the current repo."""
        result = subprocess.run(
            [sys.executable, str(VALIDATE_DOCS)],
            capture_output=True,
            text=True,
            cwd=ROOT,
        )
        self.assertEqual(result.returncode, 0, f"validate-docs.py failed:\n{result.stderr}")

    def test_all_skill_references_exist(self):
        """All files referenced in SKILL.md references section must exist."""
        skill_md = ROOT / "skills" / "skill-discovery" / "SKILL.md"
        if not skill_md.exists():
            self.skipTest("SKILL.md not found")
        text = skill_md.read_text(encoding="utf-8")
        refs_dir = skill_md.parent / "references"
        # Find all references/*.md links — match just the filename part
        refs_found = set(re.findall(r"references/([a-z0-9_-]+\.md)", text))
        refs_on_disk = {f.name for f in refs_dir.glob("*.md")} if refs_dir.exists() else set()
        missing = refs_found - refs_on_disk
        self.assertEqual(missing, set(), f"SKILL.md references files not on disk: {missing}")


if __name__ == "__main__":
    unittest.main()
