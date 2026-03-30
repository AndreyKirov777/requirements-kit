# Examples

This folder contains one working example of each artifact type from the DBP (Digital Battery Passport) project.

Use these files as a reference when creating your own artifacts. Each example shows correct frontmatter structure, content format, and linking conventions.

## What is here

| Folder | Example file | Artifact type |
|--------|-------------|---------------|
| `00-meta/glossary/` | `dbp.md` | Domain glossary (12 terms with code_names) |
| `00-meta/taxonomy/` | `domains.md` | Domain and component registry (8 domains) |
| `01-product/vision/` | `PRODUCT-VISION.md` | Product vision |
| `01-product/personas/` | `PERSONA-DBP-001.md` | User persona |
| `01-product/assumptions/` | `ASSUM-DBP-001.md` | Assumption |
| `02-requirements/epics/` | `EPIC-INGEST-001.md` | Epic |
| `02-requirements/fr/` | `FR-INGEST-001.md` | Functional requirement |
| `02-requirements/user-stories/` | `US-INGEST-001.md` | User story |
| `02-requirements/nfr/` | `NFR-SEC-001.md` | Non-functional requirement |
| `02-requirements/constraints/` | `CON-SEC-001.md` | Constraint |
| `03-architecture/adr/` | `ADR-INGEST-001.md` | Architecture decision record |
| `03-architecture/code-map/` | `dbp-accelerator.md` | Code map |
| `04-delivery/tasks/` | `TASK-INGEST-001.md` | Implementation task |
| `04-delivery/change-requests/` | `CR-INGEST-001.md` | Change request |
| `05-quality/acceptance/` | `TEST-INGEST-001.md` | Acceptance test |
| `05-quality/traceability/` | `TRACEABILITY-MAP.md` | Traceability map (auto-generated) |

## How to use

1. Find the template for the artifact type you need in `00-meta/templates/`.
2. Copy the template to the appropriate folder in the vault root.
3. Give it a stable ID: `TYPE-DOMAIN-NNN` (e.g., `FR-AUTH-001`).
4. Use the example here as a reference for filling in the content.
5. Run `python scripts/validate-frontmatter.py --path .` to verify.

Do not work directly in this folder — keep it as read-only reference.
