# ReciGraph DSL

The ReciGraph Domain-Specific Language (DSL) defines the authoring format used to describe recipes as structured knowledge.

The DSL is intentionally independent of the compiler implementation.

Authors write YAML using the DSL.

The compiler validates that YAML, resolves relationships between entities and produces one or more outputs such as websites, books or shopping lists.

---

# Design Goals

The DSL has five primary goals.

## Human Readable

Recipes should remain pleasant to author and review using ordinary text editors.

YAML is chosen because it is concise, widely understood and works well with version control.

## Declarative

The DSL describes **what exists**, not **how it should be rendered**.

Presentation concerns belong to renderers rather than the language itself.

## Strongly Structured

Every entity has a well-defined schema.

Relationships between entities are explicit.

This allows the compiler to validate the knowledge base before publication.

## Composable

Reusable components should exist exactly once.

Recipes are assembled from reusable building blocks rather than duplicated documents.

## Stable

The DSL is the public interface of ReciGraph.

The compiler implementation may evolve over time without requiring changes to authored content.

---

# Language Overview

The DSL consists of a number of entity types.

Examples include:

* Ingredient
* Procedure
* Step
* Ingredient Family
* Ingredient Choice
* Equipment
* Container

Each entity has:

* an identifier
* a defined schema
* relationships to other entities where appropriate

The complete language specification is organised into one document per entity type.

---

# Entity References

Relationships between entities are expressed using dotted references.

For example:

```yaml
target: ingredient.whole_milk
```

The syntax is described in detail in `references.md`.

---

# Versioning

The DSL should evolve conservatively.

Whenever practical, changes should remain backwards compatible.

Breaking changes should be introduced only when there is a clear long-term benefit and accompanied by migration guidance.

The compiler implementation may change freely provided the published DSL remains stable.
