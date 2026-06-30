# Releasing

This document explains how versions are determined, how releases are created,
and how the release pipeline works end to end.

---

## Version strategy

Versions are derived **entirely from Git tags**.  There is no version string
in any source file.  The single source of truth is a tag of the form:

```
v<major>.<minor>.<patch>
```

`setuptools-scm` reads that tag at build time and injects the version into the
built wheel and sdist.

### What versions look like

| Situation | Example version |
|---|---|
| Exact tag `v0.3.0` | `0.3.0` |
| 5 commits after `v0.3.0` | `0.3.1.dev5+gabc1234` |
| Uninstalled source tree | `0.0.0.dev0+uninstalled` |

---

## Obtaining the version at runtime

**Do not import a `__version__` constant from the source tree.**  Use the
stdlib `importlib.metadata` API instead:

```python
from importlib.metadata import version

print(version("recigraph"))
```

The `recigraph` package also exposes a convenience attribute for interactive
use:

```python
import recigraph

print(recigraph.__version__)
```

This attribute is a thin proxy to `importlib.metadata` and is never
hard-coded.

---

## Conventional Commits

All commits that should appear in the changelog or influence the next version
must follow the [Conventional Commits](https://www.conventionalcommits.org/)
specification.

### Supported prefixes

| Prefix | Effect |
|---|---|
| `feat:` | Bumps the **minor** version |
| `fix:` | Bumps the **patch** version |
| `perf:` | Bumps the **patch** version |
| `docs:` | No version bump (hidden in changelog) |
| `refactor:` | No version bump (hidden in changelog) |
| `test:` | No version bump (hidden in changelog) |
| `build:` | No version bump (hidden in changelog) |
| `ci:` | No version bump (hidden in changelog) |
| `chore:` | No version bump (hidden in changelog) |

### Breaking changes

A breaking change bumps the **major** version.  Mark it with either:

```
feat!: redesign ingredient model
```

or a footer in the commit body:

```
feat: redesign ingredient model

BREAKING CHANGE: the `Ingredient.unit` field is now required
```

---

## Release lifecycle

```
Developer
    │
    │  git commit -m "feat: add procedure compiler"
    │  git push origin main
    ▼
GitHub Actions – CI workflow
    │  ruff lint + format check
    │  pyright
    │  pytest
    │  uv build (packaging smoke-test)
    ▼
Release Please
    │  Watches merged PRs on main
    │  Accumulates Conventional Commits
    │  Opens (or updates) a Release PR
    │  Generates CHANGELOG.md entry
    │  Proposes next SemVer version
    ▼
Maintainer merges Release PR
    │
    ▼
Release Please pushes Git tag  (e.g. v0.3.0)
    │
    ▼
GitHub Actions – release.yml
    │  uv sync
    │  uv build  →  wheel + sdist
    │  twine check
    │  (PyPI publish – when configured)
    │  Create GitHub Release
    │  Attach wheel + sdist as release assets
    ▼
GitHub Release published
```

---

## Creating a release (step by step)

1. Merge one or more PRs that use Conventional Commits into `main`.
2. Release Please automatically opens a Release PR titled
   `chore: release <next-version>`.  The PR body contains the draft
   changelog.
3. Review the Release PR and merge it when ready.
4. Release Please pushes the Git tag.  The `release.yml` workflow starts
   automatically.
5. The workflow builds the packages, verifies them, and creates a GitHub
   Release with the wheel and sdist attached.

No manual version editing or `git tag` commands are required.

---

## Enabling PyPI publishing

Publishing to PyPI is configured but disabled by default (the publish job has
`if: false`).  To enable it:

1. Go to [pypi.org](https://pypi.org) and create a project for `recigraph`.
2. Configure a [Trusted Publisher](https://docs.pypi.org/trusted-publishers/)
   linking this GitHub repository, the `release.yml` workflow, and the
   environment name `pypi`.
3. Create a GitHub environment named `pypi` in
   *Settings → Environments* and (optionally) add protection rules.
4. In `.github/workflows/release.yml`, change the `publish` job's guard from

   ```yaml
   if: false
   ```

   to

   ```yaml
   if: true
   ```

No API tokens or secrets are needed when using Trusted Publishing.

---

## Release Please configuration

| File | Purpose |
|---|---|
| `release-please-config.json` | Configures the release type, changelog sections, and tag format |
| `.release-please-manifest.json` | Tracks the current version for each package in the repository |

The manifest is updated automatically by Release Please when it merges a
Release PR.  **Do not edit it manually.**

---

## Toolchain reference

| Tool | Role |
|---|---|
| `setuptools-scm` | Derives package version from Git tags at build time |
| `uv` | Dependency management, environment sync, package building |
| `ruff` | Linting and formatting |
| `pyright` | Static type checking |
| `pytest` | Testing |
| Release Please | Release PR automation and changelog generation |
| GitHub Actions | CI, release build, and publish orchestration |
