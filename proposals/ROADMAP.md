# Roadmap and implementation record

This file contains active maintenance decisions and a compact implementation
record. It is not a changelog; release notes come from commit history. Remove
completed detail when it no longer explains a current constraint.

## Maintenance discipline

When behavior, CI, or repository structure changes:

1. Update the affected README workflow, payload, validation, or layout section.
2. Update the relevant shipped reference when the agent needs new guidance.
3. Update dated evidence only after checking the provider's current contract.
4. Record the decision here in one concise dated entry.
5. Run the documented validation gate in `CONTRIBUTING.md`.

The shipped runtime boundary is `skills/skill-discovery/`. Repository tooling,
research, CI, and roadmap files remain outside the payload.

## Vision: agent-integrated discovery orchestration

`skill-discovery` interprets the user's request, searches the best available
local and external sources, filters candidates against constraints, inspects the
strongest matches, and presents an evidence-backed recommendation to the agent
and user before any installation.

The project is an assessment and decision layer over catalogs such as
skills.sh and learn-skills.dev, not a competing catalog. Its value is the
translation from an ambiguous need to a bounded, provenance-aware recommendation
with explicit compatibility, capability, and authorization boundaries.

```text
request → need and constraints → source search → candidate filtering
→ evidence inspection → recommendation → explicit installation decision
```

The current implementation delivers this vision as a static, read-only skill.
Future orchestration work must preserve these non-goals: no popularity-based
trust score, automatic installation, or default execution of untrusted skills;
no runtime service or catalog duplication without measured user need.

### Cross-cutting invariants

These are planning constraints, not new runtime phases:

- **Human decision boundary:** the agent gathers evidence and prepares a
  recommendation, but the user decides when requirements are ambiguous,
  evidence conflicts, a candidate is conditional or stale, or installation
  would mutate files, use credentials, access the network, or send messages.
- **File-swamp avoidance:** keep the runtime payload to one focused `SKILL.md`
  plus targeted references; load detail progressively; keep research, fixtures,
  catalogs, and CI outside the payload; enforce file/byte/depth caps; and avoid
  generated indexes unless a concrete consumer requires one.

Any future provider or assessment work must preserve both invariants. They do
not authorize changes to the current workflow without a measured user need,
fixture, and reviewable implementation boundary.

## Active deferred decisions

### Official format conformance gate

Implemented: run the official `skills-ref validate` command from CI and the
tagged release workflow against every shipped skill, pinned to an immutable
`agentskills` commit. Keep the
repository validator as a supplementary check for local links, budgets, and
documentation. Add offline fixtures for validator failures, marketplace
authentication limits, stale/unknown catalog freshness, provenance mismatch,
and source-revision changes. Do not add `read-properties` or `to-prompt` until
the repository has a real inventory or host-integration consumer.

### Markdown style linter

Deferred. The documentation validator already checks fences, relative links,
frontmatter, expiry, and payload integrity. Reconsider if formatting defects
become a recurring review problem; do not add a second style policy without a
demonstrated failure pattern.

### Pre-commit hooks

Deferred. CI is the authoritative gate and local hooks would add setup friction
for the solo-maintained project. Reconsider if contributor volume or repeated
local-only failures justify the maintenance cost.

### Solo evaluation branch policy

Active 2026-09-07. While the project is a solo-maintained candidate under
heavy evaluation, `main` keeps signed-commit and linear-history protection but
does not require pull-request checks or administrator enforcement. CI still
runs on every push and pull request. Use focused PRs for risky, externally
reviewed, or collaborative changes. Re-enable required PR checks before the
repository accepts regular external contributions or needs a formal release
review.

### Runtime execution harness for third-party skills

Not planned. Discovery remains static by default. Behavior checks require
explicit authorization, synthetic fixtures, isolation, and no credentials or
network. The repository maintains offline report-contract fixtures instead of
executing untrusted skills.

### Registry integrations

Not planned. Provider APIs and marketplace rankings are volatile and add
external maintenance burden. Use documented, read-only provider interfaces at
query time; keep current contracts in the shipped catalog reference and dated
observations in `docs/hub-marketplace-research.md`.

### Future gateway implementation language

Deferred. Do not migrate the current Markdown/Python skill and maintainer tools
to Go for presumed HTTP performance. Search latency is dominated by provider
network latency, authentication, rate limits, candidate inspection, and agent
reasoning rather than local request code. Reconsider Go only for a future
assessment gateway after a measured workload demonstrates a need for high
concurrency, a long-running service, a standalone binary, or stricter runtime
resource isolation. Any migration requires a benchmark, a named owner, and an
explicit maintenance-cost justification.

### Search-efficiency guidance

When real usage shows that discovery is too slow, optimize in this order:

1. Use [`learn-skills.dev`](https://www.learn-skills.dev) for broad retrieval.
2. Keep local-first search.
3. Parallelize independent provider lookups.
4. Cache only timestamped, provenance-qualified metadata.
5. Measure search latency and candidate usefulness.
6. Consider Go only if benchmarks show the current implementation is the
   actual bottleneck.

These are evaluation priorities, not a mandate to add a catalog, cache, or
second implementation now.

### Python-source evaluation

Completed 2026-09-07. For Python coding requests, prefer the local `py-review`
router for focused review routing and use `ludo-technologies/python-best-practices`
as supplementary general standards when its contextual caveats fit. The
`jasong98/code-skills` Python skill is conditional because its repository has no
declared license, tests, or CI, and its Chinese-only, prescriptive guidance is
less portable. Do not hard-code provider candidates into runtime ranking;
re-check revision, license, toolchain, and project fit at query time.

### Diagram-source evaluation

Completed 2026-09-07. For diagram requests, use catalog metadata only to find
candidates, then inspect and smoke-test the canonical source. Current evidence
supports this capability-scoped order: `proyecto26/system-design-skills` for
general offline HTML/SVG architecture diagrams; AWS’s `aws-architecture-diagram`
for AWS-specific draw.io diagrams; Lanshu for explicitly animated Excalidraw-
style output (maintainer usefulness 2/3 because of readability adaptation).
The `coleam00` Excalidraw renderer remains conditional because its pinned
`esm.sh` dependency failed to load in the isolated test. Do not hard-code these
repositories into runtime ranking; re-check revision, license, dependencies,
and output quality at query time.

### Provider orchestration

Documented as the next future capability: select the smallest useful provider
set rather than querying every catalog. Keep local-first search, use
learn-skills.dev generated data for broad structured retrieval, then skills.sh
and other providers as candidate sources, with authenticated GitHub or web
search as fallbacks. Provider adapters must
preserve timestamp, authentication, result-count, failure, and provenance
fields; catalog data must never replace canonical source inspection. Keep a
provider's total result count distinct from the bounded inspection shortlist.
Do not scrape the learn-skills.dev website, adopt an undocumented endpoint, or
build a multi-provider cache until its contract and usefulness are measured.

### Assessment gateway

Proposed as a future product boundary, not as a change to the shipped payload.
The gateway would consume read-only catalog candidates (including
`learn-skills.dev` outputs), pin each candidate to an exact source revision,
and produce provenance, static-safety, compatibility, maintenance, and later
behavioral-evaluation evidence before a user chooses to install. It must not
become a second catalog, treat install counts as quality proof, or install and
mutate a user's skill directory as a side effect of discovery.

The current repository remains static by default. Any runtime evaluation would
need a separate isolated runner, synthetic fixtures, explicit authorization,
and a documented no-credentials/no-network boundary; it is not part of the
current skill payload or CI gate.

## Current implementation state

### Validation and CI

- CI validates payload, documentation, links, version consistency, workflows,
  evaluation fixtures, and dependencies on push and pull request.
- Scheduled monitoring checks external evidence reachability and expiry.
- Weekly repository health checks cover link integrity, reference integrity,
  payload budget, and advisory-baseline drift.
- GitHub Actions are SHA-pinned and Dependabot monitors workflow actions.

### Discovery methodology

- Local-first, bounded discovery with explicit inaccessible-root reporting.
- Documented provider fallbacks with freshness and status per source.
- Revision-pinned candidate inspection with compatibility and capability gates.
- Candidate inspection budgets: 32 files, 100 KiB per file, 1 MiB total, depth 3.
- Remote request budget: 15 seconds per request and two minutes per search.
- No installation, copying, creation, or execution without explicit approval.
- No secrets, private URLs, personal data, or credentials copied into reports.
- Report contract requires per-source and per-candidate evidence rows.

### Evaluation

`tests/discovery-evaluations.json` is a network-free calibration set covering
direct, conditional, partial, blocked, and rejected outcomes, plus freshness,
loader, privacy, and behavior-validation states. The validator checks schema,
coverage, and consistency. These fixtures do not execute candidate content.

## Future assessment-gateway roadmap

This roadmap is exploratory. Do not change the shipped discovery behavior or
release a runtime harness until the earlier stage has evidence and acceptance
criteria. Each stage must remain independently revertible.

### Stage 0 — Assessment contract

Define a machine-readable assessment record containing source URL, repository,
skill path, exact commit, checker version, findings, review date, and status.
Keep provenance, static risk, compatibility, maintenance, and behavioral fit as
separate signals; do not collapse them into one trust score.

Acceptance criteria:

- Fixtures represent known-safe, clearly hazardous, ineffective, and ambiguous
  candidates.
- Every result is reproducible from a pinned source revision and checker
  version.
- Status semantics are non-certifying (`unreviewed`, `inspected`, `tested`,
  `reviewed`, `stale`, `deprecated`).

### Stage 1 — Read-only static assessment MVP

Accept a GitHub skill URL or a candidate from a catalog feed. Resolve the exact
`SKILL.md`, deduplicate by provenance-qualified identity, and report metadata,
required tools, referenced files, permissions, external fetches, subprocesses,
secret access, instruction-injection indicators, and unsupported assumptions.

Acceptance criteria:

- No installation, copying, execution, or user-directory mutation occurs.
- Reports are available as Markdown and JSON.
- Findings include severity, evidence location, checker version, and source
  hash.
- Network-dependent observations are distinct from deterministic local checks.

### Stage 2 — Discovery integration and shortlist

Use `learn-skills.dev` and other documented providers only as candidate sources.
Rank by task fit, compatibility, maintenance, and review state; keep install
counts and rankings as popularity signals only. Produce a bounded shortlist
with alternatives, evidence, warnings, and the exact reviewed revision.

Acceptance criteria:

- Provider data cannot overwrite the pinned assessment without a new review.
- Source changes invalidate or stale the prior assessment.
- Discovery and installation remain separate authorization steps.

### Stage 3 — Isolated behavioral evaluation

Only after Stages 0–2 are stable, add opt-in execution in a disposable
environment using synthetic fixtures, no credentials, no private data, and no
network by default. Record client, model, tool, environment, fixture, and
source-revision context alongside results.

Acceptance criteria:

- The runner distinguishes `not run`, `partial`, `pass`, and `fail`.
- Results include side-effect checks and reproducibility metadata.
- False-positive, false-negative, reviewer-time, and repeatability measures
  are collected before broadening the fixture suite.

### Stage 4 — Review and distribution

Add dated human decisions, advisory baselines, expiry/reassessment triggers,
and a machine-readable assessment API. Installer integrations remain opt-in
and must show the source, revision, findings, target path, and operation before
requesting confirmation.

### Stage 5 — Evidence-backed skill authoring

Only after the assessment and evaluation contracts are stable, add an opt-in
authoring flow. Clarify the task, target client, scope, expected behavior, and
allowed tools; search existing skills first; preserve provenance for borrowed
patterns; draft the smallest valid `SKILL.md`; and generate offline fixtures
and review prompts.

Acceptance criteria:

- A failed discovery result never implicitly authorizes creation.
- Drafts are written only after explicit user approval and are validated before
  installation or publication.
- Generated content identifies borrowed sources and separates them from new
  project-specific guidance.
- Static safety, portability, frontmatter, reference, and fixture checks run on
  the draft before it is offered for installation.
- Creation, installation, and publication remain separate user decisions.

Completion boundary: the gateway is useful when it reliably separates clearly
hazardous, behaviorally ineffective, and review-worthy candidates without
claiming that a passing assessment certifies safety. Authoring is complete only
when a draft can be validated and reviewed without making discovery or
installation implicitly mutating.

## Implementation record

### 2026-09-06 — Static discovery scope complete

- Completed the non-Claude roadmap for the portable discovery skill.
- Confirmed the pinned `skills-ref` conformance gate in CI and the release
  workflow.
- Confirmed skills.sh indexing, install instructions, detail page, and README
  badge for `skill-discovery`.
- Moved the project into maintenance and evidence-gathering mode. The future
  assessment-gateway stages remain deferred until real usage demonstrates a
  repeatable need; no gateway, runtime harness, or catalog aggregation service
  is implied by this completion status.

### 2026-09-06 — Search-efficiency baseline

- Measured five representative local queries in
  [`docs/search-efficiency-evaluation.md`](../docs/search-efficiency-evaluation.md).
- Raw retrieval was sub-second, but broad roots contained 110,470 skill files
  and exceeded the workflow's bounded-search cap. Root selection and duplicate
  exclusion are therefore more important than a language migration.
- No index, cache, parallel provider layer, or Go implementation is justified
  until real tasks provide usefulness and latency evidence.
- The provider pilot found learn-skills.dev fast and broad for generic queries,
  but incomplete for niche terms; skills.sh is auth-gated for API retrieval.
  Continue with provider-aware fallback and measure candidate usefulness before
  implementing adapters or persistent caching.

### 2026-09-07 — Broad provider query correction

- A broad `golang` query against the synchronized learn-skills.dev generated
  index returned 158 lexical matches; the leading results clustered in one
  collection. Direct website access was rate-limited with HTTP 429.
- This reinforces the provider boundary: use learn-skills.dev for broad,
  timestamped candidate retrieval, then inspect canonical repositories; do not
  infer quality from ranking or build against an unverified search endpoint.

### 2026-09-06 — Real-task fit pilot started

- Added a lightweight scoring protocol and recorded the first two real
  discovery requests in
  [`docs/search-efficiency-evaluation.md`](../docs/search-efficiency-evaluation.md).
- User acceptance remains explicitly unknown; continued conversation is not
  counted as success evidence.
- Collect at least five additional requests with explicit usefulness and
  acceptance ratings before considering ranking, provider orchestration,
  caching, or implementation-language changes.
- Four additional requests were recorded on 2026-09-07; provisional fit is
  documented, but acceptance is still unknown. Obtain explicit ratings before
  drawing a product or architecture conclusion.
- A seventh request (mobile app design) was added on 2026-09-07. The sample
  now spans seven requests, but still lacks explicit user acceptance ratings.
- Four trending selections (Next.js on Cloudflare, Postgres safety,
  brainstorming, and UX design) were recorded on 2026-09-07. The sample now
  spans eleven requests; trend status remains a retrieval hint and acceptance
  ratings are still required.
- Three additional selections (sprint planning, forge idea, and AI video
  generation) were recorded on 2026-09-07. The sample now spans fourteen
  requests; stale catalog provenance and service dependencies remain common
  failure modes. The requester subsequently rated all three latest results
  3/3 and accepted them; popularity was recorded only as user-provided context,
  not as quality evidence.
- Two BMAD candidates (`bmad-sprint-planning` and `bmad-forge-idea`) were added
  on 2026-09-07. The sample now spans sixteen requests; agent-fit scores are
  2/3 and 3/3 respectively, while user usefulness and acceptance remain
  pending.
- The popular `code review` query was followed by canonical inspection of
  `mattpocock/skills` at commit `3cca18b368ae95cdbdebbff572ccafa662551015`.
  Its focused payload is a strong 3/3 static fit when fixed-point, issue/spec,
  and parallel-sub-agent prerequisites exist; otherwise it is conditional 2/3.
  User acceptance remains pending, so no ranking or provider adapter is
  justified yet.
- A synthetic smoke test at fixed point `d864511` confirmed the candidate's
  fixed-point gate, separate Standards/Spec reporting, and correct no-spec
  handling. Parallel sub-agent behavior was not executed in the isolated test,
  so the result validates the report contract only; user acceptance remains
  pending.
- A read-only Go pilot tested three promising `samber/cc-skills-golang` skills
  against shallow `spf13/cobra`, `go-chi/chi`, and `gin-gonic/gin` checkouts.
  Code-style review was highly actionable (3/3); testing guidance was useful
  but over-broad on integration tags (2/3); security guidance was relevant but
  required caller/data-flow context to avoid framework false positives (2/3).
  Bundled eval fixtures (24/14/43) improve instruction coverage but are not
  executable proof. No implementation change is justified until user
  usefulness is explicitly rated.
- A read-only Python pilot tested `py-review` against Requests, HTTPX, and
  pytest (framework checkouts were excluded) and compared it with a broad
  Python-standards candidate. `py-review` was a direct 3/3 routing fit; the
  standards collection was a contextual 2/3 supplement. A writing pilot found
  `creative-writing-craft` a direct 3/3 fit for a small prose task, while
  `writing-for-agents` was a scope mismatch; one catalog path was stale.
  Keep these as evidence for canonical inspection and task-fit filtering, not
  as automated quality scores. User acceptance is still required before
  ranking, provider adapters, caching, or a language rewrite.

### 2026-09-06 — Proportioned cross-platform CI

- Retained Ubuntu Python 3.10/3.14 coverage and one macOS Python 3.14
  portability job.
- Removed the redundant macOS Python 3.10 job for the solo-maintainer model;
  restore it only if a macOS-specific failure or support requirement appears.

### 2026-08-24 — v0.1.3 release

- Released `v0.1.3` with the post-v0.1.2 CI gate hardening, evidence refresh,
  documentation consolidation, and discovery-methodology improvements.
- Confirmed project metadata, citation metadata, and `uv.lock` agree on the
  release version.
- Release validation passed and GitHub generated the release notes.

### 2026-08-24 — Methodology hardening

- Made package-runner bootstrapping explicitly opt-in.
- Added local, remote, and candidate inspection budgets.
- Reworked the report template for per-source and per-candidate evidence.
- Added redaction requirements and robust catalog-shape examples.
- Expanded evaluation fixtures to cover all decision classes.
- Rewrote maintainer guidance using Diátaxis-oriented sections.

### 2026-08-24 — Assessment gateway proposal

- Recorded a future, read-only assessment-gateway direction using catalog
  ingestion, pinned provenance, static checks, task-fit shortlists, and a
  separately gated isolated evaluation stage.
- Added a separately gated future authoring stage for provenance-preserving
  drafts, offline fixtures, and explicit creation approval.
- Preserved the current static-only discovery boundary; no runtime harness,
  registry aggregation service, or automatic installation was added.

### 2026-08-21 — Repository hardening and v0.1.2

- Added workflow action pinning, Dependabot, Ruff, issue templates, URL drift
  monitoring, research expiry checks, repository health checks, and advisory
  baselines.
- Consolidated shared validation utilities and added payload safety checks,
  reference-size budgets, CI policy self-tests, and README stale-drift checks.
- Released `v0.1.2` after aligning version metadata and release validation.

### 2026-08-16 — Discovery and evaluation baseline

- Added local-first discovery, freshness separation, compatibility gates,
  privacy guidance, loader states, bounded shortlists, and inspection-blocked
  outcomes.
- Added the initial offline evaluation fixture contract.

### 2026-07-22 — Skill format and validation baseline

- Added the skill-format and trust-review references.
- Added the standalone payload validator and unit tests.
- Kept scaffolding and authoring templates out of this discovery payload.

## Scope exclusions

The project does not currently need CODEOWNERS, PR templates, stale-issue bots,
CodeQL, extra release automation, a changelog file, a registry aggregation
service, or automatic execution of discovered skills. Reconsider exclusions only
when usage produces a concrete, repeatable failure or the contributor model
changes.
