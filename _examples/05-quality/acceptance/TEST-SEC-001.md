---
id: TEST-SEC-001
title: Verify encryption at rest and differentiated data access
status: draft
owner: "@qa"
verifies:
  - "[[NFR-SEC-001]]"
verifies_control:
  - "[[CTRL-SEC-001]]"
type: security
priority: critical
covers_criteria: []
tags: [test, security]
updated: 2026-03-28
---

# Objective

Provide evidence that battery passport data is encrypted at rest ([[NFR-SEC-001]])
and that confidential fields are disclosed only to authorized parties
([[CTRL-SEC-001]]).

# Preconditions

- Storage provisioned with encryption configuration applied.
- Test identities exist for each user category (public, legitimate-interest, authority).

# Test Ideas

## Encryption at rest (NFR-SEC-001)
- Inspect the storage configuration → assert AES-256 is in effect for all data volumes.
- Scan infrastructure for any unencrypted volume → expect none.
- Verify key-access events are logged.

## Differentiated access (CTRL-SEC-001)
- As a public user, request a passport → assert confidential fields are absent.
- As a legitimate-interest holder, request the same passport → assert permitted
  fields are present and others are absent.
- As an authority, request the passport → assert full permitted view.
- For every request, assert an audit event is recorded with the access decision.

# Expected Results

- 100% of data at rest encrypted with AES-256.
- Each user category receives only its permitted fields; every access decision is
  audited.
