# Portable examples

## Search a JSON index

This standard-library example tolerates common top-level list shapes:

```python
import json
from pathlib import Path

document = json.loads(Path(catalog_path).read_text(encoding="utf-8"))
skills = document if isinstance(document, list) else document.get("skills", document.get("data", []))
terms = {term.casefold() for term in search_terms}

matches = []
for skill in skills:
    haystack = " ".join(
        str(skill.get(field, "")) for field in ("name", "description", "tags")
    ).casefold()
    if any(term in haystack for term in terms):
        matches.append(skill)
```

## Locate skill files

Use filesystem tools only to locate candidates; parse frontmatter separately so
folded YAML values are handled correctly:

```bash
find . -type f -name SKILL.md -print
```

If PyYAML or another YAML parser is not already available, do not silently install
it. Use the current client's metadata listing, a standard-library parser suitable
for the limited fields, or ask before adding a dependency.

## Recommendation summary

```text
Need: format Markdown tables without changing fenced code
Searched: local skills, client catalog, skills.sh CLI, authenticated GitHub search
Freshness: local index generated 2026-07-14

Recommendation: owner/repo@formatter
Why it fits: explicitly preserves fences and validates GFM table structure
Trust review: read SKILL.md and two scripts at commit <sha>; no network access;
  writes only the selected Markdown files; dependency versions disclosed
Compatibility: available from the client's project skill directory
Tradeoffs: requires Node.js <supported-version>

Not performed: no installation or execution without approval.
```
