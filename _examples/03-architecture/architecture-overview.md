---
id: ARCH-OVERVIEW
title: DBP Accelerator — Architecture Overview
type: architecture-overview
status: approved
owner: "@techlead"
domain: all
tags: [architecture]
updated: 2026-03-28
---

# Architecture Style

A modular, event-friendly backend organized around a three-tier data architecture
(Bronze → Silver → Gold), chosen for auditability and regulatory traceability. See
[[ADR-INGEST-001]] for the decision record.

# System Context

Economic operators submit battery data via a REST API; public users and authorities
read passport data via QR-linked views. External systems include the operators'
manufacturing pipelines and (future) EU registry integrations.

# Component Overview

| Component      | Type    | Responsibility                          | Domain |
| -------------- | ------- | --------------------------------------- | ------ |
| ingestion-api  | service | Accept and persist raw submissions      | INGEST |
| bronze-store   | db      | Immutable raw data                      | INGEST |
| access-control | service | Enforce differentiated data access      | SEC    |

# Technology Stack

| Layer    | Technology  | Notes                    |
| -------- | ----------- | ------------------------ |
| Backend  | Node.js/TS  | REST ingestion API       |
| Storage  | PostgreSQL  | Encrypted at rest        |

# Cross-Cutting Concerns

Authentication (OAuth2 bearer), encryption at rest ([[NFR-SEC-001]]), and audit
logging of access decisions ([[CTRL-SEC-001]]).

# Domain Architecture Index

| Domain | Document            | Status   | Summary                     |
| ------ | ------------------- | -------- | --------------------------- |
| INGEST | [[ARCH-INGEST-001]] | proposed | Ingestion pipeline internals |

# Key Decisions

- [[ADR-INGEST-001]] — three-tier data architecture.

# Constraints and Trade-offs

- Runtime-configurable access rules pending implementing acts — see [[CON-SEC-001]].

# Related Artifacts

- Vision: [[VISION-DBP-001]]
- Epics: [[EPIC-INGEST-001]]
- Data models: [[DM-INGEST-001]]
- Contracts: [[CONTRACT-INGEST-001]]
