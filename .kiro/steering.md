# AI Agent Instructions — Kiro Requirements Vault Integration

This repository contains both source code and a requirements vault for [PROJECT_NAME]. This file tells Kiro (Amazon's AI coding agent) how to work with the requirements system.

## Project Context

[PROJECT_NAME] is organized around a structured product vision and domain-driven architecture. Key concepts:
- **Multi-tier data architecture**: [TIER_1] (raw ingestion) → [TIER_2] (validated/normalized) → [TIER_3] (business-ready outputs)
- **Access control model**: Configurable user tiers with field-level visibility rules
- **Completeness tracking**: Every entity has a `[completenessMetric]` per data cluster
- Read `01-product/vision/PRODUCT-VISION.md` for the full product vision.

## Domains

The system is organized into multiple domains. See `00-meta/taxonomy/domains.md` for the full registry.

## Before Starting Any Task

1. **Find your task.** Look in `04-delivery/tasks/` for a `TASK-*` file with `status: ready` assigned to you (or unassigned).

2. **Read the requirement.** Follow the `implements` field to the parent functional requirement (FR) in `02-requirements/fr/`. Read the full file — especially the **Requirement** section (what the system shall do) and **Out of Scope** (what NOT to do). Then follow `part_of_story` to the User Story (US) in `02-requirements/user-stories/` to read the **Acceptance Criteria** (how we verify the delivered value) and understand the "why" and "for whom".

3. **Check dependencies.** Read `depends_on` — verify those requirements are already `implemented` or `verified`. If not, flag a blocker.

4. **Read the ADR.** Follow `related_adrs` in the requirement to understand architectural constraints and decisions.

5. **Find target files.** Check `target_files` in the task, or look up `03-architecture/code-map/[PROJECT_NAME].md` for the component mapping.

6. **Read the glossary.** Check `00-meta/glossary/[DOMAIN].md` for domain-specific terminology. Use the specified `code_name` for all identifiers (e.g., if glossary specifies `batteryPassport`, use that consistently — not `passport`, `battery_data`, or other variants).

7. **Check constraints.** Read `02-requirements/constraints/` — understand all applicable constraints for this work.

## During Implementation

- Read the **User Story** (`US-*` file via `part_of_story`) first to understand the business purpose and **Acceptance Criteria** — it tells you "why", "for whom", and "how we verify".

- Write code that satisfies each acceptance criterion (AC-N) in the user story (`US-*`) — the FR tells you "what the system shall do", the AC in the US tells you "how we accept it":
  - Acceptance criteria use **Given/When/Then** format with `AC-N` identifiers
  - Example: `Given [precondition] When [action] Then [expected outcome]` with ID `AC-1`
  - Each AC must be testable (unit, integration, e2e, or manual)

- Follow naming conventions from the glossary — do not invent new names for existing concepts.

- Respect the three-tier architecture: never write directly to [TIER_3] layer from [TIER_1] (ingestion) code.

- Respect constraints from `02-requirements/constraints/`.

- If you need to make an architectural choice not covered by an existing ADR, create a new `ADR-*` file in `03-architecture/adr/` with status `proposed` and stop for review.

## After Implementation

1. **Update the task.** Set `status: done` in the TASK file.

2. **Update the requirement.** Add your implementation files to `implemented_by` (use relative paths from repo root). If all tasks for this requirement are done, transition `status: in-implementation` → `implemented`.

3. **Write or update tests.** Ensure each acceptance criterion (AC-N) has a corresponding test. Link tests in `verified_by`.

4. **Run validation.** Execute `python scripts/validate-frontmatter.py` to check all frontmatter is valid.

5. **Check orphans.** Execute `python scripts/check-orphans.py` to ensure no requirements are left without tests.

## Status Transitions

See `00-meta/status-transitions.md` for allowed state changes per artifact type. **Do not skip states** — always follow the defined progression (e.g., `proposed` → `approved` → `in-implementation` → `implemented` → `verified`).

## ID Format

All artifact IDs follow: `<TYPE>-<DOMAIN>-<NNN>` where:
- **TYPE**: EPIC, FR, US, NFR, ADR, CR, TEST, CON, TASK
- **DOMAIN**: uppercase domain code (see `00-meta/taxonomy/domains.md`)
- **NNN**: three or more digits, zero-padded

When creating new artifacts, check existing IDs in the target folder and increment sequentially.

## Acceptance Criteria Format

Acceptance criteria use **Given/When/Then** format in the markdown body (not YAML frontmatter):

```
## Acceptance Criteria

**AC-1**: Given [precondition], When [action], Then [expected outcome]
**AC-2**: Given [precondition], When [action], Then [expected outcome]

Each AC must be testable via: unit test | integration test | e2e test | manual test
```

- Map each AC to at least one test in `verified_by`
- All test references must exist and have status `passed`
- Do not change ACs once a requirement is `approved` or higher

## What NOT to Do

- **Do not modify approved artifacts without a Change Request (CR).** If an FR or US has status `approved` or higher, you must file a `CR-*` before making changes.

- **Do not delete or rename artifact files.** Deprecate them instead by adding `deprecated: true` to frontmatter.

- **Do not modify PRODUCT-VISION.md or EPIC-* files.** These require human approval.

- **Do not commit code that breaks existing verified acceptance criteria.** All `verified_by` tests must continue to pass.

- **Do not bypass the multi-tier architecture.** Follow [TIER_1] → [TIER_2] → [TIER_3] data flow.

- **Do not hardcode access rules or domain logic.** Use configurable policy engines for role and attribute-based access control (see related ADRs).

- **Do not invent new identifiers or naming patterns.** Always check the glossary first and use the specified `code_name`.

## Workflow Summary

```
Find task (TASK-*)
  ↓
Read functional requirement (FR-*)
  ↓
Read user story (US-*)
  ↓
Check dependencies (depends_on)
  ↓
Read architecture decision records (ADR-*)
  ↓
Identify target files (code-map)
  ↓
Check glossary for naming conventions
  ↓
Implement against acceptance criteria (AC-N)
  ↓
Write/update tests
  ↓
Update statuses (task → requirement → tests)
  ↓
Run validation scripts
```

## Key Files to Check First

- `00-meta/status-transitions.md` — allowed state changes
- `00-meta/taxonomy/domains.md` — domain registry
- `00-meta/glossary/[DOMAIN].md` — naming conventions
- `01-product/vision/PRODUCT-VISION.md` — product context
- `03-architecture/code-map/[PROJECT_NAME].md` — component mapping
- `02-requirements/constraints/` — project-wide constraints
