---
id: PERSONA-DBP-002
title: Integration Engineer Ravi
type: persona
status: approved
owner: "@pm"
domain: INGEST
tags: [persona]
updated: 2026-03-28
---

# Persona

**Ravi** is a data integration engineer at an economic operator (a battery
manufacturer). He owns the pipelines that push manufacturing and supply-chain data
into external systems.

# Goals

- Submit static battery data automatically from existing manufacturing systems.
- Migrate a backlog of thousands of existing batteries with minimal manual effort.
- Get clear, machine-readable error feedback when a submission is rejected.

# Frustrations

- One-record-at-a-time APIs that make bulk migration slow.
- Opaque validation errors that don't say which field failed.

# Relevant Artifacts

Primary actor of [[US-INGEST-001]]; motivates change request [[CR-INGEST-001]]
(batch ingestion).
