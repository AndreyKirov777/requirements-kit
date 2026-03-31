---
id: ADR-INGEST-001
title: Use three-tier data architecture for battery passport data
status: proposed
owner: '@techlead'
date: '2026-03-28'
related_requirements:
- '[[FR-INGEST-001]]'
- '[[FR-INGEST-003]]'
- '[[FR-PASSPORT-001]]'
tags:
- adr
- ingest
- architecture
updated: '2026-03-28'
domain: ''
superseded_by: ''
---

# Context
Battery passport data arrives from many sources in different formats and quality levels. Manufacturers submit via API, distributors provide EDI feeds, regulatory bodies contribute compliance data, and end users supply operational metrics. The system must accommodate this heterogeneity while maintaining data quality, lineage, and auditability.

Regulatory compliance (EU 2023/1542) requires traceable data provenance and the ability to distinguish between raw, unvalidated data and authoritative passport information. Business needs demand both historical archival (raw data preservation) and real-time access to current, validated passport state.

# Decision
Implement a three-tier data architecture:

1. **Bronze Tier (Raw)**: Immutable storage of all ingested data as-received. Includes source metadata (timestamp, origin, format). No transformation or validation. Serves as the authoritative source for audit trails and data lineage.

2. **Silver Tier (Validated/Normalized)**: Cleansed, validated, and normalized data. Applies source schema validation, deduplication, and standardization to a unified battery passport model. Includes validation status and any quality flags. Supports business logic and intermediate analytics.

3. **Gold Tier (Business-Ready)**: Aggregated, enriched, and curated passport data optimized for downstream consumption. Includes regulatory compliance assessments, lifecycle state, derived attributes (e.g., environmental impact scores), and access-controlled views based on data classification.

Data flows unidirectionally: Bronze → Silver → Gold. Each tier is independently queryable and retains full lineage to its sources.

# Alternatives Considered

**Option A: Two-tier (Raw + Processed)**
- Simpler implementation with fewer storage layers
- Loses the explicit validation/normalization step
- Risk of mixing validation concerns with business logic
- Harder to audit intermediate data quality transformations

**Option B: Single Normalized Store**
- Minimal storage overhead
- Simplest architecture
- No preservation of raw, unvalidated data (audit and regulatory compliance gap)
- Cannot support forensic reconstruction of data quality issues
- Brittle to schema changes

**Option C: Event Sourcing / CQRS**
- Full event audit trail built into architecture
- Adds significant operational complexity
- Overkill if regulatory requirements are satisfied by Bronze + audit logs
- Higher latency for read-heavy workloads in Gold

# Consequences

## Benefits
- **Full Data Lineage**: Every passport can be traced back to its raw source(s), with validation and transformation steps recorded
- **Immutable Raw Data**: Bronze serves as legal proof of what was ingested, protecting against later disputes
- **Clear Data Quality Boundaries**: Each tier has explicit validation contracts; SLAs can target specific tiers
- **Regulatory Compliance**: EU 2023/1542 audit requirements met through transparent data flow
- **Operational Debugging**: When downstream systems report inconsistencies, traces can pinpoint which tier the issue originated from
- **Re-processing Capability**: If validation logic is corrected, Silver and Gold can be rebuilt from Bronze without losing source data

## Costs
- **Storage Footprint**: Storing data three times increases costs; Bronze may be especially large for high-volume ingest
- **Pipeline Complexity**: Three distinct ETL stages, each requiring monitoring, error handling, and SLA management
- **Operational Overhead**: Three tiers to maintain, upgrade, and troubleshoot
- **Data Freshness Trade-off**: Multi-hop latency (Bronze → Silver → Gold) may delay availability of validated data to end users

## Trade-offs
Increased storage and pipeline complexity are justified by stronger auditability and regulatory alignment. The three-tier model trades operational simplicity for governance and forensic capability—appropriate for a heavily regulated domain like battery passports.

# Links
- Requirements: [[FR-INGEST-001]], [[FR-INGEST-003]], [[FR-PASSPORT-001]]
- NFR: [[NFR-INGEST-001]] (latency budget applies to Bronze persistence)
- Related ADRs: [[ADR-SEC-001]] (applies encryption to all tiers)
- Tickets: INGEST-45, INGEST-67
