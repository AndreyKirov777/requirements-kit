---
id: TEST-INGEST-001
title: Verify static battery data ingestion via REST API
status: draft
owner: '@qa'
verifies:
- '[[FR-INGEST-001]]'
type: functional
priority: high
covers_criteria:
- AC-1
- AC-2
- AC-3
- AC-4
tags:
- test
- ingest
- api
updated: '2026-03-28'
domain: ''
verifies_control: []
---

# Objective
Verify that the static data ingestion endpoint accepts valid payloads, rejects invalid ones, enforces authentication, and emits audit events — covering all acceptance criteria of US-INGEST-001.

# Preconditions
- Ingestion API is deployed and reachable
- Bronze layer storage is available and writable
- Test API credentials (valid and expired) are provisioned
- Audit event consumer is running

# Test Ideas

## AC-1: Successful ingestion
- Submit a valid static data payload with all required fields for a new batteryId → expect HTTP 201 with ingestionId and timestamp
- Submit valid payload for an existing batteryId (duplicate) → expect HTTP 201 with a new unique ingestionId
- Verify data is persisted to bronzeLayer in raw form (no transformation applied)

## AC-2: Validation errors
- Submit payload with missing required fields → expect HTTP 400 with field-level error list
- Submit payload with invalid data types (e.g., string where number expected) → expect HTTP 400 with type mismatch details
- Submit empty payload → expect HTTP 400

## AC-3: Authentication enforcement
- Submit request without Authorization header → expect HTTP 401
- Submit request with expired credentials → expect HTTP 401
- Submit request with invalid token format → expect HTTP 401
- Verify no data is persisted when authentication fails

## AC-4: Audit event emission
- After successful ingestion, verify an audit event is recorded with: submitter identity, timestamp, batteryId, action type "STATIC_DATA_INGEST"
- Verify audit event is NOT emitted for rejected requests (HTTP 400, 401)

# Expected Results
- All acceptance criteria of US-INGEST-001 are covered
- No partial data committed on failure scenarios
- Audit trail is complete and accurate for successful operations

# Notes
- Use glossary code names: `batteryId`, `staticData`, `bronzeLayer`
- Edge cases (payload size limits, concurrent submissions) are documented in FR-INGEST-001 edge cases but not covered by these acceptance criteria — see test-ideas/ for exploratory coverage
