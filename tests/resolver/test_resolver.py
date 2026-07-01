"""Tests for the Phase 5 reference resolver."""

import pytest

from recigraph.model import (
    EntityReference,
    OverrideSet,
    Procedure,
    ReferenceBinding,
    Step,
    Substitution,
)
from recigraph.registry import (
    ContainerRegistry,
    EquipmentRegistry,
    IngredientRegistry,
    ProcedureRegistry,
)
from recigraph.resolver import (
    ReferenceResolutionError,
    RegistrySet,
    resolve_procedure_references,
    resolve_reference,
)


def _registry_set() -> RegistrySet:
    ingredients = IngredientRegistry()
    procedures = ProcedureRegistry()
    equipment = EquipmentRegistry()
    containers = ContainerRegistry()

    ingredients.add("whole_milk", "ingredient:whole_milk")
    ingredients.add("oat_milk", "ingredient:oat_milk")
    ingredients.add("sugar", "ingredient:sugar")
    ingredients.add("base_mix", "ingredient:base_mix")
    procedures.add("mix", "procedure:mix")
    equipment.add("blender", "equipment:blender")
    containers.add("jar", "container:jar")

    return RegistrySet(
        ingredient=ingredients,
        procedure=procedures,
        equipment=equipment,
        container=containers,
    )


def test_resolve_reference_routes_to_correct_registry() -> None:
    resolved = resolve_reference(
        EntityReference(domain="equipment", identifier="blender"),
        path="step.action",
        registries=_registry_set(),
    )

    assert resolved.entity == "equipment:blender"
    assert resolved.path == "step.action"


def test_resolve_reference_keeps_version_as_v1_stub() -> None:
    resolved = resolve_reference(
        EntityReference(domain="ingredient", identifier="whole_milk", version=2),
        path="procedure.inputs[0]",
        registries=_registry_set(),
    )

    assert resolved.entity == "ingredient:whole_milk"
    assert resolved.version == 2


def test_resolve_reference_raises_for_missing_identifier() -> None:
    with pytest.raises(ReferenceResolutionError, match="MISSING_REFERENCE"):
        resolve_reference(
            EntityReference(domain="ingredient", identifier="missing"),
            path="procedure.inputs[0]",
            registries=_registry_set(),
        )


def test_resolve_procedure_references_collects_all_reference_paths() -> None:
    procedure = Procedure(
        id="procedure.vanilla_base",
        steps=(
            Step(
                id="mix_base",
                action=EntityReference(domain="procedure", identifier="mix"),
                inputs=(
                    ReferenceBinding(
                        target=EntityReference(domain="ingredient", identifier="whole_milk"),
                    ),
                    ReferenceBinding(
                        target=EntityReference(domain="ingredient", identifier="sugar"),
                        override=OverrideSet(
                            substitutions=(
                                Substitution.model_validate({
                                    "from": EntityReference(
                                        domain="ingredient",
                                        identifier="sugar",
                                    ),
                                    "to": EntityReference(
                                        domain="ingredient",
                                        identifier="oat_milk",
                                    ),
                                }),
                            )
                        ),
                    ),
                ),
                outputs=(EntityReference(domain="ingredient", identifier="base_mix"),),
            ),
        ),
        inputs=(EntityReference(domain="ingredient", identifier="whole_milk"),),
        outputs=(EntityReference(domain="ingredient", identifier="base_mix"),),
    )

    resolved = resolve_procedure_references(procedure, registries=_registry_set())
    paths = {item.path for item in resolved.references}

    assert "procedure.inputs[0]" in paths
    assert "procedure.steps[0].action" in paths
    assert "procedure.steps[0].inputs[1].override.substitutions[0].to" in paths


def test_resolve_procedure_references_raises_with_multiple_issues() -> None:
    procedure = Procedure(
        id="procedure.vanilla_base",
        steps=(
            Step(
                action=EntityReference(domain="procedure", identifier="missing_procedure"),
                inputs=(
                    ReferenceBinding(
                        target=EntityReference(
                            domain="ingredient", identifier="missing_ingredient"
                        ),
                    ),
                ),
            ),
        ),
    )

    with pytest.raises(ReferenceResolutionError) as exc_info:
        resolve_procedure_references(procedure, registries=_registry_set())

    assert len(exc_info.value.issues) == 2
