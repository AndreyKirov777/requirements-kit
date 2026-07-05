---
id: NFR-SEC-001
title: Encrypt battery passport data at rest
status: proposed
priority: critical
owner: "@techlead"
domain: SEC
quality_attribute: security
parent_epic: "[[EPIC-INGEST-001]]"
derives_from:
  - "[[CTRL-SEC-001]]"
depends_on: []
measurement_method: Security audit of storage configuration plus infrastructure scanning for unencrypted volumes
target_value: 100% of data at rest encrypted with AES-256; master keys rotated at least annually
updated: 2026-03-28
---

# Summary

Battery passport data at rest must be encrypted so that a physical storage compromise does not disclose proprietary manufacturer data or personal data protected under EU 2023/1542.

# Context

Passport data includes proprietary manufacturer information and personal data about users and authorities. Confidential data must be protected independently of the application layer.

# Requirement Statement

All battery passport data at rest shall be encrypted using AES-256, and confidential data shall reside in a storage partition with independent access controls.

# Measurement

Encryption algorithm and key size are verified via security audit; key rotation and access logging are checked against the key-management policy; partition separation is verified through infrastructure-as-code review.

# Target

100% of data at rest encrypted with AES-256; master keys rotated at least annually; all key access logged and auditable.

# Verification

Annual penetration testing targeting data at rest, key-management audit, and infrastructure scanning to detect unencrypted storage.

# Open Questions

- Should the platform support customer-managed encryption keys (CMEK) for future flexibility?
