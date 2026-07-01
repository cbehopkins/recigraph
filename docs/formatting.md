# Text Output Formatting (v1)

This document defines the canonical plain-text output produced by the current renderer.

The goal is deterministic output that can be validated with golden files in `examples/*/expected/output.txt`.

## Scope

This specification applies to CLI text output from `recigraph render`.

It does not apply to HTML output.

## Section Structure

Output is rendered in this order:

1. Recipe title
2. Ingredients section
3. Equipment section (optional)
4. Method section

Each section is separated by a blank line.

## Canonical Shape

```text
<Title>

Ingredients

• <Ingredient 1>
• <Ingredient 2>
...

Equipment

• <Equipment 1>
• <Equipment 2>
...

Method

1. <Sentence 1>.
2. <Sentence 2>.
...
```

If no equipment is available, the entire `Equipment` section is omitted.

## Style Rules

1. Oxford comma is required for three or more list items in method sentences.
2. Two-item method lists use `and` without a comma.
3. Method lines are sentence-cased and end with a period.
4. Ingredient and equipment bullet labels use their display names from source data.

## Determinism Rules

1. Output must be byte-stable for identical input.
2. Output uses UTF-8 text encoding.
3. Output ends with a trailing newline.
4. Substitutions are reflected in rendered ingredients and method text.

## Substitution Behavior

When a step uses override substitutions:

1. Replaced ingredient targets are removed from rendered ingredients.
2. Replacement ingredient targets are included.
3. Method text must not mention substituted-away ingredients.

Example: if `ingredient.whole_milk` is substituted with `ingredient.oat_milk` and `ingredient.sugar`, rendered output should mention oat milk and sugar, not whole milk.

## Current Golden References

- `examples/001_hello_world/expected/output.txt`
- `examples/002_simple/expected/output.txt`
- `examples/003_equipment/expected/output.txt`
- `examples/004_substitution/expected/output.txt`
