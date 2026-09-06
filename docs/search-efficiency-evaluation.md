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

- No external catalog or skills.sh request was timed.
- No candidate was inspected for task fit or safety as part of this timing run.
- Results depend on this machine's filesystem, cache state, and root set.
