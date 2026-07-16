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

> **Shortcut:** `python {{VAULT_PREFIX}}/scripts/assemble-context.py TASK-XXX-NNN` collects the full trace chain below (task, requirement, user story with AC, obligation chain, related ADRs, target files) into a single markdown bundle — one read instead of ten. Use it, then only open individual files if you need more depth.
>
> The steps are **tiered**. Do the *always* steps for every task; do the *conditional* steps only when the trigger applies. This keeps the ritual cheap for simple tasks without cutting corners on complex ones.

**Always (every task):**

1. **Find your task.** Look in `{{VAULT_PREFIX}}/04-delivery/tasks/` for a `TASK-*` file with `status: ready` assigned to you (or unassigned).
<!-- IF-PROFILE M L -->
2. **Read the requirement.** Follow the `implements` field to the parent functional requirement (FR) in `{{VAULT_PREFIX}}/02-requirements/fr/`. Read the full file — especially the **Requirement** section (what the system shall do) and **Out of Scope** (what NOT to do). Then follow `part_of_story` to the User Story (US) in `{{VAULT_PREFIX}}/02-requirements/user-stories/` to read the **Acceptance Criteria** (how we verify the delivered value) and understand the "why" and "for whom".
<!-- END-IF -->
<!-- IF-PROFILE S -->
2. **Read the story.** Follow the `part_of_story` field to the parent User Story (US) in `{{VAULT_PREFIX}}/02-requirements/user-stories/` — in this project's profile there is no FR, so the User Story *is* the requirement. Read the full file, especially the **Acceptance Criteria** (how we verify the delivered value), and understand the "why" and "for whom".
<!-- END-IF -->
3. **Read the glossary.** Check `{{VAULT_PREFIX}}/00-meta/glossary/{{GLOSSARY_DOMAIN}}.md` for the domain. Use the specified `code_name` for all identifiers (do not invent alternate names).
4. **Find target files.** Check `target_files` in the task, or look up `{{VAULT_PREFIX}}/03-architecture/code-map/` for the component mapping.
5. **Check dependencies.** Read `depends_on` — verify those requirements are already `implemented` or `verified`. If not, flag a blocker.
6. **Read the architecture rules.** Read `{{VAULT_PREFIX}}/03-architecture/architecture-rules.md` — the normative rulebook auto-generated from accepted ADRs. Every rule is binding on every task; rules are cited by ID (e.g., `ADR-CORE-001.R2`) in reviews. Open the full ADR only when you need the rationale behind a rule.

**Conditional (only when the trigger applies):**

<!-- IF-PROFILE M L -->
7. **Trace the "why"** — *when the task touches compliance, security, or regulated behavior, or when the "what" is unclear.* Follow the `derives_from` field in the FR/NFR to the parent artifact: a business rule (`BR-*`), a control (`CTRL-*` in `{{VAULT_PREFIX}}/01-product/controls/`), a constraint (`CON-*` in `{{VAULT_PREFIX}}/01-product/constraints/`), or a business requirement (`BRQ-*`). BRQ tells you the business or regulatory motivation; BR encodes the specific domain rule or regulatory logic; CTRL specifies what must be enforced and what evidence is needed; CON defines external constraints that limit the solution space. If a BRQ or CON has a `source_ref` field, follow it to the Source Document (`SRC-*` in `{{VAULT_PREFIX}}/01-product/sources/`) for the original text.
<!-- END-IF -->
<!-- IF-PROFILE L -->
8. **Read the architecture** — *when `estimated_complexity: complex`, or the task introduces a component, integration, or data-model change.* Start with `{{VAULT_PREFIX}}/03-architecture/architecture-overview.md`, then the domain `ARCH-{DOMAIN}-*` file, then any ADRs whose `related_requirements` include your FR.
<!-- END-IF -->
<!-- IF-PROFILE M L -->
9. **Check constraints** — *when the task involves platform, performance, cost, or regulatory limits.* Read `{{VAULT_PREFIX}}/01-product/constraints/`.
<!-- END-IF -->

## During Implementation

- Read the **User Story** (`US-*` file via `part_of_story`) first to understand the business purpose and **Acceptance Criteria** — it tells you "why", "for whom", and "how we verify".
<!-- IF-PROFILE M L -->
- Write code that satisfies each acceptance criterion (AC-N) in the user story (`US-*`) — the FR tells you "what the system shall do", the AC in the US tells you "how we accept it".
<!-- END-IF -->
<!-- IF-PROFILE S -->
- Write code that satisfies each acceptance criterion (AC-N) in the user story (`US-*`) — in this profile the US itself is both "what" and "how we accept it" (there is no separate FR).
<!-- END-IF -->
- Follow naming conventions from the glossary — do not invent new names for existing concepts.
- Use the code names specified in the glossary, not alternate variants or abbreviations.
- Respect the {{ARCHITECTURE_PATTERN}} architecture: do not bypass intended data flow or layer separation.
- Respect every rule in `{{VAULT_PREFIX}}/03-architecture/architecture-rules.md`. If a rule blocks your intended approach, do not work around it silently — flag it, citing the rule ID.
<!-- IF-PROFILE M L -->
- Respect constraints from `{{VAULT_PREFIX}}/01-product/constraints/`.
<!-- END-IF -->
- If you need to make an architectural choice not covered by an existing ADR, create a new `ADR-*` file in `{{VAULT_PREFIX}}/03-architecture/adr/` with status `proposed` (including a draft `# Rules` section) and stop for review.

## After Implementation

1. **Update the task.** Set `status: done` in the TASK file.
<!-- IF-PROFILE M L -->
2. **Update the requirement status.** If all tasks for this FR are done, set `status: implemented`. (Reverse links like `implemented_by` and `verified_by` are computed automatically by the traceability script — do not add them manually.)
<!-- END-IF -->
<!-- IF-PROFILE S -->
2. **Update the requirement status.** If all tasks for this US are done, set `status: implemented`. (Reverse links like `implemented_by` and `verified_by` are computed automatically by the traceability script — do not add them manually.)
<!-- END-IF -->
<!-- IF-PROFILE M L -->
3. **Write or update tests.** Ensure each acceptance criterion has a corresponding test. Set the `verifies` field in the TEST file to link to the FR/NFR.
<!-- END-IF -->
<!-- IF-PROFILE S -->
3. **Write or update tests.** Ensure each acceptance criterion has a corresponding test. Set the `verifies` field in the TEST file to link to the US.
<!-- END-IF -->
4. **Run validation.** Execute `python {{VAULT_PREFIX}}/scripts/validate-frontmatter.py --path {{VAULT_PREFIX}}` to check all metadata is valid.
5. **Check duplicates.** Execute `python {{VAULT_PREFIX}}/scripts/check-duplicates.py` to ensure all IDs are unique and filenames match.
6. **Check orphans.** Execute `python {{VAULT_PREFIX}}/scripts/check-orphans.py` to ensure no requirements are left without tests.

## Status Transitions

See `{{VAULT_PREFIX}}/_framework/status-transitions.md` for allowed state changes per artifact type. Do not skip states.

## Requirement Hierarchy

<!-- IF-PROFILE S -->
This project uses profile **S** — the chain is intentionally short:

`VISION → US (carries Acceptance Criteria) → TASK (part_of_story) → TEST (verifies)`

with **ADR** (`03-architecture/adr/`) alongside: accepted ADRs feed `architecture-rules.md`, which is binding on every task. There is no FR/NFR/EPIC/CON layer in this profile — the User Story is both the "what" and the "for whom". If the project outgrows this profile, see the kit's upgrade path (profile M adds FR/NFR/EPIC/CON/CR).
<!-- END-IF -->
<!-- IF-PROFILE M L -->
The kit follows a layered requirement model aligned with BABOK and INCOSE:
<!-- END-IF -->

<!-- IF-FLAG sources -->
- **SRC** (Source Document) = ORIGIN — the regulation, strategy, policy, standard, or contract from which requirements are extracted. Passive reference artifact — no lifecycle, no ownership. Lives in `01-product/sources/`.
<!-- END-IF -->
<!-- IF-FLAG compliance -->
- **BRQ** (Business Requirement) = WHY — the business or regulatory motivation
- **CTRL** (Control) = WHAT MUST BE ENFORCED/PROVEN — auditable control statement (compliance-driven projects only)
<!-- END-IF -->
<!-- IF-PROFILE M L -->
- **FR/NFR/CON** (System Requirements) = WHAT THE SYSTEM SHALL DO
- **ADR/ARCH** (Design) = HOW WE CHOSE TO DO IT
- **TEST** (Evidence) = HOW WE PROVE IT

Traceability has **two distinct dimensions** — keep them separate:

- **Obligation chain** (why the system must act): `SRC → BRQ → BR / CTRL —(derives_from)→ FR / NFR`
- **Solution structure** (how the work is organized): `Epic ⊃ (FR ↔ US) → TASK → TEST`

An **Epic groups** solution-space work; it is *not* a link in the obligation chain (there is no semantic "CTRL → Epic" edge). FR/NFR carry the `derives_from` link into the obligation chain and `parent_epic` into the solution structure.
<!-- END-IF -->

<!-- IF-FLAG sources -->
**SRC** (Source Document) is a passive reference artifact — a regulation, strategy, policy, standard, or contract stored as structured markdown in `01-product/sources/`. SRC has no lifecycle statuses, no ownership, and does not participate in the obligation stack. BRQ and CON can reference specific SRC sections via the `source_ref` field (e.g., `SRC-GDPR-001#article-17`). Not all projects need SRC — it is optional and most useful for regulatory-driven or strategy-driven projects where traceability to original documents is important.
<!-- END-IF -->

<!-- IF-FLAG compliance -->
**BR** (Business Rule) encodes atomic, verifiable domain facts — regulatory logic, contractual conditions, and business policies. BR derives from BRQ and sits between BRQ (why) and FR/NFR (what the system does). Lives in `01-product/business-rules/`. Compliance tier — optional for non-regulated projects.
<!-- END-IF -->

<!-- IF-PROFILE M L -->
**CON** (Constraint) lives in `01-product/constraints/` — external forces (business, regulatory, or technical) that shape the solution space before requirements elaboration. Each CON has a `constraint_type` field: `business`, `regulatory`, or `technical`. Core tier — relevant to any project.

FR and US are **peer-level**: FR defines *what the system shall do* (technical spec), US defines *for whom* and carries **Acceptance Criteria**. They link to each other via `delivers`/`delivered_by`. Both link to their parent Epic via `parent_epic`.
<!-- END-IF -->

<!-- IF-FLAG compliance -->
For standard projects, CTRL is optional — BRQ links directly to FR/NFR via `derives_from`. For compliance-driven projects, CTRL sits between BRQ and FR/NFR to provide the auditable layer.
<!-- END-IF -->

## ID Format

All artifact IDs follow: `<TYPE>-<DOMAIN>-<NNN>` where:
<!-- IF-PROFILE S -->
- TYPE: VISION, US, TASK, TEST, ADR — the only types enabled in this project's profile (S)
<!-- END-IF -->
<!-- IF-PROFILE M L -->
- TYPE: EPIC, FR, NFR, US, TASK, TEST, ADR, CR, CON (core); PERSONA, JOURNEY, ASSUM, UC (discovery); BRQ, BR, CTRL (compliance); SRC (source documents); ARCH, CONTRACT, DM (architecture); RISK, REL (delivery); VISION
<!-- END-IF -->
- DOMAIN: uppercase domain code (use your domain list)
- NNN: three or more digits, zero-padded

When creating new artifacts, check existing IDs in the target folder and increment. The filename must match the ID exactly (e.g., `US-INGEST-001.md` for `id: US-INGEST-001`). IDs must be globally unique across the entire vault — run `python {{VAULT_PREFIX}}/scripts/check-duplicates.py` to verify.

## Resolving Wiki Links

A wiki link `[[ID]]` (optionally `[[ID#section]]` or `[[ID|alias]]`) resolves to the file `ID.md`. Because every ID is globally unique, the link is unambiguous. The folder that holds the file is determined by the ID's **type prefix** via `kit-manifest.json` (`artifact_types.<TYPE>.folder`) — for example `[[US-INGEST-001]]` lives in `02-requirements/user-stories/`, `[[ADR-INGEST-001]]` in `03-architecture/adr/`.

If you are not running inside Obsidian (which resolves links automatically), resolve a link by locating the file named `ID.md` anywhere under the vault root, or by looking up the folder for the ID's prefix in `kit-manifest.json`. Links are stored **upward only**; never write reverse links into frontmatter.

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
<!-- IF-PROFILE M L -->
- Do not change functional requirements (FR) or user stories (US) with status `approved` or higher without a Change Request (`CR-*`).
<!-- END-IF -->
<!-- IF-PROFILE S -->
- Do not change user stories (US) with status `approved` or higher without human review via a normal PR — profile S has no Change Request (CR) artifact; the human review gate is the PR itself.
<!-- END-IF -->
<!-- IF-FLAG compliance -->
- Do not change business requirements (BRQ) or controls (CTRL) with status `approved` or higher without a Change Request (`CR-*`). Changes to BRQ/CTRL require impact analysis on all derived artifacts.
<!-- END-IF -->
<!-- IF-PROFILE M L -->
- Do not modify `PRODUCT-VISION.md` or `EPIC-*` files without human approval.
<!-- END-IF -->
<!-- IF-PROFILE S -->
- Do not modify `PRODUCT-VISION.md` without human approval.
<!-- END-IF -->

**Code & Architecture:**
- Do not bypass the {{ARCHITECTURE_PATTERN}} architecture or intended data flow.
- Do not hardcode configuration that should be externalized — check constraints and ADRs for configurable patterns.
- Do not introduce technologies not listed in `{{VAULT_PREFIX}}/03-architecture/architecture-overview.md` without proposing a new ADR.
- Do not commit code that breaks existing verified acceptance criteria.

**Repository Hygiene:**
- Do not delete or rename artifact files — deprecate them instead.
<!-- IF-PROFILE M L -->
- Do not create FR/NFR/CON without linking to at least one BRQ via `derives_from` — orphan system requirements must be flagged.
- Do not modify requirements after a CR has been approved — create a new CR instead.
<!-- END-IF -->

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
<!-- IF-PROFILE M L -->
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
<!-- END-IF -->
<!-- IF-PROFILE S -->
┌─────────────────────────────────────────────────────────┐
│                    BEFORE IMPLEMENTATION                │
├─────────────────────────────────────────────────────────┤
│ 1. Find TASK-* with status: ready                       │
│ 2. Read US-* (Acceptance Criteria, why/for whom)        │
│ 3. Verify depends_on (check blockers)                   │
│ 4. Read architecture-rules.md (from ADRs)               │
│ 5. Find target_files and code-map locations             │
│ 6. Check glossary (code_name consistency)               │
└─────────────────────────────────────────────────────────┘
<!-- END-IF -->
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
<!-- IF-PROFILE M L -->
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
<!-- END-IF -->
<!-- IF-PROFILE S -->
┌─────────────────────────────────────────────────────────┐
│                   AFTER IMPLEMENTATION                   │
├─────────────────────────────────────────────────────────┤
│ 1. Update TASK status: done                             │
│ 2. Update US status if all tasks done                   │
│ 3. Write tests covering each AC-N                       │
│ 4. Set verifies field in TEST files (-> US)             │
│ 5. Run validate-frontmatter.py                          │
│ 6. Run check-orphans.py                                 │
│ 7. Commit code + tests                                  │
│ 8. Do NOT commit code breaking verified ACs             │
└─────────────────────────────────────────────────────────┘
<!-- END-IF -->
```

## Key Reminders

- **Read before coding.** Always read the full requirement, user story, and ADRs before writing code.
- **Acceptance criteria are law.** Implement exactly what AC-N says, nothing more or less.
- **Glossary is canonical.** Use code_names from the glossary; do not invent variants.
- **Tests are required.** Every AC must have at least one passing test before marking done.
- **Architecture matters.** Respect layered architecture and externalize policy-driven behavior.
- **Dependencies first.** Never implement a task if its dependencies are not `implemented` or `verified`.
<!-- IF-FLAG compliance -->
- **Trace the "why".** Always understand the business motivation (BRQ) and any control requirements (CTRL) behind each requirement.
<!-- END-IF -->
<!-- IF-PROFILE M L -->
- **Human approval required.** Do not transition status on EPIC, US, FR, BRQ, or CTRL to `approved` without human review.
<!-- END-IF -->
<!-- IF-PROFILE S -->
- **Human approval required.** Do not transition status on US to `approved` without human review.
<!-- END-IF -->
