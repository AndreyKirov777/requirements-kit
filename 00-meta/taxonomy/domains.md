---
id: META-TAXONOMY-DOMAINS
title: Domain and Component Registry
updated: YYYY-MM-DD
---

# Domain and Component Registry

This file lists all recognized domains and their components for [PROJECT_NAME]. Use these values in the `domain` and `component` frontmatter fields. AI agents should not create new domains or components without adding them here first.

> **Template:** Replace the examples below with your project's domains. See `_examples/00-meta/taxonomy/domains.md` for a fully worked example (Digital Battery Passport with 8 domains).

## Domains

### [DOMAIN-CODE] — [Domain Full Name]

| Field       | Value                                                      |
| ----------- | ---------------------------------------------------------- |
| Code        | [DOMAIN-CODE]                                              |
| Full Name   | [Domain Full Name]                                         |
| Description | Brief description of what this domain covers               |
| Owner       | @owner                                                     |
| Glossary    | [[glossary-file]] (`00-meta/glossary/[domain].md`)         |

**Components:**

| Component      | Code Path (see code-map)       | Description                                           |
| -------------- | ------------------------------ | ----------------------------------------------------- |
| component-name | `src/[domain]/[component]/`    | What this component does                              |

## How to Add a New Domain

1. Choose a short uppercase code that does not conflict with existing domains.
2. Add it to this file with owner, description, and initial components.
3. Create or update the glossary in `00-meta/glossary/` with domain-specific terms.
4. Create or update the code-map in `03-architecture/code-map/`.
5. Update this document's date.
