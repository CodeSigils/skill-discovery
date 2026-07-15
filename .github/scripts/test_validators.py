#!/usr/bin/env python3
"""Deterministic unit tests for repository validators."""

from __future__ import annotations

import importlib.util
import sys
import tempfile
import unittest
from pathlib import Path


def load_script(name: str):
    path = Path(__file__).with_name(f"{name}.py")
    spec = importlib.util.spec_from_file_location(name.replace("-", "_"), path)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    sys.modules[spec.name] = module
    spec.loader.exec_module(module)
    return module


validate_docs = load_script("validate-docs")
verify_urls = load_script("verify-marketplace-urls")


class DocumentationTests(unittest.TestCase):
    def test_parse_folded_description(self):
        content = "---\nname: example\ndescription: >\n  folded value\n---\n# Example\n"
        frontmatter = validate_docs.parse_frontmatter(content)
        self.assertEqual(frontmatter["description"], "folded value")

    def test_skill_name_must_match_directory(self):
        original_root = validate_docs.ROOT
        with tempfile.TemporaryDirectory() as directory:
            validate_docs.ROOT = Path(directory)
            try:
                path = Path(directory) / "wrong" / "SKILL.md"
                path.parent.mkdir()
                path.write_text("---\nname: right\ndescription: useful\n---\n# Test\n", encoding="utf-8")
                errors = validate_docs.validate_skill(path)
            finally:
                validate_docs.ROOT = original_root
        self.assertTrue(any("does not match directory" in error for error in errors))

    def test_missing_relative_link_is_rejected(self):
        path = validate_docs.ROOT / "README.md"
        errors = validate_docs.check_relative_links(path, "[missing](does-not-exist.md)")
        self.assertTrue(any("missing link target" in error for error in errors))

    def test_unlabelled_fence_is_rejected(self):
        errors = validate_docs.check_fences("```\nexample\n```", "example.md")
        self.assertTrue(any("has no language" in error for error in errors))


class ContractTests(unittest.TestCase):
    def test_array_schema(self):
        self.assertEqual(
            verify_urls.validate_json_shape([], {"type": "array"}),
            "VALID_SCHEMA",
        )

    def test_object_required_keys(self):
        result = verify_urls.validate_json_shape(
            {"count": 1},
            {"type": "object", "required_keys": ["count", "skills"]},
        )
        self.assertEqual(result, "SCHEMA:missing-skills")

    def test_manifest_rejects_schema_without_json(self):
        entry = {
            "name": "test",
            "url": "https://example.com",
            "expected_statuses": [200],
            "source_section": "test",
            "json_schema": {"type": "object"},
        }
        with self.assertRaisesRegex(ValueError, "content_type=json"):
            verify_urls.validate_entry(entry)

    def test_expected_401_is_valid_without_json(self):
        entry = {
            "expected_statuses": [401],
        }
        result = verify_urls.CheckResult(401, 0, "HTTP_401")
        self.assertTrue(verify_urls.result_is_valid(entry, result))


if __name__ == "__main__":
    unittest.main()
