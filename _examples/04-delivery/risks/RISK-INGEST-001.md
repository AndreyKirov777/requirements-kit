---
id: RISK-INGEST-001
title: Bronze-layer write throughput may not sustain bulk migration
type: risk
status: open
severity: high
likelihood: medium
owner: "@techlead"
domain: INGEST
affects:
  - "[[FR-INGEST-001]]"
  - "[[EPIC-INGEST-001]]"
mitigation_status: planned
tags: [risk, ingest, performance]
updated: 2026-03-28
---

# Risk

During initial onboarding, economic operators will migrate thousands of historical
batteries. The single-record ingestion path ([[FR-INGEST-001]]) may not sustain the
write throughput required, causing timeouts and partial migrations.

# Impact

- Slow, error-prone onboarding damages early-adopter trust.
- Repeated retries increase load and can amplify the problem.

# Likelihood

Medium — the volume is known to be high, but exact throughput ceilings are untested.

# Mitigation

- Load-test the Bronze write path before onboarding.
- Add batch ingestion (tracked by [[CR-INGEST-001]]) to reduce per-record overhead.
- Provide back-pressure and idempotent retries.

# Notes

Reassess severity after load-testing results are available.
