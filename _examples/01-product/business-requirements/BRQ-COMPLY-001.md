---
id: BRQ-COMPLY-001
title: Provide a Digital Battery Passport for every in-scope battery
status: approved
source_type: regulation
priority: critical
owner: "@pm"
domain: COMPLY
source_ref: "SRC-COMPLY-001#article-77"
source_docs:
  - "[[SRC-COMPLY-001]]"
regulatory_refs:
  - framework: EU-2023-1542
    article: "77"
stakeholders:
  - "@compliance"
  - "@pm"
compliance_deadline: 2027-02-18
updated: 2026-03-28
---

# Business Requirement

Every battery placed on the EU market that is in scope of EU 2023/1542 Article 77
must have a Digital Battery Passport, accessible via a QR code, containing the
mandatory data fields with access differentiated by user category.

# Motivation

The regulation makes the passport a market-access condition: without it, in-scope
batteries cannot legally be placed on the EU market. This BRQ is the top of the
obligation chain — business rules ([[BR-COMPLY-001]]) and controls ([[CTRL-SEC-001]])
decompose it into verifiable requirements.

# Scope

- LMT batteries, industrial batteries > 2 kWh, and EV batteries.
- Both the data model and the access mechanism (QR → passport view).

# Notes

Detailed legitimate-interest access rules are pending implementing acts; see
[[CON-SEC-001]].
