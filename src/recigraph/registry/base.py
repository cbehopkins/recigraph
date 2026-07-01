"""Base registry protocol for entity lookups."""

from typing import Protocol, TypeVar

T = TypeVar("T")


class EntityRegistry(Protocol[T]):
    """Protocol for domain-scoped entity registries."""

    def get(self, identifier: str) -> T | None:
        """Retrieve entity by identifier, or None if not found."""
        ...

    def exists(self, identifier: str) -> bool:
        """Check if entity with identifier exists."""
        ...

    def add(self, identifier: str, entity: T) -> None:
        """Register an entity with an identifier."""
        ...


class InMemoryRegistry[T]:
    """Simple in-memory registry backed by a dictionary."""

    def __init__(self) -> None:
        self._entities: dict[str, T] = {}

    def get(self, identifier: str) -> T | None:
        """Retrieve entity by identifier, or None if not found."""
        return self._entities.get(identifier)

    def exists(self, identifier: str) -> bool:
        """Check if entity with identifier exists."""
        return identifier in self._entities

    def add(self, identifier: str, entity: T) -> None:
        """Register an entity with an identifier."""
        self._entities[identifier] = entity

    def _all(self) -> dict[str, T]:
        """Return all registered entities (for testing/inspection only)."""
        return self._entities.copy()
