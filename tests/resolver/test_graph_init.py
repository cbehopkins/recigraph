"""Tests for Phase 6 graph-state initialization."""

from recigraph.model import EntityReference, Procedure, Step
from recigraph.registry import (
    ContainerRegistry,
    EquipmentRegistry,
    IngredientRegistry,
    ProcedureRegistry,
)
from recigraph.resolver import RegistrySet, resolve_procedure_references
from recigraph.resolver.graph_init import initialize_graph_state


def _registry_set() -> RegistrySet:
    ingredients = IngredientRegistry()
    procedures = ProcedureRegistry()
    equipment = EquipmentRegistry()
    containers = ContainerRegistry()

    ingredients.add("whole_milk", "ingredient:whole_milk")
    ingredients.add("sugar", "ingredient:sugar")
    ingredients.add("base_mix", "ingredient:base_mix")
    procedures.add("mix", "procedure:mix")

    return RegistrySet(
        ingredient=ingredients,
        procedure=procedures,
        equipment=equipment,
        container=containers,
    )


def test_initialize_graph_state_builds_g0_from_procedure_inputs() -> None:
    procedure = Procedure(
        id="procedure.vanilla_base",
        steps=(Step(action=EntityReference(domain="procedure", identifier="mix")),),
        inputs=(
            EntityReference(domain="ingredient", identifier="whole_milk"),
            EntityReference(domain="ingredient", identifier="sugar"),
        ),
        outputs=(EntityReference(domain="ingredient", identifier="base_mix"),),
    )
    resolved = resolve_procedure_references(procedure, registries=_registry_set())

    graph = initialize_graph_state(resolved)

    assert graph.snapshot_id == "G0"
    assert graph.entities == procedure.inputs
    assert graph.derived_entities == ()


def test_initialize_graph_state_writes_entity_map_metadata() -> None:
    procedure = Procedure(
        id="procedure.vanilla_base",
        steps=(Step(action=EntityReference(domain="procedure", identifier="mix")),),
        inputs=(EntityReference(domain="ingredient", identifier="whole_milk"),),
    )
    resolved = resolve_procedure_references(procedure, registries=_registry_set())

    graph = initialize_graph_state(resolved)
    metadata = dict(graph.metadata)

    assert metadata["source_procedure_id"] == "procedure.vanilla_base"
    assert metadata["input_count"] == "1"
    assert metadata["entity_map"] == "ingredient.whole_milk=ingredient:whole_milk"


def test_initialize_graph_state_handles_empty_inputs() -> None:
    procedure = Procedure(
        id="procedure.vanilla_base",
        steps=(Step(action=EntityReference(domain="procedure", identifier="mix")),),
    )
    resolved = resolve_procedure_references(procedure, registries=_registry_set())

    graph = initialize_graph_state(resolved)
    metadata = dict(graph.metadata)

    assert graph.entities == ()
    assert graph.derived_entities == ()
    assert metadata["input_count"] == "0"
