---
id: BR-COMPLY-001
title: A battery passport must contain all mandatory data fields
status: approved
priority: high
owner: "@compliance"
domain: COMPLY
classification: regulatory
derives_from:
  - "[[BRQ-COMPLY-001]]"
regulatory_ref:
  framework: EU-2023-1542
  article: "77"
  paragraph: "Annex XIII"
updated: 2026-03-28
---

# Rule

A Digital Battery Passport shall contain every mandatory data field defined in
Annex XIII of EU 2023/1542 for the battery's category. A passport missing any
mandatory field is non-compliant and must not be published.

# Rationale

This decomposes the regulatory obligation [[BRQ-COMPLY-001]] into an atomic,
verifiable domain fact. It drives the functional requirement that ingests and
persists the source data ([[FR-INGEST-001]]) and any later validation requirement.

# Examples

- An LMT battery passport without the `manufacturingDate` field → non-compliant.
- An EV battery passport without state-of-health data → non-compliant.

# Notes

When the implementing acts adjust the mandatory field list, updating this rule
cascades to every requirement that derives from it.
