---
id: VISION-XXX-001
title: ""
type: vision
status: draft
owner: ""
domain: all
tags: [vision]
updated: YYYY-MM-DD
# --- AI Agent Metadata ---
# Downstream agents use these fields to scope PRD generation,
# persona creation, and requirements elaboration.
agent_instructions:
  next_stage: product-discovery
  generates:
    - personas
    - journeys
    - assumptions
    - epics
  approval_gate: human
  parseable_sections:
    - vision_statement
    - product_description
    - goals
    - non_goals
    - target_users
    - key_differentiators
    - constraints_and_risks
    - success_metrics
    - regulatory_or_domain_context
    - related_artifacts
---

<!-- ============================================================
     PRODUCT VISION TEMPLATE
     ============================================================
     PURPOSE:
       This is the top-level artifact in the AI SDLC pipeline.
       A human provides a high-level product description; the
       PM / Analyst agent expands it into this structured vision.
       Once approved, downstream agents use it to generate
       personas, journeys, assumptions, epics, and requirements.

     HOW TO USE:
       1. Replace all placeholder text (including "XXX" in the ID).
       2. Fill every section — agents rely on each section being
          present and non-empty to generate downstream artifacts.
       3. Submit for review: set status → proposed.
       4. After human approval: status → approved.
       5. Do NOT modify after status reaches "approved" without
          a Change Request (CR-*).

     AI AGENT GUIDANCE:
       - Read `agent_instructions` in frontmatter to determine
         what to generate next and which sections to parse.
       - Each section header maps to a `parseable_sections` key
         (lowercase, underscored). Use this mapping for extraction.
       - Goals are numbered for traceability — downstream epics
         MUST reference which goal(s) they serve.
       - Target Users entries become seeds for PERSONA-* artifacts.
       - Non-Goals are explicit scope boundaries — do not generate
         requirements for anything listed here.
     ============================================================ -->

# Vision Statement

<!-- A concise (1–3 sentence) aspirational statement describing the product's
     purpose and the future state it enables. This is the "north star."
     Example: "To become the leading platform for X by enabling Y." -->

# Product Description

<!-- A paragraph (3–8 sentences) describing what the product IS, what it does,
     and how it delivers value. Focus on capabilities, not implementation.
     This section feeds into epic and requirement generation. -->

# Goals

<!-- Numbered list of measurable outcomes the product must achieve.
     Each goal should be specific enough that you could write acceptance
     criteria for it. Downstream epics link back to these goal numbers.

     Format:
       1. [Goal statement — action verb + measurable outcome]
       2. …
-->

1. …
2. …

# Non-Goals

<!-- Explicit scope boundaries. List things the product will NOT do in this
     version/phase. Agents must not generate requirements for items listed here.
     Use this to prevent scope creep and set clear expectations.

     Format:
       - [Thing that is explicitly out of scope and why]
-->

- …

# Target Users

<!-- Each entry becomes a seed for a PERSONA-* artifact in product discovery.
     Provide enough context for the agent to generate a full persona.

     Format:
       - **[Role Name]** — [1-sentence description of who they are and
         their primary interaction with the product]
-->

- **[Role]** — …

# Key Differentiators

<!-- What makes this product unique compared to alternatives?
     List 3–6 differentiators. These inform competitive positioning
     and help agents prioritize requirements that protect differentiation.

     Format:
       - [Differentiator]: [brief explanation of why it matters]
-->

- …

# Success Metrics

<!-- Quantifiable indicators that the product vision is being realized.
     Each metric should have a target value and measurement method.
     These feed into NFR and test generation downstream.

     | Metric              | Target          | Measurement Method       |
     | ------------------- | --------------- | ------------------------ |
     | [Metric name]       | [Target value]  | [How to measure]         |
-->

| Metric | Target | Measurement Method |
| ------ | ------ | ------------------ |
| …      | …      | …                  |

# Constraints and Risks

<!-- High-level constraints (technical, regulatory, budget, timeline) and
     strategic risks. Each entry seeds CON-* and RISK-* artifacts downstream.

     ## Constraints
     - [Constraint]: [impact on the product]

     ## Risks
     - [Risk]: [likelihood] / [severity] — [brief mitigation idea]
-->

## Constraints

- …

## Risks

- …

# Regulatory or Domain Context

<!-- External regulations, standards, or domain-specific context that shapes
     the product. Include regulation names, effective dates, and key
     requirements. This section is critical for compliance-driven products
     and informs constraint and NFR generation.

     If not applicable, write "No specific regulatory requirements identified." -->

# Assumptions

<!-- SEED LIST — not the source of truth for assumptions.
     Write short, one-line assumptions here while drafting the vision.
     Format:
       - [Assumption statement] — Risk if wrong: [low/medium/high]

     LIFECYCLE:
       1. DRAFT stage: author writes seed assumptions in this section.
       2. APPROVED stage → Product Discovery (Stage 2): the analyst agent
          expands each seed into a full ASSUM-* artifact in
          `01-product/assumptions/` with validation plan, impact analysis,
          and its own status lifecycle.
       3. After ASSUM-* files are generated, replace the seed list below
          with wikilinks in the "Related Artifacts" section.

     AI AGENT RULE: Do not treat this section as canonical once ASSUM-*
     files exist. Always read `01-product/assumptions/` for current state.
-->

- …

# Related Artifacts

<!-- Wikilinks to downstream artifacts generated from this vision.
     This section is populated as the pipeline progresses — leave empty
     in initial drafts.

     - Personas: [[PERSONA-XXX-001]], …
     - Epics: [[EPIC-XXX-001]], …
     - Assumptions: [[ASSUM-XXX-001]], …
-->
