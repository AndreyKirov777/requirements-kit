#!/usr/bin/env python3
"""
Validate that artifact statuses are consistent with the defined state machine.
Checks current status validity and cross-references parent/child status consistency.

Usage:
    python scripts/check-status-transitions.py [--path PATH]

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

# Valid statuses per artifact type prefix
VALID_STATUSES = {
    "FR": {"draft", "proposed", "approved", "in-implementation", "implemented", "verified", "deprecated"},
    "NFR": {"draft", "proposed", "approved", "in-implementation", "implemented", "verified", "deprecated"},
    "CON": {"draft", "proposed", "approved", "deprecated"},
    "US": {"draft", "proposed", "approved", "in-implementation", "implemented", "verified", "deprecated"},
    "EPIC": {"draft", "proposed", "approved", "in-progress", "completed", "deprecated"},
    "ADR": {"proposed", "accepted", "rejected", "superseded", "deprecated"},
    "TASK": {"backlog", "ready", "in-progress", "done", "blocked"},
    "TEST": {"draft", "ready", "passed", "failed"},
    "CR": {"proposed", "approved", "applied", "rejected"},
    "PERSONA": {"draft", "proposed", "approved", "deprecated"},
    "ASSUM": {"unvalidated", "validating", "validated", "invalidated", "deprecated"},
    "JOURNEY": {"draft", "proposed", "approved", "deprecated"},
    "RISK": {"open", "mitigating", "mitigated", "accepted", "closed"},
    "REL": {"planned", "ready", "released", "rolled-back"},
    "UC": {"draft", "proposed", "approved", "deprecated"},
    "CONTRACT": {"draft", "proposed", "approved", "deprecated"},
    "DM": {"draft", "proposed", "approved", "deprecated"},
    "VISION": {"draft", "proposed", "approved", "superseded", "deprecated"},
    "BRQ": {"identified", "analyzed", "approved", "allocated", "covered", "deprecated"},
    "BR": {"draft", "proposed", "approved", "deprecated"},
    "CTRL": {"identified", "defined", "allocated", "implemented", "verified", "audited", "deprecated"},
}

# Status ordering for consistency checks
REQ_STATUS_ORDER = ["draft", "proposed", "approved", "in-implementation", "implemented", "verified", "deprecated"]


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
    parser = argparse.ArgumentParser(description="Check status transitions")
    parser.add_argument("--path", default=".", help="Root of requirements vault")
    args = parser.parse_args()

    root = Path(args.path)
    artifacts = {}
    issues = []

    for md_file in sorted(root.rglob("*.md")):
        if "templates" in md_file.parts:
            continue
        fm = extract_frontmatter(md_file)
        if fm is None or "id" not in fm:
            continue
        artifacts[fm["id"]] = {"fm": fm, "path": md_file}

    # Build computed reverse-link maps (v0.5.0: "link up only" principle).
    # Test.verifies → requirement, Task.implements → requirement
    verified_by_map = {}  # req_id -> [test_ids]
    implemented_by_map = {}  # req_id -> [task_ids]
    for aid_inner, info_inner in artifacts.items():
        fm_inner = info_inner["fm"]
        prefix_inner = aid_inner.split("-")[0]
        if prefix_inner == "TEST":
            for vid in extract_ids(fm_inner.get("verifies", [])):
                verified_by_map.setdefault(vid, []).append(aid_inner)
        if prefix_inner == "TASK":
            for iid in extract_ids(fm_inner.get("implements", "")):
                implemented_by_map.setdefault(iid, []).append(aid_inner)

    for aid, info in artifacts.items():
        fm = info["fm"]
        prefix = aid.split("-")[0]
        status = fm.get("status", "")

        # Check valid status
        if prefix in VALID_STATUSES:
            if status not in VALID_STATUSES[prefix]:
                issues.append(
                    f"INVALID STATUS: {aid} has status '{status}' — "
                    f"allowed: {', '.join(sorted(VALID_STATUSES[prefix]))}"
                )

        # Cross-check: requirement is "implemented" but has tasks still "in-progress"
        if prefix in ("FR", "NFR") and status == "implemented":
            for task_id in implemented_by_map.get(aid, []):
                if task_id in artifacts:
                    task_status = artifacts[task_id]["fm"].get("status", "")
                    if task_status not in ("done",):
                        issues.append(
                            f"INCONSISTENT: {aid} is 'implemented' but {task_id} is '{task_status}'"
                        )

        # Cross-check: requirement is "verified" but tests are not "passed"
        # (computed from Test.verifies instead of deprecated FR.verified_by)
        if prefix in ("FR", "NFR") and status == "verified":
            for vid in verified_by_map.get(aid, []):
                if vid in artifacts:
                    test_status = artifacts[vid]["fm"].get("status", "")
                    if test_status != "passed":
                        issues.append(
                            f"INCONSISTENT: {aid} is 'verified' but test {vid} is '{test_status}'"
                        )

        # Cross-check: task is "ready" but parent requirement is not "approved" or beyond
        if prefix == "TASK":
            implements = extract_ids(fm.get("implements", ""))
            for req_id in implements:
                if req_id in artifacts:
                    req_status = artifacts[req_id]["fm"].get("status", "")
                    approved_idx = REQ_STATUS_ORDER.index("approved") if "approved" in REQ_STATUS_ORDER else -1
                    req_idx = REQ_STATUS_ORDER.index(req_status) if req_status in REQ_STATUS_ORDER else -1
                    if req_idx < approved_idx and status in ("ready", "in-progress"):
                        issues.append(
                            f"PREMATURE: {aid} is '{status}' but parent {req_id} is only '{req_status}'"
                        )

    if issues:
        print(f"\n{'='*60}")
        print(f"STATUS CHECK — {len(issues)} issue(s) found")
        print(f"{'='*60}\n")
        for issue in sorted(issues):
            print(f"  ✗ {issue}")
        print()
        sys.exit(1)
    else:
        print(f"\n✓ All statuses valid and consistent. Checked {len(artifacts)} artifacts.")
        sys.exit(0)


if __name__ == "__main__":
    main()
