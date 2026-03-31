# Obsidian Requirements Kit for AI SDLC

> **Version 0.4.0** — Domain-agnostic edition | [Changelog](CHANGELOG.md)

This kit turns an Obsidian vault into an AI-agent-friendly requirements hub designed for the full autonomous software development lifecycle.

It is designed for teams that want:
- Markdown-based requirements readable by both humans and AI coding agents
- Strong linking between product vision, requirements, architecture, tasks, and quality artifacts
- Simple versioning with Git in a monorepo alongside code
- AI-assisted review, impact analysis, task breakdown, and implementation
- A defined pipeline with human approval gates at strategic points

## Supported AI Agents

The kit provides agent instruction files for four coding agents:

| Agent | Instruction File |
|-------|-----------------|
| Claude Code | `CLAUDE.md` |
| Codex | `.codex/instructions.md` |
| Cursor | `.cursor/rules/requirements-vault.mdc` |
| Kiro | `.kiro/steering.md` |

All instruction files are domain-agnostic templates. Customize the placeholders (`[PROJECT_NAME]`, `[DOMAIN_LIST]`, etc.) for your project.

## What is Inside

- A vault folder structure with clear separation of concerns
- Ready-to-use templates for all artifact types (`_framework/templates/`)
- One working example of each artifact type (`_examples/`) — uses DBP (Digital Battery Passport) as a sample project
- JSON Schemas for all artifact types (`schema/`) — 17 schemas for frontmatter validation
- Status transition rules (state machines) for all artifact types (`_framework/status-transitions.md`)
- A domain glossary and taxonomy starters (`00-meta/glossary/`, `00-meta/taxonomy/`)
- An SDLC pipeline definition with stages and gates (`_framework/sdlc-pipeline.md`)
- Validation scripts for CI integration (`scripts/`)
- Agent prompts for each role in the AI SDLC (`scripts/agent-prompts.md`)

## Quick Start

1. Copy this folder into your repository (monorepo recommended).
2. Configure agent instruction files — customize `CLAUDE.md` and/or the agent file for your tool.
3. Read `_framework/sdlc-pipeline.md` to understand the stages and gates.
4. Update `00-meta/taxonomy/domains.md` with your project's domains and components.
5. Update `00-meta/glossary/` with your domain terminology.
6. Browse `_examples/` to see working samples of each artifact.
7. Use templates from `_framework/templates/` to create your first real artifacts.
8. Run `python scripts/validate-frontmatter.py --path .` to verify metadata.
9. Use agent prompts from `scripts/agent-prompts.md` or let agents discover tasks automatically.

## Evaluating the Kit

`docs/success-criteria.md` contains 37 measurable success criteria across 8 dimensions — agent comprehension, output quality, traceability, cross-agent portability, process efficiency, scalability, requirements quality, and developer experience. Use it to assess whether the kit is delivering value in your project and to structure A/B experiments comparing the Requirements as Code approach against ad-hoc prompting.

## Folder Layout

```text
CLAUDE.md                    # Agent instructions for Claude Code
.codex/instructions.md       # Agent instructions for Codex
.cursor/rules/               # Agent rules for Cursor
.kiro/                       # Agent steering for Kiro

_examples/                   # One working example per artifact type (reference only)

_framework/                  # Kit infrastructure — do not edit (updated from upstream)
  templates/                 # Templates for all artifact types
  sdlc-pipeline.md           # Pipeline stages and approval gates
  status-transitions.md      # Valid state machines per artifact type

00-meta/                     # Project-specific context — customize for your project
  glossary/                  # Domain terms → code naming conventions
  taxonomy/                  # Domain and component registry

01-product/
  vision/                    # Product vision documents
  personas/                  # User personas
  journeys/                  # User journey maps
  assumptions/               # Assumptions to validate

02-requirements/
  epics/                     # EPIC-* files
  fr/                        # FR-* functional requirements
  user-stories/              # US-* user stories
  use-cases/                 # UC-* use case descriptions
  nfr/                       # NFR-* non-functional requirements
  constraints/               # CON-* constraint definitions

03-architecture/
  architecture-overview.md   # System-wide architecture (one per project)
  ARCH-{DOMAIN}-{NNN}.md     # Domain-specific architecture documents
  adr/                       # ADR-* architecture decision records
  code-map/                  # Domain → source file mappings
  contracts/                 # API and interface contracts
  integrations/              # External integration specs
  data-model/                # Data model definitions

04-delivery/
  tasks/                     # TASK-* implementation units for AI agents
  change-requests/           # CR-* change requests
  releases/                  # REL-* release definitions
  risks/                     # RISK-* risk assessments

05-quality/
  acceptance/                # TEST-* test definitions
  test-ideas/                # Exploratory test ideas
  traceability/              # Auto-generated traceability map

99-attachments/              # Images, diagrams, reference docs

schema/                      # JSON Schemas per artifact type
scripts/                     # Validation scripts and agent prompts
docs/                        # Kit-level documentation
  success-criteria.md        # 37 success criteria for evaluating the kit
```

## Naming Convention

```text
EPIC-<DOMAIN>-<NNN>.md       # Epics
FR-<DOMAIN>-<NNN>.md         # Functional requirements
US-<DOMAIN>-<NNN>.md         # User stories
NFR-<DOMAIN>-<NNN>.md        # Non-functional requirements
ADR-<DOMAIN>-<NNN>.md        # Architecture decision records
ARCH-<DOMAIN>-<NNN>.md       # Domain-specific architecture documents
TASK-<DOMAIN>-<NNN>.md       # Implementation tasks
TEST-<DOMAIN>-<NNN>.md       # Test definitions
CR-<DOMAIN>-<NNN>.md         # Change requests
CON-<DOMAIN>-<NNN>.md        # Constraints
UC-<DOMAIN>-<NNN>.md         # Use cases
RISK-<DOMAIN>-<NNN>.md       # Risks
REL-<DOMAIN>-<NNN>.md        # Releases
PERSONA-<DOMAIN>-<NNN>.md   # User personas
JOURNEY-<DOMAIN>-<NNN>.md   # User journeys
ASSUM-<DOMAIN>-<NNN>.md     # Assumptions
CONTRACT-<DOMAIN>-<NNN>.md  # API/interface contracts
DM-<DOMAIN>-<NNN>.md        # Data model definitions
VISION-<DOMAIN>-<NNN>.md    # Product vision
```

architecture-overview.md     # System-wide architecture overview (fixed name, one per project)

Domain codes are registered in `00-meta/taxonomy/domains.md`. IDs use three or more digits.

## Core Principles

1. **One requirement per file.** Atomic, linkable, diffable.
2. **Every artifact links upstream and downstream.** BRQ → [CTRL →] Epic → FR ↔ US → Task → Code → Test. FR and US are peer-level: FR defines *what* the system shall do, US defines *for whom* and carries Acceptance Criteria. They link via `delivers`/`delivered_by`.
3. **Glossary-driven naming.** Domain terms map to code identifiers via the glossary.
4. **Human gates at strategic points.** Vision, requirements, and architecture require human approval.
5. **Structured acceptance criteria.** Use Given/When/Then format with AC-N identifiers.
6. **Status transitions are enforced.** See `_framework/status-transitions.md`.
7. **Code-map bridges requirements to code.** AI agents find targets via `03-architecture/code-map/`.
8. **Architecture has two levels.** `architecture-overview.md` describes the whole system; `ARCH-{DOMAIN}-*` files detail each domain.

## AI Agent Roles

**Analyst** — reviews requirement quality, proposes requirements from product vision.  
**Architect** — creates ADRs, code-maps, contracts; reviews architectural consistency.  
**Planner** — breaks approved requirements into TASK files; runs impact analysis.  
**Coding Agent** (Claude Code / Codex / Cursor / Kiro) — implements tasks autonomously using requirements, code-map, and glossary.
**QA Agent** — generates tests from acceptance criteria; updates test status.  
**Librarian** — audits vault: validates frontmatter, finds orphans, checks status consistency.

## Validation

```bash
pip install pyyaml jsonschema

python scripts/validate-frontmatter.py --path .
python scripts/check-orphans.py --path .
python scripts/check-status-transitions.py --path .
python scripts/generate-traceability.py --path .
```

## Git Workflow

- One requirement per branch for non-trivial changes.
- Require PR review for any `approved` status transition.
- Run validation scripts in CI.
- Use Change Requests (CR) for modifications to approved artifacts.
