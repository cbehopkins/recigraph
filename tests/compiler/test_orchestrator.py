"""Tests for the Phase 9 compiler orchestrator."""

from pathlib import Path

import pytest

from recigraph.compiler import compile, compile_file
from recigraph.model import CompilerOutput
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
