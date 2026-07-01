"""Recipe source discovery utilities for build orchestration."""

from pathlib import Path


def discover_recipe_sources(
    source_dir: Path,
    *,
    patterns: tuple[str, ...] = ("*.yaml", "*.yml"),
) -> tuple[Path, ...]:
    """Discover recipe YAML files under ``source_dir`` with deterministic ordering."""

    if not source_dir.exists():
        raise FileNotFoundError(f"Recipe source directory does not exist: {source_dir}")
    if not source_dir.is_dir():
        raise NotADirectoryError(f"Recipe source path is not a directory: {source_dir}")

    discovered: set[Path] = set()
    for pattern in patterns:
        if not pattern:
            continue
        discovered.update(path for path in source_dir.rglob(pattern) if path.is_file())

    return tuple(sorted(discovered, key=lambda path: path.relative_to(source_dir).as_posix()))
