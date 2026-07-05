#!/usr/bin/env python3
"""
check-updated-dates.py — warn when an artifact's `updated:` field disagrees with
the date of the file's last git commit. A hand-maintained `updated:` drifts from
reality; this surfaces the mismatch as a warning (does not fail CI by default).

Usage:
    python scripts/check-updated-dates.py [--path PATH] [--strict]

--strict exits non-zero if any mismatch is found (opt-in for stricter CI).

Requires: pip install pyyaml ; a git repository.
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

try:
    import yaml
except ImportError:
    print("ERROR: Install dependencies first: pip install pyyaml")
    sys.exit(1)

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)


def extract_updated(path: Path) -> str | None:
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return None
    val = fm.get("updated")
    return str(val) if val is not None else None


def git_last_date(path: Path, root: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", "log", "-1", "--format=%ad", "--date=short", "--", str(path)],
            cwd=root, capture_output=True, text=True, check=False,
        )
    except FileNotFoundError:
        return None
    if out.returncode != 0:
        return None
    return out.stdout.strip() or None


def main():
    parser = argparse.ArgumentParser(description="Warn on stale `updated:` dates")
    parser.add_argument("--path", default=".", help="Root of requirements vault")
    parser.add_argument("--strict", action="store_true", help="Exit non-zero on any mismatch")
    args = parser.parse_args()

    root = Path(args.path)
    if subprocess.run(["git", "rev-parse", "--is-inside-work-tree"], cwd=root,
                      capture_output=True).returncode != 0:
        print("ℹ git not available — skipping updated-date check.")
        sys.exit(0)

    skip = {"templates", "scripts", "_examples"}
    mismatches = []
    for md in sorted(root.rglob("*.md")):
        if any(part in skip for part in md.parts):
            continue
        updated = extract_updated(md)
        if not updated or not re.match(r"^\d{4}-\d{2}-\d{2}$", updated):
            continue
        git_date = git_last_date(md, root)
        if git_date and git_date != updated:
            mismatches.append((md, updated, git_date))

    if mismatches:
        print(f"\n{len(mismatches)} file(s) where `updated:` differs from last git commit date:\n")
        for md, updated, git_date in mismatches:
            print(f"  ⚠ {md}: updated={updated} but last commit={git_date}")
        print("\n(Uncommitted local edits can cause benign mismatches.)")
        sys.exit(1 if args.strict else 0)

    print("✓ All `updated:` dates match git history.")
    sys.exit(0)


if __name__ == "__main__":
    main()
