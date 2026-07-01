---
description: "Use when writing or modifying Python code, tests, and bug fixes in this repository. Enforces tooling, typing, TDD workflow, and scoped change policy."
applyTo:
  - "src/**/*.py"
  - "tests/**/*.py"
  - "scripts/**/*.py"
---

# Recigraph Python Development Defaults

## Runtime And Toolchain

- Use Python 3.13 or newer.
- Use uv for dependency and environment workflows.
- Use tox for environment orchestration and full-suite verification.
- Use pyright for static type checking.
- Use ruff for linting and formatting.

## Code Quality And Typing
- never from __future__ import annotations <- this is not needed in Python 3.13 and newer.
- prefer collections.abc over typing for type hints.
- Keep strict typing enabled.
- pydantic models are preferred for data validation and serialization.


## Testing Workflow

- Follow TDD for bug fixes: Red, Green, then Refactor (minimal and local only).
- Prefer the VS Code pytest test runner for pytest execution during development.
- Unit tests live under the tests directory.
- Fixtures live in dedicated fixture directories and are first-class test assets.
- Name unit test files as test_<associated_source_file>.py.
- Avoid broad, catch-all test files; split tests into focused files named test_<subject>_<logical_grouping>.py.
- At task completion, run the full tox suite.

## Bug-Fix Scope Rules

- Keep changes minimal and tightly scoped to the request.
- Avoid broad refactors during bug fixes.
- If requirements or expected behavior are ambiguous, ask before proceeding.
