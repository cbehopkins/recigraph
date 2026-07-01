"""Tests for HTML rendering vertical-slice behavior."""

from pathlib import Path

from recigraph.build.types import CompiledRecipe
from recigraph.model import CompilerOutput, EntityReference, GraphState
from recigraph.rendering.html import HtmlRenderer
from recigraph.rendering.html.view_models import RecipePageViewModel, build_recipe_site_view_model


def _compiled_recipe(
    path: Path,
    *,
    snapshot_id: str,
    ingredients: tuple[str, ...],
) -> CompiledRecipe:
    entities = tuple(
        EntityReference(domain="ingredient", identifier=identifier) for identifier in ingredients
    )
    output = CompilerOutput(
        final_graph=GraphState(snapshot_id=snapshot_id, entities=entities),
        trace=(),
    )
    return CompiledRecipe(source_path=path, output=output)


def test_build_recipe_site_view_model_transforms_graph_ir_to_recipe_pages(tmp_path: Path) -> None:
    compiled = (
        _compiled_recipe(
            tmp_path / "recipes" / "vanilla_base.yaml",
            snapshot_id="G2",
            ingredients=("milk", "sugar"),
        ),
    )

    site_model = build_recipe_site_view_model(compiled)

    assert len(site_model.pages) == 1
    page = site_model.pages[0]
    assert isinstance(page, RecipePageViewModel)
    assert page.slug == "vanilla_base"
    assert page.title == "Vanilla Base"
    assert page.graph_snapshot_id == "G2"
    assert page.ingredient_references == ("ingredient.milk", "ingredient.sugar")


def test_html_renderer_renders_index_and_recipe_pages(tmp_path: Path) -> None:
    output_dir = tmp_path / "dist"
    output_dir.mkdir()

    site_model = build_recipe_site_view_model((
        _compiled_recipe(tmp_path / "a_recipe.yaml", snapshot_id="G1", ingredients=("milk",)),
        _compiled_recipe(tmp_path / "b_recipe.yaml", snapshot_id="G3", ingredients=("sugar",)),
    ))
    result = HtmlRenderer().render(site_model, output_dir)

    assert result.renderer_name == "html"
    assert [artifact.relative_path.as_posix() for artifact in result.artifacts] == [
        "index.html",
        "recipes/a_recipe.html",
        "recipes/b_recipe.html",
    ]

    index_html = (output_dir / "index.html").read_text(encoding="utf-8")
    assert "recipes/a_recipe.html" in index_html
    assert "recipes/b_recipe.html" in index_html

    recipe_html = (output_dir / "recipes" / "a_recipe.html").read_text(encoding="utf-8")
    assert "A Recipe" in recipe_html
    assert "ingredient.milk" in recipe_html
