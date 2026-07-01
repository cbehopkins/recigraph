## ReciGraph DSL

The ReciGraph DSL is the YAML-based authoring language used to describe recipes as structured, reusable knowledge.

It is a declarative public interface, not an execution language.

### What the DSL Defines

The DSL describes the core culinary domain using immutable, strongly structured entities such as:

- Ingredients
- Procedures
- Steps
- Equipment
- Containers
- Entity references between those concepts

### What the DSL Does Not Define

- Rendering details
- Runtime execution
- Mutable application state
- Presentation-specific fields

Those concerns belong to the compiler pipeline and renderers.

### Reference Syntax

Entity relationships use stable dotted references such as `ingredient.whole_milk` and `procedure.vanilla_base`.

Binding and substitution logic is always local to a Step and never propagates between Steps.

### Reading Order

For the full language and compiler model, start with:

1. [docs/architecture.md](architecture.md)
2. [docs/dsl/README.md](dsl/README.md)
3. [docs/dsl/grammar.md](dsl/grammar.md)
4. [docs/dsl/references.md](dsl/references.md)
5. [docs/dsl/procedure.md](dsl/procedure.md)
6. [docs/dsl/step.md](dsl/step.md)
7. [docs/dsl/step_semantics.md](dsl/step_semantics.md)

### Versioning

The DSL should evolve conservatively.

Breaking changes require clear migration guidance and should be avoided unless they materially improve the language.
