#!/usr/bin/env python3
"""
Triage — classify extracted BRQ artifacts by relevance to the target system.

Reads BRQ artifacts from _temp/<regulation>/artifacts/brq/,
batches them into triage packs with the Product Vision as context,
and outputs a triage report + updated frontmatter with relevance field.

Relevance categories:
  - relevant:    creates system functionality (data model, API, UI, logic)
  - contextual:  influences requirements indirectly (definitions, scope, deadlines)
  - out-of-scope: not related to the target system (member state duties, committee procedures)

Usage:
  python triage.py <artifacts-dir> <vision-file> [--batch-size 50] [--output-dir triage/]

Input:  _temp/<regulation>/artifacts/brq/*.md
        Product vision .md file
Output: _temp/<regulation>/triage/
          triage-report.json     (full classification results)
          brq/BRQ-*.md           (updated with relevance + relevance_rationale)
          br/BR-*.md             (relevance inherited from parent BRQ)
          ctrl/CTRL-*.md         (relevance inherited from parent BRQ)
"""

import argparse
import json
import re
import sys
from pathlib import Path

import yaml


# ---------------------------------------------------------------------------
# Load artifacts
# ---------------------------------------------------------------------------

def load_artifact(filepath: Path) -> dict:
    """Load a single artifact file, returning frontmatter + body."""
    text = filepath.read_text()
    if not text.startswith("---"):
        return {"file": filepath.name, "error": "No frontmatter"}

    parts = text.split("---", 2)
    if len(parts) < 3:
        return {"file": filepath.name, "error": "Malformed frontmatter"}

    try:
        fm = yaml.safe_load(parts[1].strip())
    except yaml.YAMLError as e:
        return {"file": filepath.name, "error": f"YAML error: {e}"}

    return {
        "file": filepath.name,
        "frontmatter": fm,
        "body": parts[2].strip(),
        "raw": text,
    }


def load_all_artifacts(artifacts_dir: Path) -> dict:
    """Load all BRQ, BR, CTRL artifacts from subdirectories."""
    result = {"brq": [], "br": [], "ctrl": []}

    for art_type in ("brq", "br", "ctrl"):
        type_dir = artifacts_dir / art_type
        if not type_dir.exists():
            continue
        for f in sorted(type_dir.glob("*.md")):
            if f.name.startswith("_"):
                continue
            art = load_artifact(f)
            if "error" not in art:
                result[art_type].append(art)

    return result


# ---------------------------------------------------------------------------
# Build triage packs
# ---------------------------------------------------------------------------

TRIAGE_PROMPT_TEMPLATE = """\
# Role

You are a requirements analyst performing relevance triage.

# Task

Classify each Business Requirement (BRQ) by its relevance to the target system \
described in the Product Vision below. Your goal is to determine which regulatory \
obligations need to be implemented as system features, which provide important context, \
and which are unrelated to this system.

# Product Vision

<vision>
{vision_text}
</vision>

# Relevance categories

- **relevant**: This BRQ creates or directly constrains system functionality. \
The system must implement features, data models, APIs, UI elements, or business logic \
to satisfy this obligation. Examples: data attributes that must be stored, access control \
rules, QR code requirements, completeness tracking, audit logging.

- **contextual**: This BRQ does not create system functionality directly but influences \
requirements. Examples: definitions used by other requirements, scope articles that \
determine which batteries are covered, deadlines that affect implementation planning, \
delegated act provisions that may change future requirements.

- **out-of-scope**: This BRQ has no relation to the target system. Examples: member state \
obligations (collection/treatment infrastructure), committee procedures, penalties, \
market surveillance procedures, waste management obligations not involving the passport system, \
obligations placed solely on distributors/importers for physical handling.

# Classification guidelines

1. The system is a Digital Battery Passport platform. Requirements about battery passport \
data content, access, storage, and lifecycle are almost always **relevant**.
2. Requirements about physical battery properties (durability, safety, chemical composition) \
are **relevant** only if they define data that must appear in the passport. If they only \
define physical/chemical requirements with no data dimension, classify as **out-of-scope**.
3. Requirements for carbon footprint declarations, performance classes, due diligence — \
classify as **relevant** if the regulation requires this information in the battery passport \
or if it must be accessible via QR code.
4. Member state obligations for setting up collection points, treatment facilities, etc. \
are **out-of-scope** unless they directly require data exchange with the passport system.
5. Delegated/implementing act provisions are **contextual** — they define future rules \
that will affect the system.

# Output format

For each BRQ, output a JSON object on a single line:

```
{{"id": "BRQ-BAT-001", "relevance": "relevant", "rationale": "Defines scope of batteries requiring digital passports"}}
```

Output one line per BRQ. Do NOT add any other text before or after the JSON lines.

# BRQ artifacts to classify

"""


def build_triage_batch(brq_artifacts: list[dict], batch_num: int) -> str:
    """Build a triage context string for a batch of BRQ artifacts."""
    parts = []
    for art in brq_artifacts:
        fm = art["frontmatter"]
        art_id = fm.get("id", "?")
        title = fm.get("title", "?")

        # Extract summary from body (first ## Summary section)
        body = art["body"]
        summary_match = re.search(r"## Summary\s*\n\s*(.*?)(?:\n\n|\n##|\Z)", body, re.DOTALL)
        summary = summary_match.group(1).strip() if summary_match else body[:200]

        # Extract source ref
        source_ref = fm.get("source_ref", "")
        reg_refs = fm.get("regulatory_refs", [])
        article = ""
        if reg_refs:
            article = f"Article {reg_refs[0].get('article', '?')}"

        parts.append(
            f"### {art_id}: {title}\n"
            f"- Source: {article}\n"
            f"- Summary: {summary}\n"
        )

    return "\n".join(parts)


def build_triage_packs(
    brq_artifacts: list[dict],
    vision_text: str,
    batch_size: int = 50,
) -> list[dict]:
    """Build triage packs from BRQ artifacts."""
    packs = []
    total = len(brq_artifacts)

    for i in range(0, total, batch_size):
        batch = brq_artifacts[i:i + batch_size]
        batch_num = (i // batch_size) + 1

        batch_content = build_triage_batch(batch, batch_num)
        full_prompt = TRIAGE_PROMPT_TEMPLATE.format(vision_text=vision_text) + batch_content

        packs.append({
            "pack_num": batch_num,
            "brq_ids": [a["frontmatter"]["id"] for a in batch],
            "content": full_prompt,
            "tokens": len(full_prompt) // 4,
        })

    return packs


# ---------------------------------------------------------------------------
# Parse triage output
# ---------------------------------------------------------------------------

def parse_triage_output(text: str) -> list[dict]:
    """Parse agent triage output — one JSON object per line."""
    results = []
    errors = []

    for line in text.strip().splitlines():
        line = line.strip()
        if not line or line.startswith("#") or line.startswith("```"):
            continue

        try:
            obj = json.loads(line)
            if "id" in obj and "relevance" in obj:
                # Validate relevance value
                if obj["relevance"] not in ("relevant", "contextual", "out-of-scope"):
                    errors.append(f"Invalid relevance '{obj['relevance']}' for {obj['id']}")
                    obj["relevance"] = "contextual"  # safe default
                results.append(obj)
            else:
                errors.append(f"Missing id/relevance in: {line[:100]}")
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code block
            json_match = re.search(r'\{.*?\}', line)
            if json_match:
                try:
                    obj = json.loads(json_match.group())
                    if "id" in obj and "relevance" in obj:
                        results.append(obj)
                        continue
                except json.JSONDecodeError:
                    pass
            errors.append(f"JSON parse error: {line[:100]}")

    return results, errors


# ---------------------------------------------------------------------------
# Propagate relevance to BR / CTRL
# ---------------------------------------------------------------------------

def propagate_relevance(
    triage_map: dict,
    br_artifacts: list[dict],
    ctrl_artifacts: list[dict],
) -> dict:
    """Propagate BRQ relevance to BR and CTRL via derives_from links.

    Propagation rule: child inherits the HIGHEST relevance from any parent.
    relevant > contextual > out-of-scope
    """
    relevance_rank = {"relevant": 3, "contextual": 2, "out-of-scope": 1}

    child_relevance = {}

    for art_type, artifacts in [("br", br_artifacts), ("ctrl", ctrl_artifacts)]:
        for art in artifacts:
            fm = art["frontmatter"]
            art_id = fm.get("id", "")
            derives_from = fm.get("derives_from", [])

            # Extract parent BRQ IDs from derives_from (handles [[BRQ-BAT-001]] format)
            parent_ids = []
            for ref in derives_from:
                # Strip [[ ]] wiki-link syntax
                clean = str(ref).strip("[]").strip()
                if clean.startswith("BRQ-"):
                    parent_ids.append(clean)

            # Find highest-ranked parent relevance
            best_relevance = "out-of-scope"
            best_rationale = "No parent BRQ found"

            for pid in parent_ids:
                if pid in triage_map:
                    parent_rel = triage_map[pid]["relevance"]
                    if relevance_rank.get(parent_rel, 0) > relevance_rank.get(best_relevance, 0):
                        best_relevance = parent_rel
                        best_rationale = f"Inherited from {pid}: {triage_map[pid].get('rationale', '')}"

            child_relevance[art_id] = {
                "relevance": best_relevance,
                "rationale": best_rationale,
                "parents": parent_ids,
            }

    return child_relevance


# ---------------------------------------------------------------------------
# Write triage results
# ---------------------------------------------------------------------------

def update_artifact_file(
    source_path: Path,
    output_path: Path,
    relevance: str,
    relevance_rationale: str,
):
    """Copy artifact file with relevance fields added to frontmatter."""
    text = source_path.read_text()
    if not text.startswith("---"):
        output_path.write_text(text)
        return

    parts = text.split("---", 2)
    if len(parts) < 3:
        output_path.write_text(text)
        return

    try:
        fm = yaml.safe_load(parts[1].strip())
    except yaml.YAMLError:
        output_path.write_text(text)
        return

    # Add relevance fields
    fm["relevance"] = relevance
    fm["relevance_rationale"] = relevance_rationale

    # Rebuild file
    yaml_str = yaml.dump(fm, default_flow_style=False, allow_unicode=True, sort_keys=False)
    output_path.write_text(f"---\n{yaml_str}---\n\n{parts[2].strip()}\n")


def write_triage_results(
    triage_map: dict,
    child_relevance: dict,
    artifacts: dict,
    source_dir: Path,
    output_dir: Path,
):
    """Write updated artifacts with relevance fields to output directory."""

    stats = {
        "brq": {"relevant": 0, "contextual": 0, "out-of-scope": 0},
        "br": {"relevant": 0, "contextual": 0, "out-of-scope": 0},
        "ctrl": {"relevant": 0, "contextual": 0, "out-of-scope": 0},
    }

    # Write BRQ
    brq_out = output_dir / "brq"
    brq_out.mkdir(parents=True, exist_ok=True)
    for art in artifacts["brq"]:
        art_id = art["frontmatter"]["id"]
        if art_id in triage_map:
            rel = triage_map[art_id]["relevance"]
            rationale = triage_map[art_id].get("rationale", "")
        else:
            rel = "contextual"
            rationale = "Not classified by triage agent"
        stats["brq"][rel] += 1

        source_file = source_dir / "brq" / art["file"]
        update_artifact_file(source_file, brq_out / art["file"], rel, rationale)

    # Write BR and CTRL (inherited relevance)
    for art_type in ("br", "ctrl"):
        type_out = output_dir / art_type
        type_out.mkdir(parents=True, exist_ok=True)
        for art in artifacts[art_type]:
            art_id = art["frontmatter"]["id"]
            if art_id in child_relevance:
                rel = child_relevance[art_id]["relevance"]
                rationale = child_relevance[art_id]["rationale"]
            else:
                rel = "contextual"
                rationale = "No derives_from link to classified BRQ"
            stats[art_type][rel] += 1

            source_file = source_dir / art_type / art["file"]
            update_artifact_file(source_file, type_out / art["file"], rel, rationale)

    # Write report
    report = {
        "total_brq": len(artifacts["brq"]),
        "total_br": len(artifacts["br"]),
        "total_ctrl": len(artifacts["ctrl"]),
        "stats": stats,
        "brq_classifications": {
            art_id: info for art_id, info in sorted(triage_map.items())
        },
        "child_classifications": {
            art_id: info for art_id, info in sorted(child_relevance.items())
        },
    }
    report_path = output_dir / "triage-report.json"
    report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False))

    return report, stats


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="Triage BRQ artifacts by relevance to target system."
    )
    parser.add_argument(
        "artifacts_dir",
        help="Path to artifacts directory with brq/, br/, ctrl/ subdirectories"
    )
    parser.add_argument(
        "vision_file",
        help="Path to Product Vision .md file"
    )
    parser.add_argument(
        "--batch-size", "-b",
        type=int,
        default=50,
        help="Number of BRQ per triage batch (default: 50)"
    )
    parser.add_argument(
        "--output-dir", "-o",
        default=None,
        help="Output directory (default: sibling 'triage/' next to artifacts/)"
    )
    args = parser.parse_args()

    artifacts_dir = Path(args.artifacts_dir)
    vision_path = Path(args.vision_file)

    print(f"Loading artifacts from: {artifacts_dir}")
    artifacts = load_all_artifacts(artifacts_dir)
    print(f"  BRQ: {len(artifacts['brq'])}")
    print(f"  BR:  {len(artifacts['br'])}")
    print(f"  CTRL: {len(artifacts['ctrl'])}")

    print(f"\nLoading vision from: {vision_path}")
    vision_text = vision_path.read_text()
    # Strip frontmatter from vision
    if vision_text.startswith("---"):
        parts = vision_text.split("---", 2)
        if len(parts) >= 3:
            vision_text = parts[2].strip()

    print(f"\nBuilding triage packs (batch size: {args.batch_size})...")
    packs = build_triage_packs(artifacts["brq"], vision_text, args.batch_size)
    print(f"  Packs: {len(packs)}")
    for p in packs:
        print(f"    Pack {p['pack_num']}: {len(p['brq_ids'])} BRQs, ~{p['tokens']:,} tokens")

    # Write packs for agent processing
    output_dir = Path(args.output_dir) if args.output_dir else artifacts_dir.parent / "triage"
    packs_dir = output_dir / "packs"
    packs_dir.mkdir(parents=True, exist_ok=True)

    for pack in packs:
        pack_file = packs_dir / f"triage-pack-{pack['pack_num']:03d}.md"
        pack_file.write_text(pack["content"])

    manifest = {
        "total_packs": len(packs),
        "total_brq": len(artifacts["brq"]),
        "batch_size": args.batch_size,
        "packs": [
            {
                "file": f"triage-pack-{p['pack_num']:03d}.md",
                "pack_num": p["pack_num"],
                "brq_ids": p["brq_ids"],
                "tokens": p["tokens"],
            }
            for p in packs
        ],
    }
    manifest_path = packs_dir / "_manifest.json"
    manifest_path.write_text(json.dumps(manifest, indent=2, ensure_ascii=False))

    print(f"\nTriage packs written to: {packs_dir}")
    print(f"Manifest: {manifest_path}")
    print(f"\nNext step: run each triage pack through the analyst agent,")
    print(f"then use --apply mode to propagate results.")
    print("\nDone.")


if __name__ == "__main__":
    main()
