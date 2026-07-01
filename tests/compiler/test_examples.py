"""Phase 12 example pipeline tests using fixture procedures."""

from pathlib import Path

from recigraph.compiler import compile_file
from recigraph.model import EntityReference
from recigraph.registry import (
    ContainerRegistry,
    EquipmentRegistry,
    IngredientRegistry,
    ProcedureRegistry,
)
from recigraph.resolver import RegistrySet


def _registry_set() -> RegistrySet:
    ingredients = IngredientRegistry()
    procedures = ProcedureRegistry()
    equipment = EquipmentRegistry()
    containers = ContainerRegistry()

    ingredients.add("whole_milk", "ingredient:whole_milk")
    ingredients.add("oat_milk", "ingredient:oat_milk")
    ingredients.add("sugar", "ingredient:sugar")
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


def _fixture_path(name: str) -> Path:
    return Path(__file__).resolve().parent.parent / "fixtures" / "procedures" / name


def test_compile_example_vanilla_base_fixture() -> None:
    output = compile_file(_fixture_path("vanilla_base.yaml"), registries=_registry_set())

    assert output.final_graph.snapshot_id == "G2"
    assert len(output.trace) == 2
    assert output.trace[0].step_id == "mix_base"
    assert output.trace[1].step_id == "heat_base"
    assert (
        EntityReference(domain="ingredient", identifier="heated_mix") in output.final_graph.entities
    )


def test_compile_example_substitution_fixture() -> None:
    output = compile_file(_fixture_path("substitution_base.yaml"), registries=_registry_set())

    assert output.final_graph.snapshot_id == "G1"
    assert len(output.trace) == 1
    assert output.trace[0].step_id == "mix_substitution"
    assert "substitute:ingredient.whole_milk->[ingredient.oat_milk,ingredient.sugar]" in (
        output.trace[0].transformations_applied
    )
    assert (
        EntityReference(domain="ingredient", identifier="whole_milk")
        not in output.final_graph.entities
    )
    assert (
        EntityReference(domain="ingredient", identifier="oat_milk") in output.final_graph.entities
    )
    assert EntityReference(domain="ingredient", identifier="sugar") in output.final_graph.entities
