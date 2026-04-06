#!/usr/bin/env python3
"""
Context Builder — assembles context packs for the analyst agent.

Takes chunks produced by regulation_chunker.py and builds self-contained
context packs, each containing:
  1. System prompt with extraction instructions and output schema
  2. Definitions section (Article 3 or equivalent)
  3. One or more target articles to extract BRQ/BR/CTRL from
  4. Cross-referenced articles (summaries) needed for context

Context packs are batched by chapter for coherence. Each pack stays within
a configurable token budget.

Usage:
  python context_builder.py <chunks-dir> [--max-tokens 30000] [--output-dir packs/]

Output:
  _temp/<regulation>/packs/
    pack-001.md   (Chapter I articles)
    pack-002.md   (Chapter II articles, part 1)
    ...
    _manifest.json (pack index with article assignments)
"""

import argparse
import json
import re
import sys
from collections import defaultdict
from pathlib import Path


# ---------------------------------------------------------------------------
# Token estimation
# ---------------------------------------------------------------------------

def estimate_tokens(text: str) -> int:
    """Rough token estimate: 1 token ≈ 4 chars for English text."""
    return len(text) // 4


# ---------------------------------------------------------------------------
# Load chunks
# ---------------------------------------------------------------------------

def load_chunks(chunks_dir: Path) -> dict:
    """Load _index.json and all article files from a chunks directory."""
    index_path = chunks_dir / "_index.json"
    if not index_path.exists():
        print(f"Error: {index_path} not found", file=sys.stderr)
        sys.exit(1)

    index = json.loads(index_path.read_text())

    # Load definitions
    definitions_path = chunks_dir / "_definitions.md"
    definitions_text = ""
    if definitions_path.exists():
        definitions_text = definitions_path.read_text()
        # Strip frontmatter for inclusion as context
        if definitions_text.startswith("---"):
            parts = definitions_text.split("---", 2)
            if len(parts) >= 3:
                definitions_text = parts[2].strip()

    # Load each article's content
    articles = []
    for art_info in index["articles"]:
        art_path = chunks_dir / art_info["file"]
        if art_path.exists():
            full_content = art_path.read_text()
            # Split frontmatter and body
            if full_content.startswith("---"):
                parts = full_content.split("---", 2)
                if len(parts) >= 3:
                    frontmatter_raw = parts[1].strip()
                    body = parts[2].strip()
                else:
                    frontmatter_raw = ""
                    body = full_content
            else:
                frontmatter_raw = ""
                body = full_content

            articles.append({
                **art_info,
                "body": body,
                "frontmatter_raw": frontmatter_raw,
                "tokens": estimate_tokens(body),
            })

    return {
        "index": index,
        "articles": articles,
        "definitions": definitions_text,
        "definitions_tokens": estimate_tokens(definitions_text),
    }


# ---------------------------------------------------------------------------
# Group articles by chapter
# ---------------------------------------------------------------------------

def group_by_chapter(articles: list[dict]) -> list[tuple[str, list[dict]]]:
    """Group articles by parent_chapter, preserving article order."""
    groups = defaultdict(list)
    chapter_order = []

    for art in articles:
        chapter = art.get("parent_chapter") or "Ungrouped"
        if chapter not in groups:
            chapter_order.append(chapter)
        groups[chapter].append(art)

    return [(ch, groups[ch]) for ch in chapter_order]


# ---------------------------------------------------------------------------
# Build context packs
# ---------------------------------------------------------------------------

SYSTEM_PROMPT_TEMPLATE = """\
# Role

You are a regulatory analyst. Your task is to extract **Business Requirements (BRQ)**, \
**Business Rules (BR)**, and **Controls (CTRL)** from EU regulation articles.

# Source regulation

- **Regulation:** {regulation_id}
- **SRC ID:** {src_id}
- **Title:** {regulation_title}

# Definitions

The following definitions from Article 3 of the regulation apply to all articles below. \
Use these definitions when interpreting terms.

<definitions>
{definitions}
</definitions>

# Output format

For each obligation, requirement, or rule you identify, produce a **complete Markdown file** \
with YAML frontmatter. Output ALL files in sequence, separated by a line containing only `---FILE---`.

## When to create BRQ vs BR vs CTRL

- **BRQ** (Business Requirement): A high-level obligation or mandate. \
"The manufacturer SHALL provide...", "Member States SHALL ensure...", \
"Economic operators SHALL...". These are WHAT must be done.
- **BR** (Business Rule): An atomic, verifiable business logic statement. \
Thresholds, formulas, conditions, classifications, timelines. \
"Carbon footprint SHALL be calculated as kg CO2eq per kWh", \
"Batteries weighing > 5kg are classified as industrial". These are HOW.
- **CTRL** (Control): An enforceable, auditable check. \
"Declaration of conformity SHALL be verified by notified body", \
"Records SHALL be kept for 10 years". These are HOW TO VERIFY.

## If an article contains NO extractable obligations

Some articles are purely procedural (delegation of powers, committee procedures, \
entry into force). For these, output nothing — just a comment:

```
<!-- No BRQ/BR/CTRL extracted from Article N — procedural/administrative -->
```

## BRQ format

```yaml
---
id: "BRQ-{{DOMAIN}}-{{NNN}}"
title: "{{concise obligation title}}"
status: "identified"
source_type: "regulation"
priority: "{{critical|high|medium|low}}"
owner: "@analyst"
domain: "{{DOMAIN}}"
source_ref: "{src_id}#article-{{N}}"
regulatory_refs:
  - framework: "EU-{regulation_id_slug}"
    article: "{{N}}"
    paragraph: "{{P}}"
compliance_deadline: "{{YYYY-MM-DD if stated}}"
stakeholders: []
tags: [brq, {domain_tag}]
updated: "{today}"
---

## Summary

{{1-2 sentence summary of the obligation}}

## Regulatory text

> {{Exact quote from the regulation article}}

## Rationale

{{Why this obligation exists — what risk or goal it addresses}}
```

## BR format

```yaml
---
id: "BR-{{DOMAIN}}-{{NNN}}"
title: "{{concise rule title}}"
status: "draft"
priority: "{{critical|high|medium|low}}"
owner: "@analyst"
domain: "{{DOMAIN}}"
classification: "regulatory"
derives_from:
  - "[[BRQ-{{DOMAIN}}-{{NNN}}]]"
regulatory_ref:
  framework: "EU-{regulation_id_slug}"
  article: "{{N}}"
  paragraph: "{{P}}"
tags: [br, {domain_tag}]
updated: "{today}"
---

## Rule statement

{{Precise, atomic rule statement}}

## Source

> {{Exact quote from the regulation}}
```

## CTRL format

```yaml
---
id: "CTRL-{{DOMAIN}}-{{NNN}}"
title: "{{concise control title}}"
status: "identified"
priority: "{{critical|high|medium|low}}"
owner: "@analyst"
domain: "{{DOMAIN}}"
derives_from:
  - "[[BRQ-{{DOMAIN}}-{{NNN}}]]"
verification_method: "{{inspection|test|demonstration|analysis}}"
compliance_deadline: "{{YYYY-MM-DD if stated}}"
tags: [ctrl, {domain_tag}]
updated: "{today}"
---

## Control statement

{{What must be verified and how}}

## Source

> {{Exact quote from the regulation}}
```

# Numbering rules

- Use **domain** = `BAT` for all battery regulation artifacts (override with source-specific domain if obvious)
- Start numbering from **{start_num}** for this batch: BRQ-BAT-{start_num:03d}, BR-BAT-{start_num:03d}, CTRL-BAT-{start_num:03d}
- Number sequentially within this batch, incrementing independently for each type

# Instructions

1. Read each article below carefully
2. Identify ALL obligations, rules, thresholds, deadlines, and verification requirements
3. For each, decide: BRQ, BR, or CTRL
4. Write complete Markdown artifacts with frontmatter
5. Include exact regulatory quotes in the body
6. If a deadline is stated (e.g. "by 18 February 2027"), convert to compliance_deadline: YYYY-MM-DD
7. Do NOT invent requirements not present in the text
8. Do NOT create FR or NFR — only BRQ, BR, CTRL
"""


def build_pack(
    pack_num: int,
    chapter: str,
    target_articles: list[dict],
    all_articles: dict[str, dict],
    definitions: str,
    config: dict,
) -> dict:
    """Build a single context pack."""

    # Collect cross-referenced articles needed as context
    cross_ref_nums = set()
    for art in target_articles:
        for ref in art.get("cross_refs", []):
            # Only include if not already a target article
            if ref not in {a["num"] for a in target_articles}:
                cross_ref_nums.add(ref)

    # Build cross-reference context (abbreviated)
    cross_ref_section = ""
    if cross_ref_nums:
        parts = []
        for ref_num in sorted(cross_ref_nums, key=lambda x: int(re.match(r"(\d+)", x).group(1))):
            if ref_num in all_articles:
                ref_art = all_articles[ref_num]
                # Include only first ~500 chars as context summary
                summary = ref_art["body"][:500]
                if len(ref_art["body"]) > 500:
                    summary += "\n[...truncated...]"
                parts.append(f"### Article {ref_num} (context only)\n\n{summary}")
        if parts:
            cross_ref_section = (
                "\n\n# Referenced articles (for context only — do NOT extract from these)\n\n"
                + "\n\n".join(parts)
            )

    # Build target articles section
    target_section_parts = []
    for art in target_articles:
        target_section_parts.append(
            f"## Article {art['num']} — {art['title']}\n\n{art['body']}"
        )
    target_section = "\n\n---\n\n".join(target_section_parts)

    # Assemble system prompt
    system_prompt = SYSTEM_PROMPT_TEMPLATE.format(
        regulation_id=config["regulation_id"],
        regulation_id_slug=config["regulation_id"].replace("/", "-"),
        src_id=config["src_id"],
        regulation_title=config["title"],
        definitions=definitions,
        domain_tag=config.get("domain_tag", "battery-regulation"),
        today=config.get("today", "2026-04-06"),
        start_num=config.get("start_num", 1) + (pack_num - 1) * 50,
    )

    # Full pack content
    full_pack = (
        system_prompt
        + f"\n\n# Chapter context: {chapter}\n\n"
        + "# Articles to analyze\n\n"
        + "Extract BRQ, BR, and CTRL from the following articles.\n\n"
        + target_section
        + cross_ref_section
    )

    return {
        "pack_num": pack_num,
        "chapter": chapter,
        "articles": [a["num"] for a in target_articles],
        "cross_refs": sorted(cross_ref_nums),
        "content": full_pack,
        "tokens": estimate_tokens(full_pack),
    }


def build_all_packs(
    data: dict,
    max_tokens: int = 30000,
) -> list[dict]:
    """Build context packs for all articles, grouped by chapter."""

    config = {
        "regulation_id": data["index"]["regulation_id"],
        "src_id": data["index"]["src_id"],
        "title": data["index"]["title"],
        "domain_tag": "battery-regulation",
        "today": "2026-04-06",
        "start_num": 1,
    }

    # Build article lookup by number
    all_articles = {a["num"]: a for a in data["articles"]}

    # Group by chapter
    chapter_groups = group_by_chapter(data["articles"])

    # Budget: system prompt + definitions are constant overhead
    definitions = data["definitions"]
    prompt_overhead = estimate_tokens(
        SYSTEM_PROMPT_TEMPLATE.format(
            regulation_id="X", regulation_id_slug="X", src_id="X",
            regulation_title="X", definitions="X", domain_tag="X",
            today="X", start_num=1,
        )
    )
    definitions_overhead = data["definitions_tokens"]
    fixed_overhead = prompt_overhead + definitions_overhead + 500  # margin

    available_per_pack = max_tokens - fixed_overhead

    packs = []
    pack_num = 1

    for chapter, articles in chapter_groups:
        current_batch = []
        current_tokens = 0

        for art in articles:
            art_tokens = art["tokens"]

            # Estimate cross-ref overhead for this article
            cross_ref_tokens = 0
            for ref in art.get("cross_refs", []):
                if ref in all_articles and ref != art["num"]:
                    cross_ref_tokens += min(125, all_articles[ref]["tokens"])  # ~500 chars

            total_for_art = art_tokens + cross_ref_tokens

            # Check if adding this article exceeds budget
            if current_batch and (current_tokens + total_for_art > available_per_pack):
                # Flush current batch
                packs.append(build_pack(
                    pack_num, chapter, current_batch, all_articles,
                    definitions, config,
                ))
                pack_num += 1
                current_batch = []
                current_tokens = 0

            current_batch.append(art)
            current_tokens += total_for_art

        # Flush remaining articles in this chapter
        if current_batch:
            packs.append(build_pack(
                pack_num, chapter, current_batch, all_articles,
                definitions, config,
            ))
            pack_num += 1

    return packs


# ---------------------------------------------------------------------------
# Output
# ---------------------------------------------------------------------------

def write_packs(packs: list[dict], output_dir: Path):
    """Write context packs and manifest to output directory."""
    output_dir.mkdir(parents=True, exist_ok=True)

    manifest = {
        "total_packs": len(packs),
        "total_articles": sum(len(p["articles"]) for p in packs),
        "total_tokens": sum(p["tokens"] for p in packs),
        "packs": [],
    }

    for pack in packs:
        filename = f"pack-{pack['pack_num']:03d}.md"
        filepath = output_dir / filename
        filepath.write_text(pack["content"])

        manifest["packs"].append({
            "file": filename,
            "pack_num": pack["pack_num"],
            "chapter": pack["chapter"],
            "articles": pack["articles"],
            "cross_refs": pack["cross_refs"],
            "tokens": pack["tokens"],
        })

    manifest_path = output_dir / "_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))

    print(f"  Packs written: {len(packs)}")
    print(f"  Manifest: {manifest_path}")
    return manifest


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Build context packs for analyst agent from regulation chunks."
    )
    parser.add_argument(
        "chunks_dir",
        help="Path to chunks directory (output of regulation_chunker.py)"
    )
    parser.add_argument(
        "--max-tokens", "-t",
        type=int,
        default=30000,
        help="Max tokens per context pack (default: 30000)"
    )
    parser.add_argument(
        "--output-dir", "-o",
        default=None,
        help="Output directory (default: sibling 'packs/' next to chunks/)"
    )
    args = parser.parse_args()

    chunks_dir = Path(args.chunks_dir)
    print(f"Loading chunks from: {chunks_dir}")
    data = load_chunks(chunks_dir)
    print(f"  Articles: {len(data['articles'])}")
    print(f"  Definitions: {data['definitions_tokens']} tokens")

    print(f"\nBuilding context packs (max {args.max_tokens:,} tokens each)...")
    packs = build_all_packs(data, max_tokens=args.max_tokens)

    output_dir = Path(args.output_dir) if args.output_dir else chunks_dir.parent / "packs"
    print(f"\nWriting to: {output_dir}")
    manifest = write_packs(packs, output_dir)

    # Summary
    tokens_list = [p["tokens"] for p in packs]
    print(f"\nSummary:")
    print(f"  Total packs: {manifest['total_packs']}")
    print(f"  Total articles covered: {manifest['total_articles']}")
    print(f"  Total tokens: {manifest['total_tokens']:,}")
    print(f"  Tokens per pack: min={min(tokens_list):,}, max={max(tokens_list):,}, avg={sum(tokens_list)//len(tokens_list):,}")

    # Show pack breakdown
    print(f"\nPack breakdown:")
    for p in manifest["packs"]:
        arts = ", ".join(p["articles"][:5])
        if len(p["articles"]) > 5:
            arts += f" ... (+{len(p['articles'])-5} more)"
        print(f"  Pack {p['pack_num']:3d}: {p['tokens']:>6,} tok | {len(p['articles']):>2d} articles | {p['chapter'][:50]}")

    print("\nDone.")


if __name__ == "__main__":
    main()
