---
id: TASK-INGEST-001
title: Implement REST API endpoint for static battery data ingestion
type: implementation-task
status: backlog
owner: "@techlead"
assigned_to: ai-agent
implements: "[[FR-INGEST-001]]"
part_of_story: "[[US-INGEST-001]]"
acceptance_criteria_subset: [AC-1, AC-2, AC-3]
target_files:
  - src/ingest/api/static-data-handler.ts
  - src/ingest/api/static-data-handler.test.ts
  - src/ingest/api/routes.ts
depends_on_tasks: []
estimated_complexity: medium
release_target: 2026-Q3
tags: [task, ingest]
updated: 2026-03-28
---

# Objective

Implement the REST API endpoint `POST /api/v1/batteries/{batteryId}/static-data` that accepts static battery passport data, authenticates the submitter, validates the payload structure, and persists raw data to the Bronze layer.

# Implementation Notes

- Use the existing auth middleware for submitter authentication (OAuth2 bearer token).
- Validate payload structure against the static data JSON schema (see `src/shared/schema/eu-2023-1542.ts`).
- Persist to Bronze layer using the raw data repository — data must be stored in original form, immutable.
- Return HTTP 201 with an ingestion receipt containing `ingestionId`, `batteryId`, `timestamp`.
- Return HTTP 400 with a structured error listing all missing/invalid fields.
- Return HTTP 401 for unauthenticated requests.
- Use glossary code names: `batteryId`, `staticData`, `bronzeLayer`.

# Target Files

- `src/ingest/api/static-data-handler.ts` — request handler with validation and persistence logic
- `src/ingest/api/static-data-handler.test.ts` — unit tests for AC-1, AC-2, AC-3
- `src/ingest/api/routes.ts` — route registration

# Acceptance Criteria Covered

From [[US-INGEST-001]]:

- **AC-1**: Given valid static data payload and authenticated submitter, when POST endpoint is called, then data is persisted to `bronzeLayer` with HTTP 201 and ingestion receipt. `testable_by: integration`
- **AC-2**: Given invalid or incomplete payload, when submitted, then HTTP 400 with validation errors. `testable_by: unit`
- **AC-3**: Given unauthenticated request, when submitted, then HTTP 401. `testable_by: unit`

# Done Checklist

- [ ] Endpoint handler implemented with auth check
- [ ] Payload validation against static data schema
- [ ] Bronze layer persistence (raw, immutable)
- [ ] Ingestion receipt returned on success
- [ ] Structured error response on validation failure
- [ ] Unit tests for all 3 acceptance criteria
- [ ] FR-INGEST-001 `implemented_by` updated
- [ ] Validation scripts pass
