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

## Active deferred decisions

### Markdown style linter

Deferred. The documentation validator already checks fences, relative links,
frontmatter, expiry, and payload integrity. Reconsider if formatting defects
become a recurring review problem; do not add a second style policy without a
demonstrated failure pattern.

### Pre-commit hooks

Deferred. CI is the authoritative gate and local hooks would add setup friction
for the solo-maintained project. Reconsider if contributor volume or repeated
local-only failures justify the maintenance cost.

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

## Implementation record

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
