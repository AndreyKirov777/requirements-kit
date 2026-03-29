#!/usr/bin/env python3
"""
Check for orphan artifacts: requirements without tests, tests without requirements,
tasks without requirements, and other missing links.

Usage:
    python scripts/check-orphans.py [--path PATH]

Requires: pip install pyyaml
"""

import argparse
import re
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: Install dependencies first: pip install pyyaml")
    sys.exit(1)

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")


def extract_frontmatter(filepath: Path) -> dict | None:
    text = filepath.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None
    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None


def extract_ids(value) -> list[str]:
    ids = []
    if isinstance(value, str):
        for m in WIKILINK_RE.finditer(value):
            ids.append(m.group(1))
    elif isinstance(value, list):
        for item in value:
            ids.extend(extract_ids(item))
    return ids


def main():
    parser = argparse.ArgumentParser(description="Check for orphan artifacts")
    parser.add_argument("--path", default=".", help="Root of requirements vault")
    parser.add_argument("--schema-dir", default=None, help="Path to schema directory (for consistency, not directly used)")
    args = parser.parse_args()

    root = Path(args.path)
    artifacts = {}
    issues = []

    # Collect all artifacts
    for md_file in sorted(root.rglob("*.md")):
        if "templates" in md_file.parts:
            continue
        fm = extract_frontmatter(md_file)
        if fm is None or "id" not in fm:
            continue
        aid = fm["id"]
        # Skip reference docs (META-, GLOSS-, CODEMAP-)
        if aid.startswith("META-") or aid.startswith("GLOSS-") or aid.startswith("CODEMAP-"):
            continue
        artifacts[aid] = {"fm": fm, "path": md_file}

    # Check requirements without tests
    for aid, info in artifacts.items():
        fm = info["fm"]
        prefix = aid.split("-")[0]

        if prefix in ("FR", "NFR"):
            verified_by = extract_ids(fm.get("verified_by", []))
            if not verified_by:
                issues.append(f"ORPHAN: {aid} has no verified_by (no tests linked)")
            else:
                for vid in verified_by:
                    if vid not in artifacts:
                        issues.append(f"BROKEN LINK: {aid} references {vid} in verified_by, but it does not exist")

            # Check if requirement has at least one task
            has_task = any(
                extract_ids(a["fm"].get("implements", "")) == [aid] or aid in extract_ids(a["fm"].get("implements", ""))
                for a in artifacts.values()
                if a["fm"].get("id", "").startswith("TASK")
            )
            status = fm.get("status", "")
            if status in ("approved", "in-implementation") and not has_task:
                issues.append(f"MISSING TASK: {aid} is '{status}' but has no TASK referencing it")

        # Check tests without requirements
        if prefix == "TEST":
            verifies = extract_ids(fm.get("verifies", []))
            if not verifies:
                issues.append(f"ORPHAN TEST: {aid} does not verify any requirement")
            else:
                for vid in verifies:
                    if vid not in artifacts:
                        issues.append(f"BROKEN LINK: {aid} references {vid} in verifies, but it does not exist")

        # Check tasks without valid requirement
        if prefix == "TASK":
            implements = extract_ids(fm.get("implements", ""))
            if not implements:
                issues.append(f"ORPHAN TASK: {aid} does not implement any requirement")
            else:
                for iid in implements:
                    if iid not in artifacts:
                        issues.append(f"BROKEN LINK: {aid} references {iid} in implements, but it does not exist")

        # Check for broken depends_on links
        for dep in extract_ids(fm.get("depends_on", [])):
            if dep not in artifacts:
                issues.append(f"BROKEN LINK: {aid} depends_on {dep}, but it does not exist")

        # Check for broken related_adrs links
        for adr in extract_ids(fm.get("related_adrs", [])):
            if adr not in artifacts:
                issues.append(f"BROKEN LINK: {aid} references ADR {adr}, but it does not exist")

    # Report
    if issues:
        print(f"\n{'='*60}")
        print(f"ORPHAN CHECK — {len(issues)} issue(s) found")
        print(f"{'='*60}\n")
        for issue in sorted(issues):
            print(f"  ✗ {issue}")
        print()
        sys.exit(1)
    else:
        print(f"\n✓ No orphans or broken links found. Checked {len(artifacts)} artifacts.")
        sys.exit(0)


if __name__ == "__main__":
    main()
