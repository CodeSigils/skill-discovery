#!/usr/bin/env python3
"""Validate CI configuration files."""

from __future__ import annotations

import re
import sys

from _common import ROOT

WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"
AGENTS_SYMLINK = ROOT / ".agents" / "skills" / "skill-discovery"
PAYLOAD_DIR = ROOT / "skills" / "skill-discovery"

SHA_PIN_RE = re.compile(r"^[^@\s]+@[0-9a-f]{40}$")

# Python version policy — single source of truth for CI version checks
LINT_PYTHON_VERSION = "3.14"
TEST_MATRIX_YAML = '["3.10", "3.14"]'

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
    "uv run python .github/scripts/ci-check.py",
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
            rf"(?m)^\s*run:\s*{re.escape(command)}\s*(?:#.*)?$",
            body,
        )
    )


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

    # Path triggers
    push = section_body(active, "push")
    pull_request = section_body(active, "pull_request")
    if push is None:
        errors.append("ci.yml: missing push event")
    else:
        if not re.search(r"(?m)^\s*paths:\s*&ci_paths\s*$", push):
            errors.append("ci.yml: push paths must define the shared ci_paths anchor")
        if not re.search(r'(?m)^\s+-\s+["\']?\.gitignore["\']?\s*$', push):
            errors.append("ci.yml: shared workflow paths must include .gitignore")
        if not re.search(r'(?m)^\s+-\s+["\']?tests/\*\*["\']?\s*$', push):
            errors.append("ci.yml: shared workflow paths must include tests/**")
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

    # SHA-pinned actions
    uses = re.findall(r"(?m)^\s*(?:-\s+)?uses:\s*([^\s#]+)", active)
    if not uses:
        errors.append("ci.yml: workflow must declare its external actions explicitly")
    for reference in uses:
        if reference.startswith("./"):
            continue
        if not SHA_PIN_RE.fullmatch(reference):
            errors.append(f"ci.yml: action reference must use a full commit SHA: {reference}")

    return errors


def main() -> int:
    errors: list[str] = []

    if not WORKFLOW.exists():
        print(f"FAIL: {WORKFLOW} not found", file=sys.stderr)
        return 1

    workflow = WORKFLOW.read_text(encoding="utf-8")
    errors.extend(validate_workflow(workflow))
    errors.extend(check_symlink())

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
            "removed push paths anchor",
            workflow.replace("paths: &ci_paths", "paths:"),
            "push paths must define the shared ci_paths anchor",
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
    ]

    for name, mutated, expected_fragment in tests:
        errors = validate_workflow(mutated)
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
