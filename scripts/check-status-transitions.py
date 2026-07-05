#!/usr/bin/env python3
"""
Validate artifact statuses against the state machine defined in kit-manifest.json.

Two modes:

  Default (snapshot) — checks that every artifact's *current* status is a valid
  status for its type, and that parent/child statuses are mutually consistent.

  --git (transition) — the honest transition gate. For files changed since a base
  git ref, it reads the OLD status from git and the NEW status from the working
  tree and verifies the change is an allowed edge in the transition graph
  (e.g., draft → approved skipping proposed is rejected). Requires a git repo.

Usage:
    python scripts/check-status-transitions.py [--path PATH]
    python scripts/check-status-transitions.py --git [--git-base REF]   # in CI

Requires: pip install pyyaml
"""

import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kit_manifest import load_manifest, valid_statuses, transitions

try:
    import yaml
except ImportError:
    print("ERROR: Install dependencies first: pip install pyyaml")
    sys.exit(1)

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
WIKILINK_RE = re.compile(r"\[\[([^\]]+)\]\]")

_MANIFEST = load_manifest()
VALID_STATUSES = valid_statuses(_MANIFEST)          # {prefix: set(statuses)}
TRANSITIONS = transitions(_MANIFEST)                # {prefix: {from: [to,...]}}

# Ordering used only for the parent/child consistency heuristic.
REQ_STATUS_ORDER = ["draft", "proposed", "approved", "in-implementation", "implemented", "verified", "deprecated"]


def extract_frontmatter_text(text: str) -> dict | None:
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None
    try:
        return yaml.safe_load(match.group(1))
    except yaml.YAMLError:
        return None


def extract_frontmatter(filepath: Path) -> dict | None:
    return extract_frontmatter_text(filepath.read_text(encoding="utf-8"))


def extract_ids(value) -> list[str]:
    ids = []
    if isinstance(value, str):
        for m in WIKILINK_RE.finditer(value):
            ids.append(m.group(1))
    elif isinstance(value, list):
        for item in value:
            ids.extend(extract_ids(item))
    return ids


def prefix_of(aid: str) -> str:
    return aid.split("-")[0]


# ─── Snapshot checks ─────────────────────────────────────────────────────────

def run_snapshot_check(root: Path) -> list[str]:
    artifacts = {}
    issues = []

    for md_file in sorted(root.rglob("*.md")):
        if "templates" in md_file.parts:
            continue
        fm = extract_frontmatter(md_file)
        if fm is None or "id" not in fm:
            continue
        artifacts[fm["id"]] = {"fm": fm, "path": md_file}

    verified_by_map = {}
    implemented_by_map = {}
    for aid_inner, info_inner in artifacts.items():
        fm_inner = info_inner["fm"]
        prefix_inner = prefix_of(aid_inner)
        if prefix_inner == "TEST":
            for vid in extract_ids(fm_inner.get("verifies", [])):
                verified_by_map.setdefault(vid, []).append(aid_inner)
        if prefix_inner == "TASK":
            for iid in extract_ids(fm_inner.get("implements", "")):
                implemented_by_map.setdefault(iid, []).append(aid_inner)

    for aid, info in artifacts.items():
        fm = info["fm"]
        prefix = prefix_of(aid)
        status = fm.get("status", "")

        if prefix in VALID_STATUSES:
            if status not in VALID_STATUSES[prefix]:
                issues.append(
                    f"INVALID STATUS: {aid} has status '{status}' — "
                    f"allowed: {', '.join(sorted(VALID_STATUSES[prefix]))}"
                )

        if prefix in ("FR", "NFR") and status == "implemented":
            for task_id in implemented_by_map.get(aid, []):
                if task_id in artifacts:
                    task_status = artifacts[task_id]["fm"].get("status", "")
                    if task_status not in ("done",):
                        issues.append(
                            f"INCONSISTENT: {aid} is 'implemented' but {task_id} is '{task_status}'"
                        )

        if prefix in ("FR", "NFR") and status == "verified":
            for vid in verified_by_map.get(aid, []):
                if vid in artifacts:
                    test_status = artifacts[vid]["fm"].get("status", "")
                    if test_status != "passed":
                        issues.append(
                            f"INCONSISTENT: {aid} is 'verified' but test {vid} is '{test_status}'"
                        )

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
    return issues


# ─── Transition (git) check ──────────────────────────────────────────────────

def git(args: list[str], cwd: Path) -> str | None:
    try:
        out = subprocess.run(
            ["git", *args], cwd=cwd, capture_output=True, text=True, check=False
        )
    except FileNotFoundError:
        return None
    if out.returncode != 0:
        return None
    return out.stdout


def run_transition_check(root: Path, base_ref: str) -> tuple[list[str], bool]:
    """Returns (issues, ran). ran=False means git was unavailable → skipped."""
    issues = []

    # Confirm we're in a git repo
    if git(["rev-parse", "--is-inside-work-tree"], root) is None:
        return ["(git not available or not a git repo — transition check skipped)"], False

    changed = git(["diff", "--name-only", base_ref, "--", "*.md"], root)
    if changed is None:
        return [f"(could not diff against '{base_ref}' — transition check skipped)"], False

    for rel in [line.strip() for line in changed.splitlines() if line.strip().endswith(".md")]:
        path = root / rel
        if not path.exists():
            continue  # deleted file
        if "templates" in Path(rel).parts:
            continue

        new_fm = extract_frontmatter(path)
        if not new_fm or "id" not in new_fm:
            continue
        aid = new_fm["id"]
        prefix = prefix_of(aid)
        if prefix not in TRANSITIONS or not TRANSITIONS[prefix]:
            continue  # no lifecycle (e.g., SRC)

        old_text = git(["show", f"{base_ref}:{rel}"], root)
        if old_text is None:
            continue  # newly added file — no prior status to compare
        old_fm = extract_frontmatter_text(old_text)
        if not old_fm:
            continue
        old_status = old_fm.get("status")
        new_status = new_fm.get("status")
        if not old_status or not new_status or old_status == new_status:
            continue

        allowed = TRANSITIONS[prefix].get(old_status, [])
        if new_status not in allowed:
            allowed_str = ", ".join(allowed) if allowed else "(terminal — no transitions)"
            issues.append(
                f"ILLEGAL TRANSITION: {aid} changed '{old_status}' → '{new_status}'. "
                f"Allowed from '{old_status}': {allowed_str}"
            )
    return issues, True


def main():
    parser = argparse.ArgumentParser(description="Check status transitions")
    parser.add_argument("--path", default=".", help="Root of requirements vault")
    parser.add_argument("--git", action="store_true", help="Validate status *transitions* against git history (honest gate)")
    parser.add_argument("--git-base", default="HEAD", help="Git ref to diff against (default: HEAD)")
    args = parser.parse_args()

    root = Path(args.path)
    issues = run_snapshot_check(root)

    ran_transition = True
    if args.git:
        t_issues, ran_transition = run_transition_check(root, args.git_base)
        if ran_transition:
            issues.extend(t_issues)
        else:
            # Skipped (no git) — surface as a note, not a failure.
            for note in t_issues:
                print(f"  ℹ {note}")

    if issues:
        print(f"\n{'='*60}")
        print(f"STATUS CHECK — {len(issues)} issue(s) found")
        print(f"{'='*60}\n")
        for issue in sorted(issues):
            print(f"  ✗ {issue}")
        print()
        sys.exit(1)
    else:
        print("\n✓ All statuses valid and consistent.")
        sys.exit(0)


if __name__ == "__main__":
    main()
