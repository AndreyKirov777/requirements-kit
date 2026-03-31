---
id: NFR-SEC-001
title: Data encryption at rest
type: non-functional-requirement
status: proposed
priority: critical
owner: '@techlead'
domain: SEC
quality_attribute: security
component:
- encryption
source_docs: []
related_adrs: []
depends_on: []
implemented_by: []
verified_by: []
release_target: 2026-Q3
risk: high
tags:
- nfr
- security
- encryption
updated: '2026-03-28'
stakeholders: []
blocks: []
parent_epic: ''
delivered_by: []
derives_from: []
implements_control: []
---

# Summary
Encryption at rest protects sensitive battery passport data from unauthorized disclosure in the event of physical storage compromise, theft, or unauthorized access. This is a foundational security control mandated by EU 2023/1542 and industry best practices.

# Context
Battery passport data includes proprietary information from manufacturers (composition, sourcing, performance characteristics) and personal information about users and authorities. Confidential data as defined by regulation must be stored separately with independent access controls to prevent cross-tier exposure.

# Requirement Statement
All battery passport data at rest shall be encrypted using AES-256. Confidential data (per regulation) shall be stored in a separate secure storage partition with independent access controls.

# Measurement
- Encryption algorithm and key size verification via security audit
- Key management compliance check (key rotation, storage, access logging)
- Separation of confidential and non-confidential data partitions verified through infrastructure code review

# Target
- 100% of data at rest encrypted with AES-256
- Key rotation policy: rotate master keys annually; rotate data keys on schedule or after compromise
- All encryption key access logged and auditable

# Conditions
Applies to:
- All persistent storage (databases, data lakes, backups, archives)
- Temporary caches (if any retain sensitive data for >1 hour)
- Snapshots and replicas of encrypted data

Does NOT require in-flight encryption (covered by separate TLS/mTLS requirements).

# Verification
- Annual penetration testing targeting data at rest
- Key management audit by internal security team or third party
- Compliance certification (SOC 2, ISO 27001)
- Infrastructure scanning to detect unencrypted storage

# Risks
If this requirement is not met:
- Regulatory non-compliance with EU 2023/1542
- Potential data breach exposure if storage is compromised
- Loss of user and manufacturer trust
- Legal and financial penalties

# Open Questions
- Are there performance implications of AES-256 vs. AES-128 or hardware-accelerated encryption?
- How often should data encryption keys be rotated vs. master keys?
- Should we support customer-managed encryption keys (CMEK) for future flexibility?
