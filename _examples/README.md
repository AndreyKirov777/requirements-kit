# Examples

This folder contains one working example of each artifact type from the DBP (Digital Battery Passport) project.

Use these files as a reference when creating your own artifacts. Each example shows correct frontmatter structure, content format, and linking conventions.

## What is here

The examples form **one coherent, cross-linked project** so you can see a full trace
chain end to end. The obligation chain runs
`SRC-COMPLY-001 → BRQ-COMPLY-001 → BR-COMPLY-001 → FR-INGEST-001` (with the security
branch `BRQ-SEC-001 → CTRL-SEC-001 → NFR-SEC-001` and constraint `CON-SEC-001`), and
the solution structure runs `EPIC-INGEST-001 ⊃ (FR-INGEST-001 ↔ US-INGEST-001) →
TASK-INGEST-001 → TEST-INGEST-001`.

Every example validates against its schema and passes all kit scripts
(`validate-frontmatter`, `check-duplicates`, `check-orphans`,
`check-status-transitions`). Try `python scripts/assemble-context.py TASK-INGEST-001`
to see the whole chain assembled into one bundle.

| Folder | Example file | Artifact type |
|--------|-------------|---------------|
| `00-meta/glossary/` | `dbp.md` | Domain glossary |
| `00-meta/taxonomy/` | `domains.md` | Domain and component registry |
| `01-product/vision/` | `PRODUCT-VISION.md` | Product vision (VISION) |
| `01-product/sources/` | `SRC-COMPLY-001.md` | Source document (SRC) |
| `01-product/personas/` | `PERSONA-DBP-001.md`, `PERSONA-DBP-002.md` | User personas |
| `01-product/journeys/` | `JOURNEY-DBP-001.md` | User journey |
| `01-product/assumptions/` | `ASSUM-DBP-001.md` | Assumption |
| `01-product/use-cases/` | `UC-INGEST-001.md` | Use case |
| `01-product/business-requirements/` | `BRQ-COMPLY-001.md`, `BRQ-SEC-001.md` | Business requirements |
| `01-product/business-rules/` | `BR-COMPLY-001.md` | Business rule |
| `01-product/controls/` | `CTRL-SEC-001.md` | Compliance control |
| `01-product/constraints/` | `CON-SEC-001.md` | Constraint (regulatory) |
| `02-requirements/epics/` | `EPIC-INGEST-001.md` | Epic |
| `02-requirements/fr/` | `FR-INGEST-001.md` | Functional requirement |
| `02-requirements/nfr/` | `NFR-SEC-001.md` | Non-functional requirement |
| `02-requirements/user-stories/` | `US-INGEST-001.md` | User story |
| `03-architecture/` | `architecture-overview.md`, `ARCH-INGEST-001.md` | Architecture overview + domain architecture |
| `03-architecture/adr/` | `ADR-INGEST-001.md` | Architecture decision record |
| `03-architecture/code-map/` | `dbp-accelerator.md` | Code map |
| `03-architecture/data-model/` | `DM-INGEST-001.md` | Data model |
| `03-architecture/contracts/` | `CONTRACT-INGEST-001.md` | API/interface contract |
| `04-delivery/tasks/` | `TASK-INGEST-001.md` | Implementation task |
| `04-delivery/change-requests/` | `CR-INGEST-001.md` | Change request |
| `04-delivery/risks/` | `RISK-INGEST-001.md` | Risk |
| `04-delivery/releases/` | `REL-DBP-001.md` | Release |
| `05-quality/acceptance/` | `TEST-INGEST-001.md`, `TEST-SEC-001.md` | Acceptance tests |
| `05-quality/traceability/` | `TRACEABILITY-MAP.md` | Traceability map (auto-generated) |

## How to use

1. Find the template for the artifact type you need in `_framework/templates/`.
2. Copy the template to the appropriate folder in the vault root.
3. Give it a stable ID: `TYPE-DOMAIN-NNN` (e.g., `FR-AUTH-001`).
4. Use the example here as a reference for filling in the content.
5. Run `python scripts/validate-frontmatter.py --path .` to verify.

Do not work directly in this folder — keep it as read-only reference.
