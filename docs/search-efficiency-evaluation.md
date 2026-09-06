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
