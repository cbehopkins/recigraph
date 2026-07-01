"""View-model construction for the HTML renderer."""

from pathlib import Path

from pydantic import ConfigDict, Field

from recigraph.build.types import CompiledRecipe
from recigraph.rendering.common.view_model import ViewModel


class RecipePageViewModel(ViewModel):
    """Presentation-ready data required for a single recipe page."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    slug: str = Field(min_length=1)
    title: str = Field(min_length=1)
    source_path: Path
    graph_snapshot_id: str = Field(min_length=1)
    trace_length: int = Field(ge=0)
    ingredient_references: tuple[str, ...] = ()


class RecipeSiteViewModel(ViewModel):
    """Collection view model consumed by the HTML site renderer."""

    model_config = ConfigDict(frozen=True, extra="forbid")

    pages: tuple[RecipePageViewModel, ...] = ()


def build_recipe_site_view_model(
    compiled_recipes: tuple[CompiledRecipe, ...],
) -> RecipeSiteViewModel:
    """Transform compiled Graph IR into HTML presentation-ready recipe view models."""

    pages = tuple(_build_recipe_page_view_model(recipe) for recipe in compiled_recipes)
    return RecipeSiteViewModel(pages=pages)


def _build_recipe_page_view_model(recipe: CompiledRecipe) -> RecipePageViewModel:
    ingredient_references = tuple(
        sorted(
            reference.reference_text
            for reference in recipe.output.final_graph.entities
            if reference.domain == "ingredient"
        )
    )
    slug = recipe.source_path.stem
    return RecipePageViewModel(
        slug=slug,
        title=slug.replace("_", " ").replace("-", " ").title(),
        source_path=recipe.source_path,
        graph_snapshot_id=recipe.output.final_graph.snapshot_id,
        trace_length=len(recipe.output.trace),
        ingredient_references=ingredient_references,
    )
