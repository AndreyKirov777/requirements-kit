# AI Agent Instructions — [PROJECT_NAME]

This repository contains both source code and a requirements vault for [PROJECT_NAME] — a system for [ONE-SENTENCE PURPOSE]. This file tells AI coding agents (Codex, Cursor, Kiro) how to work with the requirements system.

## Product Context

[PROJECT_NAME] is built around these key concepts:

- **[ARCHITECTURE_PATTERN]**: Brief description of your layered/tiered/modular architecture and how data flows through it
- **[KEY_CONCEPT_1]**: Explanation of a primary domain entity (e.g., a core resource, model, or user role)
- **[KEY_CONCEPT_2]**: Explanation of another key pattern or constraint (e.g., access control, validation rules, state management)
- Read `01-product/vision/PRODUCT-VISION.md` for the full product vision.

## Domains

The system is organized into domains: [DOMAIN_LIST]. See `00-meta/taxonomy/domains.md` for the full registry.

## Before Starting Any Task

1. **Find your task.** Look in `04-delivery/tasks/` for a `TASK-*` file with `status: ready` assigned to you (or unassigned).

2. **Read the requirement.** Follow the `implements` field to the parent functional requirement (FR) in `02-requirements/fr/`. Read the full file — especially the **Requirement** section (what the system shall do) and **Out of Scope** (what NOT to do). Then follow `part_of_story` to the User Story (US) in `02-requirements/user-stories/` to read the **Acceptance Criteria** (how we verify the delivered value) and understand the "why" and "for whom".

3. **Trace the "why".** Follow the `derives_from` field in the FR/NFR to the parent business requirement (`BRQ-*` in `02-requirements/business-requirements/`). This tells you the business or regulatory motivation. If the FR also has `implements_control`, read the control (`CTRL-*` in `02-requirements/controls/`) to understand what must be enforced and what evidence is needed.

4. **Check dependencies.** Read `depends_on` — verify those requirements are already `implemented` or `verified`. If not, flag a blocker.

5. **Read the architecture.** Start with `03-architecture/architecture-overview.md` for the system-wide picture. If your task belongs to a specific domain, read the corresponding `ARCH-{DOMAIN}-*` file. Then follow `related_adrs` in the requirement to understand specific decisions.

6. **Find target files.** Check `target_files` in the task, or look up `03-architecture/code-map/` for the component mapping.

7. **Read the glossary.** Check `00-meta/glossary/[GLOSSARY_DOMAIN].md` for the domain. Use the specified `code_name` for all identifiers (do not invent alternate names).

8. **Check constraints.** Read `02-requirements/constraints/` — these define non-functional and regulatory requirements.

---

## During Implementation

- Read the **User Story** (`US-*` file via `part_of_story`) first to understand the business purpose and **Acceptance Criteria** — it tells you "why", "for whom", and "how we verify".

- Write code that satisfies each acceptance criterion (AC-N) in the user story (`US-*`) — the FR tells you "what the system shall do", the AC in the US tells you "how we accept it".

- Follow naming conventions from the glossary — do not invent new names for existing concepts.

- Use the code names specified in the glossary, not alternate variants or abbreviations.

- Respect the [ARCHITECTURE_PATTERN] architecture: do not bypass intended data flow or layer separation.

- Respect constraints from `02-requirements/constraints/`.

- If you need to make an architectural choice not covered by an existing ADR, create a new `ADR-*` file in `03-architecture/adr/` with status `proposed` and stop for review.

---

## After Implementation

1. **Update the task.** Set `status: done` in the TASK file.

2. **Update the requirement.** Add your implementation files to `implemented_by` (use relative paths from repo root). If all tasks for this requirement are done, set `status: in-implementation` → `implemented`.

3. **Write or update tests.** Ensure each acceptance criterion has a corresponding test. Link tests in `verified_by` field. Tests must be in `05-quality/acceptance/`.

4. **Run validation.** Execute the frontmatter validation script to check all metadata is valid.

5. **Check orphans.** Execute the orphan-check script to ensure no requirements are left without tests.

6. **Do not commit** code that breaks existing verified acceptance criteria.

---

## Status Transitions

See `00-meta/status-transitions.md` for allowed state changes per artifact type. Do not skip states — use the prescribed workflow.

---

## Requirement Hierarchy

The kit follows a layered requirement model aligned with BABOK and INCOSE:

- **BRQ** (Business Requirement) = WHY — the business or regulatory motivation
- **CTRL** (Control) = WHAT MUST BE ENFORCED/PROVEN — auditable control statement (compliance-driven projects only)
- **FR/NFR/CON** (System Requirements) = WHAT THE SYSTEM SHALL DO
- **ADR/ARCH** (Design) = HOW WE CHOSE TO DO IT
- **TEST** (Evidence) = HOW WE PROVE IT

Traceability chain: `BRQ → [CTRL →] Epic → FR ↔ US → TASK → TEST`

FR and US are **peer-level**: FR defines *what the system shall do* (technical spec), US defines *for whom* and carries **Acceptance Criteria**. They link to each other via `delivers`/`delivered_by`. Both link to their parent Epic via `parent_epic`.

For standard projects, CTRL is optional — BRQ links directly to FR/NFR via `derives_from`. For compliance-driven projects, CTRL sits between BRQ and FR/NFR to provide the auditable layer.

---

## ID Format

All artifact IDs follow: `<TYPE>-<DOMAIN>-<NNN>` where:

- **TYPE**: One of `EPIC`, `FR`, `US`, `NFR`, `ADR`, `ARCH`, `CR`, `TEST`, `CON`, `TASK`, `BRQ`, `CTRL`, `UC`, `DM`, `RISK`, `REL`, `PERSONA`, `JOURNEY`, `ASSUM`, `CONTRACT`, `VISION`
- **DOMAIN**: uppercase domain code (use your domain list)
- **NNN**: three or more digits, zero-padded

When creating new artifacts, check existing IDs in the target folder and increment.

---

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

---

## What NOT to Do

**Regulatory & Approval:**
- Do not change functional requirements (FR) or user stories (US) with status `approved` or higher without a Change Request (`CR-*`).
- Do not change business requirements (BRQ) or controls (CTRL) with status `approved` or higher without a Change Request (`CR-*`). Changes to BRQ/CTRL require impact analysis on all derived artifacts.
- Do not approve or transition status on requirements you did not author (human approval only for EPIC, US, FR transitions to `approved`).
- Do not modify `PRODUCT-VISION.md` or `EPIC-*` files without human approval.

**Code & Architecture:**
- Do not bypass the [ARCHITECTURE_PATTERN] architecture or intended data flow.
- Do not hardcode configuration that should be externalized — check constraints and ADRs for configurable patterns.
- Do not introduce technologies not listed in `architecture-overview.md` without proposing a new ADR.
- Do not commit code that breaks existing verified acceptance criteria.
- Do not refactor unrelated code in the same commit as implementing a task — keep commits focused.

**Repository Hygiene:**
- Do not delete or rename artifact files — deprecate them instead (add `status: deprecated` and document the replacement).
- Do not create orphaned requirements (every FR and US must link to a parent EPIC; every TASK must link to an FR or US).
- Do not create FR/NFR/CON without linking to at least one BRQ via `derives_from` — orphan system requirements must be flagged.
- Do not modify requirements after a CR has been approved — create a new CR instead.
- Do not merge code without tests covering all acceptance criteria.

**Naming & Consistency:**
- Do not invent new names for existing concepts. Always use the `code_name` from the glossary.
- Do not use variant spellings or abbreviations of standard identifiers.

---

## Glossary and Naming Rules

**Domain-specific terminology** is defined in `00-meta/glossary/[GLOSSARY_DOMAIN].md` with assigned `code_name` values. These code names are mandatory for all code, comments, and documentation.

**Standard naming conventions:**
- **Database fields & code identifiers** use `camelCase` (e.g., `entityId`, `qualityScore`, `createdAt`).
- **File paths & module names** use `kebab-case` (e.g., `main-entity`, `access-control`, `data-validation`).
- **User-facing labels** follow domain convention (may use spaces, title case, etc.).
- **Constants** use `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`, `DEFAULT_TIMEOUT`).

**Consistency rules:**
- If the glossary defines a concept, use its `code_name` everywhere.
- If you encounter a term not in the glossary, check related ADRs and existing code for usage patterns.
- If a term is truly new and not in the glossary, flag it during PR review so it can be added.

---

## Cross-Agent Synchronization

Keep these files synchronized for consistent behavior:

- **CLAUDE.md** — Claude Code agent
- **.codex/instructions.md** — Codex agent (Visual Studio Code)
- **.cursor/rules/requirements-vault.mdc** — Cursor agent (Cursor IDE)
- **.kiro/** — Kiro agent (automation tasks)

Update all files when you change policies, glossary references, domain lists, or workflow steps.

---

## Reference: Workflow Summary

```
┌─────────────────────────────────────────────────────────┐
│                    BEFORE IMPLEMENTATION                │
├─────────────────────────────────────────────────────────┤
│ 1. Find TASK-* with status: ready                       │
│ 2. Read FR-* (Requirement, Out of Scope)               │
│ 3. Trace BRQ-* and CTRL-* (business & control logic)   │
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
│ • Respect [ARCHITECTURE_PATTERN] patterns               │
│ • Externalize policy-driven behavior                    │
│ • Keep scope tight (acceptance criteria only)          │
│ • Do not hardcode configuration or access rules        │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   AFTER IMPLEMENTATION                   │
├─────────────────────────────────────────────────────────┤
│ 1. Update TASK status: done                            │
│ 2. Add implemented_by to FR-*                          │
│ 3. Write tests covering each AC-N                       │
│ 4. Link tests in verified_by field                      │
│ 5. Run validate-frontmatter.py                          │
│ 6. Run check-orphans.py                                 │
│ 7. Commit code + tests                                  │
│ 8. Do NOT commit code breaking verified ACs            │
└─────────────────────────────────────────────────────────┘
```

---

## Key Reminders

- **Read before coding.** Always read the full requirement, user story, and ADRs before writing code.
- **Acceptance criteria are law.** Implement exactly what AC-N says, nothing more or less.
- **Glossary is canonical.** Use code_names from the glossary; do not invent variants.
- **Tests are required.** Every AC must have at least one passing test before marking done.
- **Architecture matters.** Respect layered architecture and externalize policy-driven behavior.
- **Dependencies first.** Never implement a task if its dependencies are not `implemented` or `verified`.
- **Trace the "why".** Always understand the business motivation (BRQ) and any control requirements (CTRL) behind each requirement.
- **Human approval required.** Do not transition status on EPIC, US, FR, BRQ, or CTRL to `approved` without human review.

---

## Questions?

If you encounter:
- **Missing ADR** for an architectural choice → create one with status `proposed` and stop for review.
- **Ambiguous requirement** → ask in PR comments or task discussion.
- **Conflicting constraints** → flag in the task and request clarification.
- **Out-of-scope request** → check "Out of Scope" in the FR; if unclear, ask before proceeding.

Good luck, and happy coding!
