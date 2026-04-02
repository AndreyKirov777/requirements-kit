---
id: META-SDLC-PIPELINE
title: AI SDLC Pipeline Definition
updated: 2026-03-28
---

# AI SDLC Pipeline

This document defines the stages, inputs, outputs, and approval gates for the autonomous AI software development lifecycle.

## Stages

### 1. Vision

| Field    | Value                                       |
| -------- | ------------------------------------------- |
| Input    | Human product description                   |
| Agent    | PM / Analyst agent                          |
| Output   | `01-product/vision/PRODUCT-VISION.md`       |
| Gate     | **Human approval** — vision must be `approved` before proceeding |

### 2. Product Discovery

| Field    | Value                                       |
| -------- | ------------------------------------------- |
| Input    | Approved vision                             |
| Agent    | Analyst agent                               |
| Output   | Personas, journeys, assumptions in `01-product/` |
| Gate     | **Human review** of personas and journeys   |

### 3. Business Requirements & Obligations

| Field    | Value                                       |
| -------- | ------------------------------------------- |
| Input    | Approved vision + product discovery + external sources (laws, standards, contracts, policies) |
| Agent    | Analyst agent                               |
| Output   | `BRQ-*` files in `01-product/business-requirements/`; optionally `CTRL-*` files in `02-requirements/controls/` for compliance-driven projects |
| Gate     | **Human approval** — BRQ must reach `approved` before deriving system requirements |

> **Why this stage?** Business requirements and obligations are the "why" layer (BABOK Business Requirements). They capture external drivers — regulations, contracts, policies, business goals — before decomposition into system requirements. For compliance-driven projects, controls (CTRL) are derived from BRQ to specify what must be enforced and proven. For standard projects, BRQ can be used to capture high-level business goals without controls.

> **Semantic rule:** BRQ = why; BR = what the business/regulation says; CTRL = what must be enforced/proven; FR/NFR = what the system shall do; ADR = how we chose to do it; TEST = how we prove it.

### 4. Business Rules (compliance-driven projects)

| Field    | Value                                       |
| -------- | ------------------------------------------- |
| Input    | Approved BRQ + external regulatory/contractual sources |
| Agent    | Analyst agent                               |
| Output   | `BR-*` files in `01-product/business-rules/` |
| Gate     | **Human approval** — BR must reach `approved` before deriving FR/NFR |

> **Why this stage?** Business rules decompose regulatory obligations (BRQ) into atomic, verifiable domain facts: "A battery passport must contain N required fields", "Public users see only non-confidential data". Each BR traces to a specific article or clause. One BR may drive multiple FR/NFR. When implementing acts change, updating the BR cascades to all affected FR/NFR.

> **When to skip:** For non-compliance projects, this stage is optional. BRQ can derive FR/NFR directly.

### 5. Requirements Elaboration

| Field    | Value                                       |
| -------- | ------------------------------------------- |
| Input    | Approved BRQ/BR/CTRL + vision + product discovery artifacts |
| Agent    | Analyst agent                               |
| Output   | `EPIC-*`, `US-*`, `FR-*`, `NFR-*` files in `02-requirements/`; `CON-*` files in `01-product/constraints/`. Each FR/NFR/CON links back to BRQ, BR, or CTRL via `derives_from` |
| Gate     | **Human review** — requirements move from `draft` → `proposed` → `approved` |

> **Traceability rule:** Every FR/NFR/CON should have a `derives_from` link to at least one BRQ, BR, or CTRL. Orphan system requirements without a business justification must be flagged during review.

### 6. Architecture

| Field    | Value                                       |
| -------- | ------------------------------------------- |
| Input    | Approved requirements                       |
| Agent    | Architect agent                             |
| Output   | `ADR-*` in `03-architecture/adr/`, code maps, contracts, data models |
| Gate     | **Human approval** of ADRs                  |

### 7. Task Breakdown

| Field    | Value                                       |
| -------- | ------------------------------------------- |
| Input    | Approved requirements + architecture + code map |
| Agent    | Planner agent                               |
| Output   | `TASK-*` files in `04-delivery/tasks/`      |
| Gate     | **Automatic** if requirements are `approved` and ADRs are `accepted` |

### 8. Implementation

| Field    | Value                                       |
| -------- | ------------------------------------------- |
| Input    | Tasks with `status: ready`                  |
| Agent    | Coding agent (Claude Code / Codex)          |
| Output   | Source code, unit tests, updated requirement metadata |
| Gate     | CI passes + all acceptance criteria covered by tests |

### 9. Verification

| Field    | Value                                       |
| -------- | ------------------------------------------- |
| Input    | Implemented code + test results             |
| Agent    | QA agent                                    |
| Output   | `TEST-*` results, requirement status → `verified`. For compliance-driven projects: CTRL status → `verified`, evidence collected |
| Gate     | All acceptance criteria pass, no orphan requirements. For compliance: all CTRLs have evidence |

### 10. Release

| Field    | Value                                       |
| -------- | ------------------------------------------- |
| Input    | All requirements for release target at `verified` |
| Agent    | Planner agent                               |
| Output   | Release notes in `04-delivery/releases/`    |
| Gate     | **Human approval** before deploy            |

## Gate Summary

| Stage                             | Gate Type  | Who Approves           |
| --------------------------------- | ---------- | ---------------------- |
| Vision                            | Manual     | Product Owner          |
| Product Discovery                 | Manual     | Product Owner          |
| Business Requirements & Obligations | Manual   | Product Owner + Compliance (if regulatory) |
| Business Rules (compliance)       | Manual     | Compliance + PM        |
| Requirements Elaboration          | Manual     | PM + Tech Lead         |
| Architecture                      | Manual     | Tech Lead              |
| Task Breakdown                    | Automatic  | —                      |
| Implementation                    | Automatic  | CI pipeline            |
| Verification                      | Automatic  | QA agent + CI          |
| Release                           | Manual     | Product Owner          |

## Principles

1. **Human-in-the-loop at strategic gates.** Agents propose; humans approve vision, requirements, and architecture.
2. **Automatic at execution gates.** Once requirements and architecture are approved, task breakdown, implementation, and verification can proceed autonomously.
3. **No stage skipping.** Every artifact must pass through its defined status transitions (see `status-transitions.md`).
4. **Traceability at every stage.** Every downstream artifact links back to its upstream source.
