#!/usr/bin/env python3
"""
generate-status-transitions.py

Regenerates _framework/status-transitions.md from kit-manifest.json so the
human-readable state-machine reference always matches the machine-checked graph
used by check-status-transitions.py. Do not edit the generated file by hand.

Usage:
    python scripts/generate-status-transitions.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kit_manifest import load_manifest

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "_framework" / "status-transitions.md"


def render() -> str:
    m = load_manifest()
    lines = [
        "---",
        "id: META-STATUS-TRANSITIONS",
        "title: Status Transitions — State Machines",
        f"updated: {m['updated']}",
        "---",
        "",
        "# Status Transitions",
        "",
        "> **Generated file — do not edit by hand.** Source of truth is `kit-manifest.json`.",
        "> Re-run `python scripts/generate-status-transitions.py` after changing the manifest.",
        "",
        "This document lists the allowed lifecycle statuses and the legal transitions",
        "between them for every artifact type. The same graph is enforced automatically:",
        "",
        "- `check-status-transitions.py` (default) validates that each artifact's current",
        "  status is legal for its type and that parent/child statuses stay consistent.",
        "- `check-status-transitions.py --git` validates that each *change* to a `status`",
        "  field follows an allowed edge below (no skipping states).",
        "",
        "A terminal status (no outgoing edges) can only be left via a Change Request that",
        "creates a new artifact. `deprecated` is reachable from every non-terminal status.",
        "",
    ]

    # Group by tier for readability
    tiers_order = ["core", "compliance", "discovery", "source", "architecture", "delivery"]
    types = m["artifact_types"]
    by_tier = {}
    for prefix, cfg in types.items():
        by_tier.setdefault(cfg["tier"], []).append((prefix, cfg))

    for tier in tiers_order:
        entries = by_tier.get(tier)
        if not entries:
            continue
        lines.append(f"## {tier.capitalize()} tier")
        lines.append("")
        for prefix, cfg in sorted(entries):
            lines.append(f"### {prefix}")
            lines.append("")
            if not cfg.get("has_lifecycle", True):
                statuses = ", ".join(f"`{s}`" for s in cfg.get("statuses", []))
                lines.append(
                    f"{prefix} has **no managed lifecycle**. Its `status` field is an objective "
                    f"property of the underlying document, not a workflow state. Recognized values: {statuses}."
                )
                lines.append("")
                continue
            statuses = ", ".join(f"`{s}`" for s in cfg.get("statuses", []))
            lines.append(f"**Statuses:** {statuses}")
            lines.append("")
            gates = cfg.get("human_gate_statuses", [])
            if gates:
                lines.append(f"**Human approval gate at:** {', '.join(f'`{g}`' for g in gates)}")
                lines.append("")
            lines.append("| From | Allowed next |")
            lines.append("| --- | --- |")
            for frm, tos in cfg.get("transitions", {}).items():
                tos_str = ", ".join(f"`{t}`" for t in tos) if tos else "— (terminal)"
                lines.append(f"| `{frm}` | {tos_str} |")
            lines.append("")

    return "\n".join(lines) + "\n"


def main():
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(render(), encoding="utf-8")
    print(f"✓ Wrote {OUT.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
