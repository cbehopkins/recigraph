"""Tests for YAML-to-model parser utilities."""

from pathlib import Path

import pytest

from recigraph.loader import (
    parse_entity_reference,
    parse_procedure,
    parse_procedure_yaml_file,
    parse_procedure_yaml_text,
)
from recigraph.model import Composition, EntityReference, Procedure


def test_parse_entity_reference_from_dotted_syntax() -> None:
    reference = parse_entity_reference("ingredient.whole_milk@2")

    assert reference.domain == "ingredient"
    assert reference.identifier == "whole_milk"
    assert reference.version == 2


def test_parse_entity_reference_rejects_invalid_value() -> None:
    with pytest.raises(ValueError, match="invalid entity reference"):
        parse_entity_reference("ingredient.WholeMilk")


def test_parse_procedure_from_mapping_payload() -> None:
    procedure = parse_procedure({
        "id": "procedure.vanilla_base",
        "name": "Vanilla Base",
        "steps": [
            {
                "id": "mix_base",
                "action": "procedure.mix",
                "inputs": [
                    {
                        "target": "ingredient.whole_milk",
                        "override": {
                            "substitutions": [
                                {
                                    "from": "ingredient.whole_milk",
                                    "to": {
                                        "ingredients": [
                                            "ingredient.oat_milk",
                                            "ingredient.sugar",
                                        ],
                                        "adjustments": [
                                            {
                                                "type": "add",
                                                "target": "ingredient.vanilla",
                                            }
                                        ],
                                    },
                                }
                            ]
                        },
                    }
                ],
                "outputs": ["ingredient.base_mix"],
                "context": {"notes": "example", "tags": ["base"]},
            }
        ],
        "inputs": ["ingredient.whole_milk", "ingredient.sugar"],
        "outputs": ["ingredient.base_mix"],
        "tags": ["dessert"],
    })

    assert isinstance(procedure, Procedure)
    assert procedure.steps[0].id == "mix_base"
    assert procedure.steps[0].action == EntityReference(domain="procedure", identifier="mix")
    assert procedure.steps[0].inputs[0].override is not None
    assert isinstance(procedure.steps[0].inputs[0].override.substitutions[0].to, Composition)


def test_parse_procedure_requires_steps() -> None:
    with pytest.raises(ValueError, match=r"procedure\.steps is required"):
        parse_procedure({"id": "procedure.vanilla_base"})


def test_parse_procedure_yaml_text_roundtrips() -> None:
    yaml_text = """
id: procedure.vanilla_base
steps:
  - action: procedure.mix
inputs:
  - ingredient.whole_milk
"""

    procedure = parse_procedure_yaml_text(yaml_text)

    assert procedure.id == "procedure.vanilla_base"
    assert procedure.steps[0].action.identifier == "mix"
    assert procedure.inputs[0].identifier == "whole_milk"


def test_parse_procedure_yaml_file_roundtrips(tmp_path: Path) -> None:
    yaml_file = tmp_path / "procedure.yaml"
    yaml_file.write_text(
        """
id: procedure.vanilla_base
steps:
  - action: procedure.mix
""",
        encoding="utf-8",
    )

    procedure = parse_procedure_yaml_file(yaml_file)

    assert procedure.id == "procedure.vanilla_base"
    assert procedure.steps[0].action.identifier == "mix"
