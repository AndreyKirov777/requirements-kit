---
id: CON-SEC-001
title: Legitimate-interest access rules pending implementing acts
type: constraint
status: approved
priority: high
owner: '@pm'
domain: SEC
source_docs:
- '[[VISION-DBP-001]]'
related_adrs: []
impacts:
- '[[FR-SEC-003]]'
tags:
- constraint
- regulation
updated: '2026-03-28'
risk: high
component: []
stakeholders: []
depends_on: []
blocks: []
implemented_by: []
verified_by: []
release_target: ''
quality_attribute: ''
parent_epic: ''
delivered_by: []
derives_from: []
implements_control: []
---

# Statement
Access rights for persons with legitimate interest will be specified in implementing acts due 18 August 2026. Until then, access rights can only be generally defined and must remain configurable.

# Context
EU Regulation 2023/1542 requires different data visibility for different user groups (public, legitimate-interest holders, and regulatory authorities). The specific access rules for legitimate-interest users are not yet finalized in the implementing acts, which are scheduled for August 2026.

# Impact
RBAC/ABAC system must support runtime-configurable access rules per user group without code changes. The security architecture must allow administrators to adjust access policies based on the final implementing acts without redeploying the system.

# Allowed Options
- Runtime configuration of access rules in a policy engine (e.g., attribute-based access control with editable policies)
- Feature flags to enable/disable access tiers pending finalization
- Role-based access control with configurable role definitions

# Forbidden Options
- Hardcoded access rules in application code
- Static role definitions that require code recompilation
- Inflexible permission matrices

# Notes
- This constraint directly shapes the architecture of EPIC-SEC-001 (Security and regulation-aligned access control)
- Must coordinate with legal team as implementing acts approach
- Dashboard should display which access rules are provisional vs. finalized
