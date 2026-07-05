---
id: META-STATUS-TRANSITIONS
title: Status Transitions — State Machines
updated: 2026-07-04
---

# Status Transitions

> **Generated file — do not edit by hand.** Source of truth is `kit-manifest.json`.
> Re-run `python scripts/generate-status-transitions.py` after changing the manifest.

This document lists the allowed lifecycle statuses and the legal transitions
between them for every artifact type. The same graph is enforced automatically:

- `check-status-transitions.py` (default) validates that each artifact's current
  status is legal for its type and that parent/child statuses stay consistent.
- `check-status-transitions.py --git` validates that each *change* to a `status`
  field follows an allowed edge below (no skipping states).

A terminal status (no outgoing edges) can only be left via a Change Request that
creates a new artifact. `deprecated` is reachable from every non-terminal status.

## Core tier

### ADR

**Statuses:** `proposed`, `accepted`, `rejected`, `superseded`, `deprecated`

**Human approval gate at:** `proposed`

| From | Allowed next |
| --- | --- |
| `proposed` | `accepted`, `rejected` |
| `accepted` | `superseded`, `deprecated` |
| `rejected` | — (terminal) |
| `superseded` | `deprecated` |
| `deprecated` | — (terminal) |

### CON

**Statuses:** `draft`, `proposed`, `approved`, `deprecated`

**Human approval gate at:** `proposed`

| From | Allowed next |
| --- | --- |
| `draft` | `proposed`, `deprecated` |
| `proposed` | `approved`, `draft`, `deprecated` |
| `approved` | `deprecated` |
| `deprecated` | — (terminal) |

### CR

**Statuses:** `proposed`, `approved`, `applied`, `rejected`

**Human approval gate at:** `proposed`

| From | Allowed next |
| --- | --- |
| `proposed` | `approved`, `rejected` |
| `approved` | `applied`, `rejected` |
| `applied` | — (terminal) |
| `rejected` | — (terminal) |

### EPIC

**Statuses:** `draft`, `proposed`, `approved`, `in-progress`, `completed`, `deprecated`

**Human approval gate at:** `proposed`

| From | Allowed next |
| --- | --- |
| `draft` | `proposed`, `deprecated` |
| `proposed` | `approved`, `draft`, `deprecated` |
| `approved` | `in-progress`, `deprecated` |
| `in-progress` | `completed`, `deprecated` |
| `completed` | `in-progress`, `deprecated` |
| `deprecated` | — (terminal) |

### FR

**Statuses:** `draft`, `proposed`, `approved`, `in-implementation`, `implemented`, `verified`, `deprecated`

**Human approval gate at:** `proposed`

| From | Allowed next |
| --- | --- |
| `draft` | `proposed`, `deprecated` |
| `proposed` | `approved`, `draft`, `deprecated` |
| `approved` | `in-implementation`, `deprecated` |
| `in-implementation` | `implemented`, `deprecated` |
| `implemented` | `verified`, `in-implementation`, `deprecated` |
| `verified` | `in-implementation`, `deprecated` |
| `deprecated` | — (terminal) |

### NFR

**Statuses:** `draft`, `proposed`, `approved`, `in-implementation`, `implemented`, `verified`, `deprecated`

**Human approval gate at:** `proposed`

| From | Allowed next |
| --- | --- |
| `draft` | `proposed`, `deprecated` |
| `proposed` | `approved`, `draft`, `deprecated` |
| `approved` | `in-implementation`, `deprecated` |
| `in-implementation` | `implemented`, `deprecated` |
| `implemented` | `verified`, `in-implementation`, `deprecated` |
| `verified` | `in-implementation`, `deprecated` |
| `deprecated` | — (terminal) |

### TASK

**Statuses:** `backlog`, `ready`, `in-progress`, `done`, `blocked`

| From | Allowed next |
| --- | --- |
| `backlog` | `ready`, `blocked` |
| `ready` | `in-progress`, `backlog`, `blocked` |
| `in-progress` | `done`, `blocked` |
| `blocked` | `ready`, `in-progress`, `backlog` |
| `done` | — (terminal) |

### TEST

**Statuses:** `draft`, `ready`, `passed`, `failed`

| From | Allowed next |
| --- | --- |
| `draft` | `ready` |
| `ready` | `passed`, `failed` |
| `passed` | `failed` |
| `failed` | `ready`, `passed` |

### US

**Statuses:** `draft`, `proposed`, `approved`, `in-implementation`, `implemented`, `verified`, `deprecated`

**Human approval gate at:** `proposed`

| From | Allowed next |
| --- | --- |
| `draft` | `proposed`, `deprecated` |
| `proposed` | `approved`, `draft`, `deprecated` |
| `approved` | `in-implementation`, `deprecated` |
| `in-implementation` | `implemented`, `deprecated` |
| `implemented` | `verified`, `in-implementation`, `deprecated` |
| `verified` | `in-implementation`, `deprecated` |
| `deprecated` | — (terminal) |

### VISION

**Statuses:** `draft`, `proposed`, `approved`, `superseded`, `deprecated`

**Human approval gate at:** `proposed`

| From | Allowed next |
| --- | --- |
| `draft` | `proposed`, `deprecated` |
| `proposed` | `approved`, `draft`, `deprecated` |
| `approved` | `superseded`, `deprecated` |
| `superseded` | `deprecated` |
| `deprecated` | — (terminal) |

## Compliance tier

### BR

**Statuses:** `draft`, `proposed`, `approved`, `deprecated`

**Human approval gate at:** `proposed`

| From | Allowed next |
| --- | --- |
| `draft` | `proposed`, `deprecated` |
| `proposed` | `approved`, `draft`, `deprecated` |
| `approved` | `deprecated` |
| `deprecated` | — (terminal) |

### BRQ

**Statuses:** `identified`, `analyzed`, `approved`, `allocated`, `covered`, `deprecated`

**Human approval gate at:** `analyzed`

| From | Allowed next |
| --- | --- |
| `identified` | `analyzed`, `deprecated` |
| `analyzed` | `approved`, `identified`, `deprecated` |
| `approved` | `allocated`, `deprecated` |
| `allocated` | `covered`, `deprecated` |
| `covered` | `allocated`, `deprecated` |
| `deprecated` | — (terminal) |

### CTRL

**Statuses:** `identified`, `defined`, `allocated`, `implemented`, `verified`, `audited`, `deprecated`

**Human approval gate at:** `defined`

| From | Allowed next |
| --- | --- |
| `identified` | `defined`, `deprecated` |
| `defined` | `allocated`, `deprecated` |
| `allocated` | `implemented`, `deprecated` |
| `implemented` | `verified`, `deprecated` |
| `verified` | `audited`, `implemented`, `deprecated` |
| `audited` | `deprecated` |
| `deprecated` | — (terminal) |

## Discovery tier

### ASSUM

**Statuses:** `unvalidated`, `validating`, `validated`, `invalidated`, `deprecated`

| From | Allowed next |
| --- | --- |
| `unvalidated` | `validating`, `deprecated` |
| `validating` | `validated`, `invalidated`, `deprecated` |
| `validated` | `invalidated`, `deprecated` |
| `invalidated` | `deprecated` |
| `deprecated` | — (terminal) |

### JOURNEY

**Statuses:** `draft`, `proposed`, `approved`, `deprecated`

**Human approval gate at:** `proposed`

| From | Allowed next |
| --- | --- |
| `draft` | `proposed`, `deprecated` |
| `proposed` | `approved`, `draft`, `deprecated` |
| `approved` | `deprecated` |
| `deprecated` | — (terminal) |

### PERSONA

**Statuses:** `draft`, `proposed`, `approved`, `deprecated`

**Human approval gate at:** `proposed`

| From | Allowed next |
| --- | --- |
| `draft` | `proposed`, `deprecated` |
| `proposed` | `approved`, `draft`, `deprecated` |
| `approved` | `deprecated` |
| `deprecated` | — (terminal) |

### UC

**Statuses:** `draft`, `proposed`, `approved`, `deprecated`

**Human approval gate at:** `proposed`

| From | Allowed next |
| --- | --- |
| `draft` | `proposed`, `deprecated` |
| `proposed` | `approved`, `draft`, `deprecated` |
| `approved` | `deprecated` |
| `deprecated` | — (terminal) |

## Source tier

### SRC

SRC has **no managed lifecycle**. Its `status` field is an objective property of the underlying document, not a workflow state. Recognized values: `in_force`, `adopted`, `draft`, `proposed`.

## Architecture tier

### ARCH

**Statuses:** `draft`, `proposed`, `approved`, `deprecated`

**Human approval gate at:** `proposed`

| From | Allowed next |
| --- | --- |
| `draft` | `proposed`, `deprecated` |
| `proposed` | `approved`, `draft`, `deprecated` |
| `approved` | `deprecated` |
| `deprecated` | — (terminal) |

### ARCH-OVERVIEW

**Statuses:** `draft`, `proposed`, `approved`, `deprecated`

**Human approval gate at:** `proposed`

| From | Allowed next |
| --- | --- |
| `draft` | `proposed`, `deprecated` |
| `proposed` | `approved`, `draft`, `deprecated` |
| `approved` | `deprecated` |
| `deprecated` | — (terminal) |

### CONTRACT

**Statuses:** `draft`, `proposed`, `approved`, `deprecated`

**Human approval gate at:** `proposed`

| From | Allowed next |
| --- | --- |
| `draft` | `proposed`, `deprecated` |
| `proposed` | `approved`, `draft`, `deprecated` |
| `approved` | `deprecated` |
| `deprecated` | — (terminal) |

### DM

**Statuses:** `draft`, `proposed`, `approved`, `deprecated`

**Human approval gate at:** `proposed`

| From | Allowed next |
| --- | --- |
| `draft` | `proposed`, `deprecated` |
| `proposed` | `approved`, `draft`, `deprecated` |
| `approved` | `deprecated` |
| `deprecated` | — (terminal) |

## Delivery tier

### REL

**Statuses:** `planned`, `ready`, `released`, `rolled-back`

| From | Allowed next |
| --- | --- |
| `planned` | `ready` |
| `ready` | `released`, `planned` |
| `released` | `rolled-back` |
| `rolled-back` | — (terminal) |

### RISK

**Statuses:** `open`, `mitigating`, `mitigated`, `accepted`, `closed`

| From | Allowed next |
| --- | --- |
| `open` | `mitigating`, `accepted`, `closed` |
| `mitigating` | `mitigated`, `accepted`, `closed` |
| `mitigated` | `closed`, `open` |
| `accepted` | `closed`, `open` |
| `closed` | — (terminal) |

