---
id: ASSUM-DBP-001
title: Economic operator provides all battery data
type: assumption
status: unvalidated
owner: "@pm"
domain: INGEST
risk_if_wrong: high
related_requirements: ["[[EPIC-INGEST-001]]"]
tags: [assumption]
updated: 2026-03-28
---

# Economic Operator Provides All Battery Data

## Statement
All static and dynamic battery passport data will be provided by the economic operator. The DBP accelerator does not generate, invent, or derive battery data from other sources.

## Rationale
Under EU 2023/1542, the economic operator (battery manufacturer) is legally responsible for the accuracy and completeness of battery passport data. The accelerator acts as a custodian and distributor of operator-provided data, not a data generator.

## Impact If Wrong
If this assumption is invalid:
- Manual data entry UI would be required
- Data generation or modeling capabilities would need to be built
- Regulatory liability would shift (ambiguous responsibility for data accuracy)
- MVP scope would expand significantly, delaying delivery

## Related Requirements
- [[EPIC-INGEST-001]]

## Risk Level
**High** — Violating this assumption could compromise regulatory compliance and MVP timeline.

---

_Created 2026-03-28. Owned by @pm._
