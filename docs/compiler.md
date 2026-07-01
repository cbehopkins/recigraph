## ReciGraph Compiler

ReciGraph is a deterministic, single-pass compiler for a YAML-authored recipe DSL.

The compiler transforms authored domain models into a resolved graph representation and a trace of the transformations that produced it.

The compiler is not the top-level website generation entrypoint.

Top-level orchestration lives in the build layer (`recigraph.build`), which coordinates discovery, compilation, view-model construction, renderer execution and output management.

Renderer architecture details and boundaries are defined in [docs/decisions/adr-010.md](decisions/adr-010.md).

### Pipeline

The compiler is organised into a fixed linear flow:

1. Parse YAML into domain models.
2. Validate schema and structural constraints.
3. Resolve dotted entity references through registries.
4. Initialise graph state from procedure inputs.
5. Apply each Step as a pure graph transformation through a graph rewrite engine.
6. Emit final graph state plus execution trace.

### Compilation Context

Compilation state is carried through passes using an explicit `CompilationContext` object.

The context is immutable and stores pass-relevant state such as:

- compiler configuration
- registries
- diagnostics
- current graph snapshot
- compilation trace

The context is pass-local and explicit. It is not a global singleton.

### Pass Structure

The orchestration layer exposes explicit pass boundaries in order:

1. Parse
2. Validate
3. Resolve
4. Initialise Graph
5. Apply Step Transformations
6. Emit CompilerOutput

This keeps compiler flow easy to follow while preserving single-pass deterministic behavior.

### Graph Transformation Engine

Step execution semantics are owned by `GraphTransformer` (`DefaultGraphTransformer` by default).

`procedure_loop` is responsible for ordered Step iteration only.

The transformer is responsible for:

- step-local binding rewrites
- graph snapshot transitions
- transformation trace records
- graph IR relationship/provenance updates

### Core Constraints

- Domain objects are immutable.
- Reference bindings are Step-local only.
- The compiler performs graph rewrites only; it does not execute recipes.
- Presentation concerns belong to renderers, not the DSL.

### Source of Truth

The authoritative DSL and compiler references live in:

- [docs/architecture.md](architecture.md)
- [docs/dsl/README.md](dsl/README.md)
- [docs/dsl/compiler_spec.md](dsl/compiler_spec.md)
- [docs/dsl/grammar.md](dsl/grammar.md)
- [docs/dsl/references.md](dsl/references.md)
- [docs/dsl/procedure.md](dsl/procedure.md)
- [docs/dsl/step.md](dsl/step.md)
- [docs/dsl/step_semantics.md](dsl/step_semantics.md)

The compiler documentation is intentionally narrow: it describes the transformation model and the implementation boundaries, not renderer-specific behaviour.
