"""Concrete domain-specific registries."""

from recigraph.registry.base import InMemoryRegistry


class IngredientRegistry(InMemoryRegistry[str]):
    """Registry for ingredient entities."""

    pass


class ProcedureRegistry(InMemoryRegistry[str]):
    """Registry for procedure entities."""

    pass


class EquipmentRegistry(InMemoryRegistry[str]):
    """Registry for equipment entities."""

    pass


class ContainerRegistry(InMemoryRegistry[str]):
    """Registry for container entities."""

    pass
