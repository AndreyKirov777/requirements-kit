---
id: ARCH-OVERVIEW
title: ""
type: architecture-overview
status: draft
owner: ""
domain: all
tags: [architecture]
updated: YYYY-MM-DD
# --- AI Agent Metadata ---
agent_instructions:
  next_stage: architecture-detailing
  generates:
    - domain-architectures
    - adrs
    - code-maps
    - contracts
    - data-models
  approval_gate: human
  parseable_sections:
    - architecture_style
    - system_context
    - component_overview
    - technology_stack
    - deployment_overview
    - cross_cutting_concerns
    - domain_architecture_index
    - key_decisions
    - constraints_and_trade_offs
    - related_artifacts
---

<!-- ============================================================
     ARCHITECTURE OVERVIEW TEMPLATE
     ============================================================
     PURPOSE:
       This is the single top-level architecture document for the
       entire solution. It provides a "bird's-eye view" of the
       system: architectural style, components, technology stack,
       deployment topology, and cross-cutting concerns.

       ADRs capture individual decisions. Domain-specific ARCH-*
       files capture per-domain deep dives. This document ties
       everything together and serves as the entry point for any
       agent or human trying to understand the system architecture.

     HOW TO USE:
       1. One per project — file name: architecture-overview.md
          in 03-architecture/ (NOT in templates/).
       2. Fill every section — agents use section headers for
          parsing and downstream generation.
       3. Submit for review: set status → proposed.
       4. After human approval: status → approved.
       5. Do NOT modify after approval without a Change Request (CR-*).

     AI AGENT GUIDANCE:
       - This is your FIRST READ when entering an architecture task.
       - Use "Component Overview" to understand system boundaries
         before diving into domain-specific ARCH-* files.
       - Use "Domain Architecture Index" to navigate to per-domain
         architecture documents.
       - Use "Key Decisions" links to find relevant ADRs.
       - Technology Stack informs your implementation choices —
         do not introduce technologies not listed here without
         proposing a new ADR.
     ============================================================ -->

# Architecture Style

<!-- Describe the overall architectural pattern(s) used:
     monolith, microservices, event-driven, serverless, modular
     monolith, CQRS, hexagonal, etc. Explain WHY this style was
     chosen given the product's goals and constraints.

     Keep to 1–3 paragraphs. Link to ADR if the choice was
     formally decided. -->

# System Context

<!-- C4 Level 1: System Context diagram.
     Show your system as a box in the center, surrounded by:
     - Users / actors (who interacts with it)
     - External systems (what it integrates with)

     Use a Mermaid diagram or reference an image in 99-attachments/.

     ```mermaid
     graph LR
       User([User]) --> System[Your System]
       System --> ExtA[External System A]
       System --> ExtB[External System B]
     ```

     Below the diagram, briefly describe each actor and external
     system (1 line each). -->

# Component Overview

<!-- C4 Level 2: Container / Component diagram.
     Show the major building blocks of your system:
     - Services, applications, databases, message brokers, etc.
     - How they communicate (sync/async, protocols)

     Use a Mermaid diagram or reference an image in 99-attachments/.

     Below the diagram, list each component:

     | Component        | Type       | Responsibility                    | Domain |
     | ---------------- | ---------- | --------------------------------- | ------ |
     | [Component name] | [service / db / queue / UI / ...] | [What it does] | [Domain code] |
-->

# Technology Stack

<!-- List the core technologies, frameworks, and tools.
     Group by layer or concern. Agents use this section to validate
     that implementation choices are consistent with the architecture.

     | Layer / Concern    | Technology       | Version  | Notes                |
     | ------------------ | ---------------- | -------- | -------------------- |
     | Frontend           | [e.g., React]    | [x.y]    | [SPA / SSR / etc.]   |
     | Backend            | [e.g., Node.js]  | [x.y]    | [REST / gRPC / etc.] |
     | Database           | [e.g., PostgreSQL] | [x.y]  | [Primary data store] |
     | Message Broker     | [e.g., Kafka]    | [x.y]    | [Async events]       |
     | Infrastructure     | [e.g., AWS ECS]  | —        | [Container runtime]  |
-->

# Deployment Overview

<!-- High-level deployment topology:
     - Where does each component run (cloud, on-prem, edge)?
     - Environments (dev, staging, prod)
     - Key infrastructure patterns (load balancing, CDN, etc.)

     Use a Mermaid diagram or reference an image.
     Keep it high-level — detailed IaC lives in the code repo. -->

# Cross-Cutting Concerns

<!-- Describe how the system handles concerns that span multiple
     components. Cover at least:

     ## Authentication & Authorization
     [How users and services authenticate. AuthN/AuthZ patterns.]

     ## Observability
     [Logging, metrics, tracing. What tools, what is collected.]

     ## Error Handling
     [Strategy for error propagation, retry policies, circuit breakers.]

     ## Security
     [Data encryption, secrets management, network policies.]

     ## Configuration Management
     [How config is injected per environment. Feature flags.]

     Add or remove subsections as relevant to your project. -->

# Domain Architecture Index

<!-- Links to domain-specific architecture documents (ARCH-{DOMAIN}-*).
     This section is populated as domains are elaborated.

     | Domain | Document                   | Status   | Summary                    |
     | ------ | -------------------------- | -------- | -------------------------- |
     | [XXX]  | [[ARCH-XXX-001]]           | [draft]  | [One-line summary]         |
-->

# Key Decisions

<!-- Links to the most important ADRs that shape this architecture.
     Not every ADR needs to be listed — only the ones essential for
     understanding the overall design.

     - [[ADR-XXX-001]] — [Title / one-line summary]
     - [[ADR-XXX-002]] — [Title / one-line summary]
-->

# Constraints and Trade-offs

<!-- Summarize the top architectural constraints and the trade-offs
     made. Link to CON-* and RISK-* artifacts where applicable.

     - [Constraint / trade-off description] — see [[CON-XXX-001]]
-->

# Related Artifacts

<!-- Wikilinks to key artifacts across the vault:
     - Vision: [[VISION-XXX-001]]
     - Epics: [[EPIC-XXX-001]], …
     - Domain Architectures: [[ARCH-XXX-001]], …
     - Key ADRs: [[ADR-XXX-001]], …
     - Data Models: [[DM-XXX-001]], …
     - Contracts: [[CONTRACT-XXX-001]], …
-->
