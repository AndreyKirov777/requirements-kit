# Regulation Preprocessor — Pipeline Guide

This pipeline extracts Business Requirements (BRQ), Business Rules (BR), and Controls (CTRL)
from EU regulatory PDFs and prepares them for import into an Obsidian-based requirements vault.

All intermediate output stays in `_temp/` until you explicitly promote artifacts to `01-product/`.

---

## Prerequisites

```bash
pip install pymupdf pyyaml
```

---

## Pipeline Overview

```
PDF
 │
 ▼
1. regulation_chunker.py   →  _temp/<reg>/chunks/          (per-article Markdown)
 │
 ▼
2. context_builder.py      →  _temp/<reg>/packs/            (context packs for agent)
 │
 ▼
3. [analyst agent]         →  _temp/<reg>/extraction/       (raw agent output, manual step)
 │
 ▼
4. splitter.py             →  _temp/<reg>/artifacts/        (validated artifact files)
 │
 ▼
5. triage.py               →  _temp/<reg>/triage/packs/     (triage packs for agent)
 │
 ▼
6. [triage agent]          →  _temp/<reg>/triage/packs/*-output.md  (manual step)
 │
 ▼
7. triage_apply.py         →  _temp/<reg>/triage/           (artifacts with relevance labels)
 │
 ▼
8. promote.py              →  01-product/ or any target     (final artifacts, renumbered)
```

Steps 3 and 6 are manual: you run the context packs through an AI agent and save its output
before continuing to the next script.

---

## Step 1 — Chunk the regulation PDF

**Script:** `regulation_chunker.py`

Parses an EU regulation PDF and splits it into one Markdown file per article.
Strips Official Journal headers/footers, deduplicates articles, and extracts cross-references.

```bash
python regulation_chunker.py <input.pdf>
```

**Options:**

| Flag | Default | Description |
|------|---------|-------------|
| `--output-dir`, `-o` | `_temp/<reg>/chunks/` | Output directory |
| `--src-id` | auto-detected | SRC artifact ID (e.g. `SRC-BAT-001`) |
| `--debug` | off | Write full extracted text to `_temp/<reg>/debug_full_text.txt` |

**Output:** `_temp/<reg>/chunks/`
- `art-001.md`, `art-002.md`, ... — one file per article
- `_definitions.md` — Article 3 (or equivalent definitions article)
- `_index.json` — article index with chapter/section metadata

**Example:**
```bash
python regulation_chunker.py data/CELEX_32023R1542_EN_TXT.pdf
```

---

## Step 2 — Build context packs

**Script:** `context_builder.py`

Groups articles by chapter and assembles self-contained context packs for the analyst agent.
Each pack includes the extraction prompt, definitions, target articles, and abbreviated
cross-references — everything the agent needs in one file.

```bash
python context_builder.py <chunks-dir>
```

**Options:**

| Flag | Default | Description |
|------|---------|-------------|
| `--max-tokens`, `-t` | `30000` | Token budget per pack |
| `--output-dir`, `-o` | `_temp/<reg>/packs/` | Output directory |

**Output:** `_temp/<reg>/packs/`
- `pack-001.md`, `pack-002.md`, ... — context packs ready for the agent
- `_manifest.json` — lists which articles are in each pack

**Example:**
```bash
python context_builder.py _temp/eu-2023-1542/chunks/
```

---

## Step 3 — Run the analyst agent (manual)

Feed each `pack-NNN.md` to an AI agent with extraction instructions.
Save the agent output as `pack-NNN-output.md` in `_temp/<reg>/extraction/`.

The agent should emit artifact blocks delimited by `---FILE---`, each containing
YAML frontmatter and a Markdown body.

---

## Step 4 — Split agent output into artifact files

**Script:** `splitter.py`

Parses the agent's raw output, validates YAML frontmatter against schemas,
applies auto-fixes for common agent mistakes, and writes individual artifact files.

```bash
python splitter.py <extraction-dir>
```

**Options:**

| Flag | Default | Description |
|------|---------|-------------|
| `--output-dir`, `-o` | `_temp/<reg>/artifacts/` | Output directory |

**Output:** `_temp/<reg>/artifacts/`
- `brq/BRQ-BAT-NNN.md`
- `br/BR-BAT-NNN.md`
- `ctrl/CTRL-BAT-NNN.md`
- `_report.json` — parse summary and validation errors

**Example:**
```bash
python splitter.py _temp/eu-2023-1542/extraction/
```

---

## Step 5 — Build triage packs

**Script:** `triage.py`

Takes all extracted BRQ artifacts and a Product Vision file, and assembles triage packs
for the agent to classify each BRQ as `relevant`, `contextual`, or `out-of-scope`
relative to the target system.

```bash
python triage.py <artifacts-dir> <vision-file>
```

**Options:**

| Flag | Default | Description |
|------|---------|-------------|
| `--batch-size`, `-b` | `50` | BRQs per triage pack |
| `--output-dir`, `-o` | `_temp/<reg>/triage/` | Output directory |

**Output:** `_temp/<reg>/triage/packs/`
- `triage-pack-001.md`, ... — classification prompts for the agent
- `_manifest.json` — pack index

**Example:**
```bash
python triage.py _temp/eu-2023-1542/artifacts/ 01-product/vision/VISION-DBP-001.md
```

---

## Step 6 — Run the triage agent (manual)

Feed each `triage-pack-NNN.md` from `_temp/<reg>/triage/packs/` to an AI agent.
Save its output as `triage-pack-NNN-output.md` in the **same** `triage/packs/` directory.

The agent should output one JSON line per BRQ:
```
{"id": "BRQ-BAT-051", "relevance": "relevant", "rationale": "..."}
```

Relevance values: `relevant` · `contextual` · `out-of-scope`

---

## Step 7 — Apply triage results

**Script:** `triage_apply.py`

Collects the agent's triage output, applies `relevance` and `relevance_rationale` fields
to all BRQ artifacts, and propagates BRQ relevance to child BR and CTRL artifacts
via `derives_from` links (highest-ranked parent wins).

```bash
python triage_apply.py <artifacts-dir> <triage-packs-dir>
```

**Output:** `_temp/<reg>/triage/`
- `brq/`, `br/`, `ctrl/` — artifact copies with `relevance` field added
- `triage-report.json` — classification statistics and full mapping

**Example:**
```bash
python triage_apply.py _temp/eu-2023-1542/artifacts/ _temp/eu-2023-1542/triage/packs/
```

---

## Step 8 — Promote artifacts to the vault

**Script:** `promote.py`

Copies triaged artifacts to the target directory, renumbering IDs sequentially
and updating all cross-references. By default promotes only `relevant` artifacts.

```bash
python promote.py <triage-dir> <target-dir> [options]
```

**Options:**

| Flag | Default | Description |
|------|---------|-------------|
| `--include-contextual` | off | Also promote `contextual` artifacts |
| `--flat` | off | Use short subfolder names (`brq/`, `br/`, `ctrl/`) instead of Obsidian names |
| `--dry-run` | off | Preview what would be promoted without writing files |
| `--domain` | `BAT` | Domain prefix for renumbered IDs |

**Subfolder names by mode:**

| Mode | BRQ folder | BR folder | CTRL folder |
|------|------------|-----------|-------------|
| default (Obsidian) | `business-requirements/` | `business-rules/` | `controls/` |
| `--flat` | `brq/` | `br/` | `ctrl/` |

**Output:**
- Renumbered artifact files (gaps from batch extraction removed)
- `_promote-report.json` — old→new ID mapping

**Examples:**
```bash
# Promote to 01-product/ (final)
python promote.py _temp/eu-2023-1542/triage 01-product

# Include contextual artifacts
python promote.py _temp/eu-2023-1542/triage 01-product --include-contextual

# Test export to an arbitrary folder
python promote.py _temp/eu-2023-1542/triage _temp/eu-2023-1542/promoted --flat

# Preview before writing
python promote.py _temp/eu-2023-1542/triage 01-product --dry-run
```

---

## Complete Example — EU Battery Regulation 2023/1542

```bash
# 1. Chunk
python scripts/preprocessor/regulation_chunker.py data/CELEX_32023R1542_EN_TXT.pdf

# 2. Build context packs
python scripts/preprocessor/context_builder.py _temp/eu-2023-1542/chunks/

# 3. [Run analyst agent on each pack-NNN.md → save output to extraction/]

# 4. Split
python scripts/preprocessor/splitter.py _temp/eu-2023-1542/extraction/

# 5. Build triage packs
python scripts/preprocessor/triage.py _temp/eu-2023-1542/artifacts/ 01-product/vision/VISION-DBP-001.md

# 6. [Run triage agent on each triage-pack-NNN.md → save output to triage/packs/]

# 7. Apply triage
python scripts/preprocessor/triage_apply.py _temp/eu-2023-1542/artifacts/ _temp/eu-2023-1542/triage/packs/

# 8. Promote (preview first)
python scripts/preprocessor/promote.py _temp/eu-2023-1542/triage 01-product --dry-run
python scripts/preprocessor/promote.py _temp/eu-2023-1542/triage 01-product
```

---

## Folder Structure Reference

```
_temp/
└── eu-2023-1542/
    ├── chunks/                  # Step 1 output
    │   ├── _index.json
    │   ├── _definitions.md
    │   └── art-001.md ...
    ├── packs/                   # Step 2 output
    │   ├── _manifest.json
    │   └── pack-001.md ...
    ├── extraction/              # Step 3 input (manual)
    │   └── pack-001-output.md ...
    ├── artifacts/               # Step 4 output
    │   ├── _report.json
    │   ├── brq/
    │   ├── br/
    │   └── ctrl/
    └── triage/                  # Steps 5–7 output
        ├── triage-report.json
        ├── packs/
        │   ├── _manifest.json
        │   ├── triage-pack-001.md ...
        │   └── triage-pack-001-output.md ...  (manual)
        ├── brq/
        ├── br/
        └── ctrl/

01-product/                      # Step 8 output (version-controlled)
├── business-requirements/
├── business-rules/
└── controls/
```
