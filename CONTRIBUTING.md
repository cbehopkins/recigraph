# Contributing to ReciGraph

Thank you for contributing.  This document covers the conventions that keep the
project history clean and the release pipeline automatic.

For tool setup and day-to-day development commands see
[docs/development.md](docs/development.md).  For the release process see
[docs/releasing.md](docs/releasing.md).

---

## Branch naming

| Pattern | Purpose |
|---|---|
| `feat/<short-description>` | New feature |
| `fix/<short-description>` | Bug fix |
| `docs/<short-description>` | Documentation only |
| `refactor/<short-description>` | Code restructuring, no behaviour change |
| `test/<short-description>` | Test additions or corrections |
| `build/<short-description>` | Build system or dependency changes |
| `ci/<short-description>` | CI workflow changes |
| `chore/<short-description>` | Housekeeping (does not affect the package) |

Use lowercase kebab-case.  Keep descriptions short (3–5 words).

**Examples:**

```
feat/procedure-compiler
fix/ingredient-unit-validation
docs/dsl-stage-examples
```

---

## Commit messages — Conventional Commits

All commits must follow the [Conventional Commits](https://www.conventionalcommits.org/)
specification.  Release Please reads these to determine the next version and to
generate the changelog automatically.

```
<type>[optional scope]: <short summary>

[optional body]

[optional footer(s)]
```

The summary line should be no longer than 72 characters and written in the
imperative mood ("add", "fix", "remove" — not "added" or "fixes").

### Types and their effect on versioning

| Type | Changelog section | Version bump |
|---|---|---|
| `feat` | Features | minor |
| `fix` | Bug Fixes | patch |
| `perf` | Performance Improvements | patch |
| `docs` | Documentation | none |
| `refactor` | Code Refactoring | none |
| `test` | Tests | none |
| `build` | Build System | none |
| `ci` | Continuous Integration | none |
| `chore` | Miscellaneous | none |

### Breaking changes — major version bump

```
feat!: rename Ingredient.unit to Ingredient.measure
```

or with a footer:

```
feat: rename Ingredient.unit to Ingredient.measure

BREAKING CHANGE: the `unit` field has been renamed to `measure` across
all serialised formats.  Existing YAML files must be updated.
```

---

## Pull requests

- One logical change per PR.
- The PR title should be a valid Conventional Commit summary line (Release
  Please uses it as a fallback if the squash-commit message is not set).
- Keep PRs small enough to review in a single sitting.
- All CI checks must pass before merging.

---

## Tagging

**Do not create version tags manually.**

Tags are created automatically by Release Please when a Release PR is merged.
Tags follow the format:

```
v<major>.<minor>.<patch>
```

Examples: `v0.1.0`, `v1.0.0`, `v2.3.1`.

If you need to tag a pre-release manually (e.g. a beta for testing), use:

```
v<major>.<minor>.<patch>-<pre-release>
```

Example: `v1.0.0-beta.1`.

See [docs/releasing.md](docs/releasing.md) for the full release lifecycle.
