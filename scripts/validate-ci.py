#!/usr/bin/env python3
"""Validate CI routing contracts that keep checks deterministic and complete."""

from __future__ import annotations

import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows" / "ci.yml"
AGENTS_SYMLINK = ROOT / ".agents" / "skills" / "skill-discovery"
PAYLOAD_DIR = ROOT / "skills" / "skill-discovery"

SHA_PIN_RE = re.compile(r"^[^@\s]+@[0-9a-f]{40}$")
EXACT_VERSION_RE = re.compile(r"^[0-9]+(?:\.[0-9]+){2}$")

# NOTE: validate-ci.py verifies that actions are SHA-pinned but does NOT
# verify the SHA matches the claimed version tag. That check requires a
# network call to the GitHub API and belongs in CI, not a local validator.
# Dependabot keeps SHAs current; this script catches policy drift (unpinned
# actions, missing steps, broken anchors).

REQUIRED_VALIDATE_COMMANDS = (
    "python3 scripts/validate-ci.py",
    "ruff check .github/scripts/ scripts/",
    "python .github/scripts/test_validators.py",
    "python scripts/test_validate_skill.py",
    "python .github/scripts/ci-check.py",
    "python .github/scripts/validate-docs.py",
)


def section_body(workflow: str, name: str) -> str | None:
    match = re.search(
        rf"(?ms)^  {re.escape(name)}:\n(?P<body>.*?)(?=^  [A-Za-z0-9_-]+:\n|\Z)",
        workflow,
    )
    return match.group("body") if match else None


def top_level_section_body(workflow: str, name: str) -> str | None:
    match = re.search(
        rf"(?ms)^{re.escape(name)}:\n(?P<body>.*?)(?=^[A-Za-z0-9_-]+:\n|\Z)",
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


def has_ruff_install(body: str) -> bool:
    """Check that ruff is installed from RUFF_VERSION env var."""
    return "ruff==" in body and "RUFF_VERSION" in body


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
        if not re.search(r"(?m)^\s+-\s+[\"']?\.gitignore[\"']?\s*$", push):
            errors.append("ci.yml: shared workflow paths must include .gitignore")
    if pull_request is None:
        errors.append("ci.yml: missing pull_request event")
    elif not re.search(r"(?m)^\s*paths:\s*\*ci_paths\s*$", pull_request):
        errors.append("ci.yml: pull_request paths must reuse the ci_paths anchor")

    # Ruff version
    environment = top_level_section_body(active, "env")
    ruff_version = None
    if environment is not None:
        match = re.search(
            r"""(?m)^\s*RUFF_VERSION:\s*["']?([^"'\s]+)["']?\s*$""", environment
        )
        if match:
            ruff_version = match.group(1)
    if ruff_version is None or not EXACT_VERSION_RE.fullmatch(ruff_version):
        errors.append(
            "ci.yml: workflow-level RUFF_VERSION must be an exact three-part version"
        )

    # Validate job
    validate = section_body(active, "validate")
    if validate is None:
        errors.append("ci.yml: missing validate job")
    else:
        if "verify-marketplace-urls" in validate:
            errors.append(
                "ci.yml: live URL checks must not run in the validation matrix"
            )
        for command in REQUIRED_VALIDATE_COMMANDS:
            if not has_run_command(validate, command):
                errors.append(f"ci.yml: validation matrix missing run command {command!r}")
        if not has_ruff_install(validate):
            errors.append("ci.yml: validation matrix must install Ruff from RUFF_VERSION")
        if "matrix:" not in validate:
            errors.append("ci.yml: validate job must use a matrix strategy")
        if 'python-version: ["3.10", "3.14"]' not in validate:
            errors.append(
                "ci.yml: Python matrix must test 3.10 lower bound and 3.14 boundary"
            )

    # Monitor job
    monitor = section_body(active, "monitor-external-contracts")
    if monitor is None:
        errors.append("ci.yml: missing monitor-external-contracts job")
    else:
        if "matrix:" in monitor:
            errors.append("ci.yml: monitor job must not use a matrix")
        if "permissions:" not in monitor:
            errors.append("ci.yml: monitor job must declare permissions")

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


if __name__ == "__main__":
    raise SystemExit(main())
