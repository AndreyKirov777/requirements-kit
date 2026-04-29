---
id: META-TAXONOMY-DOMAINS
title: Domain Registry
updated: YYYY-MM-DD
---

# Domain Registry

This file lists all recognized domains for [PROJECT_NAME]. Use these values in the `domain` frontmatter field. AI agents should not create new domains without adding them here first.

> **Template:** Replace the examples below with your project's domains. See `_examples/00-meta/taxonomy/domains.md` for a fully worked example (Digital Battery Passport with 8 domains).

## Domains

### [DOMAIN-CODE] — [Domain Full Name]

| Field       | Value                                                      |
| ----------- | ---------------------------------------------------------- |
| Code        | [DOMAIN-CODE]                                              |
| Full Name   | [Domain Full Name]                                         |
| Description | Brief description of what this domain covers               |
| Owner       | @owner                                                     |

## How to Add a New Domain

1. Choose a short uppercase code that does not conflict with existing domains.
2. Add it to this file with owner and description.
3. Update the glossary in `00-meta/glossary/` with domain-specific terms.
4. Create or update the code-map in `03-architecture/code-map/`.
5. Update this document's date.
