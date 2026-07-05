---
id: BRQ-SEC-001
title: Enforce differentiated access to battery passport data
status: approved
source_type: regulation
priority: high
owner: "@compliance"
domain: SEC
source_ref: "SRC-COMPLY-001#annex-XIII"
source_docs:
  - "[[SRC-COMPLY-001]]"
regulatory_refs:
  - framework: EU-2023-1542
    article: "77"
    paragraph: "Annex XIII"
stakeholders:
  - "@compliance"
updated: 2026-03-28
---

# Business Requirement

Access to battery passport data must be differentiated by user category (general
public, persons with a legitimate interest, and market-surveillance authorities),
disclosing to each party only the data they are entitled to see.

# Motivation

Annex XIII of EU 2023/1542 grants different data-visibility rights to different
parties. Confidential manufacturer data and personal data must not be exposed to the
general public. This BRQ drives the security control [[CTRL-SEC-001]] and the
constraint [[CON-SEC-001]].

# Notes

The precise access matrix for legitimate-interest holders is deferred to implementing
acts, so the mechanism must be runtime-configurable (see [[CON-SEC-001]]).
