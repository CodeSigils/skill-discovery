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
[`references/trust-review.md`](references/trust-review.md).
`SECURITY.md` summarizes the trust boundary; it does not replace those
runtime instructions.

## Skill Trust Checklist

- [x] All shipped files redact sensitive values and report existence or location only.
- [x] Credible credential exposure stops lower-priority review and prompts rotation guidance.
- [x] Filename and pattern checks are described as heuristic, not proof of a clean repository.
- [x] Reports and recommendations exclude sensitive values.
- [x] CI checks the payload for common live-token and private-key patterns.
- [x] The shipped payload contains no destructive reset, forced-push, or secret-dumping commands.
- [x] External evidence manifests verify reachability without storing credentials.
