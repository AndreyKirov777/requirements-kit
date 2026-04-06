#!/usr/bin/env python3
"""
Promote — copy triaged artifacts from _temp to 01-product/.

By default copies only 'relevant' artifacts. Use --include-contextual
to also copy 'contextual' artifacts (definitions, scope, deadlines).

Renumbers artifacts sequentially within each type to eliminate gaps
from the batched extraction numbering.

Usage:
  python promote.py <triage-dir> <target-dir> [--include-contextual] [--dry-run] [--flat]

Examples:
  # Only relevant → 01-product (Obsidian folder names)
  python promote.py _temp/eu-2023-1542/triage 01-product

  # Relevant + contextual
  python promote.py _temp/eu-2023-1542/triage 01-product --include-contextual

  # Test export to arbitrary folder with short subfolder names
  python promote.py _temp/eu-2023-1542/triage _temp/eu-2023-1542/promoted --flat

  # Preview what would be copied
  python promote.py _temp/eu-2023-1542/triage 01-product --dry-run

Input:  _temp/<regulation>/triage/{brq,br,ctrl}/*.md
Output (default):  <target>/{business-requirements,business-rules,controls}/*.md
Output (--flat):   <target>/{brq,br,ctrl}/*.md
"""

import argparse
import json
import re
import shutil
import sys
from pathlib import Path

import yaml


# Map from artifact type to 01-product subfolder name (Obsidian convention)
TYPE_TO_FOLDER_LONG = {
    "brq": "business-requirements",
    "br": "business-rules",
    "ctrl": "controls",
}

# Short (flat) folder names — same as source triage structure
TYPE_TO_FOLDER_SHORT = {
    "brq": "brq",
    "br": "br",
    "ctrl": "ctrl",
}

# Map from artifact type to ID prefix
TYPE_TO_PREFIX = {
    "brq": "BRQ",
    "br": "BR",
    "ctrl": "CTRL",
}


def load_triaged_artifacts(triage_dir: Path, art_type: str, include_levels: set) -> list[dict]:
    """Load artifacts that match the desired relevance levels."""
    type_dir = triage_dir / art_type
    if not type_dir.exists():
        return []

    artifacts = []
    for f in sorted(type_dir.glob("*.md")):
        if f.name.startswith("_"):
            continue
        text = f.read_text()
        if not text.startswith("---"):
            continue
        parts = text.split("---", 2)
        if len(parts) < 3:
            continue
        try:
            fm = yaml.safe_load(parts[1].strip())
        except yaml.YAMLError:
            continue

        relevance = fm.get("relevance", "contextual")
        if relevance in include_levels:
            artifacts.append({
                "file": f.name,
                "path": f,
                "frontmatter": fm,
                "body": parts[2].strip(),
                "old_id": fm.get("id", ""),
            })

    return artifacts


def renumber_artifacts(artifacts: list[dict], art_type: str, domain: str = "BAT") -> list[dict]:
    """Assign sequential IDs to artifacts.

    New ID format: BRQ-BAT-001, BRQ-BAT-002, ...
    Returns artifacts with 'new_id' and 'new_file' fields added.
    """
    prefix = TYPE_TO_PREFIX[art_type]

    for i, art in enumerate(artifacts, 1):
        art["new_id"] = f"{prefix}-{domain}-{i:03d}"
        art["new_file"] = f"{art['new_id']}.md"

    return artifacts


def build_id_remap(all_artifacts: dict) -> dict:
    """Build a mapping from old IDs to new IDs across all types."""
    remap = {}
    for art_type, artifacts in all_artifacts.items():
        for art in artifacts:
            remap[art["old_id"]] = art["new_id"]
    return remap


def remap_references(text: str, remap: dict) -> str:
    """Replace old artifact IDs with new ones in text content."""
    for old_id, new_id in remap.items():
        # Replace in wiki-links: [[BRQ-BAT-051]] → [[BRQ-BAT-001]]
        text = text.replace(f"[[{old_id}]]", f"[[{new_id}]]")
        # Replace bare references
        text = text.replace(old_id, new_id)
    return text


def write_promoted_artifact(
    art: dict,
    target_dir: Path,
    art_type: str,
    remap: dict,
    folder_map: dict,
):
    """Write a single promoted artifact with new ID and remapped references."""
    fm = dict(art["frontmatter"])

    # Update ID
    fm["id"] = art["new_id"]

    # Remap derives_from references
    if "derives_from" in fm:
        new_derives = []
        for ref in fm["derives_from"]:
            clean = str(ref).strip("[]").strip()
            if clean in remap:
                new_derives.append(f"[[{remap[clean]}]]")
            else:
                new_derives.append(ref)
        fm["derives_from"] = new_derives

    # Remap source_ref if it points to a renamed artifact
    if "source_ref" in fm and fm["source_ref"] in remap:
        fm["source_ref"] = remap[fm["source_ref"]]

    # Build output
    yaml_str = yaml.dump(fm, default_flow_style=False, allow_unicode=True, sort_keys=False)
    body = remap_references(art["body"], remap)

    folder = target_dir / folder_map[art_type]
    folder.mkdir(parents=True, exist_ok=True)
    out_path = folder / art["new_file"]
    out_path.write_text(f"---\n{yaml_str}---\n\n{body}\n")

    return out_path


def main():
    parser = argparse.ArgumentParser(
        description="Promote triaged artifacts from _temp to 01-product."
    )
    parser.add_argument(
        "triage_dir",
        help="Path to triage directory with brq/, br/, ctrl/ subdirectories"
    )
    parser.add_argument(
        "target_dir",
        help="Target directory (e.g. 01-product)"
    )
    parser.add_argument(
        "--include-contextual",
        action="store_true",
        help="Also promote 'contextual' artifacts (default: only 'relevant')"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Preview what would be promoted without writing files"
    )
    parser.add_argument(
        "--flat",
        action="store_true",
        help="Use short subfolder names (brq/, br/, ctrl/) instead of Obsidian names"
    )
    parser.add_argument(
        "--domain",
        default="BAT",
        help="Domain prefix for IDs (default: BAT)"
    )
    args = parser.parse_args()

    triage_dir = Path(args.triage_dir)
    target_dir = Path(args.target_dir)
    folder_map = TYPE_TO_FOLDER_SHORT if args.flat else TYPE_TO_FOLDER_LONG

    include_levels = {"relevant"}
    if args.include_contextual:
        include_levels.add("contextual")

    level_label = " + ".join(sorted(include_levels))
    folder_style = "flat (brq/br/ctrl)" if args.flat else "obsidian (business-requirements/...)"
    print(f"Promoting: {level_label}")
    print(f"Source:    {triage_dir}")
    print(f"Target:    {target_dir}")
    print(f"Folders:   {folder_style}")
    if args.dry_run:
        print("Mode:      DRY RUN")

    # Load artifacts
    all_artifacts = {}
    for art_type in ("brq", "br", "ctrl"):
        arts = load_triaged_artifacts(triage_dir, art_type, include_levels)
        arts = renumber_artifacts(arts, art_type, args.domain)
        all_artifacts[art_type] = arts
        print(f"  {art_type.upper()}: {len(arts)} artifacts to promote")

    # Build ID remap
    remap = build_id_remap(all_artifacts)
    print(f"\nID remap entries: {len(remap)}")

    if args.dry_run:
        print(f"\n{'Old ID':<20} → {'New ID':<20} {'Relevance':<14}")
        print("-" * 58)
        for art_type in ("brq", "br", "ctrl"):
            for art in all_artifacts[art_type]:
                rel = art["frontmatter"].get("relevance", "?")
                print(f"  {art['old_id']:<18} → {art['new_id']:<18} {rel:<14}")
        print(f"\nTotal: {len(remap)} artifacts would be promoted.")
        print("Run without --dry-run to write files.")
        return

    # Write promoted artifacts
    promoted = []
    for art_type in ("brq", "br", "ctrl"):
        for art in all_artifacts[art_type]:
            out_path = write_promoted_artifact(art, target_dir, art_type, remap, folder_map)
            promoted.append({
                "old_id": art["old_id"],
                "new_id": art["new_id"],
                "type": art_type,
                "relevance": art["frontmatter"].get("relevance", "?"),
                "file": str(out_path),
            })

    # Write promote report
    report = {
        "include_levels": sorted(include_levels),
        "domain": args.domain,
        "counts": {t: len(a) for t, a in all_artifacts.items()},
        "total": len(promoted),
        "id_remap": remap,
        "promoted": promoted,
    }
    report_path = target_dir / "_promote-report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))

    # Summary
    total = sum(len(a) for a in all_artifacts.values())
    print(f"\nPromoted {total} artifacts:")
    for art_type in ("brq", "br", "ctrl"):
        count = len(all_artifacts[art_type])
        folder = folder_map[art_type]
        print(f"  {art_type.upper()}: {count} → {target_dir / folder}/")

    print(f"\nReport: {report_path}")
    print("Done.")


if __name__ == "__main__":
    main()
