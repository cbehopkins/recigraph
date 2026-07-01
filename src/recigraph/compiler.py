"""Phase 9 compiler orchestrator entry points."""

from pathlib import Path

from recigraph.loader import parse_procedure_yaml_file, parse_procedure_yaml_text
from recigraph.model import CompilerOutput, Procedure
from recigraph.resolver import (
    RegistrySet,
    resolve_procedure_references,
    run_resolved_procedure_loop,
)
from recigraph.validation import assert_valid_procedure_structure


def compile_procedure(
    procedure: Procedure,
    *,
    registries: RegistrySet,
) -> CompilerOutput:
    """Compile an already parsed Procedure through validation/resolution/transform."""

    assert_valid_procedure_structure(procedure)
    resolved = resolve_procedure_references(procedure, registries=registries)
    final_graph, trace = run_resolved_procedure_loop(resolved, registries=registries)
    return CompilerOutput(final_graph=final_graph, trace=trace)


def compile(yaml_input: str, *, registries: RegistrySet) -> CompilerOutput:
    """Compile YAML text into a final graph and execution trace."""

    procedure = parse_procedure_yaml_text(yaml_input)
    return compile_procedure(procedure, registries=registries)


def compile_file(path: str | Path, *, registries: RegistrySet) -> CompilerOutput:
    """Compile a YAML file from disk into a final graph and execution trace."""

    procedure = parse_procedure_yaml_file(path)
    return compile_procedure(procedure, registries=registries)
