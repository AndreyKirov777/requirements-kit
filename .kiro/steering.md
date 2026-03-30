# AI Agent Instructions — [PROJECT_NAME] (Kiro)

<!--
TEMPLATE NOTE: This is the Kiro agent variant of the AI agent instruction template.
Customize the placeholders below for your specific project:
- [PROJECT_NAME]: Name of your product/project
- [DOMAIN_LIST]: Your architecture domain tags (e.g., "API, DATA, UI, AUTH")
- [ARCHITECTURE_PATTERN]: Brief description of your data/system architecture
- [KEY_CONCEPT_1]: Primary domain concept (e.g., "Order", "User", "Document")
- [KEY_CONCEPT_2]: Secondary domain concept (e.g., access control, validation rules)
- [GLOSSARY_DOMAIN]: Domain name in your glossary

This template is shared across 4 agent instruction files (keep synchronized):
1. CLAUDE.md (Claude Code) — source of truth
2. .codex/instructions.md (Codex — Visual Studio Code)
3. .cursor/rules/requirements-vault.mdc (Cursor IDE)
4. .kiro/steering.md (Kiro agent — internal automation)
-->

This repository contains both source code and a requirements vault for [PROJECT_NAME] — a system for [ONE-SENTENCE PURPOSE]. This file tells Kiro (and other AI agents) how to work with the requirements system.

## Project Context

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

3. **Trace the why.** Follow the `derives_from` field in the FR/NFR to the parent business requirement (`BRQ-*` in `02-requirements/business-requirements/`). This tells you the business or regulatory motivation. If the FR also has `implements_control`, read the control (`CTRL-*` in `02-requirements/controls/`) to understand what must be enforced and what evidence is needed.

4. **Check dependencies.** Read `depends_on` — verify those requirements are already `implemented` or `verified`. If not, flag a blocker.

5. **Read the architecture.** Start with `03-architecture/architecture-overview.md` for the system-wide picture. If your task belongs to a specific domain, read the corresponding `ARCH-{DOMAIN}-*` file. Then follow `related_adrs` in the requirement to understand specific decisions.

6. **Find target files.** Check `target_files` in the task, or look up `03-architecture/code-map/` for the component mapping.

7. **Read the glossary.** Check `00-meta/glossary/[GLOSSARY_DOMAIN].md` for the domain. Use the specified `code_name` for all identifiers (do not invent alternate names).

8. **Check constraints.** Read `02-requirements/constraints/` — these define non-functional and regulatory requirements.

## During Implementation

- Read the **User Story** (`US-*` file via `part_of_story`) first to understand the business purpose and **Acceptance Criteria** — it tells you "why", "for whom", and "how we verify".
- Write code that satisfies each acceptance criterion (AC-N) in the user story (`US-*`) — the FR tells you "what the system shall do", the AC in the US tells you "how we accept it".
- Follow naming conventions from the glossary — do not invent new names for existing concepts.
- Use the code names specified in the glossary, not alternate variants or abbreviations.
- Respect the [ARCHITECTURE_PATTERN] architecture: do not bypass intended data flow or layer separation.
- Respect constraints from `02-requirements/constraints/`.
- If you need to make an architectural choice not covered by an existing ADR, create a new `ADR-*` file in `03-architecture/adr/` with status `proposed` and stop for review.

## After Implementation

1. **Update the task.** Set `status: done` in the TASK file.
2. **Update the requirement.** Add your implementation files to `implemented_by` (use relative paths from repo root). If all tasks for this requirement are done, set `status: in-implementation` → `implemented`.
3. **Write or update tests.** Ensure each acceptance criterion has a corresponding test. Link tests in `verified_by`.
4. **Run validation.** Execute the frontmatter validation script to check all metadata is valid.
5. **Check orphans.** Execute the orphan-check script to ensure no requirements are left without tests.

## Status Transitions

See `00-meta/status-transitions.md` for allowed state changes per artifact type. Do not skip states — always follow the defined progression.

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

## ID Format

All artifact IDs follow: `<TYPE>-<DOMAIN>-<NNN>` where:

- **TYPE**: EPIC, FR, US, NFR, ADR, ARCH, CR, TEST, CON, TASK, BRQ, CTRL, UC, DM, RISK, REL, PERSONA, JOURNEY, ASSUM, CONTRACT, VISION
- **DOMAIN**: uppercase domain code (use your domain list)
- **NNN**: three or more digits, zero-padded

When creating new artifacts, check existing IDs in the target folder and increment sequentially.

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

- Do not change functional requirements (FR) or user stories (US) with status `approved` or higher without a Change Request (`CR-*`).
- Do not change business requirements (BRQ) or controls (CTRL) with status `approved` or higher without a Change Request (`CR-*`). Changes to BRQ/CTRL require impact analysis on all derived artifacts.
- Do not delete or rename artifact files — deprecate them instead.
- Do not modify `PRODUCT-VISION.md` or `EPIC-*` files without human approval.
- Do not commit code that breaks existing verified acceptance criteria.
- Do not bypass the [ARCHITECTURE_PATTERN] architecture or intended data flow.
- Do not introduce technologies not listed in `architecture-overview.md` without proposing a new ADR.
- Do not hardcode configuration that should be externalized — check constraints and ADRs for configurable patterns.
- Do not modify requirements after a CR has been approved — create a new CR instead.
- Do not create FR/NFR/CON without linking to at least one BRQ via `derives_from` — orphan system requirements must be flagged.

## Cross-Agent Synchronization

Keep these files synchronized for consistent behavior:

- **CLAUDE.md** (Claude Code agent) — source of truth
- **.codex/instructions.md** (Codex agent, Visual Studio Code)
- **.cursor/rules/requirements-vault.mdc** (Cursor agent, Cursor IDE)
- **.kiro/steering.md** (this file) — Kiro agent

Update all files when you change policies, glossary references, domain lists, or workflow steps.

## Traceability Chain

End-to-end traceability from business driver through verification:

```
BRQ (Business Requirement)
 ↓
[CTRL (Control — optional, compliance projects only)]
 ↓
EPIC (Product epic)
 ↓
FR (Functional Requirement) ↔ US (User Story)
 ↓
TASK (Implementation task)
 ↓
TEST (Verification artifact)
```

**Key rules:**
- Every FR/NFR/CON must have `derives_from: BRQ-*` or `implements_control: CTRL-*`
- Every FR must have `part_of_story: US-*` (peer-level link)
- Every US must have `delivered_by: FR-*` (peer-level link)
- Every TASK must have `implements: FR-*` and `acceptance_criteria_subset: [AC-1, AC-2, ...]`
- Every TEST must have `verifies: US-*` and `status: passed` before US reaches `verified`

## Workflow Summary

```
Task ready (TASK-*)
  ↓
Read FR-* → Out of Scope
  ↓
Read US-* → Acceptance Criteria
  ↓
Trace BRQ-* and CTRL-* (if any)
  ↓
Check depends_on (blocker detection)
  ↓
Read ARCH-{DOMAIN}-* and ADR-*
  ↓
Identify target files (code-map)
  ↓
Check glossary ([GLOSSARY_DOMAIN].md)
  ↓
Implement against AC-N
  ↓
Write/update tests for each AC
  ↓
Update statuses: TASK → FR/US → TEST
  ↓
Run validation & orphan-check scripts
  ↓
Done
```

## Key Files to Check First

- `00-meta/status-transitions.md` — allowed state changes per artifact type
- `00-meta/taxonomy/domains.md` — domain registry
- `00-meta/glossary/[GLOSSARY_DOMAIN].md` — naming conventions and code names
- `01-product/vision/PRODUCT-VISION.md` — product context and constraints
- `02-requirements/business-requirements/` — BRQ artifacts (why)
- `02-requirements/controls/` — CTRL artifacts (what must be enforced)
- `02-requirements/fr/` — FR artifacts (what the system shall do)
- `02-requirements/user-stories/` — US artifacts (for whom, with AC)
- `02-requirements/constraints/` — non-functional and regulatory constraints
- `03-architecture/architecture-overview.md` — system-wide architecture
- `03-architecture/adr/` — architecture decision records
- `03-architecture/code-map/` — component mapping
- `04-delivery/tasks/` — implementation tasks
