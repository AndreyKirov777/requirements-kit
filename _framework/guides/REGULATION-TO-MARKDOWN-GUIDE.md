# Source Document PDF to SRC Markdown Conversion Guide

> **Purpose:** Step-by-step instructions for an AI Agent to convert a regulatory
> or standards PDF into a structured SRC artifact compatible with the
> obsidian-requirements kit.
>
> **Output:** A single `SRC-<DOMAIN>-<NNN>.md` file in `01-product/sources/`
> with valid frontmatter (per `src.schema.json`) and heading-anchored content
> that downstream agents can reference via `source_ref`.
>
> **Scope:** This guide covers PDF-to-SRC conversion only. Extraction of BRQ and
> CON artifacts from SRC is a separate downstream activity.
>
> **Size target:** The output markdown should be **5-10% of the original PDF page
> count** (e.g., a 100-page document produces 5-10 pages of markdown).
>
> **Applies to:** EU regulations, ISO/DIN/IEC standards, national legislation,
> delegated/implementing acts, industry standards, and any other normative
> document that serves as a source for requirements.

---

## Phase 0 - Preparation

Before opening the PDF, gather metadata for the SRC frontmatter. Every field
must conform to `schema/src.schema.json`.

### Step 0.1 - Assign SRC identity

Determine the artifact ID following the kit convention `SRC-<DOMAIN>-<NNN>`:

- **DOMAIN** = uppercase code from the project taxonomy (2-5 characters derived
  from the document's subject area).
- **NNN** = next available number in `01-product/sources/`.

Examples:

| Document | Domain code | SRC ID |
|---|---|---|
| GDPR (EU 2016/679) | GDPR | SRC-GDPR-001 |
| ISO 27001:2022 | ISMS | SRC-ISMS-001 |
| EU Battery Regulation | BAT | SRC-BAT-001 |
| EU AI Act | AIACT | SRC-AIACT-001 |
| PCI DSS v4.0 | PCI | SRC-PCI-001 |

### Step 0.2 - Fill frontmatter

```yaml
---
id: SRC-GDPR-001
title: "General Data Protection Regulation (EU) 2016/679"
category: regulation               # regulation | standard | policy | strategy | contract
status: in_force                    # in_force | adopted | draft | proposed
version: "2016/679"
publication_date: "2016-05-04"
effective_date: "2018-05-25"
source_url: "https://eur-lex.europa.eu/eli/reg/2016/679/oj"
original_document: "99-attachments/gdpr-2016-679.pdf"
domain: "GDPR"
tags: [data-protection, privacy, personal-data]
updated: "2026-04-03"
---
```

**Field notes:**

- **Always quote dates** in YAML frontmatter (`"2023-07-28"` not `2023-07-28`).
  Unquoted dates are parsed as Python `datetime.date` objects by PyYAML, which
  breaks schema validation.
- **`category`** — choose the type that best describes the document:
  `regulation` (legally binding acts), `standard` (ISO, DIN, IEC, NIST),
  `policy` (internal policies), `strategy` (business strategy docs),
  `contract` (agreements, SLAs).
- **`status`** is a property of the source document itself, not an artifact
  lifecycle status (SRC has no lifecycle by design).
- **`publication_date`** vs **`effective_date`**: publication is when the
  document was officially issued; effective is when it becomes binding. For
  documents with phased rollout, use the earliest binding date. For standards,
  `effective_date` is the date of publication/adoption.
- **`source_url`** points to the authoritative web source (EUR-Lex, ISO
  catalogue, official gazette). `original_document` points to the local PDF
  copy in `99-attachments/`.
- **`updated`** is the date you create or last edit this SRC file, not the
  document date.

### Step 0.3 - Place the original PDF

Copy the source PDF into `99-attachments/` with a descriptive filename
(e.g., `gdpr-2016-679.pdf`, `iso-27001-2022.pdf`). The `original_document`
field links back to it.

---

## Phase 1 - Structural Scan (read TOC only)

**Goal:** Build a section map without reading the full text. Spend no more than
5 minutes here.

### Step 1.1 - Extract the Table of Contents

Read only the TOC pages. Create a flat list of all sections with page numbers:

```
Chapter I - General provisions ..................... p.32
Chapter II - Principles ............................ p.35
Chapter III - Rights of the data subject ........... p.39
...
Annex — Conformity assessment ...................... p.85
```

If the document has no TOC, scan headings to reconstruct one.

### Step 1.2 - Classify each section

Apply these rules to every TOC entry:

| Classification | Criteria | Action |
|---|---|---|
| **EXTRACT** | Contains obligations ("shall", "must"), data requirements, deadlines, rights, thresholds, technical specifications, control requirements, or compliance criteria relevant to the target system | Read fully, convert to structured markdown |
| **SKIM** | Contains definitions, scope, or general context that may clarify EXTRACT sections | Read selectively; extract only terms/definitions referenced by EXTRACT sections |
| **SKIP** | Procedural provisions (committee procedures, comitology, voting rules), penalty/enforcement clauses, forewords, bibliographies, amendment history, transitional provisions not affecting the system | Do not read |

**Classification depends on your project context.** A penalty clause is SKIP
for a technical system but may be EXTRACT for a compliance management system.
The agent must understand what the target system is before classifying.

### Step 1.3 - Record the Section Map

Create a classification checklist. Include it in the output file as an HTML
comment for audit trail and reproducibility:

```html
<!--
SECTION MAP (conversion plan)
- [SKIM] Chapter I — General provisions (scope, definitions)
- [EXTRACT] Chapter II — Principles (Art. 5-11)
- [EXTRACT] Chapter III — Rights of the data subject (Art. 12-23)
- [EXTRACT] Chapter IV — Controller and processor (Art. 24-43)
- [EXTRACT] Chapter V — Transfers to third countries (Art. 44-49)
- [SKIP] Chapter VI — Independent supervisory authorities
- [SKIP] Chapter VII — Cooperation and consistency
- [SKIP] Chapter VIII — Remedies, liability, penalties
- [SKIM] Chapter IX — Specific processing situations (Art. 85-91)
- [SKIP] Chapter X — Delegated and implementing acts
- [SKIP] Chapter XI — Final provisions
-->
```

---

## Phase 2 - Content Extraction

Work through EXTRACT sections in document order. For each section, use the
appropriate format below.

**Critical rule:** Do NOT introduce obligation IDs (like OB-001), requirement
IDs (BRQ-*), or constraint IDs (CON-*) into the SRC file. SRC is a passive
reference artifact. Identification of obligations and constraints happens
downstream.

### Heading anchor convention

Every section must have a markdown heading that generates a predictable anchor
for `source_ref` linking. Follow the source document's own structure:

| Source structure | Markdown heading example | Generated anchor |
|---|---|---|
| Article 17 | `## Article 17 - Right to erasure` | `#article-17---right-to-erasure` |
| Section 5.2 | `## Section 5.2 - Access control` | `#section-52---access-control` |
| Clause 8.1 | `## Clause 8.1 - Operational planning` | `#clause-81---operational-planning` |
| Annex A | `## Annex A - Reference control objectives` | `#annex-a---reference-control-objectives` |
| Requirement 7.2 | `## 7.2 Competence` | `#72-competence` |

Obsidian auto-generates anchors: lowercase, spaces become hyphens, special
characters stripped. Keep headings predictable so `source_ref` links work
(e.g., `SRC-GDPR-001#article-17---right-to-erasure`).

### Format A - Normative text (obligation/requirement language)

Use for: articles, clauses, or sections containing "shall", "must", "is
required to", or equivalent mandatory language. Paraphrase into structured,
concise markdown while preserving legal meaning.

```markdown
## Article 17 - Right to erasure

**Source:** p.43-44

The data subject has the right to obtain from the controller the erasure of
personal data without undue delay where one of the following grounds applies:

- The data is no longer necessary for the purpose it was collected
- The data subject withdraws consent (where consent is the legal basis)
- The data subject objects to processing and no overriding legitimate grounds exist
- The data has been unlawfully processed
- Erasure is required for compliance with a legal obligation

**Exceptions:** The right does not apply where processing is necessary for
exercising the right of freedom of expression, compliance with a legal
obligation, reasons of public interest in public health, archiving in the
public interest, or the establishment/exercise/defence of legal claims.

**Applies to:** controllers processing personal data of EU residents
**Deadline:** from effective date (2018-05-25)
```

**Paraphrasing rules:**

- Convert passive voice to imperative where possible: "information shall be
  made available" becomes "Make [information] available to [audience]"
- Preserve exact legal qualifiers: "shall" = mandatory, "should" = recommended,
  "may" = optional
- Keep all numeric values verbatim (percentages, dates, thresholds, limits)
- Always include: WHO is obligated, WHAT they must do, WHEN (if specified)
- Include exceptions and carve-outs — they are as important as the obligations
- Do NOT copy-paste full articles verbatim — paraphrase to reduce verbosity
  while preserving meaning

### Format B - Structured tables

Use for: annex tables, control matrices, data field specifications, requirement
checklists, risk categories, or any structured tabular data in the source.

**Tables with 15 or fewer rows** - use standard markdown tables:

```markdown
### Annex A.5 - Information security policies (excerpt)

**Source:** ISO 27001:2022, Annex A, p.18

| Control ID | Control | Type | Purpose |
|------------|---------|------|---------|
| A.5.1 | Policies for information security | preventive | Define and communicate information security policies |
| A.5.2 | Information security roles | preventive | Establish a defined structure of roles and responsibilities |
| A.5.3 | Segregation of duties | preventive | Reduce risk of fraud and error |
```

**Tables with more than 15 rows** - use fenced YAML blocks with a markdown
heading above (the heading provides the anchor for `source_ref`):

```markdown
### Annex A.8 - Technology controls

**Source:** ISO 27001:2022, Annex A, p.24-28
```

````yaml
# Annex A.8 — Technology controls
controls:
  - id: "A.8.1"
    name: "User endpoint devices"
    type: "preventive"
    description: "Information stored on, processed by, or accessible via user endpoint devices shall be protected"
    notes: null

  - id: "A.8.2"
    name: "Privileged access rights"
    type: "preventive"
    description: "Allocation and use of privileged access rights shall be restricted and managed"
    notes: "Applies to all system components with administrative access"

  - id: "A.8.3"
    name: "Information access restriction"
    type: "preventive"
    description: "Access to information and application functions shall be restricted in accordance with the access control policy"
    notes: null
````

**Rules for structured table extraction:**

- One entry per row — never merge rows even if they seem similar
- Preserve the original numbering/ID system for traceability
- Include ALL footnotes from the source table as `notes` — they often contain
  critical caveats, exceptions, or applicability conditions
- When the source uses codes or abbreviations, translate them to readable
  values on first occurrence and keep the translation consistent
- If a column value is ambiguous or missing in the source, write
  `"TBD - not specified in source"` rather than guessing
- Adapt the YAML field names to match what the source table actually contains.
  There is no fixed set of fields — use whatever columns the source table has
  (id, name, type, description, applicability, threshold, deadline, etc.)

### Format C - Definitions

Extract ONLY terms referenced by EXTRACT sections. Use a simple definition list:

```markdown
## Definitions

**Source:** Article 4 / Section 3 / Clause 3.1

- **Personal data** (Art. 4(1)): any information relating to an identified or
  identifiable natural person ('data subject').

- **Processing** (Art. 4(2)): any operation or set of operations performed on
  personal data, whether or not by automated means.

- **Controller** (Art. 4(7)): the natural or legal person, public authority,
  agency, or other body which, alone or jointly with others, determines the
  purposes and means of the processing.
```

---

## Phase 3 - Cross-references

After converting all EXTRACT sections, add a cross-reference section. This is
critical for multi-regulation environments where several SRC documents coexist.

```markdown
## Cross-references

### Internal (within this document)

- Art. 17 (right to erasure) references Art. 6 (lawfulness of processing)
- Art. 35 (impact assessment) references Art. 9 (special categories of data)

### External (to other documents)

- Art. 45 references Commission adequacy decisions (list of approved countries)
- Art. 43 references ISO/IEC 17065:2012 (certification body accreditation)
- Recital 171 references Directive 95/46/EC (predecessor, now repealed)

### Pending dependencies (delegated/implementing acts not yet adopted)

- Art. 12(8): Icons for data subject information — delegated act pending
- Art. 43(8): Certification mechanisms — implementing act pending
```

When an external document already has its own SRC file in the project, use the
SRC ID: "references SRC-ISO17065-001, Section 7".

---

## Phase 4 - Deadlines

Extract all dates mentioned in EXTRACT sections into a single timeline table.
Convert all relative dates ("within 18 months of publication", "no later than
2 years after entry into force") to absolute YYYY-MM-DD using
`publication_date` and `effective_date` from frontmatter.

```markdown
## Deadlines

| Date | Event | Legal basis | Status |
|------|-------|-------------|--------|
| 2018-05-25 | GDPR becomes applicable | Art. 99(2) | in_effect |
| 2025-02-02 | AI Act: prohibited AI practices apply | AI Act Art. 5 | in_effect |
| 2025-08-02 | AI Act: GPAI model obligations apply | AI Act Art. 51-56 | upcoming |
| 2026-08-02 | AI Act: high-risk AI systems obligations apply | AI Act Art. 6-49 | upcoming |
```

If the source document contains no dates or deadlines (common for standards
like ISO), omit this section entirely.

---

## Phase 5 - Assembly

Assemble the complete SRC file in this order:

```
---
[frontmatter from Phase 0]
---

<!-- SECTION MAP from Phase 1 -->

# [Title from frontmatter]

## Overview
[1-2 paragraphs: what this document is, who it affects, why it matters
for this project]

## Definitions
[Phase 2, Format C — only terms referenced by EXTRACT sections]

## [Headings in document order]
[Phase 2, Formats A and B — all EXTRACT sections, preserving source order]

## Cross-references
[Phase 3 — only if the document has meaningful cross-references]

## Deadlines
[Phase 4 — only if the document contains dates/deadlines]
```

**File naming:** `SRC-<DOMAIN>-<NNN>.md` (e.g., `SRC-GDPR-001.md`)
**File location:** `01-product/sources/`

The Cross-references and Deadlines sections are optional — include them only
when the source document actually contains such information. Many standards
(ISO, DIN) have cross-references but no deadlines; internal policies may have
neither.

---

## Quality Checklist

Run this checklist before considering the conversion complete:

- [ ] **Frontmatter validates:** All required fields present (`id`, `title`,
  `category`, `updated`); `id` matches pattern `SRC-[A-Z0-9]+-[0-9]{3,}`
- [ ] **Traceability:** Every paraphrased obligation, table entry, and
  constraint has a source reference (article, clause, annex, page number)
- [ ] **Anchors are predictable:** Every major section has a markdown heading
  that generates a stable anchor for `source_ref` linking
- [ ] **No orphan cross-references:** Every cross-reference target exists in
  this file or is flagged as external
- [ ] **No downstream IDs:** The SRC file contains no OB-*, BRQ-*, CON-*, or
  FR-* IDs — obligation/requirement identification is a separate activity
- [ ] **Tables complete:** Every table entry has all columns present in the
  source; missing values explicitly marked as TBD
- [ ] **Table format correct:** Tables with ≤15 rows in markdown; larger
  tables in fenced YAML with a heading above for the anchor
- [ ] **Size target met:** Output is 5-10% of original page count
- [ ] **Deadlines are absolute:** No relative dates remain — all converted to
  YYYY-MM-DD
- [ ] **Footnotes preserved:** Source table footnotes captured in `notes`
  fields — they often contain critical exceptions
- [ ] **SKIP sections verified:** Re-scan SKIPped sections for any hidden
  obligations or deadlines that were missed
- [ ] **Original PDF placed:** PDF exists in `99-attachments/` and
  `original_document` field points to it

---

## Tips by Document Type

### EU Regulations (EUR-Lex)

- Recitals (numbered paragraphs before Article 1) are NOT legally binding but
  clarify intent — extract only when an article is ambiguous.
- "Delegated acts" and "implementing acts" are future regulations that add
  detail — flag in Pending Dependencies.
- Reference structure: Article → Paragraph → Subparagraph → Point
  (e.g., Art. 17(1)(b)(ii)).
- Use the consolidated version from EUR-Lex when available — it includes all
  amendments in a single document.

### Technical Standards (ISO, DIN, IEC)

- "shall" = mandatory requirement, "should" = recommendation, "may" =
  permission. This convention is defined in ISO/IEC Directives Part 2.
- Informative annexes (marked "informative") are guidance, not requirements —
  still extract if they contain useful models or examples.
- Normative annexes (marked "normative") are binding parts of the standard.
- Standards typically reference other standards extensively — the
  Cross-references section is especially important here.

### Delegated / Implementing Regulations

- These supplement a parent regulation — always reference the parent in the
  Cross-references section.
- They often contain very specific thresholds, methodologies, and criteria that
  override or refine the parent regulation's general provisions.
- Check the "amends" / "supplements" / "pursuant to" line in the title to
  identify the parent.

### National Legislation

- Beware of amendments — national laws are often amended piecemeal, and the
  official consolidated text may not exist. Note the version/amendment date
  in frontmatter.
- Section/article numbering conventions vary by country (§ in German law,
  Section in UK/US, Article in French/Spanish).

### Industry Frameworks (PCI DSS, NIST, SOC 2)

- These often use their own requirement numbering system — preserve it exactly
  for traceability.
- Requirements may be grouped by category/domain — use nested headings to
  reflect this structure.
- Applicability conditions are common ("applies to service providers only",
  "required for Level 1 merchants") — always capture them.

---

## Anti-Patterns

1. **Do not copy-paste full text verbatim.** Paraphrase into structured
   markdown. Original legal/standards language is verbose and wastes context
   window tokens.

2. **Do not include procedural provisions** (committee voting, delegation
   procedures, reporting obligations to authorities). Unless the system
   directly supports these processes, they have zero impact.

3. **Do not flatten table hierarchies.** If a source table has grouped headers,
   preserve the grouping with nested headings.

4. **Do not omit footnotes.** In normative tables, footnotes often contain
   critical exceptions, applicability conditions, or effective dates. Missing
   a footnote = missing a business rule.

5. **Do not merge similar entries.** Even if two items seem related, keep them
   as separate entries — they may have different applicability, thresholds,
   or deadlines.

6. **Do not guess missing values.** If the source does not specify something,
   write `"TBD - not specified in source"` rather than assuming.

7. **Do not skip non-mandatory items.** Recommendations ("should") and
   optional provisions ("may") are valuable context and often become
   mandatory in future revisions or supplementary acts.

8. **Do not introduce downstream IDs.** SRC is a passive reference artifact.
   BRQ/CON/FR identification is a separate downstream activity.

9. **Do not over-extract.** The 5-10% size target exists for a reason — the
   SRC must fit in an agent's context window alongside other artifacts. If
   your output exceeds 10% of the original, re-evaluate your EXTRACT
   classifications.
