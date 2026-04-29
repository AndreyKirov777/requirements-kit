---
id: GLOSS-TEMPLATE
title: "[PROJECT_NAME] Glossary"
domain: all
updated: YYYY-MM-DD
---

# [PROJECT_NAME] Glossary

This glossary defines business and domain terms for [PROJECT_NAME] and maps them to code identifiers. AI agents must use `code_name` values when creating or modifying source code.

> **Template:** Replace the examples below with your project's domain terms. See `_examples/00-meta/glossary/dbp.md` for a fully worked example (Digital Battery Passport).

## Core Terms

### [Term Name]

| Field      | Value                                                               |
| ---------- | ------------------------------------------------------------------- |
| Definition | Clear definition of what this term means in your domain             |
| Code Name  | `termName`                                                          |
| Type       | `object` / `string` / `number` / `module` / `role`                 |
| Aliases    | Other names people might use for this concept                       |

### [Another Term]

| Field      | Value                                                               |
| ---------- | ------------------------------------------------------------------- |
| Definition | ...                                                                 |
| Code Name  | `anotherTerm`                                                       |
| Type       | ...                                                                 |
| Aliases    | ...                                                                 |

## Naming Rules

1. **Variables and function parameters**: use `code_name` in camelCase as listed above.
2. **Database columns**: use snake_case version of `code_name` (e.g., `term_name`).
3. **API fields**: use camelCase `code_name` in JSON payloads.
4. **Config keys**: use kebab-case (e.g., `term-name`).
5. **Never invent synonyms.** If you need a new term, add it to this glossary first.
