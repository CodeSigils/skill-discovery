# Contributing

This page is the maintainer entry point. It follows the Diátaxis model:

- **Tutorial** — make and validate a first change.
- **How-to** — run focused checks and update evidence safely.
- **Reference** — repository boundaries, scripts, and release rules.
- **Explanation** — why the shipped payload is separate from maintenance infrastructure.

Read [SECURITY.md](SECURITY.md) before reporting a security issue.

## Tutorial: first contribution

1. Create a focused branch from current `main`.
2. Change the smallest relevant file set. The shipped runtime boundary is only
   `skills/skill-discovery/`; tooling and research stay outside it.
3. Update README, references, dated evidence, and
   [`proposals/ROADMAP.md`](proposals/ROADMAP.md) when behavior or maintenance
   policy changes.
4. Run the validation commands below.
5. Open a focused pull request with evidence for behavior, documentation, and
   changed external contracts.

Batch related documentation edits together, but keep unrelated maintenance out
of the same pull request.

## How-to: validate a change

Run the full local gate from the repository root:

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

For a payload-only edit, run:

```bash
uv run python scripts/validate-skill.py skills/skill-discovery
uv run python .github/scripts/validate-docs.py
```

If network access is unavailable, report which checks were not run. Do not make
an external contract appear verified based on an old result.

## How-to: update external evidence

1. Read the provider's current documentation before changing a URL, endpoint,
   authentication rule, response shape, or CLI command.
2. Update `docs/evidence-urls.json` with the observed status and verification
   date; keep durable guidance in the relevant reference file.
3. Run the URL verifier and documentation checks.
4. If the scheduled monitor opens a drift PR, read its check counts and review
   the diff for semantic changes. A timestamp refresh alone is not evidence
   that a contract is still correct.
5. GitHub may require explicit approval before the workflow-authored PR's
   required checks can run. Approve only after confirming the PR is
   repository-owned and changes only the evidence manifest; this approval is
   intentional and must not be weakened into a broad bypass.
6. The monitor signs its commits to satisfy the protected branch's
   signed-commit rule. Required checks must still pass before merge.

Never copy credentials, private URLs, or candidate secrets into evidence files,
issues, or reports.

## Reference: repository conventions

### Pull requests and commits

- Keep each branch and pull request focused.
- Use a short imperative commit subject and add `What:` and `Why:` lines for
  non-trivial changes.
- Required CI checks must pass before merge.
- Release notes are generated from commit history; this repository does not keep
  a separate changelog.

Example:

```text
docs: clarify catalog bootstrap boundary

What: Document that npx --yes requires explicit approval.
Why: Discovery is read-only by default and package bootstrapping executes code.
```

### Script directories

- `scripts/` contains contributor-facing tools. They auto-detect the repository
  root through `_common.ROOT` and should work from any working directory.
- `.github/scripts/` contains CI-specific helpers that may rely on GitHub
  context or repository-root execution.

Prefer `scripts/` for reusable local checks. Use `.github/scripts/` only when a
check depends on CI, GitHub APIs, or workflow-specific behavior.

### Release reference

Release from a clean, merged `main` commit:

1. Align the version in `pyproject.toml` and `CITATION.cff`.
2. Run the full validation gate and confirm the worktree is clean.
3. Create and push an annotated `vX.Y.Z` tag.
4. Create the GitHub release and review generated notes.
5. Confirm tag, release, and version metadata agree.

Release when shipped `SKILL.md` behavior, CI policy, or a meaningful group of
changes warrants a user-visible update. Isolated script fixes normally do not
need a release.

## Explanation: why the boundary matters

The skill payload is intentionally small and portable. Keeping validators,
research snapshots, CI workflows, and roadmap decisions outside
`skills/skill-discovery/` prevents maintenance dependencies from becoming
runtime requirements. Dated research records volatile facts; the skill itself
must verify those facts again at use time.
