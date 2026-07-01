"""Public entry points for ReciGraph build orchestration."""

from pathlib import Path

from recigraph.build.config import BuildConfig
from recigraph.build.pipeline import BuildResult, run_build_pipeline
from recigraph.resolver import RegistrySet, default_registry_set


def build_site(
    source_dir: Path,
    output_dir: Path,
    *,
    registries: RegistrySet | None = None,
) -> BuildResult:
    """Build a complete static site output from recipe source files."""

    build_config = BuildConfig(source_dir=source_dir, output_dir=output_dir)
    return run_build_pipeline(
        build_config,
        registries=default_registry_set() if registries is None else registries,
    )
