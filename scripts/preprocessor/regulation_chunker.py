#!/usr/bin/env python3
"""
Regulation Preprocessor — PDF → structured Markdown chunks.

Parses EU-style regulatory PDFs and splits them into per-article
Markdown files suitable for downstream AI extraction of BRQ/BR/CTRL.

Typical EU regulation structure:
  Preamble (recitals)
  TITLE / PART → CHAPTER → SECTION → Article → Paragraph

Output per article:
  - YAML frontmatter with structural metadata
  - Full article text in Markdown
  - Cross-reference annotations

Usage:
  python regulation_chunker.py <input.pdf> [--output-dir chunks/] [--src-id SRC-BAT-001]

Requirements:
  pip install pymupdf
"""

import argparse
import json
import re
import sys
import unicodedata
from dataclasses import dataclass, field
from pathlib import Path

import pymupdf


# ---------------------------------------------------------------------------
# Data model
# ---------------------------------------------------------------------------

@dataclass
class ArticleChunk:
    """A single article extracted from the regulation."""
    article_num: str            # e.g. "3", "77"
    title: str                  # article title if present
    text: str                   # full text of the article
    parent_chapter: str = ""    # e.g. "Chapter II"
    parent_title: str = ""      # e.g. "TITLE III"
    parent_part: str = ""       # e.g. "Part A"
    page_start: int = 0
    page_end: int = 0
    cross_refs: list = field(default_factory=list)


@dataclass
class RegulationStructure:
    """Parsed regulation with metadata and articles."""
    title: str = ""
    regulation_id: str = ""
    preamble: str = ""
    articles: list = field(default_factory=list)
    annexes: list = field(default_factory=list)
    total_pages: int = 0


# ---------------------------------------------------------------------------
# PDF text extraction (PyMuPDF)
# ---------------------------------------------------------------------------

def extract_pages(pdf_path: str) -> list[dict]:
    """Extract text from each page using PyMuPDF."""
    pages = []
    doc = pymupdf.open(pdf_path)
    for i, page in enumerate(doc):
        text = page.get_text()
        pages.append({
            "page_num": i + 1,
            "text": text,
        })
    doc.close()
    return pages


def merge_pages_to_text(pages: list[dict]) -> str:
    """Merge all pages into continuous text with page markers."""
    parts = []
    for p in pages:
        parts.append(f"\n<!--PAGE:{p['page_num']}-->\n")
        parts.append(p["text"])
    return "\n".join(parts)


# ---------------------------------------------------------------------------
# Structure detection — EU regulation patterns
# ---------------------------------------------------------------------------

RE_ARTICLE_START = re.compile(
    r"^Article\s+(\d+[a-z]?)\s*$",
    re.MULTILINE
)

RE_CHAPTER = re.compile(
    r"^CHAPTER\s+([IVXLCDM]+(?:\s*[a-z])?)\s*\n\s*(.+)",
    re.MULTILINE | re.IGNORECASE
)

RE_TITLE_HEADING = re.compile(
    r"^TITLE\s+([IVXLCDM]+)\s*\n\s*(.+)",
    re.MULTILINE | re.IGNORECASE
)

RE_ANNEX_START = re.compile(
    r"^ANNEX\s+([IVXLCDM]+|[A-Z0-9]+)\s*$",
    re.MULTILINE | re.IGNORECASE
)

RE_CROSS_REF = re.compile(r"Article\s+(\d+[a-z]?)")

RE_PAGE_MARKER = re.compile(r"<!--PAGE:(\d+)-->")

# EU Official Journal header/footer noise patterns
RE_OJ_HEADER = re.compile(
    r"^(?:"
    r"EN\s*$"                                         # language code
    r"|Official Journal of the European Union\s*$"    # OJ title
    r"|\d{1,2}\.\d{1,2}\.\d{4}\s*$"                  # date (28.7.2023)
    r"|L\s+\d+/\d+\s*$"                              # page ref (L 191/25)
    r")",
    re.MULTILINE
)

# Footnotes: ( N ) OJ L ... or ( N ) Directive/Regulation ...
RE_FOOTNOTE = re.compile(
    r"^\(\s*\d+\s*\)\s+(?:OJ\s|Directive\s|Regulation\s|Council\s|Commission\s|Decision\s).+$",
    re.MULTILINE
)


def detect_regulation_id(full_text: str) -> str:
    """Detect regulation number: (EU) 2023/1542 or (EC) No 1907/2006."""
    m = re.search(r"\((?:EU|EC)\)\s*(?:No\s*)?(\d{4}/\d+)", full_text)
    return m.group(1) if m else "unknown"


def detect_regulation_title(full_text: str) -> str:
    """Detect main title from first pages."""
    lines = full_text[:8000].split("\n")
    title_lines = []
    capture = False
    for line in lines:
        stripped = line.strip()
        if "REGULATION" in stripped.upper() and len(stripped) > 20:
            capture = True
        if capture:
            if stripped and not stripped.startswith("<!--"):
                title_lines.append(stripped)
            elif title_lines:
                break
    return " ".join(title_lines[:3]) if title_lines else "Unknown Regulation"


def find_page_at(full_text: str, pos: int) -> int:
    """Find page number at a given position in the merged text."""
    text_before = full_text[:pos]
    markers = list(RE_PAGE_MARKER.finditer(text_before))
    return int(markers[-1].group(1)) if markers else 0


def extract_cross_references(
    text: str, own_article: str, valid_articles: set[str] | None = None
) -> list[str]:
    """Find Article N references within the same regulation.

    Filters out:
    - Self-references
    - References to articles in external directives/regulations
      (detected by preceding "of Directive/Regulation" context)
    - Article numbers not present in this regulation (when valid_articles given)
    """
    refs = set()
    for m in RE_CROSS_REF.finditer(text):
        ref_num = m.group(1)
        if ref_num == own_article:
            continue

        # Check if this is a reference to an external document
        # Look at preceding context (up to 80 chars before the match)
        pre_start = max(0, m.start() - 80)
        preceding = text[pre_start:m.start()].lower()
        if any(kw in preceding for kw in (
            "directive", "regulation (ec)", "regulation (eu) 20",
            "regulation (eec)", "decision",
        )):
            # Likely external reference — skip unless it also matches
            # an article in our regulation
            if valid_articles and ref_num not in valid_articles:
                continue

        if valid_articles and ref_num not in valid_articles:
            continue

        refs.add(ref_num)
    return sorted(refs, key=lambda x: int(re.match(r"(\d+)", x).group(1)))


def clean_article_text(raw: str, title: str) -> str:
    """Remove PDF noise from article text.

    Strips: OJ headers/footers, footnote references, page markers,
    soft hyphens, and duplicate leading title.
    """
    text = raw

    # Remove page markers
    text = RE_PAGE_MARKER.sub("", text)

    # Remove soft hyphens
    text = text.replace("\xad", "")

    # Remove OJ header/footer lines
    text = RE_OJ_HEADER.sub("", text)

    # Remove footnotes (references to other EU legislation)
    text = RE_FOOTNOTE.sub("", text)

    # Remove isolated single-space lines left by stripping
    text = re.sub(r"^\s+$", "", text, flags=re.MULTILINE)

    # Collapse multiple blank lines
    text = re.sub(r"\n{3,}", "\n\n", text)

    # Remove duplicate title at the start of the body
    # (PyMuPDF often extracts the article title both as heading and first line)
    text = text.strip()
    if title and title != "Article" and text.startswith(title):
        text = text[len(title):].strip()

    return text


# ---------------------------------------------------------------------------
# Main parsing
# ---------------------------------------------------------------------------

def parse_regulation(full_text: str) -> RegulationStructure:
    """Parse the full regulation text into structured components."""
    reg = RegulationStructure()
    reg.regulation_id = detect_regulation_id(full_text)
    reg.title = detect_regulation_title(full_text)

    # Build hierarchy map: position → chapter/title info
    chapters = []
    for m in RE_CHAPTER.finditer(full_text):
        chapters.append((m.start(), m.group(1).strip(), m.group(2).strip()))

    title_headings = []
    for m in RE_TITLE_HEADING.finditer(full_text):
        title_headings.append((m.start(), m.group(1).strip(), m.group(2).strip()))

    # Find annex start positions (used as boundary for article search)
    annex_starts = list(RE_ANNEX_START.finditer(full_text))
    first_annex_pos = annex_starts[0].start() if annex_starts else len(full_text)

    # Find article starts ONLY in the main body (before annexes)
    main_body = full_text[:first_annex_pos]
    article_starts = list(RE_ARTICLE_START.finditer(main_body))

    # Deduplicate: keep only the first occurrence of each article number
    seen_nums = set()
    unique_starts = []
    for m in article_starts:
        num = m.group(1)
        if num not in seen_nums:
            seen_nums.add(num)
            unique_starts.append(m)
    article_starts = unique_starts

    # Build set of valid article numbers for cross-ref filtering
    valid_articles = {m.group(1) for m in article_starts}

    # Extract each article: text between this Article and the next
    for i, m in enumerate(article_starts):
        art_num = m.group(1)
        art_start = m.end()  # right after "Article N\n"

        # End boundary: next article, or first annex, or end of text
        if i + 1 < len(article_starts):
            art_end = article_starts[i + 1].start()
        else:
            art_end = first_annex_pos

        raw_text = full_text[art_start:art_end]

        # Pre-clean for title detection (remove page markers only)
        pre_clean = RE_PAGE_MARKER.sub("", raw_text).replace("\xad", "").strip()

        # Extract title: first non-empty, non-numeric, non-noise line
        title = f"Article {art_num}"
        for line in pre_clean.split("\n"):
            line = line.strip()
            if not line:
                continue
            if re.match(r"^\d+\.\s", line):
                continue  # paragraph number, not title
            if len(line) >= 200:
                continue
            if RE_OJ_HEADER.match(line):
                continue  # page header/footer noise
            if line in ("EN",):
                continue
            title = line
            break

        # Determine parent chapter
        parent_chapter = ""
        for ch_pos, ch_num, ch_title in chapters:
            if ch_pos < m.start():
                parent_chapter = f"Chapter {ch_num} — {ch_title}"

        # Determine parent title
        parent_title = ""
        for t_pos, t_num, t_title in title_headings:
            if t_pos < m.start():
                parent_title = f"Title {t_num} — {t_title}"

        # Page range
        page_start = find_page_at(full_text, m.start())
        page_end = find_page_at(full_text, art_end)
        if page_end < page_start:
            page_end = page_start

        # Full cleaning (headers, footers, footnotes, duplicate title)
        clean = clean_article_text(raw_text, title)

        # Cross-references (only to articles in this regulation)
        cross_refs = extract_cross_references(clean, art_num, valid_articles)

        chunk = ArticleChunk(
            article_num=art_num,
            title=title,
            text=clean,
            parent_chapter=parent_chapter,
            parent_title=parent_title,
            page_start=page_start,
            page_end=page_end,
            cross_refs=cross_refs,
        )
        reg.articles.append(chunk)

    # Extract annexes
    for i, m in enumerate(annex_starts):
        annex_num = m.group(1)
        annex_start = m.end()
        if i + 1 < len(annex_starts):
            annex_end = annex_starts[i + 1].start()
        else:
            annex_end = len(full_text)

        annex_text = full_text[annex_start:annex_end]
        annex_text = RE_PAGE_MARKER.sub("", annex_text).replace("\xad", "").strip()

        reg.annexes.append({
            "num": annex_num,
            "text": annex_text[:5000],
            "full_length": len(annex_text),
        })

    return reg


# ---------------------------------------------------------------------------
# Markdown output
# ---------------------------------------------------------------------------

def article_to_markdown(chunk: ArticleChunk, src_id: str, reg_id: str) -> str:
    """Convert an ArticleChunk to Markdown with YAML frontmatter."""
    anchor = f"article-{chunk.article_num}"

    cross_ref_lines = [
        f'  - "{src_id}#article-{ref}"'
        for ref in chunk.cross_refs
    ]
    cross_refs_yaml = "\n".join(cross_ref_lines) if cross_ref_lines else "  []"

    safe_title = chunk.title.replace('"', '\\"')
    safe_parent_title = chunk.parent_title.replace('"', '\\"')
    safe_parent_chapter = chunk.parent_chapter.replace('"', '\\"')

    frontmatter = (
        f'---\n'
        f'source_id: "{src_id}"\n'
        f'regulation: "{reg_id}"\n'
        f'article: "{chunk.article_num}"\n'
        f'anchor: "{anchor}"\n'
        f'title: "{safe_title}"\n'
        f'parent_title: "{safe_parent_title}"\n'
        f'parent_chapter: "{safe_parent_chapter}"\n'
        f'page_range: [{chunk.page_start}, {chunk.page_end}]\n'
        f'cross_references:\n'
        f'{cross_refs_yaml}\n'
        f'---'
    )

    body = f"# Article {chunk.article_num}\n\n**{chunk.title}**\n\n{chunk.text}\n"

    if chunk.cross_refs:
        refs_list = ", ".join([f"Article {r}" for r in chunk.cross_refs])
        body += f"\n---\n\n**Cross-references:** {refs_list}\n"

    return frontmatter + "\n\n" + body


def write_chunks(reg: RegulationStructure, output_dir: Path, src_id: str):
    """Write all articles as individual Markdown files."""
    output_dir.mkdir(parents=True, exist_ok=True)

    # Write metadata index
    index = {
        "src_id": src_id,
        "regulation_id": reg.regulation_id,
        "title": reg.title,
        "total_pages": reg.total_pages,
        "total_articles": len(reg.articles),
        "total_annexes": len(reg.annexes),
        "articles": [
            {
                "num": a.article_num,
                "title": a.title,
                "file": f"art-{a.article_num.zfill(3)}.md",
                "parent_chapter": a.parent_chapter,
                "parent_title": a.parent_title,
                "cross_refs": a.cross_refs,
                "text_chars": len(a.text),
            }
            for a in reg.articles
        ],
    }
    index_path = output_dir / "_index.json"
    index_path.write_text(json.dumps(index, indent=2, ensure_ascii=False))
    print(f"  Index: {index_path}")

    # Write each article
    for chunk in reg.articles:
        filename = f"art-{chunk.article_num.zfill(3)}.md"
        filepath = output_dir / filename
        md = article_to_markdown(chunk, src_id, reg.regulation_id)
        filepath.write_text(md)

    print(f"  Articles: {len(reg.articles)} files written")

    # Write definitions file (Article 3 is typically definitions in EU regs)
    definitions = [a for a in reg.articles if a.article_num == "3"]
    if definitions:
        def_path = output_dir / "_definitions.md"
        def_path.write_text(article_to_markdown(definitions[0], src_id, reg.regulation_id))
        print(f"  Definitions: {def_path}")

    # Write annexes summary
    if reg.annexes:
        annexes_path = output_dir / "_annexes_summary.json"
        annexes_path.write_text(json.dumps(reg.annexes, indent=2, ensure_ascii=False))
        print(f"  Annexes: {len(reg.annexes)} found, summary at {annexes_path}")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Parse EU regulation PDF into per-article Markdown chunks."
    )
    parser.add_argument("pdf", help="Path to regulation PDF")
    parser.add_argument(
        "--output-dir", "-o",
        default=None,
        help="Output directory (default: _temp/<regulation-slug>/chunks/)"
    )
    parser.add_argument(
        "--src-id",
        default=None,
        help="SRC artifact ID (e.g. SRC-BAT-001). Auto-detected if not provided."
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Print debug info during parsing"
    )
    args = parser.parse_args()

    pdf_path = Path(args.pdf)
    if not pdf_path.exists():
        print(f"Error: file not found: {pdf_path}", file=sys.stderr)
        sys.exit(1)

    print(f"Extracting text from: {pdf_path}")
    pages = extract_pages(str(pdf_path))
    print(f"  Pages extracted: {len(pages)}")

    full_text = merge_pages_to_text(pages)

    print("Parsing regulation structure...")
    reg = parse_regulation(full_text)
    reg.total_pages = len(pages)

    # Auto-detect src_id from regulation_id
    src_id = args.src_id
    if not src_id:
        if reg.regulation_id != "unknown":
            num = reg.regulation_id.split("/")[-1]
            src_id = f"SRC-EU{num}-001"
        else:
            src_id = "SRC-REG-001"

    # Derive regulation slug for directory naming
    # e.g. "2023/1542" → "eu-2023-1542", or fall back to PDF filename
    if reg.regulation_id != "unknown":
        reg_slug = f"eu-{reg.regulation_id.replace('/', '-')}"
    else:
        reg_slug = pdf_path.stem.lower()
        # Normalize: keep only ascii alphanumeric, hyphens, underscores
        reg_slug = re.sub(r"[^a-z0-9_-]", "-", reg_slug)
        reg_slug = re.sub(r"-{2,}", "-", reg_slug).strip("-")

    print(f"  Regulation: {reg.regulation_id}")
    print(f"  SRC ID: {src_id}")
    print(f"  Slug: {reg_slug}")
    print(f"  Title: {reg.title[:100]}...")
    print(f"  Articles found: {len(reg.articles)}")
    print(f"  Annexes found: {len(reg.annexes)}")

    # Determine output base dir: _temp/<slug>/
    if args.output_dir:
        output_dir = Path(args.output_dir)
    else:
        # Find project root (where _temp/ should live)
        # Walk up from script location to find kit root
        script_dir = Path(__file__).resolve().parent
        project_root = script_dir.parent.parent  # scripts/preprocessor/ → kit root
        output_dir = project_root / "_temp" / reg_slug / "chunks"

    # Write debug output to _temp/<slug>/ if requested
    if args.debug:
        temp_base = output_dir.parent
        temp_base.mkdir(parents=True, exist_ok=True)
        debug_path = temp_base / "debug_full_text.txt"
        debug_path.write_text(full_text)
        print(f"  Debug: full text written to {debug_path}")

    print(f"\nWriting chunks to: {output_dir}")
    write_chunks(reg, output_dir, src_id)

    # Summary stats
    if reg.articles:
        total_chars = sum(len(a.text) for a in reg.articles)
        avg_chars = total_chars // len(reg.articles)
        articles_with_refs = sum(1 for a in reg.articles if a.cross_refs)
        largest = max(reg.articles, key=lambda a: len(a.text))
        smallest = min(reg.articles, key=lambda a: len(a.text))
        print(f"\nSummary:")
        print(f"  Total article text: {total_chars:,} chars (~{total_chars // 4:,} tokens)")
        print(f"  Average per article: {avg_chars:,} chars (~{avg_chars // 4:,} tokens)")
        print(f"  Largest: Article {largest.article_num} ({len(largest.text):,} chars)")
        print(f"  Smallest: Article {smallest.article_num} ({len(smallest.text):,} chars)")
        print(f"  Articles with cross-refs: {articles_with_refs}/{len(reg.articles)}")

    print("\nDone.")


if __name__ == "__main__":
    main()
