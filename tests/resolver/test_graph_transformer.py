"""Tests for graph transformer abstractions."""

from recigraph.model import EntityReference, GraphState, Step
from recigraph.registry import (
    ContainerRegistry,
    EquipmentRegistry,
    IngredientRegistry,
    ProcedureRegistry,
)
from recigraph.resolver import DefaultGraphTransformer, RegistrySet
from recigraph.resolver.step_engine import apply_step


def _registry_set() -> RegistrySet:
    ingredients = IngredientRegistry()
    procedures = ProcedureRegistry()
    equipment = EquipmentRegistry()
    containers = ContainerRegistry()

    ingredients.add("whole_milk", "ingredient:whole_milk")
    ingredients.add("base_mix", "ingredient:base_mix")
    procedures.add("mix", "procedure:mix")

    return RegistrySet(
        ingredient=ingredients,
        procedure=procedures,
        equipment=equipment,
        container=containers,
    )


def test_default_graph_transformer_applies_step() -> None:
    transformer = DefaultGraphTransformer()
    input_graph = GraphState(
        snapshot_id="G0",
        entities=(EntityReference(domain="ingredient", identifier="whole_milk"),),
    )
    step = Step(
        id="mix_base",
        action=EntityReference(domain="procedure", identifier="mix"),
        outputs=(EntityReference(domain="ingredient", identifier="base_mix"),),
    )

    output_graph, record = transformer.apply_step(
        input_graph,
        step,
        registries=_registry_set(),
        step_index=0,
    )

    assert output_graph.snapshot_id == "G1"
    assert record.step_id == "mix_base"
    assert EntityReference(domain="ingredient", identifier="base_mix") in output_graph.entities


def test_apply_step_wrapper_matches_default_graph_transformer() -> None:
    transformer = DefaultGraphTransformer()
    registries = _registry_set()
    input_graph = GraphState(
        snapshot_id="G0",
        entities=(EntityReference(domain="ingredient", identifier="whole_milk"),),
    )
    step = Step(
        id="mix_base",
        action=EntityReference(domain="procedure", identifier="mix"),
        outputs=(EntityReference(domain="ingredient", identifier="base_mix"),),
    )

    transformed_graph, transformed_record = transformer.apply_step(
        input_graph,
        step,
        registries=registries,
        step_index=0,
    )
    wrapped_graph, wrapped_record = apply_step(
        input_graph,
        step,
        registries=registries,
        step_index=0,
    )

    assert transformed_graph == wrapped_graph
    assert transformed_record == wrapped_record
