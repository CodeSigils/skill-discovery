---
status: baseline
date: 2026-09-06
updated: 2026-09-06
expires: 2026-10-06
purpose: >
  Record a small, repeatable baseline for local skill-search cost before adding
  caching, indexing, or a new implementation language.
---

# Search-efficiency baseline

This is an initial maintainer measurement, not a quality or user-satisfaction
claim. It measures local candidate retrieval only; it does not measure external
provider latency, agent reasoning, inspection time, or recommendation usefulness.

## Method

On 2026-09-06, five representative queries were run with `rg` over
`/home/sand/projects` and `/home/sand/.codex/skills`, excluding `.git` and
`node_modules`. A candidate was counted when its `SKILL.md` contained the query
case-insensitively. The roots contained 110,470 skill files, including cached
and duplicated installations.

| Query | Matches | Retrieval time |
|---|---:|---:|
| `zola` | 20 | 700 ms |
| `python review` | 13 | 680 ms |
| `repository health` | 22 | 685 ms |
| `markdown formatter` | 24 | 692 ms |
| `skill discovery` | 245 | 694 ms |

## Findings

1. Raw local retrieval is sub-second on this machine, so HTTP implementation
   language is not an observed bottleneck.
2. The broad roots exceed the skill's 10,000-file search cap by an order of
   magnitude. Applicable project, user, and extension roots must be selected
   before scanning; broad recursive search creates noise despite low latency.
3. Lexical match counts are not candidate usefulness. No precision, recall,
   false-positive, or user-success measure was collected in this baseline.
4. Cached and duplicated skill trees materially distort result counts; VCS,
   cache, generated, and extension roots need separate reporting.

## Decision

Keep the current local-first, bounded workflow. Before adding an index, cache,
parallel provider requests, or Go implementation, repeat this protocol with
real user tasks and record search latency, serious-candidate count, inspection
effort, and usefulness. Treat this baseline as expired after 30 days unless
renewed with a new observation.

## Limitations

- The original baseline did not time external catalogs; the provider pilot below
  adds bounded index-load and matching measurements.
- No candidate was inspected for task fit or safety as part of this timing run.
- Results depend on this machine's filesystem, cache state, and root set.

## Provider pilot (2026-09-06)

The five-query pilot compared the bounded local baseline with the current
learn-skills.dev published index and skills.sh access paths. The learn-skills
index contained 113,253 entries and reported `updatedAt`
`2026-09-06T07:52:57Z`. Loading the 62 MB JSON index took 197 ms; lexical
matching took 71–75 ms per query.

| Query | Local matches | learn-skills matches | skills.sh result |
|---|---:|---:|---|
| `zola` | 20 | 0 | Browser search reachable; result list not present in static HTML |
| `python review` | 13 | 14 | Browser search reachable; result list not present in static HTML |
| `repository health` | 22 | 0 | Browser search reachable; result list not present in static HTML |
| `markdown formatter` | 24 | 3 | Browser search reachable; result list not present in static HTML |
| `skill discovery` | 245 | 108 | Browser search reachable; result list not present in static HTML |

The documented skills.sh API returned HTTP 401 without a Vercel OIDC token.
The known `skill-discovery` detail page and badge remained reachable, but those
are not query-result evidence. No candidate was installed or executed.

### Pilot conclusions

1. learn-skills.dev is a useful broad-retrieval provider with explicit freshness
   metadata, but lexical results show that niche coverage is incomplete.
2. skills.sh is a useful indexed source and install-path authority, but API
   authentication and client-rendered search reduce unattended retrieval value.
3. Local-first search is necessary for project-specific and niche skills.
4. Provider orchestration should select sources per request and preserve
   fallback behavior; querying all providers unconditionally is not justified.
5. Candidate usefulness, precision, and recall remain unmeasured because this
   pilot measured retrieval signals only. The next experiment should inspect a
   small sample of returned candidates and record user/task fit.

## Bounded task-fit pilot (2026-09-06)

To make the next experiment concrete, five representative requests were run
against the same local-first roots (`/home/sand/projects` and
`/home/sand/.codex/skills`). VCS metadata, dependency directories, and virtual
environments were excluded. These are maintainer-selected requests, not real
user outcomes or a benchmark of agent reasoning.

| Request | Query | Matches | Retrieval | Strongest inspected candidate | Static fit |
|---|---|---:|---:|---|---|
| Zola site generation | `zola` | 20 | 216 ms | `zola-skill/skills/zola` | Direct |
| Python code review | `python review` | 13 | 213 ms | `py-review-skill/skills/py-review` | Direct |
| Repository health scan | `repository health` | 23 | 210 ms | `repo-health-and-sync-skill/skills/repo-health-scan` | Direct |
| Markdown formatting | `markdown formatter` | 24 | 210 ms | `zero-md-formatter/skills/markdown-formatter` | Direct |
| Quantum gardening workflows | `quantum gardening` | 0 | 212 ms | None | Reject/no candidate |

The four inspected candidates had readable frontmatter and descriptions that
matched the requested task. Inspection was static only: no candidate scripts
were executed, no installation was attempted, and no claim of behavioral
quality or user satisfaction was made. The zero-result request correctly
produced no recommendation rather than triggering creation or installation.

### Pilot decision

This small task-fit sample confirms that bounded local retrieval is fast enough
for interactive use and that obvious task-specific candidates can be found. It
does not justify a Go migration, provider cache, or parallel provider layer.
The next evidence step is a real user-task sample with success ratings and
per-stage timings; until then, keep the implementation in maintenance mode.

## Emulated history-based pilot (2026-09-06)

Five realistic requests from the project's prior work were replayed against
the same two local roots. This emulation tests search behavior and review
discipline only; it cannot measure user satisfaction.

| Request | Query | Matches | Retrieval | Emulated outcome |
|---|---|---:|---:|---|
| Audit a Zola skill | `zola` | 20 | 212 ms | Direct match: `zola-skill/skills/zola` |
| Review Python code | `python review` | 13 | 211 ms | Direct match: `py-review-skill/skills/py-review` |
| Audit repository health and CI | `repository health` | 23 | 212 ms | Direct match exists, but lexical ordering does not surface it early |
| Find a discovery/catalog skill | `skill discovery` | 250 | 217 ms | Direct local match exists, but broad query produces substantial noise |
| Validate Agent Skills format | `skills-ref` | 61 | 217 ms | Conditional: many authoring-related matches; canonical validator use still requires exact tool inspection |

The replay confirms that retrieval is fast, but it also exposes a concrete
quality gap: raw lexical ordering can bury the strongest local candidate and
does not distinguish a direct task match from a broad ecosystem mention.
Aliases, frontmatter-aware ranking, and candidate inspection remain more
valuable than changing implementation language. These observations are still
not sufficient to justify implementing a ranking service; validate the pattern
against real user requests first.

## Query record: general Go skill (2026-09-06)

Request: “Find a good skill on Go language.” The request was interpreted as a
general Go-development need covering implementation, refactoring, review,
testing, and architecture, with no installation or execution authorization.

### Search effort and behavior

Local-first search covered `/home/sand/projects` and
`/home/sand/.codex/skills`, excluding VCS metadata, `node_modules`, and virtual
environments. Three lexical queries were measured independently:

| Query | Matches | Retrieval |
|---|---:|---:|
| `go golang` | 2 | 211 ms |
| `golang` | 617 | 210 ms |
| `go language` | 29 | 212 ms |

The short compound query under-retrieved, while `golang` over-retrieved from
cached catalogs and Claude-specific material. Frontmatter-aware interpretation
and manual ranking were necessary to identify useful candidates.

The local candidates inspected completely were `golang-idioms`, `go-guide`,
and `golang-expert-skill`; a specialized `review-go` candidate was inspected
enough to classify it as review-only. Candidate inspection remained static and
within the documented file/size/depth budgets. The strongest external candidate
was [`madflojo/go-style-agent-skill`](https://github.com/madflojo/go-style-agent-skill),
whose canonical `go-style-guide` payload and 11 referenced documents were
verified at commit
`0d8eed0a8ff1acb586e9fa0a4b1c67b59ed449e8`.

Provider behavior was mixed: the learn-skills.dev freshness manifest was
available and current at query time, while the skills.sh CLI was not installed
and its authenticated API path was unavailable. GitHub source inspection added
more effort but supplied the canonical revision, license, and reference-tree
evidence required for a conditional recommendation.

### Query outcome

The result was a conditional recommendation of `go-style-guide`, due to its
scope and inspectable references. The candidate’s latest source update
(`2026-06-13`) and apparent README/embedded-version mismatch were reported as
maintenance caveats. No installation, copying, execution, or behavioral claim
was made.

This query reinforces that the current bottleneck is candidate ranking and
provenance inspection, not local search speed. It is one observed request and
does not justify a Go implementation, provider cache, or parallel lookup layer.

## Query record: novel-writing skill (2026-09-06)

Request: “Find a good skill on novel writing.” The need was interpreted as a
general reusable workflow for planning, drafting, revising, and reviewing a
novel. Installation and execution were not authorized.

### Search effort and behavior

Local-first search covered `/home/sand/projects` and
`/home/sand/.codex/skills`, excluding VCS metadata, `node_modules`, and virtual
environments. Independent lexical queries produced:

| Query | Matches | Retrieval |
|---|---:|---:|
| `novel writing` | 7 | 210 ms |
| `fiction writing` | 14 | 213 ms |
| `creative writing` | 108 | 215 ms |
| `storytelling` | 1,126 | 212 ms |

The narrow novel/fiction terms were useful; `storytelling` was too broad. The
local results were primarily generated learn-skills.dev catalog content rather
than clearly installed, provenance-qualified skills. The current learn-skills
freshness manifest was available at query time (`2026-09-06T07:53:07Z`). The
skills.sh CLI was not installed and its authenticated API path was unavailable,
so GitHub search was used as the external fallback.

### Candidate inspection and outcome

The strongest local candidates were inspected statically. `creative-writing-craft`
contained useful general craft guidance but linked reference files were absent
from the inspected cache. `novel-writing-techniques` had the same reference
completeness problem. `novel-architect` was comprehensive but creates and
manages files under `~/writing/novels`, so it was treated as conditional rather
than read-only discovery guidance.

GitHub source inspection identified [`wgwtest/novel-writing`](https://github.com/wgwtest/novel-writing)
as the strongest candidate. Its complete payload, ten references,
`agents/openai.yaml`, and manuscript-checking script were present at commit
`b6382cf7ff29caa83830646432d8010ca96120f5`; the repository license was MIT.
The result was a direct fit for general novel work, with a maintenance caveat
that its latest source update was `2026-08-24`.

No candidate scripts were executed, no manuscript data was supplied, and no
installation or file mutation occurred. This query again shows that ranking,
provenance, and reference completeness matter more than local search speed.

## Query record: note-taking skill (2026-09-06)

Request: “Use skill-discovery to find a skill in note taking.” The target
storage system was unspecified, so the search considered project-file notes,
meeting notes, Obsidian, and app-backed note systems. Installation and
execution were not authorized.

### Search effort and behavior

Local-first search covered `/home/sand/projects` and
`/home/sand/.codex/skills`, excluding VCS metadata, `node_modules`, and virtual
environments. Independent lexical queries produced:

| Query | Matches | Retrieval |
|---|---:|---:|
| `note taking` | 6 | 213 ms |
| `note-taking` | 184 | 213 ms |
| `notetaking` | 1 | 212 ms |
| `knowledge management` | 145 | 210 ms |

The hyphenated and knowledge-management queries were noisy and mostly surfaced
generated catalog entries or client-specific skills. The learn-skills.dev
freshness manifest was current at query time (`2026-09-06T07:53:07Z`). No
skills.sh CLI or authenticated API path was available, so GitHub/web search was
used for provider-specific alternatives.

### Candidate inspection and outcome

The local `note-taker` candidate directly described meeting, interview, and
template-based note capture, but assumed Claude paths (`~/.claude`), Claude
tools, and persistent preferences; it was therefore incompatible with the
current Codex client without adaptation. `localbrain-collect` included a remote
installer and external service dependency, so it was not recommended. The
Ars Contexta setup/recommendation candidates were broad knowledge-system
scaffolds rather than lightweight note capture.

The strongest portable candidate was
[`OthmanAdi/planning-with-files`](https://github.com/OthmanAdi/planning-with-files),
whose Codex-specific payload, MIT license, and latest commit
`d47a61950e784fc4237ba10ddc1e9e198bd0f275` were verified. It is a conditional
fit for durable project notes because it maintains `task_plan.md`,
`findings.md`, and `progress.md`, but it is not a general meeting-notes system
and introduces file creation plus lifecycle hooks. Obsidian and Inkdrop
alternatives were classified as provider-specific because they require their
respective vault/MCP environments.

### Query outcome

No unconditional direct-fit note-taking skill passed for Codex. The result was
reported as a conditional choice: use `planning-with-files` for project-bound
working memory, or choose a provider-specific skill after naming the target
note system. This query demonstrates that destination-aware constraints are
more important than lexical match count; no ranking, cache, or language
migration is justified by this single observation.

## Query record: Agent Skills authoring best practices (2026-09-06)

Request: “Use skill-discovery to find a skill in agent skill creation best
practices.” The need was interpreted as guidance for creating, structuring,
testing, validating, and improving an Agent Skill for the current Codex client.
Installation and execution were not authorized.

### Search effort and behavior

Local-first search covered `/home/sand/projects` and
`/home/sand/.codex/skills`, excluding VCS metadata, `node_modules`, and virtual
environments. Independent lexical queries produced:

| Query | Matches | Retrieval |
|---|---:|---:|
| `skill creation` | 679 | 214 ms |
| `skill authoring` | 136 | 214 ms |
| `agent skills` | 1,481 | 219 ms |
| `skill best practices` | 34 | 216 ms |

The broad `agent skills` and `skill creation` terms were highly noisy,
dominated by generated catalog entries and client-specific authoring skills.
The local Codex system skill was identified by its name and direct path rather
than by lexical ranking. The learn-skills.dev freshness manifest was current at
query time (`2026-09-06T07:53:07Z`).

### Candidate inspection and outcome

The installed Codex `skill-creator` at
`/home/sand/.codex/skills/.system/skill-creator/SKILL.md`
was the strongest candidate: it provides scoped authoring guidance, minimal
frontmatter, progressive disclosure, references/scripts decisions, evaluation
cases, iterative improvement, and packaging. Its 229-line payload was fully
inspected and requires no external service.

The official [`anthropics/skills` skill-creator](https://github.com/anthropics/skills/tree/41bbe19d1a1a7eaab5e7bb9050a417e5c6cffc8f/skills/skill-creator)
was also inspected at commit `41bbe19d1a1a7eaab5e7bb9050a417e5c6cffc8f`.
Its complete resource tree includes evaluation runners, benchmark aggregation,
description optimization, packaging, graders, and schemas. It is strong
methodological evidence, but parts of its runner workflow assume Claude
CLI/subagents, so it is a conditional rather than a drop-in Codex replacement.

Other candidates were lower-fit: `writing-skills` requires a separate
Superpowers TDD skill; Hermes authoring guidance is Hermes-specific; and
`skill-best-practices` mandates Claude repository conventions.

### Query outcome

The direct recommendation was the already-installed Codex `skill-creator`,
with the official Anthropic implementation retained as a cross-reference for
evaluation methodology. No installation, copying, execution, or skill
replacement occurred. This query reinforces that client compatibility and
provenance-aware ranking matter more than raw lexical coverage.

## Query record: learning agent concepts (2026-09-06)

Request: “Use skill-discovery to find a skill for learning agent concepts.”
The target was interpreted as foundational, client-neutral concepts rather
than a framework-specific implementation tutorial. Installation and execution
were not authorized.

### Search effort and behavior

Local-first search covered `/home/sand/projects` and
`/home/sand/.codex/skills`, excluding VCS metadata, `node_modules`, and virtual
environments. Independent lexical queries produced:

| Query | Matches | Retrieval |
|---|---:|---:|
| `agent concepts` | 9 | 213 ms |
| `agentic concepts` | 0 | 215 ms |
| `agent fundamentals` | 6 | 211 ms |
| `agent architecture` | 345 | 215 ms |
| `multi-agent concepts` | 0 | 212 ms |

The narrow concepts queries were fast but sparse; `agent architecture` was
too broad. The apparent local hits were generated learn-skills.dev catalog
entries, not installed, provenance-qualified skills. The freshness manifest
was current at query time (`2026-09-06T07:53:07Z`). No skills.sh CLI or
authenticated API path was available, so canonical GitHub inspection was used
as the external fallback.

### Candidate inspection and outcome

`adenhq/hive` catalog entries named `hive-concepts` and
`building-agents-core` appeared to fit, but neither path exists in the
repository's current canonical tree. The repository's current `main` commit
is `0c387492067e8b7d3e1c803009169f202f30ed77` and its license is Apache-2.0;
the cached entries therefore have a source-revision mismatch and were
rejected. `all-agentic-architectures` is implementation-heavy, framework
oriented, and expects multiple dependencies/API keys, so it is not a general
concepts tutor.

The conditional external alternative for learning the Agent Skills format is
[`magnus919/agent-skills/agent-skills/SKILL.md`](https://github.com/magnus919/agent-skills/blob/main/agent-skills/SKILL.md),
but it should be re-verified at selection time. The official
[`Agent Skills overview`](https://github.com/agentskills/agentskills/blob/main/docs/home.mdx)
is stronger evidence for the standard itself than any catalog result, but is
documentation rather than a teaching skill.

### Query outcome

No unconditional direct-fit, canonical skill passed for general agent
concepts. The recommendation was to use the official standard documentation
for Agent Skills concepts, or run a second, framework-specific search after
the learner names a target runtime. No installation, copying, execution, or
cache mutation occurred. This query again shows that stale catalog provenance
can outweigh an otherwise excellent lexical match.

## Query record: frontend skill (2026-09-06)

Request: “Use skill-discovery to find a skill for front end.” The target was
interpreted as web UI/frontend design and implementation, with framework and
hosting context left unspecified. Installation and execution were not
authorized.

### Search effort and behavior

The same local-first roots and exclusions were used. Independent lexical
queries produced:

| Query | Matches | Retrieval |
|---|---:|---:|
| `front end` | 23 | 214 ms |
| `frontend development` | 294 | 214 ms |
| `frontend design` | 269 | 210 ms |
| `web frontend` | 88 | 210 ms |
| `react frontend` | 132 | 209 ms |

`front end` was precise but sparse; `frontend development` and
`frontend design` produced many client- or project-specific catalog entries.
The learn-skills.dev freshness manifest was current at query time. No skills.sh
CLI or authenticated API path was available, so canonical GitHub inspection
was used as the external fallback.

### Candidate inspection and outcome

The local `front-end-skill` entry for `0xgeorgemathew/splithub` is tightly
coupled to that repository's Next.js 15, Tailwind, Framer Motion, and NFC
payment context; its advertised path is not present at the current canonical
`main` revision (`18fda880922c223f23ec434a32dfcc2ba9d32862`), so it was
rejected. `wshobson/agents`' `web-component-design` is present and inspectable
at current commit `a30778f8c4e6b0a87567941b7cca4f534bf642b6` (MIT), and gives
useful React/Vue/Svelte component patterns, but it assumes a component-library
or design-system task rather than general frontend work.

The strongest broad UI candidate was the official
[`anthropics/skills frontend-design`](https://github.com/anthropics/skills/tree/41bbe19d1a1a7eaab5e7bb9050a417e5c6cffc8f/skills/frontend-design),
verified at commit `41bbe19d1a1a7eaab5e7bb9050a417e5c6cffc8f`. Its complete
payload covers visual direction, typography, layout, accessibility, motion,
responsive quality, and self-critique. It is design-focused rather than a
complete frontend engineering stack, and its bundled license terms should be
reviewed before redistribution.

### Query outcome

Recommend `anthropics/skills` `frontend-design` when the request is about
web UI direction or implementation quality; recommend `web-component-design`
only when the request specifically concerns reusable React/Vue/Svelte
components. Ask for the framework, repository, and deployment context before
selecting a more specialized skill. No installation, copying, execution, or
cache mutation occurred. The query confirms that frontend ranking must
separate design guidance from framework- and project-bound implementation
instructions.
