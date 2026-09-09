# Portable examples

## Search a JSON index

This standard-library example tolerates common top-level list shapes:

```python
import json
from pathlib import Path

document = json.loads(Path(catalog_path).read_text(encoding="utf-8"))
if isinstance(document, list):
    skills = document
elif isinstance(document, dict):
    skills = document.get("skills", document.get("data", []))
else:
    raise ValueError("catalog must be a list or object containing skills/data")
if not isinstance(skills, list) or not all(isinstance(item, dict) for item in skills):
    raise ValueError("catalog skills/data must be a list of objects")
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
find . -path './.git' -prune -o \
  -path './node_modules' -prune -o \
  -path './.venv' -prune -o \
  -type f -name SKILL.md -print
```

Prefer explicit project, user, admin, and extension roots when the client
exposes them. Apply the discovery caps in `SKILL.md`; do not scan an entire
home directory or follow symlinks outside those roots.

If PyYAML or another YAML parser is not already available, do not silently install
it. Use the current client's metadata listing, a standard-library parser suitable
for the limited fields, or ask before adding a dependency.

## Recommendation summary

```text
Need: format Markdown tables without changing fenced code
Searched:
| Source/root | Query | Timestamp | Status | Results/limitations |
|---|---|---|---|---|
| local/client catalog | table, markdown, formatter | <UTC timestamp> | successful | 1 local match |
| skills.sh | table, markdown, formatter | <UTC timestamp> | unknown freshness | 4 results; shortlist capped at 3 |
| GitHub code search | table, markdown, formatter | <UTC timestamp> | unavailable | authentication unavailable |

Candidate evidence:
| Candidate | Path | Revision/update/license | Freshness | Payload | References | Loader | State |
|---|---|---|---|---|---|---|---|
| owner/repo@formatter | present | commit <sha>; updated <date>; MIT | known | complete | complete | verified | payload-inspected |

Quality assessment:
| Candidate | Strengths | Risks/limitations | Capability fit | Recommendation |
|---|---|---|---|---|
| owner/repo@formatter | Preserves fenced code; validates tables | Node.js dependency; no runtime test | direct | use after local smoke test |

Evidence:
- The candidate's documented workflow explicitly preserves fenced code.

Interpretation:
- The candidate is a direct fit for the stated formatting task.

Unknowns:
- Runtime behavior was not tested.

Recommendation: owner/repo@formatter
Recommendation gate: direct_fit
Why it fits: explicitly preserves fences and validates GFM table structure
Quality suggestions: run a synthetic fence/table fixture before installation;
  keep the skill scoped to Markdown files
Trust review: read SKILL.md and two scripts at commit <sha>; no network access;
  writes only the selected Markdown files; dependency versions disclosed
Compatibility gate: valid frontmatter; references present; loader verified
Capability risk: read-only present; writes present for selected Markdown files;
  network, credentials, subprocesses, and external messages absent
Behavior validation: not run; static inspection only
Tradeoffs: requires Node.js <supported-version>

Inspection limits: 2 files; 14 KiB; no skipped files
Report completeness:
- Retrieval: complete
- Canonical inspection: complete
- Behavior validation: not run
- Recommendation confidence: medium

Performed: read-only source inspection
Not performed: no installation or execution without approval; no secrets copied.
```
