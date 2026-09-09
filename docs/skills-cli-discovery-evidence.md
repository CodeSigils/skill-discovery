---
status: current-observation
date: 2026-09-09
updated: 2026-09-09
expires: 2026-10-09
purpose: >
  Preserve a bounded Skills CLI discovery result and clarify its optional
  dependency boundary.
---

# Skills CLI discovery evidence

## Zensical query (2026-09-09)

Command, run from an isolated temporary directory after explicit
authorization:

```bash
npx --yes skills find zensical
```

Observed status: successful. The CLI displayed 21 results, including:

- `layeredcraft/skills@zensical-site` (9 installs)
- `xcode-nlp/kodaskills@koda-zensical` (4 installs)
- `kettleofketchup/dotfiles@zensical` (3 installs)
- `brpaz/agent-skills@zensical-setup` (2 installs)

The query found candidates missed by the earlier local/direct-source pass.
Each serious result still requires canonical repository, exact revision,
license, payload-path, and complete-reference inspection. Install counts and
result ordering are retrieval signals only.

## Dependency boundary

`npx` and the Skills CLI are optional discovery-time tools. They are not
runtime dependencies of this skill and must not be added to its package
dependencies. Because `npx --yes` downloads and executes external code, use it
only with explicit authorization and an isolated working directory. If it is
unavailable or unauthorized, report the provider as unavailable and continue
with canonical source-host search.

## Limits

- “21 results” means results displayed by this invocation, not a provider-wide
  total.
- Results and install counts change; rerun before a release or recommendation.
- This record does not certify candidate quality, safety, compatibility, or
  marketplace indexing.

## Quality inspection example: markdown accessibility (2026-09-09)

Candidate: `community-access/accessibility-agents@markdown-accessibility`

- Canonical repository: `Community-Access/accessibility-agents`
- Reviewed revision: `161c60c`
- License: MIT
- Repository update observed: 2026-08-11
- Skill path: `.github/skills/markdown-accessibility/SKILL.md` (present)
- Frontmatter: valid
- Payload inspection: complete for the selected skill file
- Behavior validation: not run

Strengths:

- Covers descriptive links, alt text, headings, tables, emoji, Mermaid/ASCII
  alternatives, anchors, and plain-language structure.
- Maps findings to WCAG references and severity levels.
- Distinguishes human-judgment findings from bounded auto-fixes.
- Provides remediation templates and a transparent scoring formula.

Risks and limitations:

- The repository contains broader accessibility tooling; seven sibling skills
  were skipped by the installer because of YAML parse errors.
- The numeric score and grade are opinionated and are not formal WCAG
  conformance evidence.
- Auto-fixes for headings, links, diagrams, and descriptions require context.
- No runtime scanner or fixture behavior was executed.

Assessment: conditional fit. Use as a supplementary Markdown-accessibility
reference after reviewing its scope; do not replace site-specific Zensical
accessibility review or install the entire repository automatically.

Report completeness:

- Retrieval: complete
- Canonical inspection: complete for selected candidate
- Behavior validation: not run
- Recommendation confidence: medium

## Zensical skill search report (2026-09-09)

Need: find reusable skills for Zensical site work, especially authoring, setup,
migration, and maintenance.

### Searched

| Source/root | Query | Timestamp | Status | Results/limitations |
|---|---|---|---|---|
| Installed/project skills | `zensical`, `static site`, `documentation site` | 2026-09-09 18:55 UTC | successful | Found the local `zensical-skill` plus cached comparison candidates |
| Skills CLI | `npx --yes skills find zensical` | 2026-09-09 18:55 UTC | successful | 21 displayed results; provider total not exposed |
| GitHub metadata | top repositories | 2026-09-09 | partial | Repository metadata succeeded; some later tree/raw requests hit DNS failures |

### Candidate assessment

| Candidate | Evidence | Fit | Recommendation |
|---|---|---|---|
| `CodeSigils/zensical-skill@zensical` | Complete local payload; valid frontmatter; maintenance, accessibility, links, media, builds, and deployment boundaries | Direct fit | Use for the real Zensical blog |
| `layeredcraft/skills@zensical-site` | Cached payload inspected; complete referenced reference/template files; MIT; remote currently reports update on 2026-09-09 | Conditional fit | Strong authoring/reference supplement; verify exact current payload before installation |
| `brpaz/agent-skills@zensical-setup` | Current repository metadata and payload path observed; setup, migration, `zensical.toml`, and GitHub Pages workflow guidance | Partial/conditional fit | Useful for initial setup or MkDocs migration; not a replacement for maintenance review |
| `xcode-nlp/kodaskills@koda-zensical` | Cached payload inspected; MIT; remote update observed 2026-07-21 | Partial fit | Detailed formatting guidance, but Russian-language and more prescriptive than the blog workflow |
| `zeulewan/claude-code-skills@zensical-development` | Repository exists, but no license and current payload could not be re-fetched due DNS failure | Inspection incomplete | Defer |

### Best result

Use the local `zensical-skill` for this blog. It is the only candidate already
aligned with the repository's maintenance workflow and security boundaries.

Potential supplement: `layeredcraft/skills@zensical-site` for
editorial/reference patterns, after verifying the exact remote revision. It
should not be installed wholesale automatically.

Behavior validation was not run for third-party candidates. No candidate was
installed or executed, and no secrets or private data were copied.

Report completeness:

- Retrieval: complete for local roots and Skills CLI; GitHub metadata partial
- Canonical inspection: complete for local candidates; partial for remote-only refreshes
- Behavior validation: not run
- Recommendation confidence: medium
