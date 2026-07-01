"""Tests for the registry layer."""

from recigraph.registry import (
    ContainerRegistry,
    EquipmentRegistry,
    IngredientRegistry,
    ProcedureRegistry,
)


def test_ingredient_registry_get_existing() -> None:
    """Ingredient registry returns entity for existing identifier."""
    registry = IngredientRegistry()
    registry.add("whole_milk", "whole milk ingredient")

    assert registry.get("whole_milk") == "whole milk ingredient"


def test_ingredient_registry_get_missing() -> None:
    """Ingredient registry returns None for missing identifier."""
    registry = IngredientRegistry()

    assert registry.get("nonexistent") is None


def test_ingredient_registry_exists() -> None:
    """Ingredient registry exists() works correctly."""
    registry = IngredientRegistry()
    registry.add("whole_milk", "whole milk ingredient")

    assert registry.exists("whole_milk") is True
    assert registry.exists("nonexistent") is False


def test_procedure_registry_isolation() -> None:
    """Procedure registry is isolated from other registries."""
    proc_registry = ProcedureRegistry()
    ing_registry = IngredientRegistry()

    proc_registry.add("vanilla_base", "vanilla procedure")
    ing_registry.add("whole_milk", "whole milk ingredient")

    assert proc_registry.exists("vanilla_base") is True
    assert proc_registry.exists("whole_milk") is False

    assert ing_registry.exists("whole_milk") is True
    assert ing_registry.exists("vanilla_base") is False


def test_equipment_registry() -> None:
    """Equipment registry works independently."""
    registry = EquipmentRegistry()
    registry.add("blender", "blender equipment")

    assert registry.get("blender") == "blender equipment"
    assert registry.exists("blender") is True


def test_container_registry() -> None:
    """Container registry works independently."""
    registry = ContainerRegistry()
    registry.add("creami_pint", "creami pint container")

    assert registry.get("creami_pint") == "creami pint container"
    assert registry.exists("creami_pint") is True


def test_registry_multiple_entries() -> None:
    """Registry handles multiple entities of same domain."""
    registry = IngredientRegistry()
    registry.add("whole_milk", "whole milk ingredient")
    registry.add("sugar", "sugar ingredient")
    registry.add("vanilla", "vanilla ingredient")

    assert registry.get("whole_milk") == "whole milk ingredient"
    assert registry.get("sugar") == "sugar ingredient"
    assert registry.get("vanilla") == "vanilla ingredient"

    assert registry.exists("whole_milk") is True
    assert registry.exists("sugar") is True
    assert registry.exists("vanilla") is True
    assert registry.exists("cinnamon") is False


def test_registry_overwrite() -> None:
    """Registry allows overwriting entities."""
    registry = IngredientRegistry()
    registry.add("milk", "whole milk")
    registry.add("milk", "skim milk")

    assert registry.get("milk") == "skim milk"
