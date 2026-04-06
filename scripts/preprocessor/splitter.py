#!/usr/bin/env python3
"""
Splitter — parse agent extraction output into individual artifact files.

Reads pack-NNN-output.md files from the extraction/ directory,
splits by ---FILE--- delimiter, validates YAML frontmatter,
and writes individual .md files to _temp/<regulation>/artifacts/{brq,br,ctrl}/.

Usage:
  python splitter.py <extraction-dir> [--output-dir artifacts/]

Input:  _temp/<regulation>/extraction/pack-NNN-output.md
Output: _temp/<regulation>/artifacts/
          brq/BRQ-BAT-001.md
          br/BR-BAT-001.md
          ctrl/CTRL-BAT-001.md
          _report.json  (summary + any parse errors)
"""

import argparse
import json
import re
import sys
from pathlib import Path

import yaml


# ---------------------------------------------------------------------------
# Parse extraction output
# ---------------------------------------------------------------------------

def split_raw_output(text: str) -> list[str]:
    """Split agent output into individual artifact blocks by ---FILE--- delimiter."""
    # Normalize delimiter variants agents might produce
    text = re.sub(r"^-{3,}\s*FILE\s*-{3,}\s*$", "---FILE---", text, flags=re.MULTILINE)

    blocks = text.split("---FILE---")

    # Clean and filter empty blocks
    result = []
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        # Skip comment-only blocks (no BRQ/BR/CTRL extracted)
        if block.startswith("<!--") and block.endswith("-->"):
            continue
        result.append(block)

    return result


def parse_artifact(block: str) -> dict:
    """Parse a single artifact block into frontmatter + body.

    Returns dict with keys: id, type, frontmatter (dict), body (str), raw (str), errors (list).
    """
    errors = []

    # Extract YAML frontmatter
    if not block.startswith("---"):
        return {"id": None, "type": None, "raw": block, "errors": ["No YAML frontmatter found"]}

    parts = block.split("---", 2)
    if len(parts) < 3:
        return {"id": None, "type": None, "raw": block, "errors": ["Malformed frontmatter delimiters"]}

    yaml_str = parts[1].strip()
    body = parts[2].strip()

    # Parse YAML
    try:
        fm = yaml.safe_load(yaml_str)
    except yaml.YAMLError as e:
        return {"id": None, "type": None, "raw": block, "errors": [f"YAML parse error: {e}"]}

    if not isinstance(fm, dict):
        return {"id": None, "type": None, "raw": block, "errors": ["Frontmatter is not a dict"]}

    # Extract and validate ID
    art_id = fm.get("id", "")
    if not art_id:
        errors.append("Missing 'id' field")
        return {"id": None, "type": None, "frontmatter": fm, "body": body, "raw": block, "errors": errors}

    # Clean ID — agents sometimes wrap in extra quotes
    art_id = str(art_id).strip('"').strip("'")
    fm["id"] = art_id

    # Determine artifact type from ID prefix
    art_type = None
    if art_id.startswith("BRQ-"):
        art_type = "brq"
    elif art_id.startswith("BR-"):
        art_type = "br"
    elif art_id.startswith("CTRL-"):
        art_type = "ctrl"
    else:
        errors.append(f"Unknown artifact type in ID: {art_id}")

    # Validate required fields per type
    required_common = ["id", "title", "status", "owner", "domain", "updated"]
    required_by_type = {
        "brq": required_common + ["source_type", "priority"],
        "br": required_common + ["classification", "derives_from", "priority"],
        "ctrl": required_common + ["derives_from", "verification_method", "priority"],
    }

    if art_type and art_type in required_by_type:
        for field in required_by_type[art_type]:
            if field not in fm or fm[field] is None:
                errors.append(f"Missing required field: {field}")

    # Clean null values — remove fields that are null (agent sometimes outputs null)
    fm = {k: v for k, v in fm.items() if v is not None}

    # Auto-fix common agent mistakes
    # 1. Empty string compliance_deadline — remove it (schema expects date or absent)
    if "compliance_deadline" in fm and (fm["compliance_deadline"] == "" or fm["compliance_deadline"] is None):
        del fm["compliance_deadline"]

    # 2. Missing source_type on BRQ from regulation — default to "regulation"
    if art_type == "brq" and "source_type" not in fm:
        fm["source_type"] = "regulation"

    # 3. Missing classification on BR from regulation — default to "regulatory"
    if art_type == "br" and "classification" not in fm:
        fm["classification"] = "regulatory"

    # 4. Missing derives_from on BR/CTRL — set empty list (will need manual review)
    if art_type in ("br", "ctrl") and "derives_from" not in fm:
        fm["derives_from"] = []
        errors.append("Auto-fixed: derives_from set to empty list — needs manual review")

    # 5. BR status "identified" → "draft" (agent used BRQ vocabulary)
    if art_type == "br" and fm.get("status") == "identified":
        fm["status"] = "draft"

    # 6. CTRL verification_method "documentation" → "inspection" (closest match)
    if art_type == "ctrl" and fm.get("verification_method") == "documentation":
        fm["verification_method"] = "inspection"
        errors.append("Auto-fixed: verification_method 'documentation' → 'inspection'")

    return {
        "id": art_id,
        "type": art_type,
        "frontmatter": fm,
        "body": body,
        "raw": block,
        "errors": errors,
    }


def artifact_to_markdown(artifact: dict) -> str:
    """Reconstruct a clean Markdown file from parsed artifact."""
    fm = artifact["frontmatter"]
    body = artifact["body"]

    # Serialize YAML frontmatter
    yaml_str = yaml.dump(fm, default_flow_style=False, allow_unicode=True, sort_keys=False)

    return f"---\n{yaml_str}---\n\n{body}\n"


# ---------------------------------------------------------------------------
# Process all extraction files
# ---------------------------------------------------------------------------

def process_extraction_dir(extraction_dir: Path) -> dict:
    """Process all pack-NNN-output.md files in extraction directory.

    Returns dict with artifacts list and errors list.
    """
    output_files = sorted(extraction_dir.glob("pack-*-output.md"))
    if not output_files:
        print(f"Error: no pack-*-output.md files in {extraction_dir}", file=sys.stderr)
        sys.exit(1)

    all_artifacts = []
    all_errors = []
    seen_ids = set()

    for f in output_files:
        print(f"  Processing: {f.name}")
        text = f.read_text()
        blocks = split_raw_output(text)
        print(f"    Blocks found: {len(blocks)}")

        for i, block in enumerate(blocks):
            artifact = parse_artifact(block)
            artifact["source_file"] = f.name
            artifact["block_index"] = i

            if artifact["errors"]:
                for err in artifact["errors"]:
                    all_errors.append({
                        "file": f.name,
                        "block": i,
                        "id": artifact.get("id"),
                        "error": err,
                    })

            if artifact["id"]:
                if artifact["id"] in seen_ids:
                    all_errors.append({
                        "file": f.name,
                        "block": i,
                        "id": artifact["id"],
                        "error": f"Duplicate ID: {artifact['id']}",
                    })
                else:
                    seen_ids.add(artifact["id"])
                    all_artifacts.append(artifact)

    return {
        "artifacts": all_artifacts,
        "errors": all_errors,
    }


# ---------------------------------------------------------------------------
# Write artifacts
# ---------------------------------------------------------------------------

def write_artifacts(artifacts: list[dict], errors: list[dict], output_dir: Path):
    """Write individual artifact files organized by type."""

    type_dirs = {
        "brq": output_dir / "brq",
        "br": output_dir / "br",
        "ctrl": output_dir / "ctrl",
    }
    for d in type_dirs.values():
        d.mkdir(parents=True, exist_ok=True)

    counts = {"brq": 0, "br": 0, "ctrl": 0, "skipped": 0}

    for artifact in artifacts:
        art_type = artifact.get("type")
        art_id = artifact.get("id")

        if not art_type or art_type not in type_dirs:
            counts["skipped"] += 1
            continue

        # Write file
        filename = f"{art_id}.md"
        filepath = type_dirs[art_type] / filename
        filepath.write_text(artifact_to_markdown(artifact))
        counts[art_type] += 1

    # Write report
    report = {
        "total_artifacts": sum(counts[t] for t in ("brq", "br", "ctrl")),
        "brq": counts["brq"],
        "br": counts["br"],
        "ctrl": counts["ctrl"],
        "skipped": counts["skipped"],
        "errors": len(errors),
        "error_details": errors,
    }
    report_path = output_dir / "_report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))

    return report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Split agent extraction output into individual artifact files."
    )
    parser.add_argument(
        "extraction_dir",
        help="Path to extraction directory with pack-NNN-output.md files"
    )
    parser.add_argument(
        "--output-dir", "-o",
        default=None,
        help="Output directory (default: sibling 'artifacts/' next to extraction/)"
    )
    args = parser.parse_args()

    extraction_dir = Path(args.extraction_dir)
    print(f"Reading extraction output from: {extraction_dir}")
    result = process_extraction_dir(extraction_dir)

    artifacts = result["artifacts"]
    errors = result["errors"]
    print(f"\n  Total artifacts parsed: {len(artifacts)}")
    print(f"  Parse errors: {len(errors)}")

    output_dir = Path(args.output_dir) if args.output_dir else extraction_dir.parent / "artifacts"
    print(f"\nWriting artifacts to: {output_dir}")
    report = write_artifacts(artifacts, errors, output_dir)

    print(f"\nResults:")
    print(f"  BRQ: {report['brq']}")
    print(f"  BR:  {report['br']}")
    print(f"  CTRL: {report['ctrl']}")
    print(f"  Skipped: {report['skipped']}")
    if report["errors"]:
        print(f"\n  ⚠ {report['errors']} errors — see {output_dir}/_report.json")

    print("\nDone.")


if __name__ == "__main__":
    main()
