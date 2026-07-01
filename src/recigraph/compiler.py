"""Phase 9 compiler orchestrator entry points."""

from pathlib import Path

from recigraph.loader import parse_procedure_yaml_file, parse_procedure_yaml_text
from recigraph.model import CompilationContext, CompilerOutput, Procedure
from recigraph.resolver import (
    RegistrySet,
    ResolvedProcedureReferences,
    resolve_procedure_references,
    run_resolved_procedure_loop,
)
from recigraph.validation import assert_valid_procedure_structure

COMPILATION_PASS_SEQUENCE = (
    "parse",
    "validate",
    "resolve",
    "initialize_graph",
    "apply_step_transformations",
    "produce_graph_ir",
    "emit_output",
)


def _append_pass(context: CompilationContext, pass_name: str) -> CompilationContext:
    """Append a pass name to the immutable compilation trace."""

    return context.model_copy(update={"compilation_trace": (*context.compilation_trace, pass_name)})


def _pass_parse_yaml_text(yaml_input: str) -> Procedure:
    """Parse YAML text input into a Procedure AST node."""

    return parse_procedure_yaml_text(yaml_input)


def _pass_parse_yaml_file(path: str | Path) -> Procedure:
    """Parse a YAML file path into a Procedure AST node."""

    return parse_procedure_yaml_file(path)


def _pass_validate(procedure: Procedure, *, context: CompilationContext) -> CompilationContext:
    """Validate procedure structure and carry forward compiler context."""

    assert_valid_procedure_structure(procedure)
    return _append_pass(context.model_copy(update={"procedure": procedure}), "validate")


def _pass_resolve(
    context: CompilationContext,
) -> tuple[ResolvedProcedureReferences, CompilationContext]:
    """Resolve references from the validated Procedure."""

    if context.procedure is None:
        raise ValueError("Cannot resolve references without a validated procedure")

    resolved = resolve_procedure_references(context.procedure, registries=context.registries)
    return resolved, _append_pass(
        context.model_copy(update={"resolved_reference_count": len(resolved.references)}),
        "resolve",
    )


def _pass_apply_step_transformations(
    context: CompilationContext,
    resolved: ResolvedProcedureReferences,
) -> CompilationContext:
    """Initialize G0 and apply ordered step transformations."""

    final_graph, trace = run_resolved_procedure_loop(resolved, registries=context.registries)
    context = _append_pass(context, "initialize_graph")
    context = _append_pass(context, "apply_step_transformations")
    context = _append_pass(context, "produce_graph_ir")
    return context.model_copy(update={"current_graph": final_graph, "trace": trace})


def _pass_emit_output(context: CompilationContext) -> CompilerOutput:
    """Emit the final compiler output from pass-produced context state."""

    if context.current_graph is None:
        raise ValueError("Cannot emit compiler output before graph transformation")
    return CompilerOutput(final_graph=context.current_graph, trace=context.trace)


def _run_compilation_passes_with_context(
    procedure: Procedure,
    *,
    registries: RegistrySet,
    initial_trace: tuple[str, ...] = (),
) -> tuple[CompilerOutput, CompilationContext]:
    """Run explicit passes and return both output and final compilation context."""

    context = CompilationContext(registries=registries, compilation_trace=initial_trace)
    context = _pass_validate(procedure, context=context)
    resolved, context = _pass_resolve(context)
    context = _pass_apply_step_transformations(context, resolved)
    output = _pass_emit_output(context)
    context = _append_pass(context, "emit_output")
    return output, context


def _run_compilation_passes(procedure: Procedure, *, registries: RegistrySet) -> CompilerOutput:
    """Run the explicit compiler pass pipeline for an already parsed Procedure."""

    output, _ = _run_compilation_passes_with_context(procedure, registries=registries)
    return output


def compile_procedure(
    procedure: Procedure,
    *,
    registries: RegistrySet,
) -> CompilerOutput:
    """Compile an already parsed Procedure through validation/resolution/transform."""

    return _run_compilation_passes(procedure, registries=registries)


def compile(yaml_input: str, *, registries: RegistrySet) -> CompilerOutput:
    """Compile YAML text into a final graph and execution trace."""

    procedure = _pass_parse_yaml_text(yaml_input)
    output, _ = _run_compilation_passes_with_context(
        procedure,
        registries=registries,
        initial_trace=("parse",),
    )
    return output


def compile_file(path: str | Path, *, registries: RegistrySet) -> CompilerOutput:
    """Compile a YAML file from disk into a final graph and execution trace."""

    procedure = _pass_parse_yaml_file(path)
    output, _ = _run_compilation_passes_with_context(
        procedure,
        registries=registries,
        initial_trace=("parse",),
    )
    return output
