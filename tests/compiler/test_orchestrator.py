"""Tests for the Phase 9 compiler orchestrator."""

from pathlib import Path

import pytest

from recigraph.compiler import compile, compile_file
from recigraph.loader import parse_procedure_yaml_text
from recigraph.model import CompilationContext, CompilerOutput
from recigraph.registry import (
    ContainerRegistry,
    EquipmentRegistry,
    IngredientRegistry,
    ProcedureRegistry,
)
from recigraph.resolver import ReferenceResolutionError, RegistrySet
from recigraph.validation import ProcedureValidationError


def _registry_set() -> RegistrySet:
    ingredients = IngredientRegistry()
    procedures = ProcedureRegistry()
    equipment = EquipmentRegistry()
    containers = ContainerRegistry()

    ingredients.add("whole_milk", "ingredient:whole_milk")
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


def _valid_yaml() -> str:
    return """
id: procedure.vanilla_base
steps:
  - id: mix_base
    action: procedure.mix
    outputs:
      - ingredient.base_mix
  - id: heat_base
    action: procedure.heat
    outputs:
      - ingredient.heated_mix
inputs:
  - ingredient.whole_milk
"""


def test_compile_returns_compiler_output() -> None:
    output = compile(_valid_yaml(), registries=_registry_set())

    assert isinstance(output, CompilerOutput)
    assert output.final_graph.snapshot_id == "G2"
    assert len(output.trace) == 2
    assert output.trace[0].transformation_summary == (
        "action=procedure.mix; bindings=0; outputs=ingredient.base_mix; transformations=2"
    )
    assert output.trace[1].transformation_summary == (
        "action=procedure.heat; bindings=0; outputs=ingredient.heated_mix; transformations=2"
    )


def test_compilation_context_is_explicit_and_immutable() -> None:
    context = CompilationContext(registries=_registry_set())

    assert context.current_graph is None
    assert context.trace == ()
    assert context.diagnostics == ()

    with pytest.raises((TypeError, ValueError, AttributeError)):
        context.trace = ("invalid",)


def test_compile_is_deterministic_for_same_input() -> None:
    output_a = compile(_valid_yaml(), registries=_registry_set())
    output_b = compile(_valid_yaml(), registries=_registry_set())

    assert output_a == output_b


def test_compile_file_compiles_from_yaml_path(tmp_path: Path) -> None:
    yaml_file = tmp_path / "procedure.yaml"
    yaml_file.write_text(_valid_yaml(), encoding="utf-8")

    output = compile_file(yaml_file, registries=_registry_set())

    assert output.final_graph.snapshot_id == "G2"
    assert output.trace[0].step_id == "mix_base"


def test_compile_and_compile_procedure_produce_same_output() -> None:
    from recigraph.compiler import compile_procedure

    registries = _registry_set()
    yaml_input = _valid_yaml()
    output_from_yaml = compile(yaml_input, registries=registries)
    procedure = parse_procedure_yaml_text(yaml_input)

    output_from_procedure = compile_procedure(procedure, registries=registries)

    assert output_from_yaml == output_from_procedure


def test_compile_raises_validation_error_for_empty_steps() -> None:
    invalid_yaml = """
id: procedure.vanilla_base
steps: []
"""

    with pytest.raises(ProcedureValidationError):
        compile(invalid_yaml, registries=_registry_set())


def test_compile_raises_resolution_error_for_missing_reference() -> None:
    unresolved_yaml = """
id: procedure.vanilla_base
steps:
  - action: procedure.missing_action
"""

    with pytest.raises(ReferenceResolutionError):
        compile(unresolved_yaml, registries=_registry_set())
