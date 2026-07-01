# Development guide

Practical setup and day-to-day commands for working on ReciGraph locally.

For branch naming and commit conventions see [CONTRIBUTING.md](../CONTRIBUTING.md).
For the release process see [releasing.md](releasing.md).

---

## Prerequisites

| Tool | Minimum version | Install |
|---|---|---|
| Python | 3.13 | [python.org](https://www.python.org/downloads/) or `uv python install 3.13` |
| uv | latest | [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/) |
| Git | 2.40+ | system package manager |

---

## First-time setup

```sh
# Clone the repository
git clone https://github.com/<org>/recigraph.git
cd recigraph

# Create the virtual environment and install all dependencies
# (including dev extras) in one step.
uv sync

# Install the Git hooks (only needed once per clone).
uv run pre-commit install --hook-type commit-msg --hook-type pre-commit
```

`uv sync` reads `pyproject.toml`, resolves the lock file, creates `.venv/`
automatically, and installs the project in editable mode.  You do not need to
run `python -m venv` or `pip install` manually.

The `pre-commit install` step wires two hook stages into `.git/hooks/`:

| Stage | What it does |
|---|---|
| `pre-commit` | Trailing whitespace, YAML/TOML validation, Ruff lint + format |
| `commit-msg` | Rejects commit messages that don't follow Conventional Commits |

### Activating the virtual environment

uv commands (e.g. `uv run pytest`) activate the environment implicitly.
For interactive shells:

```sh
# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# macOS / Linux
source .venv/bin/activate
```

---

## Updating dependencies

```sh
# Add a runtime dependency
uv add pyyaml

# Add a dev-only dependency
uv add --dev pytest-xdist

# Upgrade all dependencies within their constraints
uv sync --upgrade
```

The `uv.lock` file is committed.  Always commit lockfile changes together with
the `pyproject.toml` change that caused them.

---

## Running tests

```sh
# Run the full test suite
uv run pytest

# Run a specific file or test
uv run pytest tests/model/test_ingredient.py
uv run pytest tests/model/test_ingredient.py::test_unit_required

# Run with coverage
uv run pytest --cov
```

Text-rendering behavior is defined by [formatting.md](formatting.md) and validated by golden example outputs.

When a procedures file contains multiple procedures, the CLI now infers a default entrypoint from procedure references. If there is exactly one unreferenced root procedure, it is selected automatically. Use `--procedure-id` only when multiple roots exist or when you need to override the inferred entrypoint.

```sh
# Run the plain-text output golden tests
uv run pytest tests/cli/test_example_output_golden.py
```

---

## Linting and formatting

Ruff handles both linting and formatting.

```sh
# Check for lint errors
uv run ruff check .

# Auto-fix safe lint issues
uv run ruff check --fix .

# Check formatting (what CI does)
uv run ruff format --check .

# Apply formatting
uv run ruff format .
```

Run both before pushing:

```sh
uv run ruff check . ; uv run ruff format .
```

---

## Type checking

```sh
uv run pyright
```

Type checking is configured in `pyproject.toml` under `[tool.pyright]`.
Strict mode is enabled.  All new code must pass without errors.

---

## Git hooks — pre-commit

The project uses [pre-commit](https://pre-commit.com/) to enforce code quality
and commit message conventions locally, before anything reaches CI.

### One-time install (per clone)

```sh
uv run pre-commit install --hook-type commit-msg --hook-type pre-commit
```

After this, hooks run automatically on every `git commit`.

### Running hooks manually

```sh
# Run all pre-commit hooks against every file
uv run pre-commit run --all-files

# Run only the commit-msg hook against a specific message
echo "feat: add procedure compiler" | uv run pre-commit run --hook-stage commit-msg conventional-pre-commit
```

### Updating hook versions

```sh
uv run pre-commit autoupdate
```

Commit the resulting `.pre-commit-config.yaml` changes.

### Bypassing hooks (emergency only)

```sh
git commit --no-verify -m "..."
```

Use sparingly.  CI enforces the same rules — a bypassed commit will still
fail if the message is malformed.

---

## Tox — full-suite verification

tox orchestrates lint, type-check, and tests in isolated environments.
Run it before opening a PR to replicate what CI will do.

```sh
# Run all configured tox environments
uv run tox

# Run a specific environment
uv run tox -e lint
uv run tox -e typecheck
uv run tox -e tests
```

tox uses `tox-uv` so environments are created and populated by uv rather than
pip, keeping them consistent with the development environment.

---

## Building the package locally

```sh
uv build
```

Produces `dist/recigraph-<version>-py3-none-any.whl` and
`dist/recigraph-<version>.tar.gz`.

The version in the filename is derived from Git tags via `setuptools-scm`.  On
a clean tagged commit (e.g. `v0.2.0`) you get `0.2.0`.  Between tags you get a
development version such as `0.2.1.dev3+gabc1234`.

```sh
# Verify the built packages
uv run python -m twine check dist/*
```

---

## Checking the package version

```sh
# From the command line
uv run python -c "from importlib.metadata import version; print(version('recigraph'))"

# Or after activating the venv
python -c "import recigraph; print(recigraph.__version__)"
```

---

## Editor integration

### VS Code

The workspace is pre-configured for Pyright via `pyproject.toml`.  Install the
**Pylance** extension for full IntelliSense.  The **Ruff** extension provides
on-save formatting and lint feedback.

Recommended extensions:

- `ms-python.python`
- `ms-python.pylance`
- `charliermarsh.ruff`
