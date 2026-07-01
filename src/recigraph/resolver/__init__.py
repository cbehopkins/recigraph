"""Reference resolution utilities for ReciGraph."""

from recigraph.resolver.graph_init import initialize_graph_state
from recigraph.resolver.resolver import (
    ReferenceResolutionError,
    RegistrySet,
    ResolutionIssue,
    ResolvedProcedureReferences,
    ResolvedReference,
    default_registry_set,
    resolve_procedure_references,
    resolve_reference,
)
from recigraph.resolver.step_engine import apply_step

__all__ = [
    "ReferenceResolutionError",
    "RegistrySet",
    "ResolutionIssue",
    "ResolvedProcedureReferences",
    "ResolvedReference",
    "apply_step",
    "default_registry_set",
    "initialize_graph_state",
    "resolve_procedure_references",
    "resolve_reference",
]
