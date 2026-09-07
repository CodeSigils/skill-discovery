# Security Policy

## Reporting a Vulnerability

Report security issues privately through the
[GitHub Security Advisory](https://github.com/CodeSigils/skill-discovery/security/advisories/new)
rather than opening a public issue. Do not include exploit details, credentials,
or other sensitive values in public reports.

Use private reporting for any credible security vulnerability, including:

- workflow steps or scripts that could expose secrets, encourage unsafe
  configurations, or cause destructive repository changes;
- compromised or misleading shipped skill payloads;
- credentials or unsafe sensitive examples in evidence manifests; and
- supply-chain or privilege risks in repository scripts, dependencies, or CI
  workflows.

Ordinary documentation defects, feature requests, and behavior bugs without a
credible security impact may be opened as public GitHub issues. When uncertain,
report privately.

## Repository Security Scope

Repository security covers maintainer infrastructure outside the shipped
payload: GitHub Actions workflows, validation and monitoring scripts,
evidence manifests, and URL contract checks. These components must preserve
the declared shipping boundary, avoid exposing credentials, and prevent
unreviewed content from entering the runtime payload.

CI validates skill structure, portability, documentation integrity, and
external contract reachability. A passing validator is evidence for these
defined checks, not a claim that the repository or its recommendations are
free of vulnerabilities.

## Contract Monitor Security Model

The scheduled URL drift monitor opens workflow-authored pull requests to refresh
verification timestamps and correct canonical URLs in `docs/evidence-urls.json`. Its
trust model:

- Commits are **signed** by the GitHub Actions bot identity to satisfy the
  protected-branch signed-commit rule.
- CI still runs on every pull request, and maintainers should review failures
  before merging. During solo evaluation, required PR checks are not enforced
  by branch protection; signed commits and linear history remain enforced.
- GitHub may require an explicit human approval before workflow-authored PRs
  can run their checks; this approval is scoped to the monitor's bot-owned PR
  and must not be widened into a generic CI bypass.
- The monitor exposes only bounded counters (`checked_count`,
  `timestamp_refresh_count`, `canonical_url_fix_count`) to the workflow through
  `GITHUB_OUTPUT`; it does not write arbitrary files, secrets, or environment
  state back to the runner.
- A canonical URL correction in the evidence manifest requires human semantic
  review of the affected provider contract before merge.

## Assessment Gateway Static Boundary

A future assessment gateway (see `proposals/ROADMAP.md`) is scoped to static
read-only analysis of catalog candidates. It must not:

- install, copy, or mutate any user skill directory;
- execute candidate skill content;
- send credentials, private data, or network traffic by default; or
- treat a passing static assessment as a safety certification.

Any behavioral evaluation stage requires an isolated runner with synthetic
fixtures, explicit user authorization, and a documented no-network boundary.
These stages are not part of the current shipped payload or CI gate.

## Shipped Skill Trust Guarantees

The shipped payload is a single `SKILL.md` and five reference files with no
runtime scripts, no config files, and no dependencies. Shipped instructions
are checked for agent-specific references by CI portability gate.

The workflow teaches agents to inspect candidate skills for provenance,
dependencies, permissions, and maintenance activity. Suspected sensitive
values are reported by existence and location only. Credible exposure is
prioritized ahead of lower-value review, and the agent recommends revocation
or rotation without reproducing the value.

Always-on safety rules live in
[`skills/skill-discovery/SKILL.md`](skills/skill-discovery/SKILL.md).
Detailed trust evaluation guidance is in
[`references/trust-review.md`](skills/skill-discovery/references/trust-review.md).
`SECURITY.md` summarizes the trust boundary; it does not replace those
runtime instructions.

## Skill Trust Checklist

- [x] All shipped files redact sensitive values and report existence or location only.
- [x] Credible credential exposure stops lower-priority review and prompts rotation guidance.
- [x] Filename and pattern checks are described as heuristic, not proof of a clean repository.
- [x] Reports and recommendations exclude sensitive values.
- [x] CI checks the payload for prohibited agent-specific references and validates
      the shipped structure; this is not a comprehensive secret scanner.
- [x] The shipped payload contains no destructive reset, forced-push, or secret-dumping commands.
- [x] External evidence manifests verify reachability without storing credentials.
- [x] Contract monitor commits are signed and required CI checks still gate merge.
- [x] Monitor workflow approval is scoped to bot-owned drift PRs and not a generic bypass.
- [x] Monitor writes only bounded counters via `GITHUB_OUTPUT`; no secrets, files, or
      environment state outside that surface.
- [x] Assessment gateway is bounded to static, read-only analysis; runtime evaluation
      is opt-in, isolated, and explicitly out of the current shipped payload.

Last reviewed: 2026-09-05.
