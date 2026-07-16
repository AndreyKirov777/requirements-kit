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

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kit_manifest import (
    load_manifest,
    prefix_for_id,
    resolve_project_config,
    active_profile,
    enabled_types,
    out_of_profile_hint,
    ProfileConfigError,
)

try:
    import yaml
except ImportError:
    print("ERROR: Install dependencies first: pip install pyyaml")
    sys.exit(1)

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")

_MANIFEST = load_manifest()

# Profile-aware "what counts as a requirement" (spec docs/profiles-spec.md
# §8.2). Profile S has no FR/NFR — the User Story is the requirement artifact
# that needs a verifying TEST and (once approved) an implementing TASK.
# Every profile's TASK is checked against BOTH up-link fields (implements and
# part_of_story) unioned together — this keeps the checker correct during an
# S→M upgrade, when old and new TASKs may use either field.
_REQUIREMENT_PREFIXES = {
    "S": ("US",),
}
_DEFAULT_REQUIREMENT_PREFIXES = ("FR", "NFR")


def requirement_prefixes(profile: str | None) -> tuple:
    return _REQUIREMENT_PREFIXES.get(profile, _DEFAULT_REQUIREMENT_PREFIXES)


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

    project_config = resolve_project_config(root)
    try:
        profile = active_profile(project_config, _MANIFEST)
        enabled = enabled_types(project_config, _MANIFEST)
    except ProfileConfigError as e:
        print(f"ERROR: invalid project-config.json — {e}")
        sys.exit(1)

    req_prefixes = requirement_prefixes(profile)

    artifacts = {}
    issues = []
    profile_warnings = []

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

        if enabled is not None:
            prefix = prefix_for_id(aid, _MANIFEST)
            if prefix and prefix not in enabled:
                hint = out_of_profile_hint(prefix, _MANIFEST)
                profile_warnings.append(f"{aid} ({md_file}) is type {prefix}, outside profile {profile} — {hint}")

    # Build computed reverse-link maps (v0.5.0: "link up only" principle).
    # Test.verifies → requirement. Task → requirement: implements and
    # part_of_story are unioned so the checker stays correct whether a TASK
    # links via FR/NFR (implements) or via US (part_of_story, profile S) —
    # and during an S→M upgrade, where both styles can coexist.
    verified_by_map = {}  # req_id -> [test_ids]
    implemented_by_map = {}  # req_id -> [task_ids]
    for aid_inner, info_inner in artifacts.items():
        fm_inner = info_inner["fm"]
        prefix_inner = prefix_for_id(aid_inner, _MANIFEST) or aid_inner.split("-")[0]
        if prefix_inner == "TEST":
            for vid in extract_ids(fm_inner.get("verifies", [])):
                verified_by_map.setdefault(vid, []).append(aid_inner)
        if prefix_inner == "TASK":
            targets = extract_ids(fm_inner.get("implements", "")) + extract_ids(fm_inner.get("part_of_story", ""))
            for iid in targets:
                implemented_by_map.setdefault(iid, []).append(aid_inner)

    # Check requirements without tests (computed from Test.verifies)
    for aid, info in artifacts.items():
        fm = info["fm"]
        prefix = prefix_for_id(aid, _MANIFEST) or aid.split("-")[0]

        if prefix in req_prefixes:
            tests = verified_by_map.get(aid, [])
            if not tests:
                issues.append(f"ORPHAN: {aid} has no tests verifying it")

            # Check if requirement has at least one task (computed from
            # Task.implements / Task.part_of_story, unioned above)
            tasks = implemented_by_map.get(aid, [])
            status = fm.get("status", "")
            if status in ("approved", "in-implementation") and not tasks:
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

        # Check tasks without a valid up-link (implements OR part_of_story)
        if prefix == "TASK":
            implements = extract_ids(fm.get("implements", ""))
            part_of_story = extract_ids(fm.get("part_of_story", ""))
            targets = implements + part_of_story
            if not targets:
                issues.append(f"ORPHAN TASK: {aid} does not implement any requirement (no implements or part_of_story)")
            else:
                for iid in targets:
                    if iid not in artifacts:
                        field = "implements" if iid in implements else "part_of_story"
                        issues.append(f"BROKEN LINK: {aid} references {iid} in {field}, but it does not exist")

        # Check for broken depends_on links
        for dep in extract_ids(fm.get("depends_on", [])):
            if dep not in artifacts:
                issues.append(f"BROKEN LINK: {aid} depends_on {dep}, but it does not exist")

    # Report profile warnings first (informational — never affect exit code)
    if profile_warnings:
        print(f"\n{'-'*60}")
        print(f"PROFILE WARNINGS — {len(profile_warnings)} artifact(s) outside profile '{profile}'")
        print(f"{'-'*60}\n")
        for warn in sorted(profile_warnings):
            print(f"  ⚠ {warn}")
        print()

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
