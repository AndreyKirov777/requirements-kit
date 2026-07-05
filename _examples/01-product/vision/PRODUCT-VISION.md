---
id: VISION-DBP-001
title: Digital Battery Passport Accelerator Vision
status: approved
owner: "@pm"
domain: all
tags: [vision, dbp]
updated: 2026-03-28
---

# Vision

To become the leading DBP solution that lets economic operators achieve seamless EU DBP regulatory compliance by providing a rapid implementation and deployment approach based on predeveloped core digital battery passport functionality, enabling them to build and own a fully compliant solution.

# Product Description

The Digital Battery Passport Accelerator (DBP Accelerator) is a core foundation designed to build a tailored DBP management solution for a specific economic operator to comply with EU Battery Regulation 2023/1542.

With the help of a system developed on the DBP Accelerator, economic operators can track their regulatory compliance by checking the completeness status of each battery passport and clearly see which required data is still missing. The platform ensures that battery data is accurate, securely stored, and ready to be shared as required.

# Product Structure

- **Data Ingestion** — collects battery passport data from various sources (static files, APIs) into the Bronze layer.
- **Data Processing & Validation** — transforms and validates raw data through Bronze → Silver → Gold tiers, ensuring regulatory completeness.
- **Passport Management** — core module for creating, viewing, and tracking battery passport lifecycle and completeness status.
- **Access Control** — role-based and legislation-aligned permissions controlling view/edit/export per user category.
- **Audit & Lineage** — append-only audit logs and field-level data lineage for compliance traceability.
- **Integration Layer** — flexible connectors for internal systems and future EU DPP registry integration.

# Goals

1. Develop a core foundation to build a ready-to-use DBP solution for economic operators.
2. Provide economic operators with a reliable system to collect, validate, and maintain all battery passport data required by law.
3. Support updates throughout the battery lifecycle.
4. Allow economic operators to track battery passport completeness.
5. Enable secure access to battery passport data based on legislation-aligned permissions, with explicit controls over view/edit/export.
6. Allow economic operators to demonstrate compliance through traceable audit logs and field-level lineage for each battery passport.
7. Develop a flexible mechanism to support various data sources (static and dynamic).
8. Develop a flexible integration approach to support integration with both internal systems and the central EU DPP registry.

# Scope of Work

- Data ingestion from static sources (CSV, Excel, JSON) and internal APIs.
- Three-tier data processing pipeline (Bronze → Silver → Gold).
- Battery passport CRUD operations with completeness tracking.
- Role-based access control for five user categories (Compliance Officer, Admin, Public, Legitimate, Authority).
- Field-level audit logging and data lineage.
- QR code generation for public battery passport access.
- API-first architecture with integration adapters for internal systems.

# Out of Scope

- Integration with the EC registry and EC web portal (out of MVP scope).
- Integration with external systems of upstream partners for battery data collection.
- Disaster recovery.
- Manual data entry UI.

# Target Users

- **Compliance Officer** — primary user; monitors battery passport completeness and regulatory compliance.
- **Admin** — configures visibility, manages users, roles, permissions, backups, and system settings.
- **Public User** — accesses battery info via QR code; no authentication needed.
- **Legitimate User** — person with legitimate interest (second-life operators, repairers, recyclers); access rules pending implementing acts.
- **Authority** — notified bodies, market surveillance authorities, European Commission; full data access for enforcement.

# Key Differentiators

- Accelerator approach: pre-built core, bespoke per operator.
- Regulation-first design: data model and access controls derived directly from EU 2023/1542.
- Three-tier data architecture (Bronze → Silver → Gold) for auditability.
- Field-level data lineage and append-only audit logs.

# Regulatory Context

EU Regulation 2023/1542 mandates digital battery passports from February 2027 for EV batteries, LMT batteries, and industrial batteries >2 kWh. Access rights for legitimate-interest users will be specified in implementing acts by 18 August 2026.

# Related Artifacts
