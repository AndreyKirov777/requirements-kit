# Changelog

All notable changes to the Obsidian Requirements Kit are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`

- **MAJOR** — breaking changes to schema structure, frontmatter fields, or folder layout
- **MINOR** — new artifact types, new agent instruction files, new scripts, new templates
- **PATCH** — bug fixes, inconsistency corrections, documentation improvements

---

## [1.0.0] — 2026-04-02

### Changed — Breaking

- **CTRL moved from `02-requirements/controls/` to `01-product/controls/`.** Controls are enforceable, auditable statements derived from BRQ — part of the obligation stack (BRQ → BR → CTRL), not part of system specification (FR/NFR). `01-product/` now contains the complete "why" and "what constrains us" stack: vision, personas, journeys, assumptions, use-cases, BRQ, BR, CTRL, and CON.
- **FR and NFR schemas split.** `requirement.schema.json` is deprecated. New `fr.schema.json` (functional requirements) and `nfr.schema.json` (non-functional requirements) with distinct fields. NFR now has `quality_attribute` as **required** (was optional), plus new optional fields: `measurement_method` and `target_value`. FR no longer inherits the NFR-specific `quality_attribute` field.
- **CON lifecycle simplified** from 7 statuses (draft → proposed → approved → in-implementation → implemented → verified → deprecated) to 4 (draft → proposed → approved → deprecated). Rationale: constraints are accepted as binding and respected by derived FR/NFR — compliance is verified through derived requirements, not through the constraint itself.
- **`type` field removed from Vision schema required fields.** Consistent with v0.5.0 decision to encode type via ID prefix and folder location. `type: vision` may still be present in existing files but is no longer validated.
- **Use Cases moved from `02-requirements/` to `01-product/use-cases/`.** UC is a Discovery tier artifact, not a system specification.

### Added

- **Artifact Tier model.** All 23 artifact types now belong to one of five tiers, documented in README:
  - **Core** (10): Vision, Epic, FR, NFR, US, Task, Test, ADR, CR, CON
  - **Discovery** (4): Persona, Journey, Assumption, Use Case
  - **Compliance** (3): BRQ, BR, CTRL
  - **Architecture** (4): Arch Overview, Domain Architecture, Contract, Data Model
  - **Delivery** (2): Risk, Release
- **BRQ, BR, CTRL added to `check-status-transitions.py`.** These types were missing from the status validation script.
- **NFR template** gains `measurement_method` and `target_value` frontmatter fields.

### Fixed

- **Traceability chain unified** across all documents to `BRQ → [BR →] [CTRL →] Epic → FR ↔ US → Task → Test`. Agent instructions previously omitted BR.
- **Agent instructions: removed references to `implemented_by` and `verified_by` manual fields.** These are reverse links computed by the traceability script (v0.5.0 "link up only" principle). Agent instructions and prompts now correctly instruct agents to update forward links only.
- **Agent prompts (#4 Librarian, #7 Implementation)** updated to remove references to computed fields.
- **README schema count** corrected from "17" to "24".
- **README placeholder format** standardized to `{{PLACEHOLDER}}` (was `[PLACEHOLDER]`).
- **Agent instructions ID format** expanded to list all 23 artifact types grouped by tier.
- **Agent instructions step 8** corrected wording from "non-functional and regulatory requirements" to "external constraints (business, regulatory, or technical)".
- **`base.schema.json` ID pattern** removed CODEMAP and GLOSS prefixes (no schema, template, or state machine exists for these).
- **`.kit-version`** updated to 1.0.0 (was stuck at 0.5.0).

### Migration from 0.8.x

```bash
# 1. Move controls to 01-product
mv 02-requirements/controls/ 01-product/controls/

# 2. Move use-cases to 01-product
mv 02-requirements/use-cases/ 01-product/use-cases/

# 3. Simplify CON frontmatter: remove implementation statuses
# For each CON-* file with status in-implementation/implemented/verified,
# change status to "approved" (or "deprecated" if no longer relevant)

# 4. Split FR/NFR: add quality_attribute to NFR files if missing
# NFR files now require quality_attribute field

# 5. Remove type field from Vision files (optional — validation ignores it)

# 6. Re-run agent file generation and validation
python scripts/install-agent-files.py
python scripts/validate-frontmatter.py --path .
python scripts/check-status-transitions.py --path .
```

### Rationale

v1.0.0 consolidates 8 rapid iterations (v0.1–v0.8) into a consistent, documented foundation. Key architectural decisions:

1. **`01-product/` = complete obligation stack.** All artifacts that exist independently of the system (business motivation, domain rules, controls, constraints) live in one layer. `02-requirements/` contains only system specifications (EPIC, FR, NFR, US).
2. **Tier model reduces cognitive load.** 23 artifact types grouped into 5 tiers lets users adopt only what they need — Core tier for standard projects, plus Compliance for regulated projects.
3. **"Link up only" principle fully enforced.** All references to manual reverse-link fields removed from agent instructions and prompts. Forward links (child → parent) are authoritative; reverse links are computed.

---

## [0.8.0] — 2026-04-02

### Changed — Breaking

- **BR moved from `02-requirements/business-rules/` to `01-product/business-rules/`.** Business rules are atomic, verifiable domain facts — regulatory logic, contractual conditions, and business policies — that exist independently of any system. Like BRQ and CON, they belong in `01-product/` (the discovery & motivation layer) rather than `02-requirements/` (the system specification layer). `01-product/` now contains the full "why" and "what constrains us" stack: vision, personas, journeys, assumptions, BRQ, BR, and CON. `02-requirements/` retains only system-level artifacts: epics, FR, NFR, US, UC, CTRL, and controls.
- **Agent instructions updated** (`docs/agent-instructions.md`): BR path references updated to `01-product/business-rules/`.
- **SDLC pipeline updated** (`_framework/sdlc-pipeline.md`): Stage 4 output path updated.
- **Status transitions updated** (`_framework/status-transitions.md`): Location note added to BR section.

### Migration from 0.7.x

```bash
# 1. Move business-rules to 01-product
mv 02-requirements/business-rules/ 01-product/business-rules/

# 2. Re-run agent file generation and validation
python scripts/install-agent-files.py
python scripts/validate-frontmatter.py --path .
```

---

## [0.7.0] — 2026-04-02

### Changed — Breaking

- **CON moved from `02-requirements/constraints/` to `01-product/constraints/`.** Constraints are external forces — business, regulatory, or technical — that shape the solution space before requirements elaboration. Like BRQ, they represent the "why/what limits us" layer, not the "what the system shall do" layer. They now live in `01-product/` alongside vision, personas, assumptions, and business requirements.
- **CON split into its own schema (`constraint.schema.json`).** Previously CON shared `requirement.schema.json` with FR/NFR. The new dedicated schema adds a required `constraint_type` field and removes the `quality_attribute` field (which was NFR-specific).
- **New required field: `constraint_type`** on all CON artifacts. Classifies constraints by their nature:
  - `business` — budget, timeline, resource, or organizational constraints
  - `regulatory` — laws, standards, compliance mandates
  - `technical` — platform, compatibility, performance bounds, technology choices
- **`requirement.schema.json`** ID pattern narrowed from `^(FR|NFR|CON)-` to `^(FR|NFR)-`. CON now validated against `constraint.schema.json`.
- **Agent instructions updated** (`docs/agent-instructions.md`): constraint path references updated to `01-product/constraints/`; requirement hierarchy section now documents CON's location and `constraint_type` field.

### Migration from 0.6.x

```bash
# 1. Move constraints to 01-product
mv 02-requirements/constraints/ 01-product/constraints/

# 2. Add constraint_type to all CON-* files
# For each CON file, add `constraint_type: business|regulatory|technical` to frontmatter

# 3. Re-run agent file generation and validation
python scripts/install-agent-files.py
python scripts/validate-frontmatter.py --path .
```

---

## [0.6.0] — 2026-04-02

### Added

- **Business Rule (BR) artifact type.** New first-class artifact for encoding atomic, verifiable domain facts — regulatory logic, contractual conditions, and business policies that exist independently of any system. Includes:
  - `_framework/templates/br-template.md` — template with Statement, Source, Conditions, Examples sections
  - `schema/br.schema.json` — schema with `classification` field (regulatory | contractual | policy | domain-logic), `derives_from` (links to BRQ), and optional `regulatory_ref` (structured article/paragraph reference)
  - `02-requirements/business-rules/` — folder for BR artifacts
  - Status transitions in `_framework/status-transitions.md`: `draft → proposed → approved → deprecated`
  - BR prefix added to `base.schema.json` ID pattern, `validate-frontmatter.py`, `check-duplicates.py`, `migrate-artifacts.py`
- **SDLC pipeline Stage 4: Business Rules.** New optional stage between Business Requirements & Obligations (Stage 3) and Requirements Elaboration (Stage 5) for compliance-driven projects. BR decomposes BRQ into specific article-level rules before FR/NFR derivation.

### Changed — Breaking

- **BRQ moved from `02-requirements/` to `01-product/`.** Business Requirements are the "why" layer — product-level obligations, goals, and drivers. They now live alongside vision, personas, and assumptions in `01-product/business-requirements/`. This clarifies the semantic split: `01-product/` = discovery & motivation (why); `02-requirements/` = specification & rules (what).
- **Traceability chain updated.** `BRQ → [BR →] [CTRL →] Epic → FR ↔ US → Task → Code → Test`. BR sits between BRQ (why) and FR/NFR (what the system does), encoding the specific domain rules that FR must implement.
- **SDLC pipeline stages renumbered** (5–9 → 5–10) to accommodate the new Business Rules stage.
- **Agent instructions updated** (`docs/agent-instructions.md`): step 3 ("Trace the why") now references BR artifacts and the new BRQ location in `01-product/`.

### Migration from 0.5.x

```bash
# 1. Move business-requirements to 01-product
mv 02-requirements/business-requirements/ 01-product/business-requirements/

# 2. Create business-rules folder
mkdir -p 02-requirements/business-rules/

# 3. Re-run agent file generation and validation
python scripts/install-agent-files.py
python scripts/validate-frontmatter.py --path .
```

---

## [0.5.0] — 2026-04-01

### Changed — Breaking

- **Attribute audit: schemas trimmed to required-only fields.** Applied recommendations from the attribute audit report. All reverse/computed links removed from schemas — they are now derived by the traceability script. Summary of removals per schema:
  - **requirement.schema.json** (22 → 11 fields): Removed `type`, `risk`, `component`, `stakeholders`, `related_adrs`, `blocks`, `implemented_by`, `verified_by`, `release_target`, `delivered_by`, `implements_control`. Kept: `id`, `title`, `status`, `priority`, `owner`, `domain`, `updated`, `parent_epic`, `derives_from`, `depends_on`, `source_docs`, `quality_attribute`.
  - **brq.schema.json** (18 → 10 fields): Removed `type`, `risk`, `parent_epic`, `derived_requirements`, `derived_controls`, `related_brqs`, `release_target`. Kept: `id`, `title`, `status`, `source_type`, `priority`, `owner`, `domain`, `updated`, `source_docs`, `regulatory_refs`, `compliance_deadline`, `stakeholders`.
  - **ctrl.schema.json** (18 → 9 fields): Removed `type`, `derived_requirements`, `evidence_type`, `evidence_location`, `audit_status`, `control_family`, `stakeholders`, `related_ctrls`, `verified_by`, `release_target`. Audit-extension fields (evidence_*, audit_status, control_family) can be added at verification stage. Kept: `id`, `title`, `status`, `priority`, `owner`, `domain`, `updated`, `derives_from`, `verification_method`, `compliance_deadline`.
  - **epic.schema.json** (9 → 8 fields): Removed `related_requirements` (reverse link — computed via FR.parent_epic).
  - **user-story.schema.json** (12 → 10 fields): Removed `type`, `derives_from`, `tags`. Kept: `id`, `title`, `status`, `priority`, `owner`, `domain`, `persona`, `parent_epic`, `delivers`, `updated`.
  - **task.schema.json** (13 → 10 fields): Removed `type`, `depends_on_tasks`, `release_target`, `implements_control`. Added `owner` to required. Kept: `id`, `title`, `status`, `owner`, `updated`, `assigned_to`, `implements`, `part_of_story`, `acceptance_criteria_subset`, `target_files`, `estimated_complexity`.
- **Templates updated** to match new schemas — no empty optional fields in frontmatter.
- **Principle: "link up only" (child → parent).** All reverse links (`derived_requirements`, `delivered_by`, `verified_by`, `implemented_by` on parent artifacts) are computed by the traceability script. This eliminates the entire class of bidirectional sync errors.
- **`blocks` removed** — exact inverse of `depends_on`, computed by script.
- **`release_target`** kept only on Epic and Task (removed from Requirement, BRQ, CTRL).
- **`type` field** removed from all schemas — type is encoded in the ID prefix and folder location.

### Migration from 0.4.x

Remove the following fields from existing artifact frontmatter (or leave them — validation will ignore unknown fields due to `additionalProperties: true` in base schema, but they will no longer be validated):

```
# On FR/NFR/CON files:
type, risk, component, stakeholders, related_adrs, blocks, implemented_by, verified_by, release_target, delivered_by, implements_control

# On BRQ files:
type, risk, parent_epic, derived_requirements, derived_controls, related_brqs, release_target

# On CTRL files:
type, derived_requirements, evidence_type, evidence_location, audit_status, control_family, stakeholders, related_ctrls, verified_by, release_target

# On Epic files:
related_requirements

# On User Story files:
type, derives_from, tags

# On Task files:
type, depends_on_tasks, release_target, implements_control
```

Re-run `generate-traceability.py` to rebuild TRACEABILITY-MAP.md with computed reverse links.

---

## [0.4.1] — 2026-03-31

### Changed

- **Vision template**: Added three new sections — **Product Structure** (logical modules/components), **Scope of Work** (what is included in this phase), and **Out of Scope** (replaces the former "Non-Goals" section). Product Structure gives agents a business-level map for organizing epics; Scope of Work explicitly bounds what agents should generate requirements for; Out of Scope retains the same purpose as Non-Goals with a clearer name.
- **DBP example (`PRODUCT-VISION.md`)**: Updated to demonstrate the new vision sections with concrete content for the Digital Battery Passport Accelerator.

---

## [0.4.0] — 2026-03-31

### Added

- **`scripts/upgrade-kit.py`**: New migration script for upgrading between kit versions. Reads `.kit-version` to detect which structural migrations are pending, applies only outstanding ones, and updates `.kit-version` on success. Migrations are registered per version in a central registry — adding a new migration for v0.5.0 requires only adding one entry. Supports `--dry-run` (show changes without writing), `--status` (show installed vs current version and pending migrations), and `--path` (explicit vault root). Idempotent: safe to run multiple times. After running, prompts to also run `install-agent-files.py`, `migrate-artifacts.py`, and `validate-frontmatter.py`.
- **`scripts/pull-kit-update.sh`**: One-command upgrade script for git subtree installations. Runs the full update pipeline: fetch → subtree pull → structural migrations → agent file regeneration → artifact migration (with interactive confirmation) → validation → commit. Supports `--dry-run` for preview, accepts a branch or tag argument for version pinning (e.g., `pull-kit-update.sh v0.5.0`). Configurable via `KIT_REMOTE` and `KIT_PREFIX` environment variables. Stops with clear instructions if merge conflicts are detected.

### Fixed

- **`scripts/pull-kit-update.sh`**: Replaced `python` with auto-detected `python3`/`python` — macOS does not alias `python` by default, causing hard failure at step 3.
- **`scripts/pull-kit-update.sh`**: Fixed artifact migration auto-confirm logic — the grep pattern now matches actual `migrate-artifacts.py` output markers (`[!]`, `[+]`, `[§]`, `Modified: N`) instead of non-existent keywords.
- **`scripts/migrate-artifacts.py`**: Updated template directory path to `_framework/templates` (with fallback to `00-meta/templates` for pre-0.4.0 installs). Previously hardcoded `00-meta/templates` which no longer exists after the v0.4.0 restructure.

### Changed — Breaking

- **Folder layout: `_framework/` extracted from `00-meta/`**. Kit infrastructure files that are project-independent have been moved out of `00-meta/` into a dedicated `_framework/` directory:
  - `00-meta/templates/` → `_framework/templates/`
  - `00-meta/sdlc-pipeline.md` → `_framework/sdlc-pipeline.md`
  - `00-meta/status-transitions.md` → `_framework/status-transitions.md`
- **`00-meta/` is now project-context only.** It retains `glossary/` and `taxonomy/` — the two folders that are unique to each project and filled by the team.
- **`_framework/` signals read-only intent.** The underscore prefix (consistent with `_examples/`) indicates kit-managed content that should not be edited manually and will be overwritten by `git subtree pull`.

### Rationale

The previous `00-meta/` mixed two fundamentally different concerns: kit infrastructure (templates, pipeline definition, state machines) and project-specific domain context (glossary, taxonomy). This made it unclear what to customize and what to leave untouched when adopting the kit. The split makes both roles explicit.

### Migration from 0.3.x

```bash
mkdir _framework
mv 00-meta/templates _framework/
mv 00-meta/sdlc-pipeline.md _framework/
mv 00-meta/status-transitions.md _framework/
```

Update any references to the old paths in your project-specific files:
- `00-meta/templates/` → `_framework/templates/`
- `00-meta/sdlc-pipeline.md` → `_framework/sdlc-pipeline.md`
- `00-meta/status-transitions.md` → `_framework/status-transitions.md`

Agent instruction files generated by `install-agent-files.py` are updated automatically by re-running the script after pulling the new kit version.

---

## [0.3.0] — 2026-03-30

### Added

- **`docs/agent-instructions.md`**: Canonical source file for all AI agent instruction files. Contains the full requirements methodology with `{{VAULT_PREFIX}}` and `{{PROJECT_NAME}}` placeholders instead of hardcoded paths. All four previous agent instruction files (CLAUDE.md, .codex/instructions.md, .cursor/rules/requirements-vault.mdc, .kiro/steering.md) are now generated from this single source.
- **`scripts/install-agent-files.py`**: New script that reads `docs/agent-instructions.md`, replaces `{{VAULT_PREFIX}}` with the actual vault path, and injects the result into all four agent instruction files in the project root. Target files: `.claude/CLAUDE.md`, `.codex/instructions.md`, `.cursor/rules/requirements-vault.mdc`, `.kiro/steering.md` — all uniformly in hidden dot-directories. Manages a clearly marked section (`<!-- BEGIN REQUIREMENTS-KIT --> … <!-- END REQUIREMENTS-KIT -->`) — all content outside these markers (project-specific instructions) is preserved. Supports auto-detection of the vault prefix from the script's own location, explicit `--prefix` override, and `--dry-run` mode. Idempotent: re-running produces no changes if the canonical source has not changed.
- **`docs/installation-guide.md`**: Step-by-step guide for installing the kit into a real project via `git subtree` and keeping it updated. Documents the full lifecycle: initial install, agent file generation, upstream updates, conflict resolution, version pinning.

### Changed

- **Agent file location**: Claude Code instructions moved from `CLAUDE.md` (project root) to `.claude/CLAUDE.md` for consistency with other agents (`.codex/`, `.cursor/`, `.kiro/`). All four agents now use the same pattern: hidden dot-directory in the project root.
- **`CLAUDE.md`, `.codex/instructions.md`, `.cursor/rules/requirements-vault.mdc`, `.kiro/steering.md`** (in kit repo): Removed. These files no longer belong in the kit repository — they are generated into the project root by `install-agent-files.py`. To delete them from the kit repo: `git rm CLAUDE.md && git rm -r .claude/ .codex/ .cursor/ .kiro/`.

### Migration from 0.2.x

If you were previously editing agent instruction files directly (`CLAUDE.md`, `.codex/instructions.md`, etc.):

1. Copy your project-specific content (above any kit methodology) to a safe location.
2. Run `python requirements/scripts/install-agent-files.py` to generate the new managed section.
3. Re-add your project-specific instructions above the `<!-- BEGIN REQUIREMENTS-KIT -->` marker.

Going forward, edit `requirements/docs/agent-instructions.md` for methodology changes and re-run the script. Do not edit the root agent files manually — they will be overwritten on next run.

---

## [0.2.2] — 2026-03-30

### Added

- **`scripts/check-duplicates.py`**: New validation script that checks (1) every artifact ID is globally unique across the entire vault, and (2) each file's `id` in frontmatter matches its filename (e.g., `FR-INGEST-001.md` must contain `id: FR-INGEST-001`). Reports `DUPLICATE ID` and `FILENAME MISMATCH` errors with file locations. Covers all 21 artifact types. Exempts well-known fixed-name files (e.g., `PRODUCT-VISION.md`) and meta prefixes (`META-`, `GLOSS-`, `CODEMAP-`). Exit code 1 on any issue — suitable for CI pipelines.
- **`CLAUDE.md`**: Added instruction to run `check-duplicates.py` as step 5 in the "After Implementation" checklist. Updated ID format section to state that IDs must be globally unique and filenames must match the ID.

---

## [0.2.1] — 2026-03-30

### Fixed — Critical

- **`validate-frontmatter.py`**: Added `BRQ` and `CTRL` to `PREFIX_SCHEMA_MAP`. Previously, `BRQ-*` and `CTRL-*` files fell through to `base.schema.json` and lost all type-specific validation.
- **`schema/persona.schema.json`**: Status enum corrected from `["draft","proposed","approved","active","archived"]` to `["draft","proposed","approved","deprecated"]` to match `status-transitions.md`.
- **`schema/journey.schema.json`**: Same status enum fix as persona.
- **`schema/assumption.schema.json`**: Added `deprecated` to status enum — it was defined in `status-transitions.md` but missing from the schema.
- **`schema/use-case.schema.json`**: Status enum narrowed from 7 values (including `in-implementation`, `implemented`, `verified`) to 4 (`draft`, `proposed`, `approved`, `deprecated`) to match the UC state machine.
- **`schema/contract.schema.json`**: Status enum narrowed to `["draft","proposed","approved","deprecated"]` — `implemented` and `verified` are not valid CONTRACT states.
- **`schema/data-model.schema.json`**: Same status enum fix as contract.
- **`schema/user-story.schema.json`**: Added `allOf: [{"$ref": "base.schema.json"}]` — US was the only schema not inheriting from base, causing the validation script's base-merge logic to skip it.
- **`.codex/instructions.md`**: Full rewrite synced from `CLAUDE.md` as source of truth. Corrected: status transitions (removed non-existent `released`, `adopted`, `deployed`); added BRQ/CTRL step 3; corrected test path (`05-quality/acceptance/`, not `04-delivery/test-evidence/`); fixed typo `implementation_by` → `implemented_by`; expanded ID format to all 21 artifact types.
- **`.cursor/rules/requirements-vault.mdc`**: Full rewrite synced from `CLAUDE.md`. Corrected: ADR status (`accepted` not `approved/implemented`); CON state machine (`draft → proposed → approved`, not `active`); TASK starting state (`backlog` not `unassigned`); CR terminal state (`applied` not `implemented`); TEST status (`passed/failed` not `executed`); removed non-existent folders `04-delivery/test-evidence/` and `05-domain/`; added BRQ/CTRL; added peer-level FR↔US.
- **`.kiro/steering.md`**: Full rewrite synced from `CLAUDE.md`. Removed domain-specific placeholders `[TIER_1]`, `[TIER_2]`, `[TIER_3]`, `[completenessMetric]` that leaked DBP architecture; added BRQ/CTRL; added peer-level FR↔US; expanded ID format.

### Fixed — Schemas

- **`schema/test.schema.json`**: Added `unit` and `manual` to type enum. Previously the test type enum (`functional`, `non-functional`, `integration`, `e2e`, `security`, `performance`) did not include `unit` or `manual`, but Acceptance Criteria use `Testable by: unit | integration | e2e | manual`.

### Fixed — Traceability

- **`scripts/generate-traceability.py`**: Expanded `LINK_FIELDS` from 11 to 27 fields. Added: `derives_from`, `implements_control`, `derived_requirements`, `derived_controls`, `part_of_story`, `delivered_by`, `delivers`, `parent_epic`, `parent_overview`, `related_brqs`, `related_ctrls`, `verifies_control`, `covers_criteria`, `requirements_included`, `epics_included`, `related_epics`, `superseded_by`. Previously the traceability map missed most BRQ/CTRL/US/Epic relationship links.

### Fixed — Templates

- **`00-meta/templates/adr-template.md`**: Added missing required fields `domain` and `updated`. Replaced hardcoded `date: 2026-03-27` with placeholder `YYYY-MM-DD`. Template now passes its own schema validation.

### Fixed — Documentation

- **`README.md`**: Core Principle #2 traceability chain updated to `BRQ → [CTRL →] Epic → FR ↔ US → Task → Code → Test` with explicit note that FR and US are peer-level.
- **`CLAUDE.md`**: Traceability chain updated; added paragraph clarifying FR↔US peer-level relationship with `delivers`/`delivered_by` links.
- **`docs/success-criteria.md`**: Section 3 heading updated to reflect correct chain. Criterion 7.2 changed from "Каждый FR имеет ≥1 AC" to "Каждый FR доставлен хотя бы одним US с ≥1 AC", consistent with the decision that AC lives in US only.

### Changed — Domain-Agnostic Cleanup

- **`00-meta/glossary/dbp.md`**: Replaced DBP-specific glossary with a generic placeholder template. DBP content moved to `_examples/00-meta/glossary/dbp.md`.
- **`00-meta/taxonomy/domains.md`**: Replaced DBP-specific domain registry (8 DBP domains) with a generic placeholder template. DBP content moved to `_examples/00-meta/taxonomy/domains.md`.
- **`_examples/README.md`**: Added entries for the new `_examples/00-meta/glossary/` and `_examples/00-meta/taxonomy/` example files.

---

## [0.2.0] — 2026-03-28

### Added — Domain-Agnostic Edition

This release refactored the kit from a DBP-specific vault into a reusable, domain-agnostic template.

- **Agent instruction files for 4 agents:** `CLAUDE.md`, `.codex/instructions.md`, `.cursor/rules/requirements-vault.mdc`, `.kiro/steering.md` — all using generic placeholders (`[PROJECT_NAME]`, `[DOMAIN_LIST]`, `[ARCHITECTURE_PATTERN]`, etc.)
- **BRQ and CTRL artifact types:** Business Requirements and Controls added as first-class artifacts, with schemas (`brq.schema.json`, `ctrl.schema.json`), templates, and status-transitions entries.
- **Two-level architecture:** `architecture-overview.md` (system-wide) and `ARCH-{DOMAIN}-{NNN}.md` (domain-specific) with corresponding schemas and templates.
- **17 JSON schemas** covering all artifact types: `base`, `epic`, `requirement` (FR/NFR/CON), `user-story`, `brq`, `ctrl`, `adr`, `architecture-overview`, `domain-architecture`, `task`, `test`, `change-request`, `persona`, `journey`, `assumption`, `risk`, `release`, `use-case`, `contract`, `data-model`, `vision`.
- **4 validation scripts:** `validate-frontmatter.py`, `check-orphans.py`, `check-status-transitions.py`, `generate-traceability.py`.
- **Agent prompts** (`scripts/agent-prompts.md`) for 7 roles: Analyst, Change Impact, QA, Librarian, Planner, Architect, Coding Agent.
- **DBP example set** in `_examples/` — 14 working artifacts demonstrating the complete traceability chain.
- **`docs/success-criteria.md`** — 37 measurable success criteria across 8 dimensions for evaluating kit effectiveness.
- **Status transition rules** for 18 artifact types in `00-meta/status-transitions.md`.

### Changed — From v0.1.x

- All PAY/Payments domain artifacts removed.
- `PRODUCT-VISION.md` and all domain-specific files moved to `_examples/`.
- `CLAUDE.md` made domain-agnostic with placeholder instructions.

---

## [0.1.0] — 2026-03-01

### Added — Initial Release (DBP-specific)

- Initial vault structure for the Digital Battery Passport Accelerator project.
- Requirements vault with DBP domain taxonomy (INGEST, PASSPORT, SEC, QR, AUDIT, API, UI, INFRA).
- `CLAUDE.md` and `.codex/instructions.md` for Claude Code and Codex agents.
- Core schemas for FR, US, EPIC, ADR, TASK, TEST, CR.
- DBP glossary with 12 domain terms and code naming conventions.

---

## How to Contribute Changes to This File

When releasing a new version:

1. Add a new `## [X.Y.Z] — YYYY-MM-DD` section at the top of the list.
2. Group changes under: `Added`, `Changed`, `Fixed`, `Removed`, `Deprecated`, `Security`.
3. For **PATCH** releases: document only bug fixes and corrections.
4. For **MINOR** releases: document new artifact types, templates, scripts, or agent support.
5. For **MAJOR** releases: call out any breaking changes to frontmatter fields, folder paths, or schema structure that require migrating existing vaults.
6. Update the `version` field in `README.md`.
