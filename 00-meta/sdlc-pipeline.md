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

### 3. Requirements Elaboration

| Field    | Value                                       |
| -------- | ------------------------------------------- |
| Input    | Approved vision + product discovery artifacts |
| Agent    | Analyst agent                               |
| Output   | `EPIC-*`, `US-*`, `FR-*`, `NFR-*`, `CON-*` files in `02-requirements/` |
| Gate     | **Human review** — requirements move from `draft` → `proposed` → `approved` |

### 4. Architecture

| Field    | Value                                       |
| -------- | ------------------------------------------- |
| Input    | Approved requirements                       |
| Agent    | Architect agent                             |
| Output   | `ADR-*` in `03-architecture/adr/`, code maps, contracts, data models |
| Gate     | **Human approval** of ADRs                  |

### 5. Task Breakdown

| Field    | Value                                       |
| -------- | ------------------------------------------- |
| Input    | Approved requirements + architecture + code map |
| Agent    | Planner agent                               |
| Output   | `TASK-*` files in `04-delivery/tasks/`      |
| Gate     | **Automatic** if requirements are `approved` and ADRs are `accepted` |

### 6. Implementation

| Field    | Value                                       |
| -------- | ------------------------------------------- |
| Input    | Tasks with `status: ready`                  |
| Agent    | Coding agent (Claude Code / Codex)          |
| Output   | Source code, unit tests, updated requirement metadata |
| Gate     | CI passes + all acceptance criteria covered by tests |

### 7. Verification

| Field    | Value                                       |
| -------- | ------------------------------------------- |
| Input    | Implemented code + test results             |
| Agent    | QA agent                                    |
| Output   | `TEST-*` results, requirement status → `verified` |
| Gate     | All acceptance criteria pass, no orphan requirements |

### 8. Release

| Field    | Value                                       |
| -------- | ------------------------------------------- |
| Input    | All requirements for release target at `verified` |
| Agent    | Planner agent                               |
| Output   | Release notes in `04-delivery/releases/`    |
| Gate     | **Human approval** before deploy            |

## Gate Summary

| Stage                    | Gate Type  | Who Approves     |
| ------------------------ | ---------- | ---------------- |
| Vision                   | Manual     | Product Owner    |
| Product Discovery        | Manual     | Product Owner    |
| Requirements Elaboration | Manual     | PM + Tech Lead   |
| Architecture             | Manual     | Tech Lead        |
| Task Breakdown           | Automatic  | —                |
| Implementation           | Automatic  | CI pipeline      |
| Verification             | Automatic  | QA agent + CI    |
| Release                  | Manual     | Product Owner    |

## Principles

1. **Human-in-the-loop at strategic gates.** Agents propose; humans approve vision, requirements, and architecture.
2. **Automatic at execution gates.** Once requirements and architecture are approved, task breakdown, implementation, and verification can proceed autonomously.
3. **No stage skipping.** Every artifact must pass through its defined status transitions (see `status-transitions.md`).
4. **Traceability at every stage.** Every downstream artifact links back to its upstream source.
