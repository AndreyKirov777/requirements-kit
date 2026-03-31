---
id: CR-INGEST-001
title: Add batch ingestion support to static data endpoint
status: proposed
owner: '@techlead'
affects:
- '[[FR-INGEST-001]]'
reason: Early adopters need to submit multiple batteries in a single API call for efficiency
priority: medium
release_target: 2026-Q4
tags:
- change-request
- ingest
updated: '2026-03-28'
domain: ''
---

# Change Summary
Extend the existing single-record REST API endpoint (`POST /api/v1/batteries/{batteryId}/static-data`) to also support batch submission of multiple batteries in a single request.

# Rationale
During pilot onboarding, economic operators reported that submitting battery data one-at-a-time is too slow for initial data migration (thousands of existing batteries). A batch endpoint would reduce integration complexity and network overhead.

# Impact Analysis
- Affected requirements: [[FR-INGEST-001]] (new AC needed for batch mode)
- Affected ADRs: [[ADR-INGEST-001]] (Bronze layer write strategy for bulk inserts)
- Affected tests: [[TEST-INGEST-001]] (new test cases for batch happy path and partial failures)
- Affected components: ingestion-api, validator

# Decision Needed
Confirm whether batch mode is added to the existing endpoint (array payload) or as a separate endpoint (`POST /api/v1/batteries/batch`).

# Open Questions
- What is the maximum batch size (number of batteries per request)?
- How should partial failures be handled — reject entire batch or report per-item errors?
