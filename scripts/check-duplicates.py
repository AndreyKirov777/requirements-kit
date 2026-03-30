#!/usr/bin/env python3
"""
Check for duplicate artifact IDs and filename-ID mismatches.

Validates:
  1. Every artifact ID is unique across the entire vault
  2. The frontmatter 'id' matches the filename (e.g., FR-INGEST-001.md → id: FR-INGEST-001)

Usage:
    python scripts/check-duplicates.py [--path PATH]

Requires: pip install pyyaml
"""

import argparse
import re
import sys
from collections import defaultdict
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: Install dependencies first: pip install pyyaml")
    sys.exit(1)

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)

# Prefixes that follow the TYPE-DOMAIN-NNN pattern and should be checked
ARTIFACT_PREFIXES = {
    "FR", "NFR", "CON", "US", "EPIC", "ADR", "ARCH", "TEST", "TASK",
    "CR", "PERSONA", "ASSUM", "RISK", "REL", "JOURNEY", "UC",
    "CONTRACT", "DM", "VISION", "BRQ", "CTRL",
}

# Reference/meta prefixes — still checked for uniqueness, but exempt from
# filename matching (their filenames may follow different conventions)
META_PREFIXES = {"META", "GLOSS", "CODEMAP"}

# Folders to skip — contain templates, scripts, non-artifact docs
SKIP_FOLDERS = {"templates", "scripts", ".codex", "node_modules", ".git"}

# Well-known files that use a fixed filename different from their ID
# (e.g., PRODUCT-VISION.md is the canonical name for the single vision doc)
FILENAME_EXCEPTIONS = {"PRODUCT-VISION.md"}


def extract_frontmatter(filepath: Path) -> dict | None:
    """Extract YAML frontmatter from a markdown file."""
    try:
        text = filepath.read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError):
        return None
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None
    try:
        fm = yaml.safe_load(match.group(1))
        return fm if isinstance(fm, dict) else None
    except yaml.YAMLError:
        return None


def main():
    parser = argparse.ArgumentParser(description="Check for duplicate artifact IDs")
    parser.add_argument("--path", default=".", help="Root of requirements vault")
    args = parser.parse_args()

    root = Path(args.path)
    issues: list[str] = []

    # Collect all IDs → list of files that declare them
    id_to_files: dict[str, list[Path]] = defaultdict(list)

    for md_file in sorted(root.rglob("*.md")):
        # Skip non-artifact directories
        if any(part in SKIP_FOLDERS for part in md_file.parts):
            continue
        if md_file.name.startswith("README") or md_file.name == "CLAUDE.md":
            continue

        fm = extract_frontmatter(md_file)
        if fm is None or "id" not in fm:
            continue

        artifact_id: str = fm["id"]
        prefix = artifact_id.split("-")[0]

        # Only check known artifact and meta prefixes
        if prefix not in ARTIFACT_PREFIXES and prefix not in META_PREFIXES:
            continue

        id_to_files[artifact_id].append(md_file)

        # --- Check filename ↔ ID consistency (skip meta files) ---
        if prefix in ARTIFACT_PREFIXES:
            expected_filename = f"{artifact_id}.md"
            if md_file.name != expected_filename and md_file.name not in FILENAME_EXCEPTIONS:
                issues.append(
                    f"FILENAME MISMATCH: {md_file} has id '{artifact_id}' "
                    f"but filename should be '{expected_filename}'"
                )

    # --- Check for duplicate IDs ---
    for artifact_id, files in id_to_files.items():
        if len(files) > 1:
            locations = ", ".join(str(f) for f in files)
            issues.append(
                f"DUPLICATE ID: '{artifact_id}' found in {len(files)} files: {locations}"
            )

    # --- Report ---
    total_artifacts = len(id_to_files)

    if issues:
        print(f"\n{'='*60}")
        print(f"DUPLICATE / MISMATCH CHECK — {len(issues)} issue(s) found")
        print(f"{'='*60}\n")
        for issue in sorted(issues):
            print(f"  ✗ {issue}")
        print()
        sys.exit(1)
    else:
        print(f"\n✓ No duplicates or mismatches. Checked {total_artifacts} unique artifact IDs.")
        sys.exit(0)


if __name__ == "__main__":
    main()
