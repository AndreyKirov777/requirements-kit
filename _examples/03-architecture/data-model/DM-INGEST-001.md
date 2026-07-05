---
id: DM-INGEST-001
title: Bronze-layer static battery record
type: data-model
status: proposed
owner: "@techlead"
domain: INGEST
related_requirements:
  - "[[FR-INGEST-001]]"
related_adrs:
  - "[[ADR-INGEST-001]]"
tags: [data-model, ingest]
updated: 2026-03-28
---

# Data Model

The immutable record written to the Bronze layer for each static-data submission.

# Entity: BronzeStaticRecord

| Field         | Type      | Notes                                        |
| ------------- | --------- | -------------------------------------------- |
| ingestionId   | string    | Unique per submission (server-generated)     |
| batteryId     | string    | Battery identifier supplied by the operator  |
| submitterId   | string    | Authenticated operator identity              |
| payload       | json      | Raw static data, stored unmodified           |
| receivedAt    | timestamp | Server receive time                          |

# Rules

- The record is append-only and never updated in place (see [[ADR-INGEST-001]]).
- `payload` is stored exactly as received — no normalization at this tier.
- Multiple records may share a `batteryId`; each has a distinct `ingestionId`.

# Related Requirements

Persisted by [[FR-INGEST-001]].
