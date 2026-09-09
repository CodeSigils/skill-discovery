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
