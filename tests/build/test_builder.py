"""Tests for the build-layer site orchestration entrypoint."""

from pathlib import Path

from recigraph.build import build_site
from recigraph.registry import (
    ContainerRegistry,
    EquipmentRegistry,
    IngredientRegistry,
    ProcedureRegistry,
)
from recigraph.rendering.html import RecipeSiteViewModel
from recigraph.resolver import RegistrySet


def _registry_set() -> RegistrySet:
    ingredients = IngredientRegistry()
    procedures = ProcedureRegistry()
    equipment = EquipmentRegistry()
    containers = ContainerRegistry()

    ingredients.add("whole_milk", "ingredient:whole_milk")
    ingredients.add("base_mix", "ingredient:base_mix")
    ingredients.add("heated_mix", "ingredient:heated_mix")
    procedures.add("mix", "procedure:mix")
    procedures.add("heat", "procedure:heat")

    return RegistrySet(
        ingredient=ingredients,
        procedure=procedures,
        equipment=equipment,
        container=containers,
    )


def _write_fixture_recipe(path: Path, *, step_id: str, action: str, output_id: str) -> None:
    yaml = "\n".join((
        f"id: procedure.{path.stem}",
        "steps:",
        f"  - id: {step_id}",
        f"    action: procedure.{action}",
        "    outputs:",
        f"      - ingredient.{output_id}",
        "inputs:",
        "  - ingredient.whole_milk",
    ))
    path.write_text(yaml, encoding="utf-8")


def test_build_site_orchestrates_compilation_and_artifact_outputs(tmp_path: Path) -> None:
    source_dir = tmp_path / "recipes"
    output_dir = tmp_path / "dist"
    source_dir.mkdir()

    _write_fixture_recipe(
        source_dir / "b_recipe.yaml",
        step_id="mix_step",
        action="mix",
        output_id="base_mix",
    )
    _write_fixture_recipe(
        source_dir / "a_recipe.yml",
        step_id="heat_step",
        action="heat",
        output_id="heated_mix",
    )

    stale_file = output_dir / "stale.txt"
    output_dir.mkdir()
    stale_file.write_text("remove me", encoding="utf-8")

    result = build_site(source_dir, output_dir, registries=_registry_set())

    assert [path.name for path in result.source_files] == ["a_recipe.yml", "b_recipe.yaml"]
    assert len(result.compiled_recipes) == 2
    assert result.output_dir == output_dir
    assert result.render_result.renderer_name == "html"
    assert [artifact.relative_path.as_posix() for artifact in result.render_result.artifacts] == [
        "index.html",
        "recipes/a_recipe.html",
        "recipes/b_recipe.html",
    ]

    assert (output_dir / "index.html").exists()
    assert (output_dir / "recipes").exists()
    assert (output_dir / "recipes" / "a_recipe.html").exists()
    assert (output_dir / "recipes" / "b_recipe.html").exists()
    assert not stale_file.exists()


def test_build_site_writes_deterministic_index_listing(tmp_path: Path) -> None:
    source_dir = tmp_path / "recipes"
    output_dir = tmp_path / "dist"
    source_dir.mkdir()

    _write_fixture_recipe(
        source_dir / "z_recipe.yaml",
        step_id="mix_step",
        action="mix",
        output_id="base_mix",
    )
    _write_fixture_recipe(
        source_dir / "a_recipe.yaml",
        step_id="heat_step",
        action="heat",
        output_id="heated_mix",
    )

    build_site(source_dir, output_dir, registries=_registry_set())
    index_html = (output_dir / "index.html").read_text(encoding="utf-8")

    assert "recipes/a_recipe.html" in index_html
    assert "recipes/z_recipe.html" in index_html
    assert index_html.index("recipes/a_recipe.html") < index_html.index("recipes/z_recipe.html")


def test_build_site_exposes_recipe_page_view_models(tmp_path: Path) -> None:
    source_dir = tmp_path / "recipes"
    output_dir = tmp_path / "dist"
    source_dir.mkdir()

    _write_fixture_recipe(
        source_dir / "recipe.yaml",
        step_id="mix_step",
        action="mix",
        output_id="base_mix",
    )

    result = build_site(source_dir, output_dir, registries=_registry_set())

    assert isinstance(result.view_model, RecipeSiteViewModel)
    pages = result.view_model.pages
    assert len(pages) == 1
    assert pages[0].slug == "recipe"
    assert pages[0].graph_snapshot_id.startswith("G")
