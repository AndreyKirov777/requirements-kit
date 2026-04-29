---
id: META-TAXONOMY-DOMAINS-DBP
title: Domain Registry
updated: 2026-04-29
---

# Domain Registry

This file lists all recognized domains for the Digital Battery Passport Accelerator. Use these values in the `domain` frontmatter field. AI agents should not create new domains without adding them here first.

## Domains

### INGEST — Data Ingestion & Validation

| Field       | Value                                                      |
| ----------- | ---------------------------------------------------------- |
| Code        | INGEST                                                     |
| Full Name   | Data Ingestion & Validation                                |
| Description | Bronze and Silver tiers: raw data capture, cleansing, normalization, validation against regulation schema |
| Owner       | @techlead                                                  |

### PASSPORT — Passport & Compliance Services

| Field       | Value                                                      |
| ----------- | ---------------------------------------------------------- |
| Code        | PASSPORT                                                   |
| Full Name   | Passport & Compliance Services                             |
| Description | Gold tier: battery passport CRUD, completeness assessment, lifecycle management, regulatory data model |
| Owner       | @techlead                                                  |

### SEC — Security & Access Control

| Field       | Value                                                      |
| ----------- | ---------------------------------------------------------- |
| Code        | SEC                                                        |
| Full Name   | Security & Access Control                                  |
| Description | Authentication, authorization (RBAC/ABAC), encryption, field-level masking, PKI verification |
| Owner       | @techlead                                                  |

### QR — QR Code & Public Passport

| Field       | Value                                                      |
| ----------- | ---------------------------------------------------------- |
| Code        | QR                                                         |
| Full Name   | QR Code & Public Passport                                  |
| Description | QR code generation (ISO/IEC 15459), lifetime-stable URLs, public battery passport webpage |
| Owner       | @pm                                                        |

### AUDIT — Audit & Logging

| Field       | Value                                                      |
| ----------- | ---------------------------------------------------------- |
| Code        | AUDIT                                                      |
| Full Name   | Audit & Logging                                            |
| Description | Field-level data lineage, append-only event logs, API request tracing, change history |
| Owner       | @techlead                                                  |

### API — Downstream API & Data Exchange

| Field       | Value                                                      |
| ----------- | ---------------------------------------------------------- |
| Code        | API                                                        |
| Full Name   | Downstream API & Data Exchange                             |
| Description | External data access API, role-based data content, delta-based access, data export, authority submission |
| Owner       | @techlead                                                  |

### UI — Platform User Interface

| Field       | Value                                                      |
| ----------- | ---------------------------------------------------------- |
| Code        | UI                                                         |
| Full Name   | Platform User Interface                                    |
| Description | Compliance dashboard, passport management, reports, admin panel, public passport view |
| Owner       | @pm                                                        |

### INFRA — Infrastructure & Operations

| Field       | Value                                                      |
| ----------- | ---------------------------------------------------------- |
| Code        | INFRA                                                      |
| Full Name   | Infrastructure & Operations                                |
| Description | Backup/restore, WORM archiving, deployment, monitoring, infrastructure security |
| Owner       | @techlead                                                  |

## How to Add a New Domain

1. Choose a short uppercase code that does not conflict with existing domains.
2. Add it to this file with owner and description.
3. Update the glossary in `00-meta/glossary/dbp.md` with domain-specific terms.
4. Create or update the code-map in `03-architecture/code-map/`.
5. Update this document's date.
