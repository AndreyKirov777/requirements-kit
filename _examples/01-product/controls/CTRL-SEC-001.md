---
id: CTRL-SEC-001
title: Restrict confidential passport data to authorized parties
status: allocated
priority: critical
owner: "@compliance"
domain: SEC
derives_from:
  - "[[BRQ-SEC-001]]"
verification_method: test
compliance_deadline: 2027-02-18
updated: 2026-03-28
---

# Control Statement

The system shall enforce that confidential battery passport data (as classified under
Annex XIII of EU 2023/1542) is disclosed only to authenticated parties whose user
category grants access, and shall record an audit event for every access decision.

# Derivation

Enforces business requirement [[BRQ-SEC-001]]. Allocated to the security
requirement [[NFR-SEC-001]] (encryption at rest) and the access-control constraint
[[CON-SEC-001]].

# Evidence Expected

- Access-control test suite demonstrating that each user category sees only its
  permitted fields (see [[TEST-SEC-001]]).
- Audit log entries for access decisions, retained per policy.

# Verification Method

`test` — automated tests exercise the access matrix and assert both allowed and
denied paths.
