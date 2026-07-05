---
id: CONTRACT-INGEST-001
title: Static battery data ingestion REST API
type: api-contract
status: proposed
owner: "@techlead"
domain: INGEST
protocol: REST
component:
  - ingestion-api
related_requirements:
  - "[[FR-INGEST-001]]"
related_adrs:
  - "[[ADR-INGEST-001]]"
tags: [contract, ingest, api]
updated: 2026-03-28
---

# Contract

Public REST interface for submitting static battery data. Realizes [[FR-INGEST-001]].

# Endpoint

`POST /api/v1/batteries/{batteryId}/static-data`

# Request

- **Auth:** `Authorization: Bearer <token>` (OAuth2).
- **Body:** JSON static-data payload for the given `batteryId`.

# Responses

| Status | Meaning                | Body                                       |
| ------ | ---------------------- | ------------------------------------------ |
| 201    | Persisted to Bronze    | `{ ingestionId, batteryId, receivedAt }`   |
| 400    | Validation failed      | `{ errors: [{ field, message }] }`         |
| 401    | Not authenticated      | `{ error }`                                |
| 413    | Payload too large      | `{ error }`                                |

# Notes

Batch submission is not part of this contract; see [[CR-INGEST-001]].
