## ReciGraph Compiler

ReciGraph is a deterministic, single-pass compiler for a YAML-authored recipe DSL.

The compiler transforms authored domain models into a resolved graph representation and a trace of the transformations that produced it.

### Pipeline

The compiler is organised into a fixed linear flow:

1. Parse YAML into domain models.
2. Validate schema and structural constraints.
3. Resolve dotted entity references through registries.
4. Initialise graph state from procedure inputs.
5. Apply each Step as a pure graph transformation.
6. Emit final graph state plus execution trace.

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
