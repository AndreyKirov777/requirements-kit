---
id: UC-INGEST-001
title: Submit static battery data
type: use-case
status: approved
priority: high
owner: "@techlead"
domain: INGEST
actors:
  - "[[PERSONA-DBP-002]]"
related_requirements:
  - "[[FR-INGEST-001]]"
related_epics:
  - "[[EPIC-INGEST-001]]"
tags: [use-case, ingest]
updated: 2026-03-28
---

# Use Case

An authenticated economic operator submits static passport data for a single battery.

# Primary Actor

[[PERSONA-DBP-002|Integration Engineer Ravi]].

# Preconditions

- The operator has valid API credentials.
- The battery's `batteryId` is known to the operator.

# Main Success Scenario

1. The operator sends a static-data payload to the ingestion endpoint.
2. The system authenticates the submitter.
3. The system persists the raw payload to the Bronze layer.
4. The system returns an ingestion receipt (`ingestionId`, timestamp).
5. The system records an audit event.

# Extensions

- **2a. Authentication fails** → the system returns HTTP 401 and stops.
- **3a. Payload invalid** → the system returns HTTP 400 with field-level errors.

# Related Requirements

Realized by [[FR-INGEST-001]]; acceptance criteria live in [[US-INGEST-001]].
