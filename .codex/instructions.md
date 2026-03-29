# AI Agent Instructions — [PROJECT_NAME]

This repository contains both source code and a requirements vault for [PROJECT_NAME]. This file tells AI coding agents (Codex, Cursor, Kiro) how to work with the requirements system.

## Product Context

[PROJECT_NAME] is organized around the following conceptual model:
- **Core domain concepts**: Read `01-product/vision/PRODUCT-VISION.md` for the full product vision and key business drivers.
- **Domain-specific data models and architecture**: Consult domain-specific documentation in `01-product/` or domain files in `02-requirements/`.
- **Access control framework**: Understand user tiers, data visibility rules, and permission models that govern the system.

## Domains

The system is organized into domains (e.g., DOMAIN-A, DOMAIN-B, DOMAIN-C, etc.). See `00-meta/taxonomy/domains.md` for the full registry and domain definitions.

---

## Before Starting Any Task

1. **Find your task.** Look in `04-delivery/tasks/` for a `TASK-*` file with `status: ready` assigned to you (or unassigned).

2. **Read the requirement.** Follow the `implements` field to the parent functional requirement (FR) in `02-requirements/fr/`. Read the full file — especially:
   - **Requirement** (what the system shall do)
   - **Out of Scope** (what NOT to do)

   Then follow `part_of_story` to the User Story (US) in `02-requirements/user-stories/` to read the **Acceptance Criteria** (how we verify the delivered value) and understand the "why" and "for whom".

3. **Check dependencies.** Read `depends_on` in the requirement — verify those requirements are already `implemented` or `verified`. If not, flag a blocker.

4. **Read the ADR.** Follow `related_adrs` in the requirement to understand architectural constraints, decisions, and patterns already established.

5. **Find target files.** Check `target_files` in the task, or look up `03-architecture/code-map/` for component mapping and file locations.

6. **Read the glossary.** Check `00-meta/glossary/` for domain-specific terminology. Use the specified `code_name` for all identifiers — never invent new names for existing concepts. This ensures consistency across the codebase.

7. **Check constraints.** Read `02-requirements/constraints/` — understand all constraints that apply to your domain and work.

---

## During Implementation

- **Start with the User Story** (US-* file via `part_of_story`) to understand business purpose and **Acceptance Criteria** — it tells you "why", "for whom", and "how we verify".

- **Write code that satisfies each acceptance criterion** (AC-N) in the user story (US-*) — the FR tells you "what the system shall do", the AC in the US tells you "how we accept it".

- **Follow naming conventions** from the glossary. Use established `code_name` identifiers, not variations or aliases. Consistency is critical for maintainability.

- **Respect the layered/tiered architecture** defined in ADRs. Do not bypass architectural patterns (e.g., do not write directly to protected layers from unsecured entry points).

- **Respect constraints** from `02-requirements/constraints/`. These are hard requirements, not suggestions.

- **Do not hardcode policy-driven behavior**. Any business logic that varies by user tier, access level, configuration, or regulation must be externalized to a policy engine or configuration layer (see ADRs for the approved pattern).

- **If you need to make an architectural choice not covered by an existing ADR**, create a new `ADR-*` file in `03-architecture/adr/` with status `proposed` and stop for review. Do not proceed without architectural approval.

- **Keep implementation focused**. Implement only what the acceptance criteria require. Do not add "nice-to-have" features, refactoring, or out-of-scope optimizations.

---

## After Implementation

1. **Update the task.** Set `status: done` in the TASK file.

2. **Update the requirement.** Add your implementation files to `implemented_by` (use relative paths from repo root). If all tasks for this requirement are done, transition `status: in-implementation` → `implemented`.

3. **Write or update tests.** Ensure each acceptance criterion (AC-N) has a corresponding test. Link tests in `verified_by` field. Tests must be committed alongside implementation code.

4. **Run validation.** Execute `python scripts/validate-frontmatter.py` to check all frontmatter is valid.

5. **Check orphans.** Execute `python scripts/check-orphans.py` to ensure no requirements are left without tests or implementations.

6. **Do not commit** code that breaks existing verified acceptance criteria.

---

## Status Transitions

See `00-meta/status-transitions.md` for allowed state changes per artifact type. Do not skip states — use the prescribed workflow.

Artifact types and their valid transitions:
- EPIC: `proposed` → `approved` → `released` (human approval only)
- US (User Story): `proposed` → `approved` → `released` (human approval only)
- FR (Functional Requirement): `proposed` → `approved` → `in-implementation` → `implemented` → `verified` → `released`
- NFR (Non-Functional Requirement): `proposed` → `approved` → `in-implementation` → `implemented` → `verified` → `released`
- ADR (Architecture Decision Record): `proposed` → `approved` → `adopted` (human approval)
- CR (Change Request): `proposed` → `approved` → `deployed`
- TASK: `ready` → `in-progress` → `done`
- TEST: `draft` → `ready` → `verified`

Only human actors can approve transitions marked `(human approval only)`. Do not force status changes you are not authorized to make.

---

## ID Format

All artifact IDs follow the pattern:
```
<TYPE>-<DOMAIN>-<NNN>
```

Where:
- **TYPE**: One of `EPIC`, `FR`, `US`, `NFR`, `ADR`, `CR`, `TEST`, `CON`, `TASK`
- **DOMAIN**: Uppercase domain code (e.g., DOMAIN-A, DOMAIN-B, DOMAIN-C, or the domains applicable to your project)
- **NNN**: Three or more digits, zero-padded (e.g., `001`, `042`, `567`)

**When creating new artifacts:**
1. Check existing IDs in the target folder to determine the next sequential number.
2. Increment from the highest existing ID.
3. Never reuse a retired or deleted ID.

---

## Acceptance Criteria Format

Acceptance criteria live in **User Story** files (`US-*`), not in FR or Task files. They use a **structured Given/When/Then format** in the markdown body ONLY (not in YAML frontmatter).

Format in markdown:
```markdown
### Acceptance Criteria

**AC-1:** [Brief description]
- Given [precondition]
- When [action]
- Then [expected outcome]

**AC-2:** [Brief description]
- Given [precondition]
- When [action]
- Then [expected outcome]
```

Tasks reference AC from their parent User Story via `acceptance_criteria_subset` in frontmatter. Do NOT use YAML frontmatter for acceptance criteria. All AC details (given/when/then/testable_by) go in the US markdown body.

**Map each AC to at least one test** in the `verified_by` field, using relative paths:
```yaml
verified_by:
  - tests/unit/test_feature.py::test_ac_1
  - tests/integration/test_feature.py::test_ac_2
```

---

## What NOT to Do

**Regulatory & Approval:**
- Do not change functional requirements (FR) or user stories (US) with status `approved` or higher without a Change Request (`CR-*`).
- Do not approve or transition status on requirements you did not author (human approval only for EPIC, US, FR transitions to `approved`).
- Do not modify `PRODUCT-VISION.md` or `EPIC-*` files without human approval.

**Code & Architecture:**
- Do not bypass the established layered/tiered architecture (e.g., do not write directly to protected layers from unsecured entry points).
- Do not hardcode access rules, data transformation rules, or business logic that varies by user tier or configuration — externalize to a policy engine.
- Do not commit code that breaks existing verified acceptance criteria.
- Do not refactor unrelated code in the same commit as implementing a task — keep commits focused.

**Repository Hygiene:**
- Do not delete or rename artifact files — deprecate them instead (add `status: deprecated` and document the replacement).
- Do not create orphaned requirements (every FR and US must link to a parent EPIC; every TASK must link to an FR or US).
- Do not merge code without tests covering all acceptance criteria.

**Naming & Consistency:**
- Do not invent new names for existing concepts. Always use the `code_name` from the glossary.
- Do not use variant spellings or abbreviations of standard identifiers (e.g., do not use `entityId` and `entityUID` interchangeably).

---

## Glossary and Naming Rules

**Domain-specific terminology** is defined in `00-meta/glossary/` with assigned `code_name` values. These code names are mandatory for all code, comments, and documentation.

**Standard naming conventions:**
- **Database fields & code identifiers** use `camelCase` (e.g., `entityId`, `qualityScore`, `createdAt`).
- **File paths & module names** use `kebab-case` (e.g., `main-entity`, `access-control`, `data-validation`).
- **User-facing labels** follow domain convention (may use spaces, title case, etc.).
- **Constants** use `UPPER_SNAKE_CASE` (e.g., `MAX_RETRIES`, `DEFAULT_TIMEOUT`).

**Consistency rules:**
- If the glossary defines a concept, use its `code_name` everywhere.
- If you encounter a term not in the glossary, check related ADRs and existing code for usage patterns.
- If a term is truly new and not in the glossary, flag it during PR review so it can be added to the glossary.

---

## Reference: Workflow Summary

```
┌─────────────────────────────────────────────────────────┐
│                    BEFORE IMPLEMENTATION                │
├─────────────────────────────────────────────────────────┤
│ 1. Find TASK-* with status: ready                       │
│ 2. Read FR-* (Requirement, Out of Scope)               │
│ 3. Read US-* (Business context)                         │
│ 4. Verify depends_on (check blockers)                   │
│ 5. Read related ADRs (architecture constraints)         │
│ 6. Find target_files and code-map locations            │
│ 7. Check glossary (code_name consistency)              │
│ 8. Review applicable constraints                        │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                 DURING IMPLEMENTATION                    │
├─────────────────────────────────────────────────────────┤
│ • Write code satisfying each AC-N                       │
│ • Use glossary code_names, never invent identifiers    │
│ • Respect layered architecture patterns                 │
│ • Externalize policy-driven behavior                    │
│ • Keep scope tight (acceptance criteria only)          │
│ • Do not hardcode configuration or access rules        │
└─────────────────────────────────────────────────────────┘
                            ↓
┌─────────────────────────────────────────────────────────┐
│                   AFTER IMPLEMENTATION                   │
├─────────────────────────────────────────────────────────┤
│ 1. Update TASK status: done                            │
│ 2. Add implementation_by to FR-*                        │
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
- **Human approval required.** Do not transition status on EPIC, US, or FR to `approved` without human review.

---

## Questions?

If you encounter:
- **Missing ADR** for an architectural choice → create one with status `proposed` and stop for review.
- **Ambiguous requirement** → ask in PR comments or task discussion.
- **Conflicting constraints** → flag in the task and request clarification.
- **Out-of-scope request** → check "Out of Scope" in the FR; if unclear, ask before proceeding.

Good luck, and happy coding!
