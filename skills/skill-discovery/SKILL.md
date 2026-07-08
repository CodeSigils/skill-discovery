---
name: skill-discovery
description: Find, evaluate, and recommend agent skills for a task or domain. Use when asked to find a relevant skill, compare skill candidates, search skill catalogs or marketplaces, inspect GitHub skill sources, map skills to a project stack, or decide that a new skill should be created because no existing skill fits.
---

# Skill Discovery Methodology

This is a methodology, not a skill collection. It teaches agents how to
find skills, evaluate them, and recommend the best match.

## Operating Contract

When asked to find a skill:

1. Convert the user's task into search terms.
2. Search from local and structured sources outward.
3. Inspect candidate metadata and source files before recommending.
4. Rank candidates by task fit, trust, compatibility, freshness, and installability.
5. Report what was searched, what was skipped, and why the recommendation fits.
6. If no skill fits, offer a focused creation fallback instead of forcing a weak match.

Do not stop after the first keyword hit. A skill is only useful if its
instructions actually cover the user's task and can be loaded or installed by
the user's agent.

## Fallback Chain

Use the narrowest reliable source first, then widen the search:

```text
1. Installed/local skills
2. Local or hosted catalog index
3. Featured or curated sources
4. Marketplace APIs
5. Browser-rendered marketplace search
6. GitHub and web research
7. Build or draft a new skill
```

Before relying on any catalog or marketplace, check freshness and reachability
when the tooling exists. If a source cannot be checked because the agent lacks
network, browser, or shell access, say so in the final recommendation.

## Search Workflow

### 1. Map the Task to Terms

Extract 2-5 high-signal terms from the request. Prefer nouns, product names,
frameworks, file formats, and workflows.

```text
"Set up CI/CD for a Node service"
terms: ci, cd, pipeline, github actions, node

"Find a skill for editing Word docs with tracked changes"
terms: docx, word, tracked changes, redline
```

Expand each term with common aliases:

| Term | Also search |
|------|-------------|
| javascript | js, node, nodejs |
| typescript | ts, tsx |
| kubernetes | k8s |
| python | py |
| react | jsx, frontend |
| database | sql, postgres, mysql |
| ci/cd | github actions, workflow, automation |
| docx | word, office, ooxml |
| video | ffmpeg, encoding |
| audio | transcription, speech-to-text |

For multi-stack tasks, search each stack component separately, then prefer
skills that cover the intersection. If no single skill covers the whole stack,
recommend a small set of complementary skills.

### 2. Search Installed and Local Skills

Use the agent's native skill list/search tools when available. If only
filesystem access exists, recursively scan for `SKILL.md`; skill directories
may be nested by category.

```bash
find . -name SKILL.md -print
```

Inspect frontmatter first. A candidate should have at least `name` and
`description`. Search `name`, `description`, and `tags` if present.

Avoid shallow globs such as `skills/*/SKILL.md`; they miss categorized layouts
like `skills/cloud/aws-deploy/SKILL.md`.

### 3. Search Catalog Indexes

If a JSON catalog is available, parse it instead of grepping raw text. Catalogs
usually expose a flat list and may include trust, tags, source, repo, path, or
install commands.

```python
import json

with open(catalog_path, encoding="utf-8") as f:
    catalog = json.load(f)

skills = catalog if isinstance(catalog, list) else catalog.get("skills", catalog.get("data", []))
terms = ["python", "testing"]

def haystack(skill):
    fields = [
        skill.get("name", ""),
        skill.get("description", ""),
        " ".join(skill.get("tags", [])),
    ]
    return " ".join(fields).lower()

matches = [
    skill for skill in skills
    if any(term.lower() in haystack(skill) for term in terms)
]

matches.sort(key=lambda skill: (
    skill.get("trust_level") != "official",
    skill.get("source") != "official",
    skill.get("name", ""),
))
```

Check catalog metadata such as `generated_at`, `updated_at`, `version`, or
`expires`. If the index is more than two weeks old, keep searching newer
sources and mention the staleness.

### 4. Search Marketplace APIs

Prefer structured API results over browser scraping when they exist. Verify
URLs at query time; endpoints and schemas can drift.

Useful starting points:

```text
https://skills.sh/api/search?q=<term>
https://api.github.com/search/code?q=<term>+SKILL.md&per_page=10
https://crossaitools.com/api/skills?limit=100
https://skills.mercuryagent.sh/api/skills?limit=100
```

API search guidance:

- Search multiple aliases, not just the user's exact wording.
- Treat install counts and stars as weak signals, not proof of fit.
- Fetch or inspect the underlying `SKILL.md` for top candidates.
- Prefer official/vendor sources, then transparent GitHub repos, then
  aggregators.
- If an API returns a broad paginated listing with no search endpoint, filter
  locally by `name`, `description`, `tags`, and repo fields.

### 5. Use Browser Search When Needed

Some marketplaces are JavaScript-rendered. If API search returns nothing or a
marketplace has no useful API, use browser tooling when available:

1. Open the marketplace search page with the strongest term.
2. Trigger the search if the SPA does not load results automatically.
3. Read result names, descriptions, source repos, install counts, and badges.
4. Click through to top candidates.
5. Inspect the raw source repo or `SKILL.md` before recommending.

If browser tooling is unavailable, skip this stage explicitly and continue with
GitHub or web search if available.

### 6. Search GitHub and the Web

Use this when catalogs and marketplaces miss, look stale, or only return weak
matches.

Recommended searches:

```text
"SKILL.md" "<domain>"
"agentskills.io" "<domain>"
"<agent-name>" "skill" "<domain>"
site:github.com "SKILL.md" "<task keyword>"
github topic: agent-skill, claude-skill, codex-skill, mcp
```

For each repo result, check:

- Does it contain a real `SKILL.md` or compatible skill instructions?
- Does frontmatter include a clear `name` and `description`?
- Is the repo source transparent and inspectable?
- Is the skill maintained recently enough for the domain?
- Does the skill solve the user's task, or only share a broad category?
- Can the user's agent load or install it?

For volatile domains such as APIs, security tooling, legal workflows, cloud
providers, and actively changing libraries, prefer recently maintained skills
and verify current docs before relying on the skill.

## Evaluation Rubric

Classify each candidate before recommending it.

| Tier | Criteria | Action |
|------|----------|--------|
| Direct hit | The name, description, and body clearly match the requested task. Source is trusted or inspectable. Install path is clear. | Recommend first. |
| Good partial | Covers the domain but misses a feature, platform, or workflow detail. | Recommend only with the gap stated. |
| Weak partial | Shares keywords but would require substantial adaptation. | Mention only if no better option exists. |
| Off-domain | Does not actually solve the task. | Exclude. |

Use these checks:

- Task fit: Does the body describe the exact workflow the user needs?
- Trigger quality: Would the description cause the skill to be invoked for this task?
- Trust: Is it official, vendor-maintained, or from an inspectable repo?
- Freshness: Is the catalog or repo recent enough for the domain?
- Compatibility: Does it use the user's skill format and loading path?
- Installability: Is there a clear install command or directory placement?
- Resource quality: Are referenced scripts, assets, and docs present?
- Safety: Does it ask the agent to run risky commands, hide network behavior, or trust opaque binaries?
- Coverage: Did the search include aliases, tags, and nested directories?

When two skills are close, prefer the one with clearer procedural guidance and
fewer hidden assumptions over the one with higher popularity.

## Recommendation Format

Keep recommendations short, evidence-based, and reproducible.

```text
I searched: <sources and terms>
Skipped: <sources skipped because of missing tooling or access>

Top recommendation: <skill-name>
Source: <official/vendor/GitHub/community/marketplace>
Why it fits: <task-specific reason>
How to use/install: <command or path if known>
Notes: <freshness, compatibility, or safety caveats>

Alternatives:
- <skill-name>: <when it is better/worse>
- <skill-name>: <when it is better/worse>

If none fit:
No direct match found. The closest partial is <name>, but it lacks <gap>.
I recommend creating a small skill for <specific workflow>.
```

Mention the most important negative evidence. For example, say "I found five
Kubernetes skills, but none mentioned Helm charts" when that distinction
matters to the user's task.

## Project-Portfolio Mapping

When asked which skills would help a set of projects:

1. Inventory each project's stack, workflows, and pain points.
2. Search for skills per stack component and repeated workflow.
3. Check whether an installed skill already covers the need.
4. Rank by immediate utility: direct blocker, repeated workflow, quality
   improvement, already covered, speculative.
5. Recommend a small portfolio, not every plausible skill.

## Creation Fallback

Create or draft a new skill when:

- No direct or useful partial match exists.
- The best candidate is stale or unsafe for the domain.
- The user's workflow depends on local conventions no public skill can know.
- Multiple partial skills would be more confusing than one focused skill.

Minimal structure:

```yaml
---
name: my-skill-name
description: What this skill does and when to use it, including concrete triggers.
---

# My Skill Name

## Workflow

1. Do the first essential action.
2. Inspect or validate the relevant artifact.
3. Apply the domain-specific procedure.
4. Verify the result.

## Pitfalls

- Name the edge cases that would otherwise be missed.
```

For Codex-authored skills, keep frontmatter to `name` and `description` unless
the target platform explicitly requires more fields.

## Runtime Notes

External sources drift. Treat marketplace names, counts, URLs, API shapes, and
install commands as current only after verification. Static research snapshots
are useful for orientation, but recommendations should be based on what the
agent can verify during the task.

If the environment has no network access, still search local and installed
skills thoroughly, then report that external marketplace and GitHub stages were
not checked.
