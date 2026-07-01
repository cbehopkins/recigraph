"""Build pipeline orchestration from recipe sources to output artifacts."""

import shutil
from collections.abc import Callable
from pathlib import Path

from pydantic import BaseModel, ConfigDict

from recigraph.build.config import BuildConfig
from recigraph.build.discovery import discover_recipe_sources
from recigraph.build.types import CompiledRecipe
from recigraph.compiler import compile_file
from recigraph.rendering import RenderResult, ViewModel
from recigraph.rendering.html import HtmlRenderer
from recigraph.rendering.html.view_models import build_recipe_site_view_model
from recigraph.rendering.protocol import Renderer
from recigraph.resolver import RegistrySet


class BuildResult(BaseModel):
    """Deterministic outputs and metadata produced by a build run."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    source_files: tuple[Path, ...]
    compiled_recipes: tuple[CompiledRecipe, ...]
    view_model: ViewModel
    render_result: RenderResult
    output_dir: Path


type ViewModelBuilder = Callable[[tuple[CompiledRecipe, ...]], ViewModel]


def prepare_output_directory(output_dir: Path, *, clean: bool) -> None:
    """Create and normalize the build output directory structure."""

    if clean and output_dir.exists():
        shutil.rmtree(output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "recipes").mkdir(parents=True, exist_ok=True)


def compile_discovered_sources(
    source_files: tuple[Path, ...],
    *,
    registries: RegistrySet,
) -> tuple[CompiledRecipe, ...]:
    """Compile discovered recipe sources into Graph IR outputs."""

    return tuple(
        CompiledRecipe(
            source_path=source_path,
            output=compile_file(source_path, registries=registries),
        )
        for source_path in source_files
    )


def run_build_pipeline(
    config: BuildConfig,
    *,
    registries: RegistrySet,
    view_model_builder: ViewModelBuilder = build_recipe_site_view_model,
    renderer: Renderer | None = None,
) -> BuildResult:
    """Run deterministic source discovery, compilation, view-modeling, and rendering."""

    source_files = discover_recipe_sources(config.source_dir, patterns=config.normalized_patterns)
    compiled_recipes = compile_discovered_sources(source_files, registries=registries)
    view_model = view_model_builder(compiled_recipes)
    prepare_output_directory(config.output_dir, clean=config.clean_output_dir)
    active_renderer = HtmlRenderer() if renderer is None else renderer
    render_result = active_renderer.render(view_model, config.output_dir)
    return BuildResult(
        source_files=source_files,
        compiled_recipes=compiled_recipes,
        view_model=view_model,
        render_result=render_result,
        output_dir=config.output_dir,
    )
