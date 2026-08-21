#!/usr/bin/env python3
"""Tests for shared utilities in _common.py."""

from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path

from _common import (
    diff_advisories,
    load_advisory_baseline,
    save_advisory_baseline,
)


class AdvisoryBaselineTests(unittest.TestCase):
    """Tests for advisory baseline load/save/diff functions."""

    def test_load_missing_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = load_advisory_baseline(Path(tmp) / "nonexistent.json")
            self.assertEqual(result, [])

    def test_load_empty_warnings(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "baseline.json"
            path.write_text(json.dumps({"reviewed": "2026-01-01", "warnings": []}))
            result = load_advisory_baseline(path)
            self.assertEqual(result, [])

    def test_load_with_warnings(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "baseline.json"
            path.write_text(
                json.dumps({"reviewed": "2026-01-01", "warnings": ["w1", "w2"]})
            )
            result = load_advisory_baseline(path)
            self.assertEqual(result, ["w1", "w2"])

    def test_load_invalid_json(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "baseline.json"
            path.write_text("not json {{{")
            result = load_advisory_baseline(path)
            self.assertEqual(result, [])

    def test_load_non_dict_shape(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "baseline.json"
            path.write_text(json.dumps("just a string"))
            result = load_advisory_baseline(path)
            self.assertEqual(result, [])

    def test_save_creates_file(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "baseline.json"
            save_advisory_baseline(["w2", "w1"], path=path)
            data = json.loads(path.read_text())
            self.assertEqual(data["warnings"], ["w1", "w2"])  # sorted
            self.assertIn("reviewed", data)

    def test_save_overwrites(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "baseline.json"
            save_advisory_baseline(["old"], path=path)
            save_advisory_baseline(["new"], path=path)
            data = json.loads(path.read_text())
            self.assertEqual(data["warnings"], ["new"])

    def test_diff_new_warnings(self):
        new, resolved = diff_advisories(["a", "b", "c"], ["a"])
        self.assertEqual(new, ["b", "c"])
        self.assertEqual(resolved, [])

    def test_diff_resolved_warnings(self):
        new, resolved = diff_advisories(["a"], ["a", "b", "c"])
        self.assertEqual(new, [])
        self.assertEqual(resolved, ["b", "c"])

    def test_diff_mixed(self):
        new, resolved = diff_advisories(["a", "d"], ["a", "b"])
        self.assertEqual(new, ["d"])
        self.assertEqual(resolved, ["b"])

    def test_diff_empty_both(self):
        new, resolved = diff_advisories([], [])
        self.assertEqual(new, [])
        self.assertEqual(resolved, [])

    def test_diff_duplicates_dont_affect(self):
        new, resolved = diff_advisories(["a", "a"], ["a"])
        self.assertEqual(new, [])
        self.assertEqual(resolved, [])


if __name__ == "__main__":
    unittest.main()
