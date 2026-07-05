---
id: JOURNEY-DBP-001
title: Economic operator submits battery data for the first time
type: user-journey
status: approved
owner: "@pm"
domain: INGEST
persona: "[[PERSONA-DBP-002]]"
related_requirements:
  - "[[FR-INGEST-001]]"
tags: [journey, ingest]
updated: 2026-03-28
---

# Journey

How [[PERSONA-DBP-002|Integration Engineer Ravi]] onboards his organization and
submits the first battery passport records.

# Stages

1. **Discover.** Ravi reads the API documentation and obtains API credentials for his
   organization.
2. **Trial submission.** He submits a single test battery record and inspects the
   HTTP 201 ingestion receipt (`ingestionId`, timestamp).
3. **Fix validation errors.** A malformed record returns HTTP 400 with field-level
   errors; Ravi corrects the mapping in his pipeline.
4. **Automate.** He wires the submission into the nightly pipeline.
5. **Bulk migrate.** He hits the one-record-at-a-time limit for the historical
   backlog and requests batch support (motivates [[CR-INGEST-001]]).

# Pain Points

- Step 5 is slow at scale — the single-record API is the friction point.

# Related Requirements

Realized primarily by [[FR-INGEST-001]] within [[EPIC-INGEST-001]].
