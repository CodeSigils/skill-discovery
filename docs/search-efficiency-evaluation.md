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

## Real-task fit pilot protocol (started 2026-09-06)

The next evidence stage uses actual discovery requests rather than maintainer-
invented fixtures. For each request, record the request and constraints,
provider paths, retrieval time, inspection time, candidate usefulness (0–3),
whether the user accepted or rejected the recommendation, and any false
positive, stale-source, or missing-candidate finding. A usefulness score means:

| Score | Meaning |
|---:|---|
| 0 | no usable candidate or unsafe/misleading result |
| 1 | technically related but not actionable |
| 2 | actionable with caveats or adaptation |
| 3 | direct fit and actionable |

The first two real requests in this session are recorded below. User
acceptance was not explicitly stated, so it remains `unknown`; the continued
conversation is not treated as a success rating.

| Request | Retrieval | Inspection outcome | Usefulness | User acceptance |
|---|---:|---|---:|---|
| Learn agent concepts | 211–215 ms | No canonical direct fit; official standard docs offered conditionally | 1 | unknown |
| Find a frontend skill | 209–214 ms | Canonical `frontend-design` recommended conditionally; component skill as narrower alternative | 2 | unknown |

This is an observational start, not enough evidence to implement ranking,
provider orchestration, caching, or a new language. Collect at least five more
requests with explicit user ratings before changing the implementation.

## Additional real-task observations (2026-09-07)

Four follow-up requests were run to expand the pilot. These are discovery
observations, not installation or behavior tests; user acceptance remains
`unknown` until the requester rates each result.

| Request | Query | Matches | Retrieval | Candidate outcome | Provisional fit |
|---|---|---:|---:|---|---:|
| Python code review | `python review` | 13 | 217 ms | Local `py-review` is a direct Codex-oriented router with complete payload inspected | 3 |
| Go best practices | `go best practices` | 50 | 215 ms | `effective-go` matches the task, but its referenced files were absent from the catalog cache; canonical verification required | 2 |
| Note taking | `note taking` | 6 | 212 ms | Results were mostly provider- or workflow-specific; prior conditional `planning-with-files` remains the portable option | 2 |
| Novel writing | `novel writing` | 7 | 215 ms | `novel-writing-techniques` is technique-specific and its referenced files were not available in the cache; prior canonical alternative remains stronger | 2 |

The Python request is the only direct local fit. The other three require
conditional handling because of missing references, provider specificity, or
incomplete coverage. No candidate was installed, copied, executed, or used
with real personal data.

These four observations bring the pilot to six requests, but none has an
explicit acceptance rating yet. Do not treat provisional fit scores as user
success evidence or use them to justify implementation changes.

## Real-task observation: mobile app design (2026-09-07)

Request: “design mobile apps.” The need was interpreted as mobile UI/UX
guidance with no framework, platform, backend, or design-service assumption.
Installation and execution were not authorized.

| Query | Matches | Retrieval |
|---|---:|---:|
| `design mobile apps` | 4 | 213 ms |
| `mobile app design` | 19 | 209 ms |
| `mobile UI` | 98 | 211 ms |
| `ios android design` | 0 | 212 ms |

The exact phrase was precise but sparse; `mobile UI` was noisy. Local results
were primarily generated learn-skills.dev catalog entries. The strongest
candidate, `designed-by-ai/skills` `design-mobile-apps`, is present at
canonical commit `4e7e900773f213b2165dfb95d81e8e1d677a6af3` (MIT), but requires
`SLEEK_API_KEY`, sends requests to an external design service, and can create
remote projects. It is therefore a conditional fit only for users explicitly
choosing Sleek and authorizing that network/service workflow.

`mobile-app-ui-design` had a missing canonical path at the current repository
revision and was inspection-blocked. `mobile-app-design-mastery` is
Claude/project-oriented despite useful platform heuristics, so it is not a
portable default recommendation.

### Query outcome

No unconditional direct-fit mobile-app design skill passed. Recommend the
Sleek skill only when the user names Sleek and approves its key/network and
remote-project effects; otherwise refine the request with platform (iOS,
Android, Flutter, React Native, or web prototype) and provide a narrower
read-only candidate search. Provisional fit: 1/3. User acceptance: `unknown`.
No installation, copying, execution, or external project creation occurred.

## Real-task observations: trending selections (2026-09-07)

The requester selected these four topics from learn-skills.dev's trending
view. Trending was treated as a retrieval hint, not as evidence of quality,
security, or maintenance. Installation and execution were not authorized.

| Request | Query | Matches | Retrieval |
|---|---|---:|---:|
| Next.js on Cloudflare | `next js cloudflare` | 0 | 210 ms |
| Postgres safety | `postgres safety` | 1 | 210 ms |
| Brainstorming | `brainstorming` | 1,380 | 209 ms |
| UX designer | `ux designer` | 131 | 209 ms |

### Candidate review and outcomes

`cloudflare/skills` [`nextjs-on-cloudflare`](https://github.com/cloudflare/skills/tree/d924cd8f59e75e08fd3dd52843bb2776de35c77e/skills/nextjs-on-cloudflare)
was verified at commit `d924cd8f59e75e08fd3dd52843bb2776de35c77e`. It is a
direct fit for Next.js on Cloudflare Workers, but setup/deployment may invoke
an upstream installer and requires checking current vinext compatibility;
classify as conditional until the user names a deployment action.

For Postgres safety, the strongest canonical candidate was Neon’s
[`postgres-best-practices`](https://github.com/neondatabase/postgres-skills/tree/27fe45e0f71ea89a6eaf9ea4d2e4068957c81c26/skills/postgres-best-practices)
at commit `27fe45e0f71ea89a6eaf9ea4d2e4068957c81c26`. Its complete payload
links explicit security/roles, authentication, SSL, RLS, backup, transaction,
and connection-pooling references, all present at that revision. It is a
conditional-to-direct fit depending on whether “safety” means database design
review or operational changes; no mutation should be implied.
The live [skills.sh listing](https://www.skills.sh/neondatabase/postgres-skills/postgres-best-practices)
reported 1.2K installs on 2026-09-07 (the requester reported an earlier 1.1K
snapshot). This is popularity context only and is not evidence of safety or
quality.

The requester also supplied the official
[`planetscale-mcp-agent-operating-model`](https://www.learn-skills.dev/en/skills/planetscale/skills/planetscale-mcp-agent-operating-model)
listing as an alternative. Direct inspection of
[`planetscale/skills`](https://github.com/planetscale/skills/tree/999045cfbad79222f38a99599eb96bc736feabee/planetscale-mcp-agent-operating-model)
verified the complete payload at commit
`999045cfbad79222f38a99599eb96bc736feabee` (MIT). It is a conditional fit for
PlanetScale MCP work: it clearly separates insights-only access from full MCP,
forbids production writes, credential rotation, role changes, and direct
deploys by default, but it still describes networked MCP and review-workflow
operations. The catalog metadata reports 1,128 installs and `isOfficial: true`;
the live learn-skills page returned HTTP 429, so those marketplace fields remain
secondary evidence rather than a safety claim.

For brainstorming, the canonical [`iurysza/agent-skills` brainstorming
skill](https://github.com/iurysza/agent-skills/tree/f5d5de34a8ef4437ea705dcbdb80f23ed83e192e/skills/brainstorming)
was inspected at commit `f5d5de34a8ef4437ea705dcbdb80f23ed83e192e`. It is a
portable planning skill that clarifies context, compares approaches, and
captures an approved design; it is a direct fit for ideation before
implementation, not for ordinary coding.

For UX design, the canonical
[`mobile-ui-ux-designer`](https://github.com/mdrmuhaimin/agentic-skills/tree/c7c4e9fdfbcd4d8ed39bde5231813e38d83eb019/codex/mobile-ui-ux-designer)
payload was inspected at commit `c7c4e9fdfbcd4d8ed39bde5231813e38d83eb019`
(MIT). It covers mobile UX research, platform conventions, accessibility,
states, tokens, and handoff, but is 913 lines with no bundled reference tree;
classify as conditional and confirm the target platform and output depth first.

### Query outcome

The four provisional fits are: Cloudflare Next.js (conditional direct), Neon
Postgres practices (conditional direct), brainstorming (direct), and mobile UX
(conditional). The exact query precision varied sharply: brainstorming and UX
were noisy, while the two infrastructure queries under-retrieved locally and
needed canonical/web fallback. Provisional usefulness scores are 2, 2, 3, and
2 respectively; user acceptance is `unknown`. No installation, copying,
execution, deployment, database mutation, or external project creation
occurred.

The authorized synthetic smoke test was partial: the declared Python/Playwright
dependencies and Chromium installed in an isolated `/tmp` directory, but the
renderer did not produce a PNG within a bounded retry because the template waits
for its remote `esm.sh` module. This confirms the documented runtime network
dependency; it is not evidence that generated diagrams fail generally. No
credentials, repository files, or external services were used.

A follow-up retry served the same isolated template over localhost HTTP to rule
out a `file://` origin restriction. It also failed to produce a PNG within the
bounded timeout. The CDN endpoint itself returned HTTP 200, so the smoke test
remains `partial` with module-readiness/browser integration unresolved rather
than a simple connectivity failure.

Browser diagnostics showed a resource 404 while loading the template; after
10 seconds `window.__moduleReady` and `window.renderDiagram` were still
undefined. The renderer therefore cannot reach its own readiness signal in this
environment, which is a concrete integration failure rather than merely a
slow request.

A final browser trace identified the failing import precisely:
`https://esm.sh/@braintree/sanitize-url@6.0.2/es2022/dist/constants.mjs` returned
404 and the request was aborted. This dependency-level failure prevents the
Excalidraw module from defining its readiness signal in the tested renderer.

## Canonical Claude Code frontend-design check (2026-09-07)

The canonical [`anthropics/claude-code` frontend-design plugin](https://github.com/anthropics/claude-code/tree/ab9b2cf7bb9e4f98ff264c07a22e46d83c29c558/plugins/frontend-design)
was checked at commit `ab9b2cf7bb9e4f98ff264c07a22e46d83c29c558`. The skill is
located at `plugins/frontend-design/skills/frontend-design/SKILL.md`, alongside
Claude plugin metadata and a README. Its 9,390-byte payload has the same
SHA-256 as the previously reviewed `anthropics/skills` frontend-design source,
so there is no substantive instruction drift.

The plugin is Claude Code-specific and is not a drop-in Codex installation
without adapting the plugin wrapper. More importantly, the skill frontmatter
says `license: Complete terms in LICENSE.txt`, but the current plugin tree does
not contain `LICENSE.txt`; the standalone `anthropics/skills` distribution does.
Treat the Claude Code plugin as conditionally portable and resolve the license
file before redistribution. No installation, execution, or code generation
was performed.

## Real-task observations: additional trending selections (2026-09-07)

The requester selected three more topics from learn-skills.dev's trending view.
Trend status was treated as a retrieval hint only, not as evidence of quality,
safety, or maintenance. Installation and execution were not authorized.

| Request | Query | Matches | Retrieval |
|---|---|---:|---:|
| Sprint planning | `sprint planning` | 356 | 209 ms |
| Forge idea | `forge idea` | 0 | 206 ms |
| AI video generation | `ai video generation` | 207 | 210 ms |

### Candidate review and outcomes

The local `scrum-master` result was a generated catalog entry whose apparent
source repository was unavailable for canonical verification; it was therefore
inspection-blocked rather than recommended. The canonical
[`forge-shape`](https://github.com/mgratzer/forge/tree/05afc6a8852d98cdd7450aad7a1d3298c0ede3fa/skills/forge-shape)
skill (commit `05afc6a8852d98cdd7450aad7a1d3298c0ede3fa`) is a conditional fit:
it shapes a vague idea through repository investigation and one-at-a-time
questions, but is GitHub-centric and includes issue-workflow integration.

For AI video generation, the local `1nfsh` entries were not present at the
current canonical `1nfsh/skills` revision (`becc25649700d5457772a00e5143e28ccf9e5afa`);
only related prompting and marketing-video skills exist there. The cached
`ai-video-generation` payload requires an `inference.sh` CLI, login, network,
and paid/model-provider accounts, so it is inspection-blocked and
service-dependent rather than a portable recommendation. The related
`video-prompting-guide` is a partial, read-only alternative for prompt writing
only.

### Query outcome

No unconditional direct fit passed. Sprint planning needs a verified Scrum or
team-planning source; “forge idea” has a conditional match in `forge-shape`
when GitHub issue workflows are desired; AI video generation needs an explicit
provider, budget, and authorization before any service-backed skill can be
considered. Static provisional fit scores were 1, 2, and 1 respectively; the
requester later recorded user usefulness as accepted with `3/3` for
each of the three topics. The requester also described them as most popular on
skills.sh; that popularity claim is user-provided and was not used as trust
evidence. No installation, execution, login, media generation,
issue creation, or external mutation occurred.

## Real-task observations: BMAD Method selections (2026-09-07)

The requester asked for two additional pilot candidates selected from
[`bmad-code-org/bmad-method`](https://github.com/bmad-code-org/bmad-method),
whose current `main` revision is
`abe4eb1bce919c9d22cd18b3519353d5824c4b75`. Selection was based on direct
task coverage, not repository popularity. Installation and execution were not
authorized.

| Candidate | Scope and inspection | Agent fit | User usefulness | Acceptance |
|---|---|---:|---:|---|
| `bmad-sprint-planning` | 62-line payload; readiness gate, deterministic sprint-status generation, validation and repair paths | 2 | pending | unknown |
| `bmad-forge-idea` | 107-line payload; one-at-a-time questioning, pressure testing, optional brief handoff | 3 | pending | unknown |

Both candidates have valid frontmatter and clear triggers. Their workflows
reference additional BMAD project files and scripts, so they are portable only
when used inside a BMAD-configured project; they are not drop-in generic
planning utilities. No scripts, issue operations, file writes, or external
service calls were performed.

Agent fit is the maintainer's static assessment, not a user-success claim:
`bmad-sprint-planning` loses a point because it requires a BMAD-configured
project; `bmad-forge-idea` directly matches idea pressure-testing. User
usefulness and acceptance remain unmeasured until the skills are used in a
real task.

## Source checks: Browser Use, Claude Code simplify, and templates (2026-09-07)

### Browser Use

The canonical [`browser-use/browser-use`](https://github.com/browser-use/browser-use/tree/e25ab65e699af3031a1f2d348526de2844be0e89/skills)
repository is MIT-licensed and was inspected at commit
`e25ab65e699af3031a1f2d348526de2844be0e89`. It ships `browser-use`, `open-source`,
`cloud`, `qa`, `remote-browser`, and related skills. `browser-use` is a direct
fit for interactive browser automation, but it can attach to a browser,
navigate logged-in sessions, access network resources, and install a CLI via
`uv`; it is therefore conditional on explicit browser, account, and network
authorization. `qa` is a separate cloud-browser testing workflow with API-key
and billing implications. No browser, tunnel, CLI, or cloud session was
started.

### Claude Code simplify

[`anthropics/claude-code`](https://github.com/anthropics/claude-code/tree/ab9b2cf7bb9e4f98ff264c07a22e46d83c29c558/plugins/pr-review-toolkit/agents)
contains `code-simplifier.md` at commit
`ab9b2cf7bb9e4f98ff264c07a22e46d83c29c558`, not a `SKILL.md` named
`simplify`. It is a Claude agent configured to refine recently modified code,
preserve behavior, and use project standards; its metadata selects the Opus
model. It is useful for Claude Code's native agent workflow but is not a
portable Agent Skills payload for Codex without adaptation.

### claude-code-templates code reviewer

The published `claude-code-templates` package was checked at npm version
`1.29.4` (MIT). Its tarball contains the CLI and component infrastructure but
not a static `development/code-reviewer` or `development-tools/code-reviewer`
payload; the CLI resolves components dynamically from its catalog/GitHub when
run. This makes the requested component inspection-blocked from the package
alone and couples installation to `npx`, network access, and Claude's
`.claude/` layout. The package README documents the installer command, but
that is not equivalent to reviewing the exact agent source. No `npx` command
was run and no files were installed.

### Outcome

Recommend Browser Use's `browser-use` only for an explicitly authorized
interactive browser task; treat Claude Code `code-simplifier` as a native
Claude agent rather than a portable skill; and do not recommend the
`claude-code-templates` code reviewer until its exact catalog payload and
revision are available for inspection. Popularity, package availability, and
installer documentation are not substitutes for source review.

## Source check: Antigravity Awesome Skills (2026-09-07)

The supplied `antigravity-awesome-skills` name resolves to the renamed
[`sickn33/agentic-awesome-skills`](https://github.com/sickn33/agentic-awesome-skills)
repository. At commit `b1aebac60a88dffa0f5723cb3816f22cc0af6b13`, GitHub reported
46,083 stars, 6,737 forks, MIT licensing, and release `v16.9.1`; the README
registry header reports 2,113 catalog skills. The earlier claim of 22,000+
stars, 3,800+ forks, and v7.3.0 is stale.

The repository is broad and actively maintained, with a local MCP/catalog,
plugins, bundles, installers, and many `SKILL.md` files. A raw tree count is
not a unique-skill count (the current tree contains 6,648 `SKILL.md` paths,
including variants and nested agents), so “most comprehensive skill
collection” cannot be established from file count, stars, forks, or the
README's catalog total. The README itself says the catalog does not certify
suitability, compatibility, or safety.

For `skill-discovery`, classify it as a high-coverage candidate source and
assessment surface, not an authority or trust score. Its strongest value is
structured local search, exact IDs, manifests, and inspectable evidence; its
main risks are breadth/noise, duplicates, client-specific bundles, and the
additional installer/MCP control plane. Always pin a selected skill to its
source revision and inspect the individual payload before installation.
No installation, MCP setup, or candidate execution occurred.

## Source audit: unicodeveloper/shannon (2026-09-07)

The canonical [`unicodeveloper/shannon`](https://github.com/unicodeveloper/shannon/tree/6a97124bee816c7cc76c6e17bb2b0fe8c0eae032)
repository was inspected at commit `6a97124bee816c7cc76c6e17bb2b0fe8c0eae032`.
GitHub reported 50 stars, 7 forks, no declared repository license, and a
README claiming an AGPL-3.0 skill license. The repository contains a root
`SKILL.md`, README, and scripts, and points to the upstream
`KeygraphHQ/shannon` framework.

This is not a normal read-only security-review skill. Its complete payload
explicitly executes real exploits, clones or updates a framework, launches
Docker containers, reads source code, may use target credentials, and scans
live URLs. It requires explicit written authorization, a non-production target,
Docker, Git, and an Anthropic or cloud-provider credential. The skill reports a
96.15% XBOW exploit-success claim, but that benchmark assertion was not
independently validated during this inspection.

Classify Shannon as **high-risk / conditional**: potentially useful for an
authorized, isolated pentest of an owned staging target, but incompatible with
the default static, read-only discovery boundary. Never recommend it merely
because it is “popular,” and never install, authenticate, clone, or execute it
as part of discovery. Any future behavioral evaluation would require explicit
scope, synthetic fixtures where possible, isolated infrastructure, credential
handling, and a separate authorization gate.

## Source audit: PlanetScale Database Skills description (2026-09-07)

The supplied description was compared with the canonical
[`planetscale/skills`](https://github.com/planetscale/skills/tree/999045cfbad79222f38a99599eb96bc736feabee)
pack at commit `999045cfbad79222f38a99599eb96bc736feabee` (MIT). Several
claims need correction:

- `planetscale/agent-skill` is not the current repository. The documented
  Skills CLI command is `npx skills add planetscale/skills -g -y`; the setup
  script and manual sibling-directory routes are also supported.
- PlanetScale is not limited to a single “MySQL-compatible” workflow in this
  pack. The skills explicitly cover both Vitess and Postgres, with separate
  safety reviews and operating guidance.
- Branches, PRs, and deploy requests are the reviewable path, but “one branch
  for every feature” and “never touch production schema directly” are useful
  policy defaults, not universal platform guarantees. The pack permits
  development-branch DDL and review-gated deploy requests; direct production
  writes/deploys remain forbidden by default.
- The sample `2ms vs 8s at 10M rows` query estimate is not supported by an
  inspected benchmark. Keep the index and projection advice as a hypothesis to
  validate with `EXPLAIN`, representative data, and measured Insights results.

The pack is a strong conditional recommendation for database safety and
reviewable schema workflows. Its most valuable behavior is evidence-backed
assessment, explicit operation classes, rollback/approval gates, and
read-back verification—not automatic scaling guarantees. It requires a
PlanetScale account/CLI or MCP access for live operations and can create
development branches, PRs, and deploy requests when authorized by its safety
model. No CLI authentication, database access, mutation, or installation was
performed during this audit.

## Source audit: Excalidraw diagram skill (2026-09-07)

The supplied [`coleam00/excalidraw-diagram-skill`](https://github.com/coleam00/excalidraw-diagram-skill/tree/8646fcc9f74f38539c6cdb4c969723336a96ddcd)
repository was inspected at commit `8646fcc9f74f38539c6cdb4c969723336a96ddcd`.
GitHub reported 4,705 stars, 533 forks, and no declared repository license.
The inspected tree is small and self-contained: `SKILL.md`, a color palette,
element templates, a JSON-format reference, and a Python/Playwright renderer.

The requested examples are consistent with the payload: it explicitly covers
workflow, architecture, and sequence diagrams, and requires technical diagrams
to use researched event names, formats, or API methods and concrete evidence
artifacts. The “self-validation loop” is also real: the instructions require
rendering to PNG, viewing the result, checking clipping/overlap/bindings and
composition, fixing the JSON, and repeating until it is presentable. The
palette file is a useful single source of guidance for generated colors and
brand styles, but changing it is not an automatic runtime theme mechanism; the
agent must read and apply it for each generation.

Important qualifications for discovery:

- The renderer performs only basic structural checks (`type`, a non-empty
  `elements` array, and JSON parsing). Most quality gates are visual and human
  or agent inspection, not schema-complete validation.
- Rendering requires Python 3.11+, `uv`, Playwright, and a locally installed
  Chromium. The HTML renderer imports `@excalidraw/excalidraw` from
  `https://esm.sh` at runtime, so a render is not fully offline or hermetic.
- The normal workflow writes `.excalidraw` and PNG artifacts and executes a
  browser process. It does not request credentials or perform target-system
  mutations in the inspected files, but generated diagrams can still contain
  user-provided sensitive architecture details and should receive a content
  review before publication.
- The README emphasizes Claude Code’s `.claude/skills/` layout, although its
  root `SKILL.md` follows the common agent-skill shape. Treat Codex/other-agent
  portability as conditional on the host’s skill loader and path conventions.

Classify this as a **useful, conditional recommendation** for requests that
benefit from a durable architecture or workflow artifact. Its strongest value
is the combination of visual design guidance, evidence requirements, and an
iterative rendered QA loop—not popularity (4,705 stars) or the claim that the
output is automatically publishable. Before recommending installation, disclose
the unlicensed repository, runtime network dependency, browser setup, output
side effects, and the need for human review of both accuracy and sensitive
content. No installation, dependency setup, renderer execution, or diagram
generation was performed during this audit.

## Source audit: MCP Market skills leaderboard (2026-09-07)

The supplied [MCP Market skills leaderboard](https://mcpmarket.com/tools/skills/leaderboard)
is a useful additional candidate source. The public page labels itself “Top
Agent Skills” and lists up to 100 entries with category labels and compact
counts (for example, the listed diagram maker is ranked #8). It advertises
skills for Claude, Claude Code, ChatGPT, and Codex, but the page is a rendered
directory rather than a canonical source repository for the entries.

The displayed counts and ordering are not independently interpretable as user
ratings. The page does not disclose, in the inspected public content, whether
they represent unique users, views, installs, downloads, votes, or an
algorithmic popularity score; it also does not provide a review sample,
timestamp policy, identity/anti-abuse controls, or a reproducible ranking
formula. Therefore the user-rating rationale cannot be verified from this
source. Counts and rank should be treated as discovery signals only, not as
quality, safety, compatibility, maintenance, or user-satisfaction evidence.

For `skill-discovery`, use MCP Market as a broad retrieval fallback after local
search and stronger provider sources. For any candidate, resolve the linked
canonical repository or package, pin an exact revision, inspect the complete
`SKILL.md` and referenced files, check license/provenance/maintenance, and
evaluate permissions and side effects before making a recommendation. Do not
install from a leaderboard entry solely because it is highly ranked, and do not
claim its popularity is validated without an explicit methodology. No account,
installation, or candidate execution was performed during this inspection.

## Source audit: Addy Osmani agent-skills (2026-09-07)

The additional canonical source is [`addyosmani/agent-skills`](https://github.com/addyosmani/agent-skills/tree/48cb1168aeaaa70dfcbbf709eddfa2a8ed8129a)
at commit `48cb1168aeaaa70dfcbbf709eddfa2a8ed8129a`. GitHub reported 92,642 stars,
9,881 forks, MIT licensing, and a recent push on 2026-09-06. The repository is
a broad engineering collection, not a diagram-specific skill: its relevant
`frontend-ui-engineering` skill covers production UI, accessibility, responsive
layout, design systems, and visual quality, while no architecture or
Excalidraw skill was present in the inspected tree.

The collection is a useful conditional alternative when “diagram” actually
means designing or implementing a user interface. It is not a substitute for
the Excalidraw skill when the requested artifact is an architecture, workflow,
or sequence diagram. Its root `skills/<name>/SKILL.md` layout and MIT license
are favorable for portability, but the collection also includes cross-skill
references and client/plugin setup paths; inspect the selected skill and its
referenced files rather than recommending the whole repository by popularity.
No installation or execution occurred.

## Fresh-catalog pilot: first-indication policy (2026-09-07)

After updating the local `learn-skills.dev` checkout to upstream commit
`345807d4f52`, three representative requests were rerun. The catalog reported
`updatedAt=2026-09-07T03:55:10.137Z` and 113,458 entries. Measurements are
retrieval signals, not a benchmark of agent reasoning or user satisfaction.

| Request | Local matches / retrieval | learn-skills matches / matching | Assessment outcome |
|---|---:|---:|---|
| Create an architecture diagram | 9 / 246 ms | 19 / 49 ms | Excalidraw is a conditional fit after canonical inspection; catalog broadens alternatives |
| Python code review | 18 / 238 ms | 7 / 49 ms | Local `py-review` remains the strongest direct fit; external results are alternatives |
| Learn agent concepts | 1 / 235 ms | 0 / 51 ms | No direct catalog fit; retain official documentation and conditional skills as fallback |

The refreshed index improves freshness confidence and provides useful
candidate leads, but it does not replace local-first search: the Python direct
fit was local-only, while the catalog missed the agent-concepts request. The
architecture query also shows why catalog ranking should prioritize inspection,
not certification. No installation, copying, execution, or external mutation
occurred.

### Pilot decision

The first-indication policy is working as intended. Keep learn-skills.dev as the
first broad external signal after local search, preserve canonical inspection,
and do not add a provider adapter, cache, ranking score, or new language yet.
Continue collecting explicit user acceptance and task outcomes before changing
the implementation.

## Source audit: proyecto26 system-design architecture diagram (2026-09-07)

The canonical [`proyecto26/system-design-skills`](https://github.com/proyecto26/system-design-skills/tree/a70772efb956e8c9b78ef5b7538dee00cc3b9263)
repository was inspected at commit `a70772efb956e8c9b78ef5b7538dee00cc3b9263`.
GitHub reports MIT licensing, 69 stars, and a last push on 2026-06-02. The
`skills/architecture-diagram/` payload includes `SKILL.md`, a complete HTML/SVG
template, and design/interactive references.

This is a stronger architecture-diagram candidate than the tested Excalidraw
renderer. Its template is self-contained HTML with inline SVG/CSS and a system
font stack, so the diagram itself renders offline with no rendering dependency.
PNG/PDF export is optional and uses two pinned jsDelivr scripts with SRI hashes;
the base diagram remains usable if those CDN scripts are unavailable. The
instructions specify component semantics, trust boundaries, arrow order,
spacing, and a bounded 8–15 component target, making the output reviewable.

Qualifications:

- The repository describes the skill as part of a Claude Code `system-design`
  plugin. Treat portability as conditional until the host loader and whole-plugin
  references are verified.
- Export buttons require network-fetched CDN scripts (and clipboard export may
  require a secure context); this is optional, not an offline guarantee for
  every toolbar action.
- The repository is less recently maintained than other shortlisted candidates.
  Pin the reviewed revision and re-check freshness before use.
- The interactive reference can add JavaScript controls and optional prompt
  transport, so inspect that path separately before enabling it. No interactive
  transport, installation, or external mutation was performed.

Classify this as a **conditional-to-strong recommendation** for static
architecture diagrams when an HTML/SVG artifact is acceptable and the user can
accept Claude/plugin adaptation. Prefer it over the Excalidraw candidate for an
offline-first workflow; use AWS’s architecture skill instead when the request
is specifically AWS infrastructure. No runtime smoke test was run because this
is a source-template evaluation rather than an installed candidate.
