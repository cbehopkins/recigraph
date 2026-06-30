# Step Semantics (v1)

## Purpose

A Step defines a **deterministic compile-time transformation** of a recipe graph.

Steps do not execute.

Steps do not maintain state.

Steps produce a new **resolved graph state** during compilation.

---

# Core Model

At any point in compilation, the system maintains:

Graph State Gₙ

Each Step transforms:

Gₙ → Gₙ₊₁

---

# Step Structure

Step :=
{
    id?: string,

    action: EntityReference,

    inputs?: [ReferenceBinding],

    outputs?: [EntityReference],

    context?: StepContext
}

---

# Fundamental Rule

## A Step is a pure function over graph state

A Step:

- reads from the current graph state
- applies local bindings
- produces a new graph state
- does NOT mutate previous states

---

# Locality Rule (CRITICAL)

## Bindings are strictly local to a Step

Any override or substitution:

- applies ONLY within the Step
- does NOT propagate to other Steps
- does NOT modify global graph state
- does NOT persist after Step completion

---

# Step Evaluation Model

Each Step is evaluated as:

### 1. Resolve action
Resolve the procedure referenced by `action`

---

### 2. Snapshot input state
Take current graph state Gₙ

---

### 3. Apply local bindings
For each input ReferenceBinding:

- resolve EntityReference
- apply override (if present)
- apply substitutions (if present)

This produces a **Step-local working graph**

---

### 4. Execute procedure structure (compile-time expansion)

The action procedure is expanded into its internal Steps (if any).

IMPORTANT:

- This is NOT execution
- This is AST expansion / flattening

---

### 5. Produce transformed graph state

The Step emits:

Gₙ₊₁ = transformed version of Gₙ

Rules:
- only entities affected by Step are rewritten
- unchanged entities are passed through unchanged
- no global mutation occurs

---

# Key Concept: “Graph Rewrite Step”

A Step is best understood as:

> A scoped graph rewrite rule applied at a single point in a linear pipeline

---

# Outputs

## outputs are declarative only

outputs define expected results:

- for validation
- for tooling
- for downstream steps (structural reference only)

They do NOT define computation.

---

# Identity Rule

Entity identity is immutable.

A Step may:

- create new derived entities
- transform references
- substitute structures

But it may NOT:

- modify base entity definitions
- mutate global registry entities

---

# Isolation Rule

Each Step:

- sees only Gₙ
- produces only Gₙ₊₁
- cannot access future steps
- cannot modify past steps

---

# Determinism Rule

Given:

- same input graph
- same steps
- same bindings

The output graph is always identical.

---

# No Runtime Semantics

The system has:

- no execution engine
- no runtime state
- no event model
- no partial evaluation

Only compilation passes.

---

# Conditional Logic (v1 constraint)

Conditionals, if present, are:

- resolved at compile time
- evaluated as graph selection rules
- not runtime branches

---

# Step Ordering Rule

Steps in a Procedure are:

- strictly ordered
- sequentially applied
- never parallelized in semantics (though compiler may optimise internally)

---

# Composition Rule (v1)

Steps do NOT call other Steps.

A Step may reference a Procedure via `action`, but:

- it is expanded at compile time
- not executed recursively at runtime

---

# Mental Model

A Step is:

> a scoped, deterministic graph rewrite applied in sequence

NOT:

- a function call
- a runtime instruction
- a workflow task
- a mutation event

---

# Compiler Responsibility

The compiler must:

- maintain graph state G₀ → Gₙ
- apply Steps sequentially
- enforce locality of bindings
- ensure deterministic transformations
- validate reference resolution at each stage

---

# Output of Compilation

The final result of a Procedure is:

- a fully resolved graph
- suitable for rendering into:
  - website
  - PDF
  - shopping list
  - AI indexing

---

# Summary

Step semantics in v1:

- pure compile-time transformation
- local-only bindings
- sequential graph rewriting
- deterministic output
- no runtime system
