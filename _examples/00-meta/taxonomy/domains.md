---
id: META-TAXONOMY-DOMAINS-DBP
title: Domain and Component Registry
updated: 2026-03-28
---

# Domain and Component Registry

This file lists all recognized domains and their components for the Digital Battery Passport Accelerator. Use these values in the `domain` and `component` frontmatter fields. AI agents should not create new domains or components without adding them here first.

## Domains

### INGEST — Data Ingestion & Validation

| Field       | Value                                                      |
| ----------- | ---------------------------------------------------------- |
| Code        | INGEST                                                     |
| Full Name   | Data Ingestion & Validation                                |
| Description | Bronze and Silver tiers: raw data capture, cleansing, normalization, validation against regulation schema |
| Owner       | @techlead                                                  |
| Glossary    | [[dbp]] (`00-meta/glossary/dbp.md`)                        |

**Components:**

| Component      | Code Path (see code-map)       | Description                                           |
| -------------- | ------------------------------ | ----------------------------------------------------- |
| ingestion-api  | `src/ingest/api/`              | REST/streaming endpoints for receiving battery data   |
| validator      | `src/ingest/validator/`        | Schema validation, business rules, completeness check |
| transformer    | `src/ingest/transformer/`      | Cleansing, normalization, mapping to unified model    |
| data-generator | `src/ingest/data-generator/`   | Mock data generator for testing and demos             |

### PASSPORT — Passport & Compliance Services

| Field       | Value                                                      |
| ----------- | ---------------------------------------------------------- |
| Code        | PASSPORT                                                   |
| Full Name   | Passport & Compliance Services                             |
| Description | Gold tier: battery passport CRUD, completeness assessment, lifecycle management, regulatory data model |
| Owner       | @techlead                                                  |
| Glossary    | [[dbp]] (`00-meta/glossary/dbp.md`)                        |

**Components:**

| Component        | Code Path (see code-map)        | Description                                      |
| ---------------- | ------------------------------- | ------------------------------------------------ |
| passport-service | `src/passport/service/`         | Passport CRUD, search, completeness scoring      |
| compliance       | `src/passport/compliance/`      | Regulatory rule engine, field-level status        |
| lifecycle        | `src/passport/lifecycle/`       | Battery lifecycle events and state transitions    |
| data-model       | `src/passport/model/`           | Unified battery passport data model (Gold layer) |

### SEC — Security & Access Control

| Field       | Value                                                      |
| ----------- | ---------------------------------------------------------- |
| Code        | SEC                                                        |
| Full Name   | Security & Access Control                                  |
| Description | Authentication, authorization (RBAC/ABAC), encryption, field-level masking, PKI verification |
| Owner       | @techlead                                                  |
| Glossary    | [[dbp]] (`00-meta/glossary/dbp.md`)                        |

**Components:**

| Component    | Code Path (see code-map)    | Description                                          |
| ------------ | --------------------------- | ---------------------------------------------------- |
| auth         | `src/security/auth/`        | OAuth2/OIDC, MFA, session management                 |
| rbac         | `src/security/rbac/`        | Role/attribute-based access control policy engine     |
| encryption   | `src/security/encryption/`  | AES-256 at rest, field-level masking                  |
| pki          | `src/security/pki/`         | PKI certificate verification for system-to-system    |

### QR — QR Code & Public Passport

| Field       | Value                                                      |
| ----------- | ---------------------------------------------------------- |
| Code        | QR                                                         |
| Full Name   | QR Code & Public Passport                                  |
| Description | QR code generation (ISO/IEC 15459), lifetime-stable URLs, public battery passport webpage |
| Owner       | @pm                                                        |
| Glossary    | [[dbp]] (`00-meta/glossary/dbp.md`)                        |

**Components:**

| Component      | Code Path (see code-map)    | Description                                       |
| -------------- | --------------------------- | ------------------------------------------------- |
| qr-generator   | `src/qr/generator/`         | QR code creation, unique ID encoding, print-ready |
| public-passport| `src/qr/public-passport/`   | Public-facing battery passport webpage            |

### AUDIT — Audit & Logging

| Field       | Value                                                      |
| ----------- | ---------------------------------------------------------- |
| Code        | AUDIT                                                      |
| Full Name   | Audit & Logging                                            |
| Description | Field-level data lineage, append-only event logs, API request tracing, change history |
| Owner       | @techlead                                                  |
| Glossary    | [[dbp]] (`00-meta/glossary/dbp.md`)                        |

**Components:**

| Component     | Code Path (see code-map)     | Description                                      |
| ------------- | ---------------------------- | ------------------------------------------------ |
| event-log     | `src/audit/event-log/`       | Append-only event storage                        |
| data-lineage  | `src/audit/data-lineage/`    | Field-level lineage tracking across lifecycle    |
| request-trace | `src/audit/request-trace/`   | API logging and distributed request tracing      |

### API — Downstream API & Data Exchange

| Field       | Value                                                      |
| ----------- | ---------------------------------------------------------- |
| Code        | API                                                        |
| Full Name   | Downstream API & Data Exchange                             |
| Description | External data access API, role-based data content, delta-based access, data export, authority submission |
| Owner       | @techlead                                                  |
| Glossary    | [[dbp]] (`00-meta/glossary/dbp.md`)                        |

**Components:**

| Component       | Code Path (see code-map)      | Description                                       |
| --------------- | ----------------------------- | ------------------------------------------------- |
| downstream-api  | `src/api/downstream/`         | Standard data access interface for external systems |
| data-export     | `src/api/export/`             | Individual and batch passport export               |
| authority-sub   | `src/api/authority/`          | EC registry and portal data submission             |

### UI — Platform User Interface

| Field       | Value                                                      |
| ----------- | ---------------------------------------------------------- |
| Code        | UI                                                         |
| Full Name   | Platform User Interface                                    |
| Description | Compliance dashboard, passport management, reports, admin panel, public passport view |
| Owner       | @pm                                                        |
| Glossary    | [[dbp]] (`00-meta/glossary/dbp.md`)                        |

**Components:**

| Component        | Code Path (see code-map)   | Description                                         |
| ---------------- | -------------------------- | --------------------------------------------------- |
| dashboard        | `src/ui/dashboard/`        | Compliance dashboard, completeness overview          |
| passport-views   | `src/ui/passport-views/`   | Passport list, detail, search, filters               |
| admin            | `src/ui/admin/`            | User management, role config, backup/restore         |
| reports          | `src/ui/reports/`          | Reporting views, export-ready reports                |

### INFRA — Infrastructure & Operations

| Field       | Value                                                      |
| ----------- | ---------------------------------------------------------- |
| Code        | INFRA                                                      |
| Full Name   | Infrastructure & Operations                                |
| Description | Backup/restore, WORM archiving, deployment, monitoring, infrastructure security |
| Owner       | @techlead                                                  |
| Glossary    | [[dbp]] (`00-meta/glossary/dbp.md`)                        |

**Components:**

| Component   | Code Path (see code-map)      | Description                                      |
| ----------- | ----------------------------- | ------------------------------------------------ |
| backup      | `src/infra/backup/`           | Automatic backups, integrity verification        |
| archive     | `src/infra/archive/`          | WORM archival storage                            |
| monitoring  | `src/infra/monitoring/`       | Observability, alerting, health checks           |

## How to Add a New Domain

1. Choose a short uppercase code that does not conflict with existing domains.
2. Add it to this file with owner, description, and initial components.
3. Update the glossary in `00-meta/glossary/dbp.md` with domain-specific terms.
4. Create or update the code-map in `03-architecture/code-map/`.
5. Update this document's date.
