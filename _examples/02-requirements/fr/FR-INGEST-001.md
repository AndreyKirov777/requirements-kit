---
id: FR-INGEST-001
title: Ingest static battery data via REST API
status: approved
priority: high
owner: "@techlead"
domain: INGEST
parent_epic: "[[EPIC-INGEST-001]]"
derives_from:
  - "[[BR-COMPLY-001]]"
depends_on: []
updated: 2026-03-28
---

# Summary

The system needs a standardized entry point for economic operators to submit static battery passport data so it can be persisted for downstream validation and passport assembly.

# Context

Battery manufacturers and authorized partners submit static passport information (cell chemistry, design capacity, manufacturing date). This raw data must be captured and stored before any validation or enrichment. Authentication of the submitter is a security concern handled by [[NFR-SEC-001]] and control [[CTRL-SEC-001]], not by this requirement.

# Requirement

The system shall accept a static battery data payload for a given `batteryId` via a REST API endpoint and persist it, unmodified, to the Bronze layer.

# Business Value

Provides authorized parties a controlled, auditable way to submit battery passport data, forming the raw foundation for all passport operations.

# Edge Cases

- Duplicate submissions: the same `batteryId` submitted multiple times — each submission is persisted with its own unique `ingestionId`.
- Oversized payloads: payloads exceeding the configured size limit return HTTP 413.
- Interrupted persistence: on a write failure no partial record is committed to the Bronze layer.

# Out of Scope

- Submitter authentication and authorization (see [[NFR-SEC-001]]).
- Validation against EU 2023/1542 field rules (separate requirement).
- Transformation or enrichment (Bronze stores raw data only).
- Batch ingestion of multiple batteries in one request (see [[CR-INGEST-001]]).

# Open Questions

- What is the maximum allowed payload size?
