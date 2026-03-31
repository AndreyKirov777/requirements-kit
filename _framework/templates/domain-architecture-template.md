---
id: ARCH-XXX-000
title: ""
type: domain-architecture
status: draft
owner: ""
domain: ""
tags: [architecture]
updated: YYYY-MM-DD
parent_overview: "[[architecture-overview]]"
related_requirements: []
related_adrs: []
# --- AI Agent Metadata ---
agent_instructions:
  next_stage: task-planning
  generates:
    - adrs
    - code-maps
    - contracts
    - data-models
    - tasks
  approval_gate: human
  parseable_sections:
    - overview
    - internal_components
    - data_flow
    - api_and_interfaces
    - data_model
    - technology_choices
    - error_handling_and_resilience
    - security_considerations
    - key_decisions
    - constraints_and_trade_offs
    - related_artifacts
---

<!-- ============================================================
     DOMAIN ARCHITECTURE TEMPLATE
     ============================================================
     PURPOSE:
       Detailed architecture for a single domain / subsystem.
       This is the "zoom in" from the Architecture Overview.
       It describes internal components, data flows, APIs,
       data model, and domain-specific technology choices.

     HOW TO USE:
       1. Create one file per domain: ARCH-{DOMAIN}-{NNN}.md
          in 03-architecture/ root (next to adr/, code-map/, etc.).
       2. Link it from architecture-overview.md in the
          "Domain Architecture Index" section.
       3. Fill every section — agents parse section headers.
       4. Submit for review: set status → proposed.
       5. After human approval: status → approved.
       6. Do NOT modify after approval without a CR-*.

     AI AGENT GUIDANCE:
       - Read architecture-overview.md first to understand
         system-wide patterns before reading this file.
       - Use "Internal Components" to understand what to build.
       - Use "API and Interfaces" to define CONTRACT-* artifacts.
       - Use "Data Model" to create or update DM-* artifacts.
       - Use "Key Decisions" links to relevant ADRs.
       - Coding agents: this file + code-map tells you WHERE
         and HOW to implement tasks for this domain.
     ============================================================ -->

# Overview

<!-- 1–3 paragraphs describing what this domain / subsystem does,
     its responsibilities, and its boundaries.
     - What business capability does it provide?
     - What does it own (data, processes)?
     - What is explicitly NOT its responsibility? -->

# Internal Components

<!-- C4 Level 3: internal structure of this domain.
     Show services, modules, classes, or layers within the domain.

     Use a Mermaid diagram or reference an image in 99-attachments/.

     Below the diagram, list each component:

     | Component        | Responsibility                      | Key Files / Modules    |
     | ---------------- | ----------------------------------- | ---------------------- |
     | [Component name] | [What it does]                      | [Path in code-map]     |
-->

# Data Flow

<!-- Describe how data moves through this domain:
     - What triggers processing (API call, event, schedule)?
     - What are the main processing steps?
     - Where does data go after processing (DB, event bus, response)?

     Use a Mermaid sequence or flow diagram if helpful.

     ```mermaid
     sequenceDiagram
       participant Client
       participant API
       participant Service
       participant DB
       Client->>API: request
       API->>Service: process
       Service->>DB: persist
       Service-->>API: result
       API-->>Client: response
     ```
-->

# API and Interfaces

<!-- External-facing and inter-domain interfaces.
     List each endpoint or interface contract.

     | Interface        | Type          | Direction  | Contract                   |
     | ---------------- | ------------- | ---------- | -------------------------- |
     | [Endpoint/event] | [REST/gRPC/event/...] | [in/out] | [[CONTRACT-XXX-001]] |

     For detailed specs, link to CONTRACT-* files in
     03-architecture/contracts/. -->

# Data Model

<!-- Domain-specific data model.
     Show key entities, their relationships, and storage.

     Use a Mermaid ER diagram or reference an image.

     ```mermaid
     erDiagram
       EntityA ||--o{ EntityB : has
       EntityA {
         string id PK
         string name
       }
       EntityB {
         string id PK
         string entity_a_id FK
       }
     ```

     For full data model definitions, link to DM-* files in
     03-architecture/data-model/. -->

# Technology Choices

<!-- Domain-specific technology choices that differ from or
     extend the system-wide stack in architecture-overview.md.

     | Concern          | Technology     | Rationale                       | ADR              |
     | ---------------- | -------------- | ------------------------------- | ---------------- |
     | [Concern]        | [Tech]         | [Why this for this domain]      | [[ADR-XXX-001]]  |

     If this domain uses only the system-wide stack, write:
     "Uses system-wide stack — see architecture-overview.md." -->

# Error Handling and Resilience

<!-- How this domain handles failures:
     - Error propagation strategy (error codes, exceptions, result types)
     - Retry policies and idempotency
     - Circuit breakers or fallbacks
     - Monitoring / alerting specific to this domain -->

# Security Considerations

<!-- Domain-specific security concerns:
     - Data sensitivity classification
     - Access control rules (who can read/write what)
     - Encryption requirements (at rest, in transit)
     - Audit logging requirements
     - Regulatory constraints specific to this domain -->

# Key Decisions

<!-- ADRs that are particularly relevant to this domain.

     - [[ADR-XXX-001]] — [Title / one-line summary]
-->

# Constraints and Trade-offs

<!-- Domain-specific constraints and trade-offs.
     Link to CON-* and RISK-* artifacts where applicable.

     - [Constraint / trade-off] — see [[CON-XXX-001]]
-->

# Related Artifacts

<!-- Wikilinks to related artifacts:
     - Overview: [[architecture-overview]]
     - Requirements: [[FR-XXX-001]], [[NFR-XXX-001]], …
     - Code Map: [[CODEMAP-XXX-001]]
     - Data Models: [[DM-XXX-001]], …
     - Contracts: [[CONTRACT-XXX-001]], …
     - ADRs: [[ADR-XXX-001]], …
     - Tasks: [[TASK-XXX-001]], …
-->
