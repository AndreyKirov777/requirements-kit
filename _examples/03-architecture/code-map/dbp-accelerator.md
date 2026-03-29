---
id: CODEMAP-DBP
title: DBP Accelerator Code Map
type: code-map
domain: all
updated: 2026-03-28
---

# Digital Battery Passport Accelerator - Code Map

This document maps all functional domains, code components, and shared dependencies for the DBP Accelerator system. Use this as a reference for understanding the codebase structure and for directing AI agents to relevant modules.

---

## Domain Overview

The DBP Accelerator is organized into 8 functional domains:

| Domain | Purpose | Owner |
|--------|---------|-------|
| **INGEST** | Data ingestion from diverse sources | Data Platform |
| **PASSPORT** | Battery passport data model & lifecycle | Product |
| **SEC** | Security, authentication, encryption | Security |
| **QR** | QR code generation & public passport view | Product |
| **AUDIT** | Audit trails, data lineage, request tracing | Compliance |
| **API** | Downstream APIs, exports, authority integration | Integrations |
| **UI** | Web dashboards, admin panels, reporting | Frontend |
| **INFRA** | Backup, archival, monitoring | DevOps |

---

## INGEST Domain

**Purpose**: Receive, validate, and persist battery passport data from external sources (manufacturers, distributors, regulators).

### Components

#### ingestion-api
- **Path**: `src/ingest/api/`
- **Responsibility**: REST/GraphQL endpoints for single and bulk data submission
- **Key Files**:
  - `routes.ts` — HTTP route handlers
  - `middleware/auth.ts` — Request authentication
  - `middleware/rate-limit.ts` — Rate limiting per source
  - `handlers/ingest.ts` — Main ingest handler (calls validator, transformer, Bronze writer)
  - `serializers/` — Request/response serialization
- **Dependencies**: validator, transformer, audit-logger, config-loader
- **Interfaces**: Exposes POST `/api/v1/ingest`, POST `/api/v1/ingest/bulk`

#### validator
- **Path**: `src/ingest/validator/`
- **Responsibility**: Schema validation and conformance checking
- **Key Files**:
  - `schemas/` — JSON Schema definitions for each source type
  - `index.ts` — Main validator orchestrator
  - `rules/` — Business rule validators (e.g., serial number uniqueness, date ranges)
  - `error-formatter.ts` — Validation error reporting
- **Dependencies**: battery-passport-types, regulation-schema
- **Validation Gates**:
  - Structural (schema conformance)
  - Semantic (business rules)
  - Regulatory (EU 2023/1542 compliance)

#### transformer
- **Path**: `src/ingest/transformer/`
- **Responsibility**: Normalize diverse source formats to unified battery-passport data model
- **Key Files**:
  - `mappers/` — Format-specific mappers (manufacturer, distributor, regulator)
  - `index.ts` — Transformer orchestrator
  - `normalizers/` — Field normalization (unit conversion, date parsing)
  - `enrichers/` — Computed fields (derived attributes, confidence scores)
- **Dependencies**: battery-passport-types, config-loader
- **Supported Sources**: Manufacturer JSON/XML, EDI, CSV, regulatory feeds

#### data-generator
- **Path**: `src/ingest/data-generator/`
- **Responsibility**: Generate test/demo battery passport data for development and load testing
- **Key Files**:
  - `factories/` — Faker-based data factories
  - `scenarios/` — Pre-canned scenarios (typical battery, edge cases)
  - `seeder.ts` — Bulk load into Bronze for testing
- **Dependencies**: validator, transformer, battery-passport-types
- **Usage**: `npm run seed:bronze` for test data

### Tests
- **Path**: `tests/ingest/`
- **Coverage**: Unit tests for each component + integration tests for end-to-end ingest flow
- **Key Test Files**:
  - `integration/ingest-flow.test.ts` — Full Bronze persistence
  - `unit/validator.test.ts` — Validation rules
  - `unit/transformer.test.ts` — Format conversions
  - `e2e/ingest-latency.perf.ts` — NFR-INGEST-001 verification

### Data Flow
```
External Source → ingestion-api → validator → transformer → Bronze Storage
                                         ↓
                                   audit-logger (request tracking)
```

---

## PASSPORT Domain

**Purpose**: Define and manage the battery passport data model, lifecycle, and business logic.

### Components

#### passport-service
- **Path**: `src/passport/service/`
- **Responsibility**: Core business logic for passport retrieval, updates, and state transitions
- **Key Files**:
  - `index.ts` — Main service interface
  - `queries/` — Complex passport queries (by ID, serial, manufacturer)
  - `mutations/` — Create, update, delete operations with audit
  - `state-machine.ts` — Passport lifecycle state transitions
  - `validators.ts` — Business rule validation before mutations
- **Dependencies**: battery-passport-types, audit-logger, rbac-engine
- **Events Emitted**: PassportCreated, PassportUpdated, PassportRetired, etc.

#### compliance
- **Path**: `src/passport/compliance/`
- **Responsibility**: Regulatory compliance checks and reporting
- **Key Files**:
  - `eu-2023-1542.ts` — EU regulation compliance validator
  - `data-classification.ts` — Classify data as public/legitimate/confidential
  - `access-policies.ts` — Implement access tiers per regulation
  - `reports/` — Compliance reporting templates
- **Dependencies**: battery-passport-types, regulation-schema, rbac-engine
- **Compliance Checks**: Data completeness, classification accuracy, retention policies

#### lifecycle
- **Path**: `src/passport/lifecycle/`
- **Responsibility**: Manage passport state across manufacturing, in-use, and end-of-life phases
- **Key Files**:
  - `states.ts` — Enumerations of valid states (Draft, Published, InUse, Retired, Archived)
  - `transitions.ts` — Valid state transition rules
  - `handlers/` — State-specific behaviors (e.g., PublishedHandler, RetiredHandler)
- **Dependencies**: passport-service, audit-logger
- **Events Emitted**: State change events for downstream listeners

#### data-model
- **Path**: `src/passport/model/`
- **Responsibility**: TypeScript interfaces and runtime validation for battery passport schema
- **Key Files**:
  - `types.ts` — Core passport interfaces (see shared/types/battery-passport.ts for canonical definition)
  - `validators.ts` — Runtime type checks
  - `serializers.ts` — Serialize/deserialize to/from storage formats
- **Dependencies**: battery-passport-types
- **Note**: Implementation details here; canonical schema in shared/types/

### Tests
- **Path**: `tests/passport/`
- **Coverage**: Unit tests for service logic, state machine, compliance checks
- **Key Test Files**:
  - `unit/passport-service.test.ts`
  - `unit/state-machine.test.ts`
  - `unit/compliance.test.ts`
  - `integration/passport-lifecycle.test.ts`

### Data Flow
```
Silver Storage → passport-service → lifecycle → audit-logger
                      ↓
                 compliance checks
                      ↓
                 Gold Storage (enriched view)
```

---

## SEC Domain

**Purpose**: Implement security controls: authentication, authorization, encryption, and key management.

### Components

#### auth
- **Path**: `src/security/auth/`
- **Responsibility**: Authentication (verify identity) and token management
- **Key Files**:
  - `strategies/` — OAuth2, JWT, API key strategies
  - `jwt.ts` — JWT generation, validation, refresh
  - `api-key.ts` — API key provisioning and validation
  - `middleware/verify.ts` — Express/Koa middleware
  - `session-manager.ts` — Session lifecycle
- **Dependencies**: config-loader, audit-logger
- **Protocols Supported**: OAuth2, JWT, API Key, (future: SAML, OIDC)

#### rbac
- **Path**: `src/security/rbac/`
- **Responsibility**: Role-based and attribute-based access control (hybrid RBAC/ABAC)
- **Key Files**:
  - `engine.ts` — Policy evaluation engine
  - `policies/` — Policy definitions (stored in config or DB)
  - `roles.ts` — Role definitions (public_user, distributor, manufacturer, authority, researcher, admin)
  - `middleware/enforce.ts` — Express middleware to enforce policies
  - `admin/` — Admin UI backend for policy management
- **Dependencies**: battery-passport-types, config-loader, audit-logger
- **Policy Storage**: Config-driven (YAML) with optional DB override
- **Implements**: ADR-SEC-001 (RBAC/ABAC hybrid)

#### encryption
- **Path**: `src/security/encryption/`
- **Responsibility**: Data encryption at rest and key management
- **Key Files**:
  - `cipher.ts` — Symmetric encryption/decryption (AES-256)
  - `key-manager.ts` — Master key and data key lifecycle
  - `key-store.ts` — Secure key storage interface (HSM, KMS, or secure config)
  - `field-encryptors.ts` — Encrypt specific fields before persistence
- **Dependencies**: config-loader, audit-logger
- **Algorithm**: AES-256-GCM
- **Implements**: NFR-SEC-001 (encryption at rest)

#### pki
- **Path**: `src/security/pki/`
- **Responsibility**: Public Key Infrastructure for signing and verification
- **Key Files**:
  - `certificate-manager.ts` — Load and manage X.509 certificates
  - `signer.ts` — Sign data (audit logs, API responses)
  - `verifier.ts` — Verify signatures from external sources
  - `ca/` — Certificate chain validation
- **Dependencies**: encryption, config-loader
- **Use Cases**: Sign audit logs for immutability; verify manufacturer-signed data

### Tests
- **Path**: `tests/security/`
- **Coverage**: Unit tests for auth flows, RBAC policy evaluation, encryption/decryption
- **Key Test Files**:
  - `unit/auth.test.ts`
  - `unit/rbac-engine.test.ts`
  - `unit/encryption.test.ts`
  - `integration/access-control.test.ts`
  - `e2e/tls-handshake.test.ts`

### Security Considerations
- Store master keys in HSM or Key Management Service (AWS KMS, Azure Key Vault)
- Rotate data encryption keys annually; rotate master keys on schedule or after compromise
- All key operations logged and audited
- Use TLS 1.3 for all network communication

---

## QR Domain

**Purpose**: Generate QR codes for battery passports and serve public-facing, unauthenticated passport views.

### Components

#### qr-generator
- **Path**: `src/qr/generator/`
- **Responsibility**: Generate QR codes linking to public passport pages
- **Key Files**:
  - `index.ts` — QR generation orchestrator
  - `encoders/` — QR format encoders (PNG, SVG, data URL)
  - `url-builder.ts` — Construct public passport URL with passport ID
  - `schema.ts` — Embedded URL schema version/structure
- **Dependencies**: battery-passport-types, config-loader
- **Output Formats**: PNG (print), SVG (web), Base64 (data URL)
- **QR Size**: Configurable; default 200x200 px
- **URL Structure**: `https://battery-passport.eu/{passport-id}?v=1&source=manufacturer`

#### public-passport
- **Path**: `src/qr/public-passport/`
- **Responsibility**: Render battery passport information for public, unauthenticated users
- **Key Files**:
  - `routes.ts` — GET /{passport-id} handler
  - `handlers/render.ts` — Passport data retrieval (from Gold tier, public view)
  - `templates/` — HTML/React templates for passport display
  - `serializers/` — Filter data to public tier only (no legitimate/confidential fields)
  - `caching/` — Redis cache for frequently accessed passports
- **Dependencies**: passport-service, rbac-engine, config-loader
- **Access Control**: Anonymous access; returns only public data fields
- **Caching**: 1-hour TTL for static passport data
- **Implements**: NFR-QR-001 (page load time < 2 seconds on 4G mobile)

### Tests
- **Path**: `tests/qr/`
- **Coverage**: QR encoding, public passport page rendering, caching behavior
- **Key Test Files**:
  - `unit/qr-generator.test.ts`
  - `integration/public-passport.test.ts`
  - `e2e/public-passport-load.perf.ts` — NFR-QR-001 verification
  - `unit/caching.test.ts`

### Data Flow
```
Passport ID → qr-generator → QR Image (PNG/SVG)
                 ↓
Smartphone scan → public-passport handler → Gold Storage (public view) → HTML render
```

---

## AUDIT Domain

**Purpose**: Track all system actions, maintain immutable audit logs, and trace data lineage.

### Components

#### event-log
- **Path**: `src/audit/event-log/`
- **Responsibility**: Append-only audit event storage and retrieval
- **Key Files**:
  - `index.ts` — Event logger interface
  - `writers/` — Append-only writers (database, cloud storage, blockchain)
  - `readers/` — Query audit log by time range, actor, resource
  - `integrity.ts` — Cryptographic hash chain for tamper detection
  - `retention.ts` — Retention policy enforcement (archive after N days)
- **Dependencies**: encryption, pki, config-loader
- **Event Types**: Access, Ingest, Modify, Delete, Authenticate, Authorize, Archive
- **Implements**: NFR-AUDIT-001 (immutability, tamper detection)

#### data-lineage
- **Path**: `src/audit/data-lineage/`
- **Responsibility**: Track data provenance from source to current state
- **Key Files**:
  - `index.ts` — Lineage tracker interface
  - `graph.ts` — DAG representation of data transformations
  - `tracing.ts` — Tag data with source passport ID and transformation steps
  - `queries/` — Query lineage (e.g., "show me all sources that fed this passport")
- **Dependencies**: event-log, battery-passport-types
- **Lineage Metadata**: Source, timestamp, validator version, transformer version, Silver → Gold path
- **Use Case**: Regulatory audits ("prove this passport's data integrity")

#### request-trace
- **Path**: `src/audit/request-trace/`
- **Responsibility**: End-to-end request tracing for distributed debugging
- **Key Files**:
  - `index.ts` — Trace context propagation
  - `middleware/` — Express middleware to inject trace IDs
  - `exporters/` — Send traces to tracing backend (Jaeger, Datadog)
  - `spans.ts` — Define named spans for key operations
- **Dependencies**: config-loader, audit-logger
- **Protocols**: OpenTelemetry (W3C Trace Context)
- **Integration**: Works with APM tools for latency analysis

### Tests
- **Path**: `tests/audit/`
- **Coverage**: Event logging, lineage tracking, integrity verification
- **Key Test Files**:
  - `unit/event-log.test.ts`
  - `unit/data-lineage.test.ts`
  - `integration/audit-flow.test.ts`
  - `security/tamper-detection.test.ts` — NFR-AUDIT-001 verification

### Audit Event Schema
```json
{
  "id": "evt-uuid",
  "timestamp": "2026-03-28T10:15:00Z",
  "actor": "user-id or service-id",
  "action": "ingest | read | modify | delete | authenticate | authorize",
  "resource": "passport-id",
  "resourceType": "BatteryPassport",
  "result": "success | failure",
  "details": { ... },
  "signature": "HMAC-SHA256 hash"
}
```

---

## API Domain

**Purpose**: Expose battery passport data to authorized downstream systems (supply chain partners, regulators, researchers).

### Components

#### downstream-api
- **Path**: `src/api/downstream/`
- **Responsibility**: REST/GraphQL API for authorized external consumers
- **Key Files**:
  - `routes/` — REST endpoint definitions
  - `graphql/` — GraphQL schema and resolvers
  - `handlers/` — Query/mutation handlers with RBAC checks
  - `serializers/` — Response formatting per consumer type
  - `versioning/` — API versioning strategy
- **Dependencies**: passport-service, rbac-engine, audit-logger, config-loader
- **Endpoints**: GET /passports/{id}, GET /passports (filtered), POST /searches
- **Authentication**: OAuth2 or API key per downstream client

#### data-export
- **Path**: `src/api/export/`
- **Responsibility**: Export passport data in various formats for reporting and analysis
- **Key Files**:
  - `formats/` — CSV, JSON, Parquet exporters
  - `filters.ts` — Apply RBAC filters before export
  - `jobs/` — Background job orchestration for large exports
  - `handlers/` — Schedule and retrieve export jobs
- **Dependencies**: passport-service, rbac-engine, audit-logger
- **Formats**: CSV (supply chain), JSON (detailed), Parquet (data science)
- **Usage**: Used by supply chain partners for BI tools, researchers for studies

#### authority-sub
- **Path**: `src/api/authority/`
- **Responsibility**: Integration with regulatory authorities and submission APIs
- **Key Files**:
  - `index.ts` — Authority submission orchestrator
  - `formatters/` — Format data per authority requirements
  - `submission.ts` — Submit passport data to authority registry
  - `polling.ts` — Poll for regulatory updates/requirements
- **Dependencies**: passport-service, config-loader, audit-logger
- **Authorities Supported**: ETRMA (tyre), battery regulatory bodies, future extensible

### Tests
- **Path**: `tests/api/`
- **Coverage**: API endpoint behavior, RBAC enforcement, export accuracy
- **Key Test Files**:
  - `integration/downstream-api.test.ts`
  - `unit/data-export.test.ts`
  - `integration/authority-submission.test.ts`

### Data Flow
```
Gold Storage → downstream-api → (with RBAC) → JSON/GraphQL response → Client
                    ↓
                data-export → CSV/Parquet → S3/Data Lake
                    ↓
              authority-sub → Regulatory submission API
```

---

## UI Domain

**Purpose**: Web-based user interfaces for dashboard viewing, administration, and reporting.

### Components

#### dashboard
- **Path**: `src/ui/dashboard/`
- **Responsibility**: Main user-facing dashboard for passport browsing and analytics
- **Key Files**:
  - `components/` — React components (PassportSearch, PassportDetail, Timeline)
  - `pages/` — Page layouts
  - `hooks/` — Custom React hooks for data fetching, auth
  - `state/` — Redux or Zustand store
  - `api-client/` — Wrapper around downstream-api
- **Dependencies**: battery-passport-types, auth, rbac-engine, downstream-api
- **Frameworks**: React 18+, TypeScript, Vite or Next.js
- **Access**: Authenticated users only (distributor, manufacturer, researcher roles)

#### passport-views
- **Path**: `src/ui/passport-views/`
- **Responsibility**: Detailed passport views with tabbed interface (Specifications, Lifecycle, Compliance, Lineage)
- **Key Files**:
  - `components/SpecificationTab.tsx`
  - `components/LifecycleTab.tsx`
  - `components/ComplianceTab.tsx`
  - `components/LineageTab.tsx`
  - `hooks/usePassport.ts` — Data fetching with polling
- **Dependencies**: passport-service, data-lineage, compliance
- **Real-time Updates**: WebSocket polling for live state changes

#### admin
- **Path**: `src/ui/admin/`
- **Responsibility**: Administrative interface for operations and compliance teams
- **Key Files**:
  - `components/PolicyManager.tsx` — Create/edit RBAC policies
  - `components/UserManager.tsx` — User/role provisioning
  - `components/AuditBrowser.tsx` — Browse audit logs
  - `components/BackupManager.tsx` — Manage backups/restores
  - `pages/SystemHealth.tsx` — Infrastructure monitoring dashboard
- **Dependencies**: rbac-engine, event-log, auth, backup
- **Access**: Admin role only
- **Capabilities**: Policy editing, user provisioning, audit log queries, system monitoring

#### reports
- **Path**: `src/ui/reports/`
- **Responsibility**: Generate and display regulatory and business reports
- **Key Files**:
  - `components/ComplianceReport.tsx` — EU 2023/1542 compliance report
  - `components/SupplyChainReport.tsx` — Supplier and distributor metrics
  - `components/EnvironmentalReport.tsx` — Recycling and sustainability metrics
  - `generators/` — Report data aggregation and formatting
  - `exporters/` — PDF/Excel export
- **Dependencies**: data-export, compliance, passport-service
- **Scheduling**: Reports can be scheduled for periodic generation

### Tests
- **Path**: `tests/ui/`
- **Coverage**: Component rendering, state management, API integration, accessibility
- **Key Test Files**:
  - `unit/components/*.test.tsx`
  - `integration/dashboard.test.tsx`
  - `e2e/passport-search.e2e.ts` — Cypress/Playwright
  - `accessibility/a11y.test.ts` — WCAG compliance

### Build & Deployment
- **Build Tool**: Vite or Next.js
- **Bundling**: Code splitting by domain
- **Hosting**: CDN for static assets, BFF (Backend for Frontend) for API calls

---

## INFRA Domain

**Purpose**: Infrastructure concerns: backup, archival, monitoring, and disaster recovery.

### Components

#### backup
- **Path**: `src/infra/backup/`
- **Responsibility**: Backup and restore operations for disaster recovery
- **Key Files**:
  - `index.ts` — Backup orchestrator
  - `snapshots.ts` — Create consistent database snapshots
  - `uploaders/` — Upload to cloud storage (S3, Azure Blob, GCS)
  - `restore.ts` — Full and point-in-time restore logic
  - `verification.ts` — Post-restore integrity checks
  - `scheduler.ts` — Automated backup scheduling
- **Dependencies**: encryption, config-loader, audit-logger
- **RPO/RTO**: RPO < 1 hour (hourly backups); RTO < 1 hour restore time
- **Implements**: NFR-INFRA-001 (restore time < 1 hour for 1M passports)

#### archive
- **Path**: `src/infra/archive/`
- **Responsibility**: Long-term data archival and cold storage management
- **Key Files**:
  - `index.ts` — Archive orchestrator
  - `policies.ts` — Retention and archival policies
  - `movers/` — Move data from hot (frequent access) to cold (infrequent) storage
  - `retrievers.ts` — Retrieve archived data on demand
  - `cost-tracking.ts` — Monitor archival costs
- **Dependencies**: config-loader, audit-logger
- **Policies**: Data older than 3 years moves to cold storage; regulatory holds prevent deletion
- **Storage Tiers**: Hot (databases), Warm (data lake), Cold (S3 Glacier, Azure Archive)

#### monitoring
- **Path**: `src/infra/monitoring/`
- **Responsibility**: Observability, metrics, alerting, and health checks
- **Key Files**:
  - `metrics.ts` — Define and emit metrics (latency, throughput, errors)
  - `healthchecks.ts` — Readiness and liveness probes
  - `alerts/` — Alert rule definitions (Prometheus, CloudWatch)
  - `dashboards/` — Grafana or CloudWatch dashboard specs
  - `slo.ts` — Service Level Objectives and error budgets
- **Dependencies**: config-loader, audit-logger
- **Tools**: Prometheus (metrics), Grafana (dashboards), Alertmanager (alerting)
- **Key SLOs**: Ingest latency (NFR-INGEST-001), Auth latency < 100ms, API availability 99.9%

### Tests
- **Path**: `tests/infra/`
- **Coverage**: Backup/restore flows, archival policies, health checks
- **Key Test Files**:
  - `integration/backup-restore.test.ts` — NFR-INFRA-001 verification
  - `unit/archival-policy.test.ts`
  - `integration/monitoring-alerts.test.ts`

### Observability Stack
```
Application → Prometheus (metrics) → Grafana (dashboards)
           → ELK/Splunk (logs)
           → Jaeger (traces)
           → AlertManager (alerts)
```

---

## Shared Dependencies

All components depend on the following shared modules:

### battery-passport-types
- **Path**: `src/shared/types/battery-passport.ts`
- **Purpose**: Canonical TypeScript definitions for battery passport data model
- **Contents**:
  - `BatteryPassport` interface (root model)
  - `Battery`, `Chemistry`, `Specifications`, `Lifecycle` sub-models
  - `DataClassification` enum (public, legitimate, confidential)
  - `LifecycleState` enum (Draft, Published, InUse, Retired, Archived)
- **Responsibility**: Single source of truth; all other modules import from here
- **Versioning**: Semantic versioning (major.minor.patch) for backward compatibility

### audit-logger
- **Path**: `src/shared/logging/audit.ts`
- **Purpose**: Centralized audit logging interface used across all domains
- **Exports**:
  - `AuditLogger` class
  - `logAccess(actor, resource, action, result)`
  - `logIngest(source, count, status)`
  - `logModify(actor, resource, changes)`
  - `logDelete(actor, resource)`
  - `logAuth(actor, mechanism, result)`
- **Dependency**: event-log (where events are persisted)
- **Usage**: Injected as dependency into services

### config-loader
- **Path**: `src/shared/config/loader.ts`
- **Purpose**: Environment-aware configuration loading
- **Exports**:
  - `loadConfig(env)` — Load config from environment vars, config files, or secrets manager
  - `getConfig(key)` — Retrieve config value with type safety
  - `watchConfig()` — Listen for config changes (for hot reload)
- **Config Locations**: `.env`, `config/production.yaml`, AWS Secrets Manager, etc.
- **Type Safety**: Returns typed config objects, not strings

### regulation-schema
- **Path**: `src/shared/schema/eu-2023-1542.ts`
- **Purpose**: EU 2023/1542 regulation schema and validation rules
- **Contents**:
  - Data classification rules (public/legitimate/confidential fields)
  - Mandatory field definitions per passport type
  - Retention period rules
  - Authority reporting requirements
- **Used By**: validator, compliance, rbac-engine
- **Maintenance**: Update when regulation changes or implementing acts are published

---

## Using This Code Map

### For AI Agents

When working on a task within a specific domain:

1. **Identify the Domain**: Is the work related to INGEST, PASSPORT, SEC, QR, AUDIT, API, UI, or INFRA?
2. **Locate the Component**: Find the relevant component(s) in the domain section above.
3. **Understand Dependencies**: Check the "Dependencies" list to see what shared modules and cross-domain modules are needed.
4. **Review Test Patterns**: Look at existing tests in `tests/{domain}/` to understand how to test your changes.
5. **Check Related NFRs/ADRs**: Refer to the "Implements" or "Related ADRs" links to ensure architectural alignment.

### Example: Adding a new ingest source format

1. Domain: INGEST
2. Component: transformer
3. Steps:
   - Add new mapper in `src/ingest/transformer/mappers/`
   - Register mapper in `src/ingest/transformer/index.ts`
   - Add validation rules in `src/ingest/validator/schemas/`
   - Add unit tests in `tests/ingest/unit/transformer.test.ts`
   - Update config-loader to include source type configuration

### Example: Implementing a new regulatory report

1. Domain: UI
2. Component: reports
3. Steps:
   - Create new component in `src/ui/reports/components/`
   - Add data generator in `src/ui/reports/generators/`
   - Query data from compliance service and passport-service
   - Add tests in `tests/ui/`
   - Integrate with dashboard navigation

### Cross-Domain Communication

Domains should communicate through well-defined interfaces:
- INGEST → PASSPORT: Write to Silver tier via passport-service
- PASSPORT → AUDIT: Log changes via audit-logger
- SEC → all domains: Enforce via RBAC middleware
- API → PASSPORT: Query via downstream-api
- UI → API: Use downstream-api client (never direct DB access)

---

## File Tree Summary

```
src/
├── ingest/
│   ├── api/
│   ├── validator/
│   ├── transformer/
│   └── data-generator/
├── passport/
│   ├── service/
│   ├── compliance/
│   ├── lifecycle/
│   └── model/
├── security/
│   ├── auth/
│   ├── rbac/
│   ├── encryption/
│   └── pki/
├── qr/
│   ├── generator/
│   └── public-passport/
├── audit/
│   ├── event-log/
│   ├── data-lineage/
│   └── request-trace/
├── api/
│   ├── downstream/
│   ├── data-export/
│   └── authority-sub/
├── ui/
│   ├── dashboard/
│   ├── passport-views/
│   ├── admin/
│   └── reports/
├── infra/
│   ├── backup/
│   ├── archive/
│   └── monitoring/
└── shared/
    ├── types/
    ├── logging/
    ├── config/
    └── schema/

tests/
├── ingest/
├── passport/
├── security/
├── qr/
├── audit/
├── api/
├── ui/
└── infra/
```

---

## Maintenance

This code map should be updated whenever:
- A new domain or component is added
- Component responsibilities change significantly
- New shared dependencies are introduced
- File paths are reorganized

**Owner**: Architecture team
**Last Updated**: 2026-03-28
**Review Frequency**: Quarterly
