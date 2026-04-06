#!/usr/bin/env python3
"""
Triage Apply — collect triage agent output and apply relevance to all artifacts.

Reads triage-pack-NNN-output.md files, parses JSON classifications,
propagates relevance from BRQ to BR/CTRL via derives_from links,
and writes updated artifacts with relevance/relevance_rationale fields.

Usage:
  python triage_apply.py <artifacts-dir> <triage-packs-dir>

Input:  _temp/<regulation>/triage/packs/triage-pack-NNN-output.md
        _temp/<regulation>/artifacts/{brq,br,ctrl}/
Output: _temp/<regulation>/triage/{brq,br,ctrl}/  (updated copies)
        _temp/<regulation>/triage/triage-report.json
"""

import json
import re
import sys
from pathlib import Path

import yaml


def parse_triage_outputs(packs_dir: Path) -> tuple[dict, list]:
    """Parse all triage-pack-NNN-output.md files into a classification map."""
    output_files = sorted(packs_dir.glob("triage-pack-*-output.md"))
    if not output_files:
        print(f"Error: no triage-pack-*-output.md files in {packs_dir}", file=sys.stderr)
        sys.exit(1)

    triage_map = {}
    errors = []

    for f in output_files:
        for line_num, line in enumerate(f.read_text().strip().splitlines(), 1):
            line = line.strip()
            if not line or line.startswith("#") or line.startswith("```"):
                continue
            try:
                obj = json.loads(line)
                if "id" in obj and "relevance" in obj:
                    if obj["relevance"] not in ("relevant", "contextual", "out-of-scope"):
                        errors.append(f"{f.name}:{line_num}: invalid relevance '{obj['relevance']}' for {obj['id']}")
                        obj["relevance"] = "contextual"
                    triage_map[obj["id"]] = {
                        "relevance": obj["relevance"],
                        "rationale": obj.get("rationale", ""),
                    }
                else:
                    errors.append(f"{f.name}:{line_num}: missing id/relevance")
            except json.JSONDecodeError as e:
                errors.append(f"{f.name}:{line_num}: JSON error: {e}")

    return triage_map, errors


def load_artifacts(artifacts_dir: Path, art_type: str) -> list[dict]:
    """Load all artifacts of given type."""
    type_dir = artifacts_dir / art_type
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

        artifacts.append({
            "file": f.name,
            "frontmatter": fm,
            "body": parts[2].strip(),
        })
    return artifacts


def propagate_to_children(triage_map: dict, artifacts: list[dict]) -> dict:
    """Propagate BRQ relevance to BR/CTRL via derives_from."""
    relevance_rank = {"relevant": 3, "contextual": 2, "out-of-scope": 1}
    child_map = {}

    for art in artifacts:
        fm = art["frontmatter"]
        art_id = fm.get("id", "")
        derives_from = fm.get("derives_from", [])

        parent_ids = []
        for ref in derives_from:
            clean = str(ref).strip("[]").strip()
            if clean.startswith("BRQ-"):
                parent_ids.append(clean)

        best_rel = "out-of-scope"
        best_rationale = "No parent BRQ found"

        for pid in parent_ids:
            if pid in triage_map:
                prel = triage_map[pid]["relevance"]
                if relevance_rank.get(prel, 0) > relevance_rank.get(best_rel, 0):
                    best_rel = prel
                    best_rationale = f"Inherited from {pid}: {triage_map[pid].get('rationale', '')}"

        child_map[art_id] = {"relevance": best_rel, "rationale": best_rationale}

    return child_map


def write_updated_artifacts(
    artifacts: list[dict],
    relevance_map: dict,
    source_dir: Path,
    output_dir: Path,
    art_type: str,
) -> dict:
    """Write artifacts with relevance fields added."""
    type_out = output_dir / art_type
    type_out.mkdir(parents=True, exist_ok=True)

    stats = {"relevant": 0, "contextual": 0, "out-of-scope": 0}

    for art in artifacts:
        art_id = art["frontmatter"].get("id", "")
        if art_id in relevance_map:
            rel = relevance_map[art_id]["relevance"]
            rationale = relevance_map[art_id]["rationale"]
        else:
            rel = "contextual"
            rationale = "Not classified"
        stats[rel] += 1

        # Read original file and update frontmatter
        source_file = source_dir / art_type / art["file"]
        text = source_file.read_text()
        parts = text.split("---", 2)

        fm = yaml.safe_load(parts[1].strip())
        fm["relevance"] = rel
        fm["relevance_rationale"] = rationale

        yaml_str = yaml.dump(fm, default_flow_style=False, allow_unicode=True, sort_keys=False)
        out_path = type_out / art["file"]
        out_path.write_text(f"---\n{yaml_str}---\n\n{parts[2].strip()}\n")

    return stats


def main():
    if len(sys.argv) < 3:
        print("Usage: python triage_apply.py <artifacts-dir> <triage-packs-dir>")
        sys.exit(1)

    artifacts_dir = Path(sys.argv[1])
    packs_dir = Path(sys.argv[2])
    output_dir = packs_dir.parent  # triage/

    print(f"Parsing triage outputs from: {packs_dir}")
    triage_map, parse_errors = parse_triage_outputs(packs_dir)
    print(f"  BRQ classifications: {len(triage_map)}")
    if parse_errors:
        print(f"  Parse errors: {len(parse_errors)}")
        for e in parse_errors[:5]:
            print(f"    {e}")

    # Load all artifacts
    brq_arts = load_artifacts(artifacts_dir, "brq")
    br_arts = load_artifacts(artifacts_dir, "br")
    ctrl_arts = load_artifacts(artifacts_dir, "ctrl")
    print(f"\nArtifacts loaded: BRQ={len(brq_arts)}, BR={len(br_arts)}, CTRL={len(ctrl_arts)}")

    # Propagate to children
    print("Propagating relevance to BR/CTRL...")
    br_map = propagate_to_children(triage_map, br_arts)
    ctrl_map = propagate_to_children(triage_map, ctrl_arts)

    # Write updated artifacts
    print(f"\nWriting updated artifacts to: {output_dir}")
    brq_stats = write_updated_artifacts(brq_arts, triage_map, artifacts_dir, output_dir, "brq")
    br_stats = write_updated_artifacts(br_arts, br_map, artifacts_dir, output_dir, "br")
    ctrl_stats = write_updated_artifacts(ctrl_arts, ctrl_map, artifacts_dir, output_dir, "ctrl")

    # Summary
    print(f"\n{'Type':<6} {'Relevant':>10} {'Contextual':>12} {'Out-of-scope':>14} {'Total':>8}")
    print("-" * 54)
    for label, s, total in [("BRQ", brq_stats, len(brq_arts)),
                             ("BR", br_stats, len(br_arts)),
                             ("CTRL", ctrl_stats, len(ctrl_arts))]:
        print(f"{label:<6} {s['relevant']:>10} {s['contextual']:>12} {s['out-of-scope']:>14} {total:>8}")

    totals = {
        k: brq_stats[k] + br_stats[k] + ctrl_stats[k]
        for k in ("relevant", "contextual", "out-of-scope")
    }
    total_all = len(brq_arts) + len(br_arts) + len(ctrl_arts)
    print("-" * 54)
    print(f"{'TOTAL':<6} {totals['relevant']:>10} {totals['contextual']:>12} {totals['out-of-scope']:>14} {total_all:>8}")

    # Write report
    report = {
        "brq_total": len(brq_arts),
        "br_total": len(br_arts),
        "ctrl_total": len(ctrl_arts),
        "brq_stats": brq_stats,
        "br_stats": br_stats,
        "ctrl_stats": ctrl_stats,
        "totals": totals,
        "parse_errors": parse_errors,
        "classifications": {
            art_id: info for art_id, info in sorted(triage_map.items())
        },
    }
    report_path = output_dir / "triage-report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))
    print(f"\nReport: {report_path}")
    print("Done.")


if __name__ == "__main__":
    main()
