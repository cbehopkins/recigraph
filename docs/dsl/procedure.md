# Procedure

## Purpose

A Procedure defines a **deterministic, ordered sequence of Steps** that transforms a graph of entities.

Procedures are not execution units.

Procedures are not workflows.

Procedures are compile-time transformation specifications composed of Steps.

---

# Core Concept

A Procedure defines a transformation pipeline:

G₀ → G₁ → G₂ → ... → Gₙ

Where each transition is produced by a Step.

---

# Procedure Structure

Procedure :=
{
    id: string,

    name?: string,

    description?: string,

    steps: [Step],

    inputs?: [EntityReference],

    outputs?: [EntityReference],

    tags?: [string]
}

---

# Fields

## id (required)

Unique identifier within the procedure registry.

Example:
procedure.vanilla_base

---

## name (optional)

Human-readable label for documentation and UI.

---

## description (optional)

Free-text explanation of the Procedure’s intent.

---

## steps (required)

An ordered list of Step definitions.

Steps define **compile-time graph transformations**.

Execution is strictly sequential in semantic order.

---

## inputs (optional)

A declarative list of expected input entities.

Inputs define:

- required entities for compilation
- validation constraints
- initial graph expectations

Inputs are NOT runtime parameters.

---

## outputs (optional)

A declarative list of expected final entities after compilation.

Outputs define:

- validation targets
- expected end-state of graph
- rendering expectations

Outputs do NOT define computation.

---

## tags (optional)

Classification metadata for tooling and discovery.

Examples:
- "base"
- "dessert"
- "vegan"
- "quick"

---

# Execution Model (IMPORTANT)

A Procedure is compiled as:

1. Initialize graph state G₀ from inputs
2. Apply Step[0] → G₁
3. Apply Step[1] → G₂
4. ...
5. Apply Step[n] → Gₙ

Each Step:
- receives only current graph state
- applies local bindings only
- produces next graph state
- does not mutate prior states

---

# Key Principle

A Procedure is:

> a declarative ordered list of graph rewrite operations

NOT:

- a script
- a runtime workflow
- a function body
- a control flow program

---

# Step Relationship

Procedures:

- contain Steps
- define order of transformation
- do NOT define behavior of transformation

Steps:

- define transformation logic
- apply local bindings
- produce graph rewrites

---

# Input / Output Semantics

## Inputs

Inputs define the **initial constraints of the graph**.

They are:

- validated against entity registry
- injected into G₀
- NOT mutable during compilation

---

## Outputs

Outputs define the **expected final state of the graph**.

They are:

- used for validation
- used for downstream rendering
- NOT computed directly

---

# No Binding Propagation

IMPORTANT v1 constraint:

- bindings are strictly local to each Step
- Procedures do NOT propagate state between Steps
- no cross-Step mutation or context sharing

Each Step operates independently on Gₙ.

---

# No Step Composition (v1)

Steps may NOT:

- call other Steps
- embed Procedures recursively
- dynamically generate Step sequences

All Steps are statically defined at compile time.

---

# Determinism

Given identical input:

- same Procedure
- same Steps
- same entity registry

The compiled output graph is always identical.

---

# Compilation Model

The compiler processes Procedures as:

### Phase 1: Load
Parse YAML into Procedure AST

### Phase 2: Initialize
Build initial graph state G₀

### Phase 3: Transform
Apply Steps sequentially:

G₀ → G₁ → G₂ → ... → Gₙ

### Phase 4: Validate
Check:
- output correctness
- entity resolution
- structural integrity

### Phase 5: Emit
Produce final resolved graph for rendering

---

# Relationship to References

Procedures operate on:

- EntityReference (identity layer)
- ReferenceBinding (local transformation layer)

But:

- do NOT modify reference definitions
- do NOT persist bindings outside Step scope

---

# Relationship to Step Semantics

This model depends on Step being:

- pure
- local
- deterministic
- graph-transformational

Procedures simply sequence those transformations.

---

# Stability

Procedures are part of the public DSL contract.

The compiler may optimise execution internally, but:

- Step order must be preserved semantically
- transformation results must remain deterministic

---

# Design Principle

Procedures are:

- declarative pipelines
- ordered transformation graphs
- compile-time only constructs

They define **structure of change**, not execution.
