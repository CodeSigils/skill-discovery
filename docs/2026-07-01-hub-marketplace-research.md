---
status: reference
date: 2026-07-01
updated: 2026-07-01
purpose: >
  Reference map of the agent-skill ecosystem — hub index, external marketplaces,
  client ecosystem, discovery layers, and design principles that shaped this repo.
  Archived research, not the shipped product itself.
---

# Hub & Marketplace Catalog Research

> **Purpose:** This document maps every discoverable source in the agent skill
> ecosystem as of 2026-07-01. It is the evidence base that informed the
> `skill-discovery` methodology. The data is a snapshot — live-verified at
> the date shown, but the ecosystem drifts continuously.

---

## 1. The Landscape (live-verified 2026-07-01)

### 1.1 Hermes Built-in Hub (local cache)

The Hermes agent ships with a pre-populated hub index. No network calls needed.

| Field | Value | Source |
|-------|-------|--------|
| Index format | JSON (`version`, `generated_at`, `skill_count`, `skills`) | `~/.hermes/skills/.hub/index-cache/hermes-index.json` |
| Index age | 2026-05-26 — **stale (~5 weeks)** | `generated_at` field |
| Total indexed | 2,460 skills | Live cache count |

**Source breakdown of the 2,460 indexed skills:**

| Source | Skills | Trust | Notes |
|--------|--------|-------|-------|
| skills.sh | 1,218 | Community | Primary public leaderboard. Powers featured cache. Install via `npx skills add` |
| lobehub | 500 | Community | LobeChat skill catalog |
| browse-sh | 330 | Community | Browser-level skill collection |
| clawhub | 200 | Evaluate | OpenClaw marketplace — treat as untrusted until inspected |
| github | 127 | High | Community repos, transparent |
| official | 84 | Highest | Hermes-bundled, maintained |
| claude-marketplace | 1 | High | Single entry |
| **Total** | **2,460** | | |

**Metadata fields per skill (all sources):** `name`, `description`, `identifier`, `source`, `repo`, `path`, `tags`, `extra`, `trust_level`. The `skills.sh` source also includes `resolved_github_id`.

**Available metadata across sources:**

```text
All sources:  name, description, identifier, source, repo, path, tags, extra, trust_level
skills.sh:    + resolved_github_id
```

**Featured skills cache:** 100 curated skills from major vendors (Anthropic, Microsoft Azure, Vercel, Remotion) at
`skills_sh_featured.json`. All sourced from skills.sh.

**Key constraint: The hub catalog is an INDEX, not an INSTALL.** Most skills exist only in the index — they are not
downloaded locally. A hub search finds entries, but physically loading a skill requires it to be installed separately.

---

### 1.2 External Marketplaces (live scan 2026-07-01)

All URLs verified with `curl -s -o /dev/null -w "%{http_code}"`.

| Marketplace | URL | Status | Role | Coverage signal |
|-------------|-----|--------|------|-----------------|
| skills.sh | https://skills.sh/ | 200 | Primary public leaderboard | 1,218 skills in hub index. All-time leaderboard, per-skill pages. |
| agentskill.sh | https://agentskill.sh/ | 200 | Broad marketplace; role/platform filtering, quality + security scores | Large cross-platform catalog |
| SkillsMP | https://skillsmp.com/ | 200 | Broad SKILL.md aggregator; occupation/category map | 270K+ SKILL.md files claimed |
| ClawHub | https://clawhub.ai/ | 200 | OpenClaw skills and plugins marketplace | 200 skills in hub index |
| skilldock.io | https://skilldock.io/ | 200 | Registry of agent skills; versioned, publish/install | 1st gen: 10+ repos, 20+ skills. V2 in development. |
| agentskills.io | https://agentskills.io/ | 200 (spec); Showcase 404→200 same day | Open specification standard | 21.3K★ repo. Showcase was 404 at ~02:00 UTC, returned to 200 by ~06:24 UTC — drift confirmed within hours |

---

### 1.3 agentskills.io Client Ecosystem

Live count from the home page carousel (deduplicated): **42 clients**.

| Client | Type | URL |
|--------|------|-----|
| Claude Code | IDE agent | claude.ai/code |
| OpenAI Codex | CLI agent | developers.openai.com/codex |
| Gemini CLI | CLI agent | geminicli.com |
| GitHub Copilot | IDE plugin | github.com |
| Cursor | IDE | cursor.com |
| VS Code | IDE | code.visualstudio.com |
| Junie | IDE agent | junie.jetbrains.com |
| OpenCode | CLI agent | opencode.ai |
| Roo Code | CLI agent | roocode.com |
| TRAE | IDE agent | trae.ai |
| Goose | CLI agent | block.github.io/goose |
| OpenHands | CLI agent | openhands.dev |
| Claude | Web agent | claude.ai |
| Spring AI | Framework | docs.spring.io/spring-ai |
| Snowflake Cortex Code | Data platform | docs.snowflake.com |
| Google AI Edge Gallery | Edge AI | github.com/google-ai-edge/gallery |
| Fast Agent | Framework | fast-agent.ai |
| Letta | Memory framework | letta.com |
| Mistral AI Vibe | CLI agent | github.com/mistralai/mistral-vibe |
| Laravel Boost | Framework | github.com/laravel/boost |
| Tabnine | IDE plugin | tabnine.com |
| Factory | AI worker | factory.ai |
| Workshop | Platform | workshop.ai |
| Qodo | Testing | qodo.ai |
| VS Code Extensions (VT Code, Amp, bub, etc.) | IDE extensions | — |
| **... and 18 more** | | |

**Notable:** Hermes Agent is NOT listed on the agentskills.io client carousel.
Hermes is an agentskills.io-compatible client (it loads skills from `skills/*/SKILL.md`),
but is not (yet) registered on the showcase.

---

### 1.4 Ecosystem Directories

| Directory | URL | Content | Structure data? |
|-----------|-----|---------|-----------------|
| Hermes Atlas | hermesatlas.com | 178+ Hermes repos across 12 categories, weekly star velocity | GitHub stars, descriptions, categories — but NOT file trees, skill counts, or reference ratios |
| agentskills.io repo | github.com/agentskills/agentskills | Specification, tools, reference implementation | README, not a skill directory |
| awesome-copilot | github.com/github/awesome-copilot | 35.9K★ community marketplace for Copilot | Links, categories — not machine-parseable |
| anthropics/claude-plugins-official | github.com/anthropics/claude-plugins-official | 37 plugins, 29+ SKILL.md files | Full repo tree |
| openai/skills | github.com/openai/skills | Official Codex skill catalog | Full repo tree |

---

### 1.5 Platform-Vendor Skill Repos (reference)

| Repo | Stars | Skills | Format | Discovery |
|------|-------|--------|--------|-----------|
| addyosmani/agent-skills | 68K | 24 | Flat SKILL.md, no YAML frontmatter | README only |
| anthropics/claude-plugins-official | 31.3K | 37 plugins, 29+ SKILL.md | agentskills.io + extensions | `.claude-plugin/` discovery |
| openai/skills | — | ~20 | agentskills.io | Codex $skill-installer |
| wondelai/skills | 1.5K | 50 | agentskills.io (book-philosophy) | Flat root directory |
| vercel-labs/skills | — | Featured on skills.sh | agentskills.io | npx skills |
| microsoft/azure-skills | — | Featured on skills.sh | agentskills.io | Featured cache |

---

## 2. Case Study: hermes-skill-hq Discovery Pipeline

The `hermes-skill-hq` repository (separate from this repo) ships a complete discovery
methodology in its `hub-explorer` skill. This section documents its architecture as a
reference — it was the primary influence for the `skill-discovery` methodology.

### 2.1 The Search Pipeline

```
INDEX.md miss
  → Hub catalog (hermes-index.json) — keyword, tag, source filter
  → Featured cache (skills_sh_featured.json)
  → External marketplaces (13 sources in references/sources.md)
  → Hermes Atlas ecosystem directory
  → Upstream GitHub search
  → Build from scratch
```

### 2.2 Search Methods

| Method | Tool | What it does |
|--------|------|--------------|
| Keyword search | Python script | Searches `name` + `description` in hermes-index.json |
| Tag discovery | Python script | Filters by `tags` field |
| Source filtering | Python script | Filters by source repo (e.g. `anthropics`, `microsoft`) |
| Featured search | Python script | Queries skills_sh_featured.json |
| External table | references/sources.md | 13 sources with trust posture, search path, use cases |

### 2.3 Evaluation Checklist

From hub-explorer SKILL.md:
- Check name (descriptive?)
- Read description (matches task?)
- Check source (official > github > others)
- Verify installed status
- If not installed: extract guidance, execute directly, offer to build
- Consider alternatives in same domain
- Check Hermes compatibility

### 2.4 Strengths

- **No network calls.** All hub data is local cache.
- **Structured fallback.** INDEX → hub → featured → external → build.
- **Trust tiers.** `official` > `github` > others. Declared in source matrix.
- **Portable methodology.** 95% of the discovery workflow is agent-agnostic.
- **Evaluation rubric.** Systematic before proposing to user.
- **Publishing pipeline.** `hermes skills publish`, `external_dirs`, Atlas registration.

### 2.5 Weaknesses Found

| Issue | Impact | Root cause |
|-------|--------|------------|
| Hub index stale (2026-05-26) | New skills invisible | Cache not auto-refreshed |
| No freshness tracking | Can't know how stale a find is | No `last_verified` on results |
| External sources table has 13 rows | Hard to maintain, risks drift | Hand-maintained prose |
| agentskills.io Client Showcase is 404 | Can't verify client count | Platform URL drift |
| Index has 7 sources but 3 dominate | skills.sh (50%) + lobehub (20%) + browse-sh (13%) = 83% | Uneven source import |
| No registry-level comparison | No structured per-source comparison | No ecosystem comparison framework applied to marketplaces |

**Cumulative:** The hermes-skill-hq discovery methodology is structurally sound
(search → evaluate → fallback → recommend), but the data it depends on (hub index,
external sources table) is hand-maintained and drifts. The `skill-discovery` methodology
addresses this by including a freshness check as the first step and teaching runtime
verification rather than hardcoding source tables.

---

## 3. Discovery Layers — What Happens at Each Level

The landscape reveals three distinct layers. They're often conflated.

### Layer A: Agent-Side Retrieval (what the runtime provides)

The CLI, config, or API that loads skills into a session. This is platform-specific:

| Platform | Retrieval mechanism |
|----------|---------------------|
| Hermes | `hermes skills search`, `skill_view()`, `skills.external_dirs`, hub cache |
| Claude Code | Directory walk `.claude/skills/`, plugin.json, skillOverrides config |
| Codex CLI | Directory walk `.codex/skills/`, `$skill-installer` |
| Gemini CLI | `gemini skills list`, `gemini skills install`, directory walk |
| Cursor | `.cursor/rules/` — no search, just glob match |

**Key decision:** This repo does NOT ship a retrieval mechanism for every
platform. The runtime provides those. What it ships is a **discovery methodology**
that any agent can follow to find skills, regardless of platform.

### Layer B: Catalog Research (what the agent does to find skills)

The systematic search across index → marketplaces → GitHub.

**Three sub-methods:**
- **Catalog search** — keyword + tag + source filter against the hub index
- **Marketplace scan** — fallback chain through known marketplaces
- **GitHub deep search** — direct repo inspection when catalogs miss

### Layer C: Publishing / Registration (how skills become discoverable)

Getting a skill into the findable pool:
- `hermes skills publish` (Hermes-specific)
- `external_dirs` config entry (Hermes-specific)
- skills.sh auto-indexing (auto from GitHub activity)
- agentskill.sh submission (manual)
- Hermes Atlas registration (GitHub issue)
- Claude Code plugin.json (platform-specific)

**Key decision:** The repo registers itself on discoverable channels
(Atlas, skills.sh auto-index), but does NOT ship publish scripts — each runtime
provides its own.

---

## 4. How the Product Decisions Emerged

This section traces the design evolution that produced the current
`skill-discovery` methodology.

### 4.1 What the Methodology Contains

1. **Fallback chain** (INDEX → hub → featured → marketplaces → GitHub → build)
2. **Keyword generation** — how to map a task description to 2-3 search keywords
3. **Search methods** — Python scripts for hub keyword/tag/source search
4. **Evaluation rubric** — name, description, source trust, installed status, alternatives
5. **Freshness check** — verify index age, note staleness in results
6. **Project-portfolio mapping** — map candidates to active projects, tier by impact
7. **Skill creation fallback** — how to build a minimal skill when nothing matches

### 4.2 Design Decisions

| Decision | Rationale |
|----------|-----------|
| Single methodology skill, not a collection | The hub already has 2,460 indexed skills — a collection adds nothing next to that. |
| No install scripts | Every platform provides native skill consumption paths. A script would compete and drift. |
| No generated indexes or catalogs | Filesystem discovery is sufficient at 1 skill. |
| No platform adapter files | User-side setup only. The repo ships only `skills/*/SKILL.md` and a cross-tool symlink. |
| One CI check | Hermes-reference drift is the only thing no runtime validates. Everything else is caught elsewhere. |
| Runtime verification over hardcoded tables | URLs drift. Teach the agent to check reachability rather than trust stale data. |

### 4.3 What This Repo Does NOT Do

- **Not a skill collection.** Static collections are what addyosmani already does.
- **Not a GitHub search tool.** The user's agent already has search capabilities.
- **Not a Hermes-specific hub explorer.** The methodology is agent-agnostic.
- **Not an index or catalog.** The hub index does that. This repo teaches agents to *use* it.
- **Not a publish pipeline.** Each runtime provides its own.
- **Not a comparison framework.** Cross-ecosystem comparison can be found in hermes-skill-hq's
  ecosystem-comparison-framework reference.

**This repo is a methodology, not a collection.**

---

## 5. Sources

| Source | URL | Method | Finding | Verified |
|--------|-----|--------|---------|----------|
| Hermes hub index (local cache) | `~/.hermes/skills/.hub/index-cache/hermes-index.json` | Live cache read | 2,460 skills, 7 sources, index dated 2026-05-26 | 2026-07-01 |
| Hermes hub featured cache | `~/.hermes/skills/.hub/index-cache/skills_sh_featured.json` | Live cache read | 100 featured skills from skills.sh | 2026-07-01 |
| Hermes installed skills | `hermes skills list` | CLI | ~240 installed, from builtin/local/skills.sh | 2026-07-01 |
| agentskills.io overview | https://agentskills.io/home | Browser | 42 client logos visible on home page | 2026-07-01 |
| agentskills.io spec | https://agentskills.io/specification | Browser | name + description required, optional ref/scripts/assets | 2026-07-01 |
| agentskills.io client-showcase | https://agentskills.io/client-showcase | Browser | **404 at ~02:00 UTC; 200 by ~06:24 UTC same day** | 2026-07-01 |
| agentskills.io repo | https://github.com/agentskills/agentskills | Browser snapshot | 21,302★ (observed on page) | 2026-07-01 |
| Hermes Atlas top skills | https://hermesatlas.com/lists/top-skills | Browser | 18 ranked entries, updated star counts (73.1K, 23.2K, 4.9K etc.) | 2026-07-01 |
| hermes-skill-hq hub-explorer skill | `guides/hub-explorer/SKILL.md` (hermes-skill-hq repo) | Code review | Full discovery pipeline: search → evaluate → fallback → recommend | 2026-07-01 |
| hermes-skill-hq external sources | `guides/hub-explorer/references/sources.md` (hermes-skill-hq repo) | Code review | 13 external sources with trust posture, search paths | 2026-07-01 |
| hermes-skill-hq ecosystem framework | `guides/hub-explorer/references/ecosystem-comparison-framework.md` (hermes-skill-hq repo) | Code review | 10-dimensional comparison protocol | 2026-07-01 |
| hermes-skill-hq cross-ecosystem skill | `research/cross-ecosystem-skill-research/SKILL.md` (hermes-skill-hq repo) | Code review | Platform vendor research, repo-level architecture, runtime bridge research | 2026-07-01 |
| hermes-skill-hq platform vendor ref | `research/cross-ecosystem-skill-research/references/platform-vendor-skill-systems.md` (hermes-skill-hq repo) | Code review | 6-platform convergence/divergence table | 2026-07-01 |
| skills.sh | https://skills.sh/ | HTTP 200 | Primary public leaderboard | 2026-07-01 |
| agentskill.sh | https://agentskill.sh/ | HTTP 200 | Broad marketplace with quality scores | 2026-07-01 |
| SkillsMP | https://skillsmp.com/ | HTTP 200 | Aggregator, 270K+ SKILL.md claimed | 2026-07-01 |
| ClawHub | https://clawhub.ai/ | HTTP 200 | OpenClaw marketplace | 2026-07-01 |
| skilldock.io | https://skilldock.io/ | HTTP 200 | Versioned skill registry, V2 in development | 2026-07-01 |

---

## 6. Open Questions (as of 2026-07-01)

| # | Question | Evidence state | Suggested research path |
|---|----------|---------------|------------------------|
| 1 | How often does the Hermes hub index auto-refresh? | Index is dated 2026-05-26. Not known if this is pull-based or push-based. | `rg -r 'hub.*refresh\|index.*update\|sync' ~/.hermes/config.yaml ~/.hermes/plugins/ --include='*.py' 2>/dev/null \| head` |
| 2 | Is there a CLI command to force-refresh the hub index? | Not in `hermes skills list` or `hermes skills search` docs seen so far. | `hermes help` / `hermes skills --help` / check `hermes_cli/skills_hub.py` in the Hermes source |
| 3 | Which agentskills.io clients support SKILL.md with optional features (scripts, references)? | Spec says optional, but per-platform support unknown. | Test on each target platform or check per-platform docs |
| 4 | What are the actual root-level skill repo patterns for top-20 Atlas repos? | Only 7 repos measured so far (research note). 20 would give statistical confidence. | `for r in ...; do curl -s "https://api.github.com/repos/$r/git/trees/main?recursive=1" \| python3 -c "..." ; done` |

---

## 7. Key Findings

### 7.1 Confirmed from Live Data

- **2,460 skills indexed** in the Hermes hub from 7 sources — the hub is useful, but discovery must span beyond it.
- **42 agentskills.io clients** — the standard is broadly adopted. The methodology follows it.
- **agentskills.io Client Showcase page was 404 at ~02:00 UTC, 200 by ~06:24 UTC** — drift confirmed within hours.
  External dependencies drift. Runtime verification is essential.
- **Hub index is 5 weeks stale** — discovery results may miss new skills. Freshness check is the first step.
- **skills.sh dominates the index** (50% of entries) — single source risk. The methodology includes fallback sources.
- **Hermes is NOT on the agentskills.io client showcase** — this repo could note this for ecosystem positioning.

### 7.2 Design Evolution

The initial plan treated this project as a **portable skill collection** — take existing
Hermes skills, strip Hermes-specific references, and ship them cleanly. Three realizations
changed the direction:

1. **The product was never a collection.** A static set of skills contradicts the core
   purpose — "scan best resources and discover best skills."
2. **Optimizing for file count masked the product question.** Reducing from 161 files to
   11 is a useful constraint exercise, but it doesn't answer "what does this repo do when
   invoked?"
3. **The methodology already existed.** The `hub-explorer` skill in hermes-skill-hq already
   had a complete discovery pipeline — it just needed to be extracted from its
   Hermes-specific shell so any agent on any platform can follow it.

### 7.3 Current Direction

> This repo ships a **portable discovery methodology skill** that teaches any agent
> how to scan the ecosystem — hub catalog, featured cache, external marketplaces, GitHub
> — evaluate candidates, and recommend the best skill for a task. It does NOT ship skills.

| Question | Earlier answer | Current answer (research-informed) |
|----------|---------------|-------------------------------------|
| What does this repo do? | Ships 3 clean portable skills | Ships a discovery methodology any agent can follow |
| How does it find skills? | From the repo's `skills/` directory | From the ecosystem — hub, marketplaces, GitHub |
| What's the core artifact? | A collection of SKILL.md files | A single SKILL.md teaching the search/evaluate/recommend workflow |
| How does it stay fresh? | CI checks file counts | The methodology always starts with a staleness check on the hub index |

---

## 8. Related Research

The data in this document was collected as part of a broader research cycle.
Related evidence:

| Resource | Location |
|----------|----------|
| Durable findings (cross-project patterns) | `~/labs/agent-concepts-study/2026-07-01-skill-discovery-durable-findings.md` |
| Hermes hub source code | Hermes Agent docs at hermes-agent.nousresearch.com |
| agentskills.io specification | agentskills.io/specification |
