# Contributing

Contributions are welcome. Keep changes focused, evidence-based, and easy to
review. Read [SECURITY.md](SECURITY.md) before reporting security issues.

## Pull requests

- Use a focused branch and pull request for each logical change.
- Batch related tiny documentation edits when practical; do not mix unrelated
  maintenance work into the same pull request.
- Required CI checks must pass before merge.
- CI status checks must pass and `main` protection rules are enforced.
- Preserve the shipped boundary: only `skills/skill-discovery/` is runtime
  payload; repository infrastructure belongs outside it.

## Commit messages

Use a short imperative subject followed by a body for non-trivial changes:

```text
docs: clarify catalog status

What: Replace a time-sensitive indexing claim with durable guidance.
Why: Catalog availability changes independently of local installability.
```

The `What:` and `Why:` lines should describe the concrete change and its
motivation. Release notes are generated from the commit history; this project
does not maintain a separate changelog.

## Script directories

The repository has two script directories with different scopes:

- **`scripts/`** — Standalone CLI tools that auto-detect the repo root via
  `_common.ROOT`. Safe to run from any working directory. Contains validation,
  health checks, and the skill validator.
- **`.github/scripts/`** — CI-specific helpers. May assume the repo root is the
  working directory and use hardcoded paths. Contains URL contract verification,
  marketplace URL checks, and CI-specific validators.

When adding new scripts, prefer `scripts/` for anything a contributor might run
locally. Use `.github/scripts/` only for logic that depends on CI context (GitHub
API tokens, workflow-specific paths, PR creation).

## Validation

Run the relevant checks before opening a pull request:

```bash
uv sync --locked --only-dev
uv run python scripts/validate-ci.py
uv run python scripts/validate-ci.py --self-test
uv run python scripts/check-version-consistency.py
uv run python scripts/check-readme-tree.py
uv run python scripts/cron-health.py
uv run ruff check .github/scripts/ scripts/
uv run python .github/scripts/test_validators.py
uv run python -m pytest .github/scripts/test_integration.py -v
uv run python scripts/test_validate_skill.py
uv run python scripts/validate-evaluation-fixtures.py
uv run python .github/scripts/validate-docs.py
```

## Release process

Releases are tagged from a clean, merged `main` commit:

1. Confirm `pyproject.toml` and `CITATION.cff` contain the intended version.
2. Run the validation commands above and confirm `main` is clean and current.
3. Create an annotated `vX.Y.Z` tag on the merged commit and push the tag.
4. Create a normal GitHub release with notes summarizing the relevant commits.
5. Confirm the tag, release, and version metadata agree.

The tag workflow reruns the release checks for every `v*.*.*` tag.

**When to release:** A new release is warranted when SKILL.md behavior
changes, CI pipeline changes, or ≥5 non-trivial PRs accumulate since
the last tag. Incremental script-only fixes do not require a release.
