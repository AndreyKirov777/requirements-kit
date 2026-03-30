# Changelog

All notable changes to the Obsidian Requirements Kit are documented here.

Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
Versioning follows [Semantic Versioning](https://semver.org/): `MAJOR.MINOR.PATCH`

- **MAJOR** — breaking changes to schema structure, frontmatter fields, or folder layout
- **MINOR** — new artifact types, new agent instruction files, new scripts, new templates
- **PATCH** — bug fixes, inconsistency corrections, documentation improvements

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
