#!/usr/bin/env python3
"""
assemble-context.py — collect the full trace-chain of a TASK into a single
markdown context bundle, so an agent performs ONE read instead of ten.

Given a TASK id, it walks the up-links defined in kit-manifest.json:

    TASK → FR/NFR (implements) → US (part_of_story, with Acceptance Criteria)
         → obligation chain (derives_from: BRQ/BR/CTRL/CON, source_ref: SRC)
         → related ADRs (computed: ADRs whose related_requirements include the FR)
         → target_files (from the task and the code-map)

Usage:
    python scripts/assemble-context.py TASK-INGEST-001 [--path PATH] [--out FILE]

Requires: pip install pyyaml
"""

import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kit_manifest import load_manifest, artifact_types

try:
    import yaml
except ImportError:
    print("ERROR: Install dependencies first: pip install pyyaml")
    sys.exit(1)

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)
WIKILINK_RE = re.compile(r"\[\[([^\]|#]+)")
ID_RE = re.compile(r"\b([A-Z]+-[A-Z0-9]+-[0-9]{3,})\b")

_MANIFEST = load_manifest()
_TYPES = artifact_types(_MANIFEST)


def parse(path: Path):
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        fm = {}
    return fm, m.group(2)


def build_index(root: Path) -> dict:
    index = {}
    for md in root.rglob("*.md"):
        if "templates" in md.parts:
            continue
        fm, body = parse(md)
        if fm and "id" in fm:
            index[fm["id"]] = {"path": md, "fm": fm, "body": body}
    return index


def ids_in(value) -> list[str]:
    out = []
    if isinstance(value, str):
        out += WIKILINK_RE.findall(value)
        out += [i for i in ID_RE.findall(value)]
    elif isinstance(value, list):
        for v in value:
            out += ids_in(v)
    # de-dup preserving order
    seen, res = set(), []
    for i in out:
        i = i.strip()
        if i and i not in seen:
            seen.add(i); res.append(i)
    return res


def prefix(aid: str) -> str:
    return aid.split("-")[0]


def up_link_fields(aid: str) -> dict:
    cfg = _TYPES.get(prefix(aid), {})
    return cfg.get("up_links", {})


def section(body: str, *headers: str) -> str | None:
    """Extract a markdown section by any of the given H1 headers."""
    for h in headers:
        m = re.search(rf"(?ms)^#\s+{re.escape(h)}\s*$(.*?)(?=^#\s+|\Z)", body)
        if m:
            return m.group(1).strip()
    return None


def emit(index: dict, task_id: str) -> str:
    if task_id not in index:
        raise SystemExit(f"ERROR: {task_id} not found in vault.")
    lines = []
    task = index[task_id]
    tfm = task["fm"]
    lines.append(f"# Context bundle for {task_id}")
    lines.append("")
    lines.append(f"> Auto-assembled by scripts/assemble-context.py — a single read of the full trace chain.")
    lines.append("")

    # TASK
    lines.append(f"## Task — {task_id}: {tfm.get('title','')}")
    lines.append(f"- status: {tfm.get('status','—')} | complexity: {tfm.get('estimated_complexity','—')}")
    if tfm.get("acceptance_criteria_subset"):
        lines.append(f"- acceptance_criteria_subset: {tfm['acceptance_criteria_subset']}")
    if tfm.get("target_files"):
        lines.append(f"- target_files: {tfm['target_files']}")
    obj = section(task["body"], "Objective")
    notes = section(task["body"], "Implementation Notes")
    if obj: lines += ["", "**Objective**", "", obj]
    if notes: lines += ["", "**Implementation Notes**", "", notes]
    lines.append("")

    # FR / NFR (profile M/L — TASK links via `implements`). If absent, this
    # TASK links directly to a User Story via `part_of_story` instead (profile
    # S has no FR/NFR) — handled in the fallback branch below.
    req_ids = ids_in(tfm.get("implements", ""))
    for rid in req_ids:
        if rid not in index:
            lines.append(f"## Requirement — {rid} (NOT FOUND)\n")
            continue
        r = index[rid]; rfm = r["fm"]
        lines.append(f"## Requirement — {rid}: {rfm.get('title','')}")
        lines.append(f"- status: {rfm.get('status','—')} | priority: {rfm.get('priority','—')} | domain: {rfm.get('domain','—')}")
        for sec in ("Requirement", "Summary", "Out of Scope", "Edge Cases"):
            s = section(r["body"], sec)
            if s:
                lines += ["", f"**{sec}**", "", s]
        lines.append("")

        # User Stories delivering this FR (with AC) — via part_of_story on the task
        # and via US.delivers pointing at the FR.
        us_ids = ids_in(tfm.get("part_of_story", ""))
        for uid, u in index.items():
            if prefix(uid) == "US" and rid in ids_in(u["fm"].get("delivers", [])):
                if uid not in us_ids:
                    us_ids.append(uid)
        for uid in us_ids:
            if uid not in index:
                continue
            u = index[uid]; ufm = u["fm"]
            lines.append(f"### User Story — {uid}: {ufm.get('title','')}")
            lines.append(f"- persona: {ufm.get('persona','—')} | status: {ufm.get('status','—')}")
            story = section(u["body"], "Story", "User Story")
            ac = section(u["body"], "Acceptance Criteria")
            if story: lines += ["", story]
            if ac: lines += ["", "**Acceptance Criteria**", "", ac]
            lines.append("")

        # Obligation chain: derives_from + source_ref, walked upward.
        seen = set()
        frontier = list(ids_in(rfm.get("derives_from", [])))
        if not frontier:
            lines.append("_No obligation chain (derives_from empty) — direct stakeholder requirement._\n")
        while frontier:
            oid = frontier.pop(0)
            if oid in seen or oid not in index:
                continue
            seen.add(oid)
            o = index[oid]; ofm = o["fm"]
            lines.append(f"#### {prefix(oid)} — {oid}: {ofm.get('title','')}")
            lines.append(f"- status: {ofm.get('status','—')}")
            summ = section(o["body"], "Summary", "Rule", "Control", "Statement", "Requirement")
            if summ: lines += ["", summ]
            # keep walking up
            for field in up_link_fields(oid):
                frontier += ids_in(ofm.get(field, ""))
            # source_ref → SRC
            sref = ofm.get("source_ref")
            if sref:
                srcid = (ID_RE.search(sref) or [None])[0] if ID_RE.search(sref) else None
                if srcid and srcid in index and srcid not in seen:
                    seen.add(srcid)
                    s = index[srcid]
                    lines.append(f"#### SRC — {srcid}: {s['fm'].get('title','')} ({sref})")
            lines.append("")

        # Related ADRs (computed reverse link)
        adrs = [aid for aid, a in index.items()
                if prefix(aid) == "ADR" and rid in ids_in(a["fm"].get("related_requirements", []))]
        for aid in adrs:
            a = index[aid]
            lines.append(f"### ADR — {aid}: {a['fm'].get('title','')} (status: {a['fm'].get('status','—')})")
            dec = section(a["body"], "Decision")
            if dec: lines += ["", dec]
            lines.append("")

    if not req_ids:
        # No FR/NFR to walk (profile S, or any task authored without
        # `implements`) — enter the chain directly via `part_of_story`.
        us_ids = ids_in(tfm.get("part_of_story", ""))
        if not us_ids:
            lines.append("_No `implements` or `part_of_story` link found on this task — nothing to trace._\n")
        for uid in us_ids:
            if uid not in index:
                lines.append(f"## User Story — {uid} (NOT FOUND)\n")
                continue
            u = index[uid]; ufm = u["fm"]
            lines.append(f"## User Story — {uid}: {ufm.get('title','')}")
            lines.append(f"- status: {ufm.get('status','—')} | priority: {ufm.get('priority','—')} | domain: {ufm.get('domain','—')}")
            story = section(u["body"], "Story", "User Story")
            ac = section(u["body"], "Acceptance Criteria")
            if story: lines += ["", story]
            if ac: lines += ["", "**Acceptance Criteria**", "", ac]
            lines.append("")

            # Related ADRs (computed reverse link) — same lookup as the FR
            # path, keyed on the US id instead of an FR/NFR id.
            adrs = [aid for aid, a in index.items()
                    if prefix(aid) == "ADR" and uid in ids_in(a["fm"].get("related_requirements", []))]
            for aid in adrs:
                a = index[aid]
                lines.append(f"### ADR — {aid}: {a['fm'].get('title','')} (status: {a['fm'].get('status','—')})")
                dec = section(a["body"], "Decision")
                if dec: lines += ["", dec]
                lines.append("")

        # VISION context — profile S has no Epic/BRQ obligation chain, so
        # surface the product vision directly as the project-level "why".
        for vid in (aid for aid in index if prefix(aid) == "VISION"):
            v = index[vid]
            lines.append(f"## Vision — {vid}: {v['fm'].get('title','')}")
            vs = section(v["body"], "Vision", "Summary")
            if vs: lines += ["", vs]
            lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def main():
    parser = argparse.ArgumentParser(description="Assemble a task's full context into one bundle")
    parser.add_argument("task_id", help="TASK id, e.g. TASK-INGEST-001")
    parser.add_argument("--path", default=".", help="Root of requirements vault")
    parser.add_argument("--out", default=None, help="Write to file instead of stdout")
    args = parser.parse_args()

    index = build_index(Path(args.path))
    bundle = emit(index, args.task_id)
    if args.out:
        Path(args.out).write_text(bundle, encoding="utf-8")
        print(f"✓ Wrote {args.out}")
    else:
        sys.stdout.write(bundle)


if __name__ == "__main__":
    main()
