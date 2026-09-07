---
status: historical-reference
date: 2026-07-01
updated: 2026-09-06
expires: 2026-10-01
purpose: >
  Preserve the evidence and lessons from the original marketplace survey while
  clearly separating dated measurements from current discovery contracts.
---

# Hub and marketplace research snapshot

This document is a historical research record. It is not product documentation
and its counts, rankings, endpoints, client support, and install commands must be
re-verified before use.

## Snapshot history

The initial 2026-07-01 survey observed a local catalog containing 2,460 records
from seven sources. That number was accurate for that cache, but it was later
copied into README and the shipped methodology as though it described the current
ecosystem.

On 2026-07-15, a local cache generated at `2026-07-14T18:44:13Z` contained
83,772 records. This does not establish a universal catalog size; it demonstrates
why catalog totals belong in timestamped evidence rather than durable guidance.

The same rule applies to the original observations of:

- 42 client logos on an agentskills.io carousel;
- marketplace claims of 21,600 or 270,000 indexed items;
- install counts and featured rankings;
- source-share and concentration percentages;
- HTTP status observations and undocumented endpoints.

These values are retained only as examples of point-in-time evidence. Do not use
them in a recommendation without a new timestamped measurement.

## Contract changes found during re-verification

### Agent Skills conformance

The official `skills-ref` reference validator is the appropriate machine gate
for the shipped `SKILL.md` format. Its result is limited to frontmatter,
naming, and structural conformance; it is not evidence that an agent will
select the skill, follow it correctly, or produce a safe result. Pin its source
to an immutable commit in CI or the manual release gate. The related
`read-properties` and `to-prompt` helpers are optional integration aids, not
additional repository requirements. See the dated study notes
`2026-09-06-NORM-agent-skills-validation-evidence.md` and
`2026-09-05-SYNTHESIS-skill-repo-standards-stack.md` for the evidence boundary.

### skills.sh

The original survey used the undocumented, unauthenticated `/api/search`
endpoint. It still responded during the 2026-07-15 review, but the documented
interface is now `/api/v1/skills/search`, uses a `data` response field, requires
Vercel OIDC authentication, and documents rate limits.

Current contract source: <https://www.skills.sh/docs/api>

For local interactive use, prefer an already-installed provider CLI:

```bash
npx skills find '<query>'
npx skills add <owner/repository> --list
```

These commands must not be treated as permission to bootstrap a package runner.
If the CLI is missing, use the documented read-only API or another fallback;
running `npx --yes` downloads and executes external code and requires explicit
approval.

### GitHub code search

Unauthenticated REST code-search requests return 401. Use authenticated `gh api`,
GitHub browser search, or a web-search fallback. Do not present a plain anonymous
`curl` command as a working API path.

### Client discovery locations

The original table became stale as clients adopted native Agent Skills support.
Current sources should be checked directly:

- Codex: <https://learn.chatgpt.com/docs/build-skills>
- Claude Code: <https://code.claude.com/docs/en/skills>
- Cursor: <https://cursor.com/docs/skills>
- OpenCode: <https://opencode.ai/docs/skills>
- Gemini CLI: <https://geminicli.com/docs/cli/using-agent-skills/>
- GitHub Copilot: <https://docs.github.com/en/copilot/concepts/agents/about-agent-skills>

In particular, Codex uses `.agents/skills` for repository and user skill
discovery; Cursor supports native skills rather than requiring `.cursor/rules`;
and GitHub Copilot supports project and personal Agent Skills locations.

## Distribution state of this repository

Observed on 2026-07-15:

| Check | Result |
|---|---|
| GitHub repository parsed by `npx skills add ... --list` | One skill found |
| Exact `skills.sh` search | No matching indexed result |
| Expected skills.sh detail page | 404 |
| Local client-hub search | No CodeSigils result |
| Direct repository `.agents/skills` discovery | Present through a canonical symlink |

Therefore “installable from a GitHub source” and “discoverable in a catalog” are
separate claims. The repository should advertise only the first until a catalog
actually indexes it.

### Current status (verified 2026-09-06)

The historical July observation above is superseded for present distribution
status: skills.sh now resolves the repository page and the skill detail page,
exposes an install command, and serves the README badge endpoint. This confirms
indexing and install-path visibility only; it does not certify quality or safety.

The current skills.sh API documentation describes authenticated v1 search with
`data` results, fuzzy/semantic search types, pagination, and source/detail
records. An anonymous request returned HTTP 401 on this date, so direct API use
depends on a Vercel OIDC token. The browser/CLI path remains a separate option.

The current learn-skills.dev repository publishes generated JSON/RSS artifacts
and a `data/version.json` manifest. The upstream manifest observed on this date
reported `updatedAt` `2026-09-06T07:53:07Z`, with SHA-256 hashes and timestamps
for its indexes and feed. Its README documents raw GitHub/CDN consumption, but
no stable public search API contract was verified. It is therefore suitable for
structured broad retrieval when the feed and schema are checked at use time,
not as a replacement for canonical source inspection.

### learn-skills.dev data consumption model

The repository is a catalog data publisher, not itself a portable Agent Skill:
it has no root-level `SKILL.md` for automatic client loading. An agent or tool
consuming the clone should read `data/version.json` first, then use the generated
`data/skills_search_index*.json` shards or `data/skills_index.json` for retrieval.
Search-index entries inline `descriptionEn` and identify the source repository,
skill ID, and paths to cached descriptions and payloads. The
`data/skills-md/**/description_en.txt` files are extracted summaries; cached
`SKILL.md` files are available only for the subset fetched by the crawler.

Therefore the safe lookup sequence is:

```text
version.json → generated index/search shards → shortlist
→ canonical repository and exact revision → complete SKILL.md inspection
```

The generated files are useful for fast, structured, agent-friendly retrieval,
but their descriptions and rankings are not quality evidence. Large search
shards should be queried selectively rather than loaded wholesale, and a
missing cached payload should trigger canonical-source inspection rather than
an automatic rejection or recommendation.

### Provider-orchestration evidence

| Question | Evidence | Conclusion |
|---|---|---|
| Does skills.sh provide structured live retrieval? | Documented authenticated v1 search, pagination, and source/detail records | Use directly when authentication or the CLI is available |
| Does learn-skills.dev provide agent-friendly structured data? | Version manifest plus generated `skills.json`, `skills_index.json`, and RSS/JSON feeds | Use as broad retrieval or fallback after verifying freshness and schema |
| Does either provider prove candidate quality? | Both expose ranking/metadata signals; canonical payload inspection remains separate | Treat both as candidate sources, never trust certification |
| Is a fixed provider order always optimal? | skills.sh may be freshest but auth-gated; learn-skills.dev is broad but crawler-dependent | Select the smallest useful provider set per request and record limitations |
| Is a new HTTP implementation language justified? | Local baseline is sub-second; provider/network and inspection costs dominate | No migration without workload and usefulness benchmarks |

## Durable findings

The survey supports a few conclusions that remain useful without carrying its
counts forward:

1. Search local skills before remote catalogs.
2. Inspect index freshness before treating an empty result as authoritative.
3. Prefer documented provider interfaces to observed private endpoints.
4. A successful HTTP response proves reachability, not schema correctness,
   provenance, safety, or task fit.
5. Marketplace metadata is not a substitute for reading the complete candidate
   payload.
6. Installation and skill creation require separate user authorization.
7. **Skill marketplaces are discovery boundaries, not installation bundles.**
   Skills require evaluation before installation. Security badges are supporting
   evidence, not proof. Install counts track popularity, not quality.
   (sources: QASkills.sh 2026-07-15, selftune 2026-03-08)

8. **Critical supply-chain attack vectors exist in skill marketplaces:**
   install count inflation via unauthenticated GET, non-deterministic security
   scanning, silent skill override (same name, different payload), and blind
   bulk updates. These validate cautious read-by-default installation posture.
   (source: Orca Security 2026-05-05)

Those conclusions are implemented in the shipped methodology. Volatile source
details live in supporting references and are re-verified at use time.

## Evidence maintenance

`docs/evidence-urls.json` records the network checks run by scheduled CI. The
validator distinguishes status, JSON syntax, and minimal response shape. It does
not treat URL reachability as proof that a marketplace claim is accurate.
Checks use bounded retries and response reads; only an otherwise-valid canonical
redirect may be auto-corrected. Status, schema, size, and reachability drift
remains a failure for human review.

The current monitor checks the 13 manifest sources concurrently once per week.
That cadence limits external traffic while the shipped workflow performs use-time
freshness checks for volatile catalogs. `last_verified` records the monitor's
observation date; it does not certify that a provider remains current between
observations.

When updating this document:

1. record the observation date and method;
2. distinguish provider claims from independently measured values;
3. update the evidence manifest when a referenced contract changes;
4. keep volatile totals out of README and the main `SKILL.md`;
5. preserve older observations as historical rows rather than silently rewriting
   what was measured.

## Re-verification log

| Date | Observation | Outcome |
|---|---|---|
| 2026-07-01 | Initial local catalog survey | 2,460 records in that cache |
| 2026-07-04 | Same cache checked again | Still 2,460; already stale |
| 2026-07-15 | Current local cache inspected | 83,772 records; static totals removed from shipped guidance |
| 2026-07-15 | skills.sh contract checked | Documented v1 API requires authentication; legacy endpoint removed from guidance |
| 2026-07-15 | Client documentation checked | Codex, Cursor, and Copilot placement claims corrected |
| 2026-07-15 | Repository discovery checked | Direct installer recognizes repository; catalogs do not yet index it |
| 2026-08-21 | Added supply-chain risk findings from Orca Security research; validated SKILL.md tension analysis | PASS |
| 2026-09-06 | Reconciled Agent Skills format guidance with pinned `skills-ref`; clarified skills.sh results as untrusted discovery pointers and documented badge/indexing limits | PASS |
| 2026-09-06 | skills.sh detail page, repository page, install command, and badge endpoint verified for `codesigils/skill-discovery` | Indexed; badge returned SVG; install path confirmed |
| 2026-09-06 | skills.sh API docs and anonymous search checked; learn-skills.dev `data/version.json` and README checked | API auth/schema confirmed; feed artifacts and freshness manifest available; no stable learn-skills search API verified |
| 2026-09-06 | Inspected learn-skills.dev search shards, `description_en.txt`, cached `SKILL.md`, and `version.json` consumption paths | Generated catalog data is agent-readable but not an auto-loaded skill; canonical payload review remains required |
| 2026-09-07 | Compared broad `q=python` retrieval with phrase queries | Current generated index contained 756 `python` matches; `python coding`, `python development`, and `python best practices` returned 12, 10, and 16 lexical matches. Earlier three-item reports were bounded shortlists, not catalog totals. Use local search → learn-skills.dev broad retrieval → skills.sh/other providers → canonical inspection → recommendation. No stable public search API contract was verified. |

## Sources

| Source | URL | Method | Notes |
|---|---|---|---|
| skills.sh API documentation | https://www.skills.sh/docs/api | docs | v1 endpoints, authentication, pagination, response fields; checked 2026-09-06 |
| skills.sh skill detail | https://www.skills.sh/codesigils/skill-discovery/skill-discovery | tested | Indexed detail page and install command; checked 2026-09-06 |
| learn-skills.dev repository | https://github.com/NeverSight/learn-skills.dev | docs | README documents generated feeds and raw/CDN consumption; checked 2026-09-06 |
| learn-skills.dev version manifest | https://raw.githubusercontent.com/NeverSight/learn-skills.dev/main/data/version.json | tested | Freshness timestamps, file hashes, and generated artifact inventory; checked 2026-09-06 |
| learn-skills.dev data README | https://raw.githubusercontent.com/NeverSight/learn-skills.dev/main/README.md | docs | Documents generated indexes, descriptions, feeds, and raw/CDN consumption; checked 2026-09-06 |
