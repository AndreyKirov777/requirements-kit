---
id: REL-DBP-001
title: DBP Accelerator 1.0 — Ingestion foundation
type: release
status: planned
owner: "@pm"
release_date: 2026-09-30
requirements_included:
  - "[[FR-INGEST-001]]"
  - "[[NFR-SEC-001]]"
epics_included:
  - "[[EPIC-INGEST-001]]"
tags: [release, dbp]
updated: 2026-03-28
---

# Release

First release of the Digital Battery Passport Accelerator, delivering the ingestion
foundation and baseline data-at-rest security.

# Scope

- [[FR-INGEST-001]] — static battery data ingestion via REST API.
- [[NFR-SEC-001]] — encryption of passport data at rest.
- [[EPIC-INGEST-001]] — ingestion and validation pipeline (partial).

# Exit Criteria

- All included requirements at `verified`.
- No open `critical` risks affecting the included scope.

# Notes

Batch ingestion ([[CR-INGEST-001]]) is deferred to a later release.
