#!/usr/bin/env python3
"""Validate CI configuration files."""

from __future__ import annotations

import re
import sys

from _common import ROOT

WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"
DEPENDABOT_WORKFLOW = ROOT / ".github" / "workflows" / "dependabot-auto-merge.yml"
RELEASE_WORKFLOW = ROOT / ".github" / "workflows" / "release.yml"
AGENTS_SYMLINK = ROOT / ".agents" / "skills" / "skill-discovery"
PAYLOAD_DIR = ROOT / "skills" / "skill-discovery"

DEPENDABOT_GUARD = (
    "github.event.pull_request.user.login == 'dependabot[bot]' "
    "&& github.repository == 'CodeSigils/skill-discovery'"
)
DEPENDABOT_MERGE_CONDITION = (
    "steps.metadata.outputs.update-type == 'version-update:semver-patch' "
    "|| steps.metadata.outputs.update-type == 'version-update:semver-minor'"
)

SHA_PIN_RE = re.compile(r"^[^@\s]+@[0-9a-f]{40}$")
CHECKOUT_STEP_RE = re.compile(
    r"(?ms)^\s*-\s+uses:\s*actions/checkout@.*?(?=^\s*-\s|\Z)"
)

# Python version policy — single source of truth for CI version checks
LINT_PYTHON_VERSION = "3.14"
TEST_MATRIX_YAML = '["3.10", "3.14"]'
MACOS_EXCLUDE_BLOCK = (
    '        exclude:\n'
    '          - os: macos-latest\n'
    '            python-version: "3.10"'
)
SKILLS_REF_COMMAND = (
    "uvx --from git+https://github.com/agentskills/agentskills.git@69ef37e"
    "#subdirectory=skills-ref skills-ref validate skills/skill-discovery"
)

# NOTE: validate-ci.py verifies that actions are SHA-pinned but does NOT
# verify the SHA matches the claimed version tag. That check requires a
# network call to the GitHub API and belongs in CI, not a local validator.
# Dependabot keeps SHAs current; this script catches policy drift (unpinned
# actions, missing steps, broken anchors).

# Lint job: version-independent checks that only need to run once
LINT_COMMANDS = (
    "uv run python3 scripts/validate-ci.py",
    "uv run python3 scripts/check-version-consistency.py",
    "uv run python3 scripts/check-readme-tree.py",
    "uv run ruff check .github/scripts/ scripts/",
    "uv run ty check --extra-search-path scripts .github/scripts scripts",
    "uv run python .github/scripts/ci-check.py",
    SKILLS_REF_COMMAND,
    "uv run python scripts/validate-evaluation-fixtures.py",
)

# Test job: version-dependent checks that run across the matrix
TEST_COMMANDS = (
    "uv run python .github/scripts/test_validators.py",
    "uv run python -m pytest .github/scripts/test_integration.py -v",
    "uv run python scripts/test_validate_skill.py",
    "uv run python .github/scripts/validate-docs.py",
)


def section_body(workflow: str, name: str) -> str | None:
    match = re.search(
        rf"(?ms)^  {re.escape(name)}:\n(?P<body>.*?)(?=^  [A-Za-z0-9_-]+:\n|\Z)",
        workflow,
    )
    return match.group("body") if match else None


def active_workflow_lines(workflow: str) -> str:
    """Remove comment-only lines before applying policy checks."""
    return "\n".join(
        line for line in workflow.splitlines() if not line.lstrip().startswith("#")
    )


def has_run_command(body: str, command: str) -> bool:
    return bool(
        re.search(
            rf"(?m)^\s*run:\s*['\"]?{re.escape(command)}['\"]?\s*(?:#.*)?$",
            body,
        )
    )


def checkout_credential_errors(workflow: str, label: str) -> list[str]:
    return [
        f"{label}: checkout must set 'persist-credentials: false'"
        for step in CHECKOUT_STEP_RE.findall(workflow)
        if "persist-credentials: false" not in step
    ]


def action_reference_errors(workflow: str, label: str) -> list[str]:
    """Require every external action to use a full commit SHA."""
    uses = re.findall(
        r"(?m)^\s*(?:-\s+)?uses:\s*([^\s#]+)",
        active_workflow_lines(workflow),
    )
    if not uses:
        return [f"{label}: workflow must declare its external actions explicitly"]
    return [
        f"{label}: action reference must use a full commit SHA: {reference}"
        for reference in uses
        if not reference.startswith("./") and not SHA_PIN_RE.fullmatch(reference)
    ]


def check_symlink() -> list[str]:
    """Verify .agents symlink points to the canonical skill directory."""
    errors: list[str] = []
    if not AGENTS_SYMLINK.is_symlink():
        if AGENTS_SYMLINK.exists():
            errors.append(f"check-symlink: {AGENTS_SYMLINK} is a directory, not a symlink")
        else:
            errors.append(f"check-symlink: {AGENTS_SYMLINK} does not exist")
        return errors
    target = AGENTS_SYMLINK.resolve()
    if target != PAYLOAD_DIR.resolve():
        errors.append(
            f"check-symlink: {AGENTS_SYMLINK} -> {target} "
            f"(expected {PAYLOAD_DIR.resolve()})"
        )
    return errors


def validate_workflow(workflow: str) -> list[str]:
    active = active_workflow_lines(workflow)
    errors: list[str] = []

    push = section_body(active, "push")
    pull_request = section_body(active, "pull_request")
    if push is None:
        errors.append("ci.yml: missing push event")
    elif re.search(r"(?m)^\s*paths(?:-ignore)?:", push):
        errors.append("ci.yml: push must not use path filters")
    if pull_request is None:
        errors.append("ci.yml: missing pull_request event")
    # Required branch-protection checks must run for every PR. A path filter
    # here can skip the workflow and leave required checks pending forever.
    elif re.search(r"(?m)^\s*paths:\s*", pull_request):
        errors.append("ci.yml: pull_request must not use paths filters")

    # Lint job
    lint = section_body(active, "lint")
    if lint is None:
        errors.append("ci.yml: missing lint job")
    else:
        for command in LINT_COMMANDS:
            if not has_run_command(lint, command):
                errors.append(f"ci.yml: lint job missing run command {command!r}")
        if "uv sync" not in lint:
            errors.append("ci.yml: lint job must install deps with uv sync")
        if "uv audit" not in lint:
            errors.append("ci.yml: lint job must run uv audit for vulnerability checking")
        if "matrix:" in lint:
            errors.append("ci.yml: lint job must not use a matrix (runs once)")
        if not re.search(rf"python-version:\s*['\"]{re.escape(LINT_PYTHON_VERSION)}['\"]", lint):
            errors.append(f"ci.yml: lint job must pin Python {LINT_PYTHON_VERSION}")

    # Test job
    test = section_body(active, "test")
    if test is None:
        errors.append("ci.yml: missing test job")
    else:
        if "verify-marketplace-urls" in test:
            errors.append(
                "ci.yml: live URL checks must not run in the test matrix"
            )
        for command in TEST_COMMANDS:
            if not has_run_command(test, command):
                errors.append(f"ci.yml: test job missing run command {command!r}")
        if "uv sync" not in test:
            errors.append("ci.yml: test job must install deps with uv sync")
        if "matrix:" not in test:
            errors.append("ci.yml: test job must use a matrix strategy")
        if TEST_MATRIX_YAML not in test:
            errors.append(f"ci.yml: Python matrix must match {TEST_MATRIX_YAML}")
        if MACOS_EXCLUDE_BLOCK not in test:
            errors.append("ci.yml: test matrix must retain only one macOS job")

    # Monitor job
    monitor = section_body(active, "monitor-external-contracts")
    if monitor is None:
        errors.append("ci.yml: missing monitor-external-contracts job")
    else:
        if "matrix:" in monitor:
            errors.append("ci.yml: monitor job must not use a matrix")
        if "permissions:" not in monitor:
            errors.append("ci.yml: monitor job must declare permissions")
        if not re.search(r"(?m)^\s*sign-commits:\s*true\s*$", monitor):
            errors.append(
                "ci.yml: monitor PR creation must enable sign-commits for protected main"
            )
        if "--expiry-only" not in monitor:
            errors.append(
                "ci.yml: monitor must check expiry with --expiry-only"
            )

    errors.extend(action_reference_errors(workflow, "ci.yml"))
    errors.extend(checkout_credential_errors(workflow, "ci.yml"))

    return errors


def validate_dependabot_workflow(workflow: str) -> list[str]:
    active = active_workflow_lines(workflow)
    errors: list[str] = []

    pull_request = section_body(active, "pull_request")
    if pull_request is None:
        errors.append("dependabot-auto-merge.yml: missing pull_request event")
    elif not re.search(r"(?m)^\s*branches:\s*\[main\]\s*$", pull_request):
        errors.append("dependabot-auto-merge.yml: pull_request must target main")

    job = section_body(active, "auto-merge")
    if job is None:
        errors.append("dependabot-auto-merge.yml: missing auto-merge job")
        return errors

    if DEPENDABOT_GUARD not in job:
        errors.append(
            "dependabot-auto-merge.yml: auto-merge must guard on pull_request.user.login "
            "and the repository"
        )
    if "github.actor ==" in job:
        errors.append("dependabot-auto-merge.yml: auto-merge must not guard on github.actor")
    if not re.search(r"(?m)^\s*timeout-minutes:\s*\d+\s*$", job):
        errors.append("dependabot-auto-merge.yml: auto-merge job must set timeout-minutes")
    if "Wait for validation" not in job:
        errors.append("dependabot-auto-merge.yml: auto-merge must wait for validate")
    if '"validate"' not in job:
        errors.append(
            "dependabot-auto-merge.yml: wait step must inspect the validate workflow"
        )
    if DEPENDABOT_MERGE_CONDITION not in job:
        errors.append(
            "dependabot-auto-merge.yml: merge condition must accept only patch and minor updates"
        )
    if "!= 'version-update:semver-major'" in job:
        errors.append(
            "dependabot-auto-merge.yml: merge condition must not use a negative major-version guard"
        )
    if "--match-head-commit" not in job:
        errors.append(
            "dependabot-auto-merge.yml: merge must pin the validated head commit"
        )
    if "actions: read" not in active:
        errors.append(
            "dependabot-auto-merge.yml: must grant actions: read for the validate run query"
        )
    workflow_permissions = active.split("jobs:", 1)[0]
    if (
        "contents: write" in workflow_permissions
        or "pull-requests: write" in workflow_permissions
    ):
        errors.append(
            "dependabot-auto-merge.yml: write permissions must be scoped to the auto-merge job"
        )

    errors.extend(action_reference_errors(workflow, "dependabot-auto-merge.yml"))
    errors.extend(checkout_credential_errors(workflow, "dependabot-auto-merge.yml"))
    return errors


def validate_release_workflow(workflow: str) -> list[str]:
    active = active_workflow_lines(workflow)
    errors: list[str] = []

    push = section_body(active, "push")
    if push is None or "v*.*.*" not in push:
        errors.append("release.yml: must trigger on v*.*.* tags")

    for job_name in ("validate-release", "release"):
        job = section_body(active, job_name)
        if job is None:
            errors.append(f"release.yml: missing {job_name} job")
        elif not re.search(r"(?m)^\s*timeout-minutes:\s*\d+\s*$", job):
            errors.append(f"release.yml: {job_name} job must set timeout-minutes")

    errors.extend(action_reference_errors(workflow, "release.yml"))
    errors.extend(checkout_credential_errors(workflow, "release.yml"))
    return errors


def main() -> int:
    errors: list[str] = []

    if not WORKFLOW.exists():
        print(f"FAIL: {WORKFLOW} not found", file=sys.stderr)
        return 1

    workflow = WORKFLOW.read_text(encoding="utf-8")
    errors.extend(validate_workflow(workflow))
    if DEPENDABOT_WORKFLOW.exists():
        errors.extend(
            validate_dependabot_workflow(
                DEPENDABOT_WORKFLOW.read_text(encoding="utf-8")
            )
        )
    else:
        errors.append(f"{DEPENDABOT_WORKFLOW.name} not found")
    if RELEASE_WORKFLOW.exists():
        errors.extend(
            validate_release_workflow(
                RELEASE_WORKFLOW.read_text(encoding="utf-8")
            )
        )
    else:
        errors.append(f"{RELEASE_WORKFLOW.name} not found")
    errors.extend(check_symlink())
    for path in sorted((ROOT / ".github" / "workflows").glob("*.y*ml")):
        if path in {WORKFLOW, DEPENDABOT_WORKFLOW, RELEASE_WORKFLOW}:
            continue
        text = path.read_text(encoding="utf-8")
        errors.extend(action_reference_errors(text, path.name))
        errors.extend(checkout_credential_errors(text, path.name))

    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1

    print("PASS: CI policy, action pins, and symlink are valid")
    return 0


def self_test() -> int:
    """Regression test: inject known regressions and assert detection."""
    if not WORKFLOW.exists():
        print("FAIL: workflow not found for self-test", file=sys.stderr)
        return 1

    workflow = WORKFLOW.read_text(encoding="utf-8")
    if not DEPENDABOT_WORKFLOW.exists():
        print("FAIL: dependabot workflow not found for self-test", file=sys.stderr)
        return 1
    dependabot = DEPENDABOT_WORKFLOW.read_text(encoding="utf-8")
    if not RELEASE_WORKFLOW.exists():
        print("FAIL: release workflow not found for self-test", file=sys.stderr)
        return 1
    release = RELEASE_WORKFLOW.read_text(encoding="utf-8")
    passed = 0
    failed = 0

    tests = [
        (
            "commented-out lint command",
            workflow.replace(
                "uv run python3 scripts/validate-ci.py",
                "# uv run python3 scripts/validate-ci.py",
            ),
            "lint job missing run command",
        ),
        (
            "push path filter",
            workflow.replace("    branches: [main]", "    branches: [main]\n    paths: ['docs/**']", 1),
            "push must not use path filters",
        ),
        (
            "mutable action tag instead of SHA",
            workflow.replace("actions/checkout@", "actions/checkout@v7"),
            "action reference must use a full commit SHA",
        ),
        (
            "removed test matrix",
            workflow.replace("matrix:", "strategy:", 2),
            "test job must use a matrix strategy",
        ),
        (
            "wrong lint Python version",
            workflow.replace(f"python-version: '{LINT_PYTHON_VERSION}'", "python-version: '3.12'"),
            f"lint job must pin Python {LINT_PYTHON_VERSION}",
        ),
        (
            "unsigned monitor commits",
            workflow.replace("sign-commits: true", "sign-commits: false"),
            "monitor PR creation must enable sign-commits",
        ),
        (
            "checkout persists credentials",
            workflow.replace("persist-credentials: false", "persist-credentials: true", 1),
            "checkout must set 'persist-credentials: false'",
        ),
        (
            "missing skills-ref gate",
            workflow.replace(
                SKILLS_REF_COMMAND,
                "uvx --from git+https://github.com/agentskills/agentskills.git@main"
                "#subdirectory=skills-ref skills-ref validate skills/skill-discovery",
            ),
            "lint job missing run command",
        ),
        (
            "full macOS matrix",
            workflow.replace(f"{MACOS_EXCLUDE_BLOCK}\n", ""),
            "test matrix must retain only one macOS job",
        ),
        (
            "monitor reruns URL checks for expiry",
            workflow.replace(
                "verify-marketplace-urls.py --expiry-only",
                "verify-marketplace-urls.py --check-expiry",
            ),
            "monitor must check expiry with --expiry-only",
        ),
    ]

    for name, mutated, expected_fragment in tests:
        errors = validate_workflow(mutated)
        if any(expected_fragment in e for e in errors):
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name} — expected {expected_fragment!r}", file=sys.stderr)
            failed += 1

    dependabot_tests = [
        (
            "actor-based Dependabot guard",
            dependabot.replace(DEPENDABOT_GUARD, "github.actor == 'dependabot[bot]'"),
            "must guard on pull_request.user.login",
        ),
        (
            "missing Dependabot repository guard",
            dependabot.replace(
                " && github.repository == 'CodeSigils/skill-discovery'",
                "",
            ),
            "must guard on pull_request.user.login and the repository",
        ),
        (
            "negative major-version merge condition",
            dependabot.replace(
                DEPENDABOT_MERGE_CONDITION,
                "steps.metadata.outputs.update-type "
                "!= 'version-update:semver-major'",
            ),
            "merge condition must accept only patch and minor updates",
        ),
        (
            "missing Dependabot main branch filter",
            dependabot.replace("  pull_request:\n    branches: [main]", "  pull_request:"),
            "pull_request must target main",
        ),
        (
            "unpinned Dependabot metadata action",
            dependabot.replace(
                "dependabot/fetch-metadata@25dd0e34f4fe68f24cc83900b1fe3fe149efef98",
                "dependabot/fetch-metadata@v3",
            ),
            "action reference must use a full commit SHA",
        ),
        (
            "workflow-level write permissions",
            dependabot.replace(
                "permissions:\n  contents: read\n",
                "permissions:\n  contents: write\n",
            ),
            "write permissions must be scoped",
        ),
    ]

    for name, mutated, expected_fragment in dependabot_tests:
        errors = validate_dependabot_workflow(mutated)
        if any(expected_fragment in e for e in errors):
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name} — expected {expected_fragment!r}", file=sys.stderr)
            failed += 1

    release_tests = [
        (
            "missing validate-release timeout",
            release.replace("    timeout-minutes: 15\n", ""),
            "validate-release job must set timeout-minutes",
        ),
        (
            "missing release timeout",
            release.replace("    timeout-minutes: 5\n", ""),
            "release job must set timeout-minutes",
        ),
        (
            "unpinned release action",
            release.replace(
                "actions/checkout@3d3c42e5aac5ba805825da76410c181273ba90b1",
                "actions/checkout@v7",
            ),
            "action reference must use a full commit SHA",
        ),
        (
            "release tag trigger drift",
            release.replace("      - 'v*.*.*'", "      - 'v1.*.*'"),
            "must trigger on v*.*.* tags",
        ),
    ]

    for name, mutated, expected_fragment in release_tests:
        errors = validate_release_workflow(mutated)
        if any(expected_fragment in e for e in errors):
            print(f"  PASS: {name}")
            passed += 1
        else:
            print(f"  FAIL: {name} — expected {expected_fragment!r}", file=sys.stderr)
            failed += 1

    print(f"\nself-test: {passed} passed, {failed} failed")
    return 1 if failed else 0


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--self-test", action="store_true", help="Run regression tests")
    args = parser.parse_args()
    if args.self_test:
        raise SystemExit(self_test())
    raise SystemExit(main())
