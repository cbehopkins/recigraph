# Ingredient

## Purpose

An Ingredient represents a single physical ingredient that may be used by one or more recipes.

Ingredients describe *what* the ingredient is.

They do not describe *how* it is used within a particular recipe.

---

# Required Fields

## `id`

Unique identifier for the ingredient.

The identifier is used throughout the DSL when referring to the ingredient.

Example:

```yaml
id: whole_milk
```

Rules:

* unique within all Ingredients
* lowercase
* snake_case
* immutable once published

---

## `name`

Human-readable display name.

Example:

```yaml
name: Whole Milk
```

The name is intended for presentation and does not need to be unique.

---

# Optional Fields

## `family`

Groups similar ingredients together.

Example:

```yaml
family: milk
```

Ingredient families are primarily used for browsing, searching and analysis.

---

## `aliases`

Alternative names that authors or users may recognise.

Example:

```yaml
aliases:
  - Full Fat Milk
  - Whole Cow's Milk
```

Aliases have no semantic meaning.

---

## `description`

Optional descriptive text.

Supports Markdown.

---

## `default_unit`

The preferred unit when this ingredient is used without an explicit unit.

Example:

```yaml
default_unit: ml
```

Future versions of the DSL may restrict this to a controlled vocabulary.

---

## `notes`

Optional author-facing notes.

Supports Markdown.

---

## `tags`

Optional collection of descriptive tags.

Example:

```yaml
tags:
  - dairy
  - refrigerated
```

Tags assist searching and categorisation.

---

# Minimal Example

```yaml
id: whole_milk

name: Whole Milk
```

---

# Complete Example

```yaml
id: whole_milk

name: Whole Milk

family: milk

aliases:
  - Full Fat Milk

description: Whole cow's milk.

default_unit: ml

notes: |
  Best results use full-fat milk.

tags:
  - dairy
  - refrigerated
```

---

# Relationships

Ingredients do not contain references to recipes.

Instead, recipes reference ingredients.

This ensures that relationships are defined in one direction only and can be analysed automatically by the compiler.

---

# Validation Rules

An Ingredient is valid if:

* required fields are present
* the identifier is unique
* the identifier matches the required format
* optional fields contain values of the correct type
* aliases do not contain duplicates
* tags do not contain duplicates

Validation rules are enforced by the compiler.
