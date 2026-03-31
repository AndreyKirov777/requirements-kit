---
id: FR-INGEST-001
title: Ingest static battery data via REST API
type: functional-requirement
status: proposed
priority: high
owner: '@techlead'
domain: INGEST
component:
- ingestion-api
- validator
stakeholders:
- '@techlead'
source_docs:
- '[[EPIC-INGEST-001]]'
parent_epic: '[[EPIC-INGEST-001]]'
related_adrs: []
depends_on: []
implemented_by: []
verified_by:
- '[[TEST-INGEST-001]]'
tags:
- req
- ingest
- api
updated: '2026-03-28'
risk: medium
blocks: []
release_target: ''
quality_attribute: ''
delivered_by: []
derives_from: []
implements_control: []
---

# Summary

The system shall accept static battery passport data via a REST API endpoint, authenticate the submitter, and persist raw data to the Bronze layer for downstream validation and enrichment.

# Context

Battery manufacturers and authorized partners need a standardized way to submit static battery passport information (e.g., cell chemistry, design capacity, manufacturing date) into the system. This data forms the foundation for all passport operations and must be securely ingested and stored in its raw form before validation.

# Requirement

The system shall accept static battery passport data via a REST API endpoint, authenticate the submitter, and persist raw data to the Bronze layer.

# Edge Cases

- Duplicate submissions: Same batteryId submitted multiple times; system shall assign unique ingestionIds and persist each submission.
- Very large payloads: Payloads exceeding configured size limits; system shall return HTTP 413 Payload Too Large.
- Network timeout during persist: Connection lost between client and server; system shall return appropriate error and ensure no partial data is committed.
- Concurrent submissions: Multiple requests for the same batteryId submitted simultaneously; system shall handle concurrency safely with eventual consistency.

# Out of Scope

- Data validation against EU 2023/1542 (handled by FR-INGEST-003).
- Transformation or enrichment of static data (Bronze layer stores raw data only).
- Batch ingestion APIs (single-record REST API only in this requirement).

# Open Questions

- Should the API support batch ingestion of multiple batteries in a single request?
- What is the maximum allowed payload size?
- Should invalid submissions trigger automatic retry notifications?


# Business Value

- ...

# Links

- Epic: [[EPIC-INGEST-001]]
- Delivered by: [[US-INGEST-001]]
- Tests: [[TEST-INGEST-001]]
