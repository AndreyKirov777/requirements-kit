# AI Agent Instructions — {{PROJECT_NAME}}

<!--
CANONICAL SOURCE for all AI agent instruction files.
DO NOT EDIT the generated copies in the project root — edit this file instead,
then run: python {{VAULT_PREFIX}}/scripts/install-agent-files.py

Placeholders to customize for your project:
- {{PROJECT_NAME}}: Name of your product/project
- {{ONE_SENTENCE_PURPOSE}}: What the system does
- {{DOMAIN_LIST}}: Your architecture domain tags (e.g., "API, DATA, UI, AUTH")
- {{ARCHITECTURE_PATTERN}}: Brief description of your data/system architecture
- {{KEY_CONCEPT_1}}: Primary domain concept
- {{KEY_CONCEPT_2}}: Secondary domain concept
- {{GLOSSARY_DOMAIN}}: Domain name in your glossary
-->

This repository contains both source code and a requirements vault for {{PROJECT_NAME}} — a system for {{ONE_SENTENCE_PURPOSE}}. This section tells AI coding agents how to work with the requirements system.

## Product Context

{{PROJECT_NAME}} is built around these key concepts:

- **{{ARCHITECTURE_PATTERN}}**: Brief description of your layered/tiered/modular architecture and how data flows through it
- **{{KEY_CONCEPT_1}}**: Explanation of a primary domain entity (e.g., a core resource, model, or user role)
- **{{KEY_CONCEPT_2}}**: Explanation of another key pattern or constraint (e.g., access control, validation rules, state management)
- Read `{{VAULT_PREFIX}}/01-product/vision/PRODUCT-VISION.md` for the full product vision.

## Domains

The system is organized into domains: {{DOMAIN_LIST}}. See `{{VAULT_PREFIX}}/00-meta/taxonomy/domains.md` for the full registry.

## Before Starting Any Task

1. **Find your task.** Look in `{{VAULT_PREFIX}}/04-delivery/tasks/` for a `TASK-*` file with `status: ready` assigned to you (or unassigned).
2. **Read the requirement.** Follow the `implements` field to the parent functional requirement (FR) in `{{VAULT_PREFIX}}/02-requirements/fr/`. Read the full file — especially the **Requirement** section (what the system shall do) and **Out of Scope** (what NOT to do). Then follow `part_of_story` to the User Story (US) in `{{VAULT_PREFIX}}/02-requirements/user-stories/` to read the **Acceptance Criteria** (how we verify the delivered value) and understand the "why" and "for whom".
3. **Trace the "why".** Follow the `derives_from` field in the FR/NFR to the parent artifact. This may be a business rule (`BR-*` in `{{VAULT_PREFIX}}/01-product/business-rules/`), a control (`CTRL-*` in `{{VAULT_PREFIX}}/01-product/controls/`), a constraint (`CON-*` in `{{VAULT_PREFIX}}/01-product/constraints/`), or a business requirement (`BRQ-*` in `{{VAULT_PREFIX}}/01-product/business-requirements/`). BRQ tells you the business or regulatory motivation; BR encodes the specific domain rule or regulatory logic; CTRL specifies what must be enforced and what evidence is needed; CON defines external constraints (business, regulatory, or technical) that limit the solution space. If a BRQ or CON has a `source_ref` field, follow it to the Source Document (`SRC-*` in `{{VAULT_PREFIX}}/01-product/sources/`) to read the original regulation, strategy, or policy text.
4. **Check dependencies.** Read `depends_on` — verify those requirements are already `implemented` or `verified`. If not, flag a blocker.
5. **Read the architecture.** Start with `{{VAULT_PREFIX}}/03-architecture/architecture-overview.md` for the system-wide picture. If your task belongs to a specific domain, read the corresponding `ARCH-{DOMAIN}-*` file. Then follow `related_adrs` in the requirement to understand specific decisions.
6. **Find target files.** Check `target_files` in the task, or look up `{{VAULT_PREFIX}}/03-architecture/code-map/` for the component mapping.
7. **Read the glossary.** Check `{{VAULT_PREFIX}}/00-meta/glossary/{{GLOSSARY_DOMAIN}}.md` for the domain. Use the specified `code_name` for all identifiers (do not invent alternate names).
8. **Check constraints.** Read `{{VAULT_PREFIX}}/01-product/constraints/` — these define external constraints (business, regulatory, or technical) that limit the solution space.

## During Implementation

- Read the **User Story** (`US-*` file via `part_of_story`) first to understand the business purpose and **Acceptance Criteria** — it tells you "why", "for whom", and "how we verify".
- Write code that satisfies each acceptance criterion (AC-N) in the user story (`US-*`) — the FR tells you "what the system shall do", the AC in the US tells you "how we accept it".
- Follow naming conventions from the glossary — do not invent new names for existing concepts.
- Use the code names specified in the glossary, not alternate variants or abbreviations.
- Respect the {{ARCHITECTURE_PATTERN}} architecture: do not bypass intended data flow or layer separation.
- Respect constraints from `{{VAULT_PREFIX}}/01-product/constraints/`.
- If you need to make an architectural choice not covered by an existing ADR, create a new `ADR-*` file in `{{VAULT_PREFIX}}/03-architecture/adr/` with status `proposed` and stop for review.

## After Implementation

1. **Update the task.** Set `status: done` in the TASK file.
2. **Update the requirement status.** If all tasks for this FR are done, set `status: implemented`. (Reverse links like `implemented_by` and `verified_by` are computed automatically by the traceability script — do not add them manually.)
3. **Write or update tests.** Ensure each acceptance criterion has a corresponding test. Set the `verifies` field in the TEST file to link to the FR/NFR.
4. **Run validation.** Execute `python {{VAULT_PREFIX}}/scripts/validate-frontmatter.py --path {{VAULT_PREFIX}}` to check all metadata is valid.
5. **Check duplicates.** Execute `python {{VAULT_PREFIX}}/scripts/check-duplicates.py` to ensure all IDs are unique and filenames match.
6. **Check orphans.** Execute `python {{VAULT_PREFIX}}/scripts/check-orphans.py` to ensure no requirements are left without tests.

## Status Transitions

See `{{VAULT_PREFIX}}/_framework/status-transitions.md` for allowed state changes per artifact type. Do not skip states.

## Requirement Hierarchy

The kit follows a layered requirement model aligned with BABOK and INCOSE:

- **SRC** (Source Document) = ORIGIN — the regulation, strategy, policy, standard, or contract from which requirements are extracted. Passive reference artifact — no lifecycle, no ownership. Lives in `01-product/sources/`.
- **BRQ** (Business Requirement) = WHY — the business or regulatory motivation
- **CTRL** (Control) = WHAT MUST BE ENFORCED/PROVEN — auditable control statement (compliance-driven projects only)
- **FR/NFR/CON** (System Requirements) = WHAT THE SYSTEM SHALL DO
- **ADR/ARCH** (Design) = HOW WE CHOSE TO DO IT
- **TEST** (Evidence) = HOW WE PROVE IT

Traceability chain: `[SRC →] BRQ → [BR →] [CTRL →] Epic → FR ↔ US → TASK → TEST`

**SRC** (Source Document) is a passive reference artifact — a regulation, strategy, policy, standard, or contract stored as structured markdown in `01-product/sources/`. SRC has no lifecycle statuses, no ownership, and does not participate in the obligation stack. BRQ and CON can reference specific SRC sections via the `source_ref` field (e.g., `SRC-GDPR-001#article-17`). Not all projects need SRC — it is optional and most useful for regulatory-driven or strategy-driven projects where traceability to original documents is important.

**BR** (Business Rule) encodes atomic, verifiable domain facts — regulatory logic, contractual conditions, and business policies. BR derives from BRQ and sits between BRQ (why) and FR/NFR (what the system does). Lives in `01-product/business-rules/`. Compliance tier — optional for non-regulated projects.

**CON** (Constraint) lives in `01-product/constraints/` — external forces (business, regulatory, or technical) that shape the solution space before requirements elaboration. Each CON has a `constraint_type` field: `business`, `regulatory`, or `technical`. Core tier — relevant to any project.

FR and US are **peer-level**: FR defines *what the system shall do* (technical spec), US defines *for whom* and carries **Acceptance Criteria**. They link to each other via `delivers`/`delivered_by`. Both link to their parent Epic via `parent_epic`.

For standard projects, CTRL is optional — BRQ links directly to FR/NFR via `derives_from`. For compliance-driven projects, CTRL sits between BRQ and FR/NFR to provide the auditable layer.

## ID Format

All artifact IDs follow: `<TYPE>-<DOMAIN>-<NNN>` where:
- TYPE: EPIC, FR, NFR, US, TASK, TEST, ADR, CR, CON (core); PERSONA, JOURNEY, ASSUM, UC (discovery); BRQ, BR, CTRL (compliance); SRC (source documents); ARCH, CONTRACT, DM (architecture); RISK, REL (delivery); VISION
- DOMAIN: uppercase domain code (use your domain list)
- NNN: three or more digits, zero-padded

When creating new artifacts, check existing IDs in the target folder and increment. The filename must match the ID exactly (e.g., `FR-INGEST-001.md` for `id: FR-INGEST-001`). IDs must be globally unique across the entire vault — run `python {{VAULT_PREFIX}}/scripts/check-duplicates.py` to verify.

## Acceptance Criteria Format

Acceptance criteria live in **User Story** files (`US-*`), not in FR or Task files. They use structured Given/When/Then format in the markdown body only — NOT in frontmatter:

```markdown
# Acceptance Criteria

- **AC-1**
  - **Given:** [precondition or initial state]
  - **When:** [action or trigger]
  - **Then:** [expected outcome or assertion]
  - **Testable by:** unit | integration | e2e | manual

- **AC-2**
  - **Given:** [precondition or initial state]
  - **When:** [action or trigger]
  - **Then:** [expected outcome or assertion]
  - **Testable by:** unit | integration | e2e | manual
```

Tasks reference AC from their parent User Story via `acceptance_criteria_subset` in frontmatter. Map each AC to at least one test case.

## What NOT to Do

**Regulatory & Approval:**
- Do not change functional requirements (FR) or user stories (US) with status `approved` or higher without a Change Request (`CR-*`).
- Do not change business requirements (BRQ) or controls (CTRL) with status `approved` or higher without a Change Request (`CR-*`). Changes to BRQ/CTRL require impact analysis on all derived artifacts.
- Do not modify `PRODUCT-VISION.md` or `EPIC-*` files without human approval.

**Code & Architecture:**
- Do not bypass the {{ARCHITECTURE_PATTERN}} architecture or intended data flow.
- Do not hardcode configuration that should be externalized — check constraints and ADRs for configurable patterns.
- Do not introduce technologies not listed in `{{VAULT_PREFIX}}/03-architecture/architecture-overview.md` without proposing a new ADR.
- Do not commit code that breaks existing verified acceptance criteria.

**Repository Hygiene:**
- Do not delete or rename artifact files — deprecate them instead.
- Do not create FR/NFR/CON without linking to at least one BRQ via `derives_from` — orphan system requirements must be flagged.
- Do not modify requirements after a CR has been approved — create a new CR instead.

**Naming & Consistency:**
- Do not invent new names for existing concepts. Always use the `code_name` from the glossary.
- Do not use variant spellings or abbreviations of standard identifiers.

## Glossary and Naming Rules

**Domain-specific terminology** is defined in `{{VAULT_PREFIX}}/00-meta/glossary/{{GLOSSARY_DOMAIN}}.md` with assigned `code_name` values. These code names are mandatory for all code, comments, and documentation.

**Standard naming conventions:**
- **Database fields & code identifiers** use `camelCase` (e.g., `entityId`, `qualityScore`, `createdAt`).
- **File paths & module names** use `kebab-case` (e.g., `main-entity`, `access-control`, `data-validation`).
- **User-facing labels** follow domain convention (may use spaces, title case, etc.).
- **Constants** use `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`, `DEFAULT_TIMEOUT`).

**Consistency rules:**
- If the glossary defines a concept, use its `code_name` everywhere.
- If you encounter a term not in the glossary, check related ADRs and existing code for usage patterns.
- If a term is truly new and not in the glossary, flag it during PR review so it can be added.

## Reference: Workflow Summary

```
┌─────────────────────────────────────────────────────────┐
│                    BEFORE IMPLEMENTATION                │
├─────────────────────────────────────────────────────────┤
│ 1. Find TASK-* with status: ready                       │
│ 2. Read FR-* (Requirement, Out of Scope)               │
│ 3. Trace BRQ-*/CTRL-* (and SRC-* via source_ref)       │
│ 4. Read US-* (Business context & AC)                    │
│ 5. Verify depends_on (check blockers)                   │
│ 6. Read architecture & ADRs (constraints)               │
│ 7. Find target_files and code-map locations            │
│ 8. Check glossary (code_name consistency)              │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                 DURING IMPLEMENTATION                    │
├─────────────────────────────────────────────────────────┤
│ • Write code satisfying each AC-N                       │
│ • Use glossary code_names, never invent identifiers    │
│ • Respect architecture patterns                         │
│ • Externalize policy-driven behavior                    │
│ • Keep scope tight (acceptance criteria only)          │
│ • Do not hardcode configuration or access rules        │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   AFTER IMPLEMENTATION                   │
├─────────────────────────────────────────────────────────┤
│ 1. Update TASK status: done                            │
│ 2. Update FR status if all tasks done                  │
│ 3. Write tests covering each AC-N                       │
│ 4. Set verifies field in TEST files                     │
│ 5. Run validate-frontmatter.py                          │
│ 6. Run check-orphans.py                                 │
│ 7. Commit code + tests                                  │
│ 8. Do NOT commit code breaking verified ACs            │
└─────────────────────────────────────────────────────────┘
```

## Key Reminders

- **Read before coding.** Always read the full requirement, user story, and ADRs before writing code.
- **Acceptance criteria are law.** Implement exactly what AC-N says, nothing more or less.
- **Glossary is canonical.** Use code_names from the glossary; do not invent variants.
- **Tests are required.** Every AC must have at least one passing test before marking done.
- **Architecture matters.** Respect layered architecture and externalize policy-driven behavior.
- **Dependencies first.** Never implement a task if its dependencies are not `implemented` or `verified`.
- **Trace the "why".** Always understand the business motivation (BRQ) and any control requirements (CTRL) behind each requirement.
- **Human approval required.** Do not transition status on EPIC, US, FR, BRQ, or CTRL to `approved` without human review.
