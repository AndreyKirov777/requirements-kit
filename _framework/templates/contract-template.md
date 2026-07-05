---
id: CONTRACT-XXX-000
title: ""
type: api-contract
status: draft
owner: ""
domain: ""
component: []
related_requirements:
  - "[[FR-XXX-000]]"
related_adrs: []
protocol: REST
tags: [contract]
updated: YYYY-MM-DD
---

# Overview

Brief description of what this API/interface does and who consumes it.

# Endpoint / Interface

| Field    | Value                  |
| -------- | ---------------------- |
| Protocol | REST / gRPC / Event    |
| Path     | `/api/v1/resource`     |
| Method   | POST / GET / …         |
| Auth     | Bearer token / API key |

# Request

```json
{
  "field": "type — description"
}
```

## Required Fields

| Field   | Type   | Description     | Validation         |
| ------- | ------ | --------------- | ------------------ |
| field   | string | What it means   | Non-empty, max 255 |

# Response

## Success (200)

```json
{
  "field": "type — description"
}
```

## Error Responses

| Code | Condition           | Body                          |
| ---- | ------------------- | ----------------------------- |
| 400  | Invalid input       | `{ "error": "description" }`  |
| 401  | Unauthorized        | `{ "error": "unauthorized" }` |
| 500  | Internal error      | `{ "error": "internal" }`     |

# Events (if applicable)

| Event Name         | Trigger              | Payload Schema            |
| ------------------ | -------------------- | ------------------------- |
| `resource.created` | After resource creation   | `{ id, type, timestamp }`        |

# SLA / Non-Functional

| Metric    | Target          |
| --------- | --------------- |
| Latency   | p95 < 300 ms    |
| Availability | 99.9%        |
