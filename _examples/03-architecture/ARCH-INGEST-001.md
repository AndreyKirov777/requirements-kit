---
id: ARCH-INGEST-001
title: Ingestion pipeline architecture
type: domain-architecture
status: proposed
owner: "@techlead"
domain: INGEST
parent_overview: "[[architecture-overview]]"
related_requirements:
  - "[[FR-INGEST-001]]"
related_adrs:
  - "[[ADR-INGEST-001]]"
tags: [architecture, ingest]
updated: 2026-03-28
---

# Overview

Detailed architecture for the INGEST domain: how a submission travels from the REST
API to immutable Bronze storage. Elaborates the system-wide picture in
[[architecture-overview]].

# Internal Components

- **static-data-handler** — validates payload shape, authenticates the submitter,
  writes to the Bronze repository.
- **bronze-repository** — append-only writer producing one immutable record with a
  unique `ingestionId` per submission.

# Data Flow

`REST POST → auth check → shape validation → bronze-repository.write() → receipt`

# API and Interfaces

Public REST contract defined in [[CONTRACT-INGEST-001]].

# Data Model

Bronze record shape defined in [[DM-INGEST-001]].

# Key Decisions

Three-tier data architecture — [[ADR-INGEST-001]].

# Constraints and Trade-offs

Bronze writes are immutable; correction happens by new submissions, never in place.

# Related Artifacts

Requirement [[FR-INGEST-001]]; risk [[RISK-INGEST-001]] (throughput).
