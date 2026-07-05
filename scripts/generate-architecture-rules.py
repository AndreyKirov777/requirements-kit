#!/usr/bin/env python3
"""
generate-architecture-rules.py — build the agent-facing architecture rulebook.

Collects the `# Rules` section from every ADR with `status: accepted` and
assembles 03-architecture/architecture-rules.md: a compact, normative file
meant to be loaded into an AI coding agent's context on EVERY task (unlike
full ADRs, which are pull-context for rationale).

Rules are extracted verbatim — this script performs no distillation. The
distillation happens at ADR authoring time (see the `# Rules` section of
the ADR template and prompt 8 in scripts/agent-prompts.md). That keeps this
generation step deterministic and CI-friendly.

Each rule gets a stable ID `<ADR-ID>.R<n>` (n = position in the section),
so review agents can cite violations precisely.

Lint (applies to accepted ADRs only):
  - `# Rules` section must exist and be non-empty
  - every bullet must start with MUST / MUST NOT / SHOULD / SHOULD NOT,
    or be the explicit opt-out `- (no normative rules)`

Usage:
    python scripts/generate-architecture-rules.py [--path PATH] [--output FILE]
    python scripts/generate-architecture-rules.py --check   # lint only, exit 1 on violations

Requires: pip install pyyaml
"""

import argparse
import re
import sys
from datetime import date
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kit_manifest import load_manifest, artifact_types

try:
    import yaml
except ImportError:
    print("ERROR: Install dependencies first: pip install pyyaml")
    sys.exit(1)

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n?(.*)$", re.DOTALL)
HTML_COMMENT_RE = re.compile(r"<!--.*?-->", re.DOTALL)
RFC2119_RE = re.compile(r"^(MUST NOT|MUST|SHOULD NOT|SHOULD)\b")
OPT_OUT = "(no normative rules)"

_MANIFEST = load_manifest()
_ADR_CFG = artifact_types(_MANIFEST)["ADR"]


def parse_file(path: Path):
    text = path.read_text(encoding="utf-8")
    m = FRONTMATTER_RE.match(text)
    if not m:
        return None, text
    try:
        fm = yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        fm = {}
    return fm, m.group(2)


def extract_rules_section(body: str) -> str | None:
    """Return the raw content of the `# Rules` H1 section, or None if absent."""
    lines = body.splitlines()
    start = None
    for i, line in enumerate(lines):
        if re.match(r"^#\s+Rules\s*$", line):
            start = i + 1
            break
    if start is None:
        return None
    section = []
    for line in lines[start:]:
        if re.match(r"^#\s+\S", line):  # next H1
            break
        section.append(line)
    return "\n".join(section)


def extract_bullets(section: str) -> list[str]:
    """Top-level bullets from the section, HTML comments stripped,
    continuation lines folded into their bullet."""
    section = HTML_COMMENT_RE.sub("", section)
    bullets = []
    for line in section.splitlines():
        if re.match(r"^-\s+\S", line):
            bullets.append(line[1:].strip())
        elif bullets and re.match(r"^\s+\S", line):
            bullets[-1] += " " + line.strip()
    return bullets


def lint_adr(adr_id: str, section: str | None, bullets: list[str]) -> list[str]:
    problems = []
    if section is None:
        problems.append(f"{adr_id}: accepted ADR has no `# Rules` section")
        return problems
    if not bullets:
        problems.append(f"{adr_id}: `# Rules` section is empty")
        return problems
    for i, b in enumerate(bullets, 1):
        if b.startswith(OPT_OUT):
            if len(bullets) > 1:
                problems.append(
                    f"{adr_id}.R{i}: `{OPT_OUT}` must be the only bullet in the section"
                )
            continue
        if not RFC2119_RE.match(b):
            problems.append(
                f"{adr_id}.R{i}: rule must start with MUST / MUST NOT / "
                f"SHOULD / SHOULD NOT — got: {b[:60]!r}"
            )
    return problems


def collect(root: Path):
    """Return (entries, problems, skipped_counts). entries are accepted ADRs
    with their rule bullets, sorted by id."""
    adr_dir = root / _ADR_CFG["folder"]
    entries, problems = [], []
    skipped = {}
    if not adr_dir.is_dir():
        return entries, [f"ADR folder not found: {adr_dir}"], skipped
    for md in sorted(adr_dir.rglob("*.md")):
        if "templates" in md.parts:
            continue
        fm, body = parse_file(md)
        if not fm or "id" not in fm:
            continue
        status = fm.get("status", "")
        if status != "accepted":
            skipped[status] = skipped.get(status, 0) + 1
            continue
        section = extract_rules_section(body)
        bullets = extract_bullets(section) if section is not None else []
        problems.extend(lint_adr(fm["id"], section, bullets))
        bullets = [b for b in bullets if not b.startswith(OPT_OUT)]
        if bullets:
            entries.append({
                "id": fm["id"],
                "title": fm.get("title", ""),
                "domain": fm.get("domain", "") or "unassigned",
                "updated": str(fm.get("updated", fm.get("date", ""))),
                "bullets": bullets,
            })
    entries.sort(key=lambda e: e["id"])
    return entries, problems, skipped


def render(entries: list[dict], skipped: dict, root: Path) -> str:
    kit_version = _MANIFEST.get("kit_version", "unknown")
    total_rules = sum(len(e["bullets"]) for e in entries)
    lines = [
        "---",
        f"generated: {date.today().isoformat()}",
        "generator: scripts/generate-architecture-rules.py",
        f"kit_version: {kit_version}",
        f"source_adrs: {len(entries)}",
        f"rule_count: {total_rules}",
        "tags: [generated, architecture-rules]",
        "---",
        "",
        "# Architecture Rules",
        "",
        "> **Auto-generated — do not edit.** Extracted from the `# Rules` sections",
        "> of accepted ADRs. To change a rule, edit its ADR and regenerate:",
        "> `python scripts/generate-architecture-rules.py`",
        ">",
        "> **For AI coding agents:** these rules are binding on every task.",
        "> Rules marked `[check: ...]` are also enforced by tooling. For the",
        "> rationale behind a rule, open the ADR it links to. If a task requires",
        "> an architectural choice not covered here, create a `proposed` ADR and",
        "> stop for review.",
        "",
    ]
    if not entries:
        lines.append("_No accepted ADRs with rules yet._")
        lines.append("")
    domains: dict[str, list[dict]] = {}
    for e in entries:
        domains.setdefault(e["domain"], []).append(e)
    for domain in sorted(domains):
        lines.append(f"## Domain: {domain}")
        lines.append("")
        for e in domains[domain]:
            title = f" — {e['title']}" if e["title"] else ""
            lines.append(f"### [[{e['id']}]]{title}")
            lines.append("")
            for i, b in enumerate(e["bullets"], 1):
                lines.append(f"- **{e['id']}.R{i}** — {b}")
            lines.append("")
    if skipped:
        skipped_str = ", ".join(f"{k}: {v}" for k, v in sorted(skipped.items()))
        lines.append(f"<!-- ADRs excluded by status — {skipped_str} -->")
        lines.append("")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Generate architecture-rules.md from accepted ADRs")
    parser.add_argument("--path", default=".", help="Vault root (default: current dir)")
    parser.add_argument("--output", default=None,
                        help="Output file (default: 03-architecture/architecture-rules.md)")
    parser.add_argument("--check", action="store_true",
                        help="Lint only: report problems, write nothing, exit 1 on violations")
    args = parser.parse_args()

    root = Path(args.path).resolve()
    entries, problems, skipped = collect(root)

    for p in problems:
        print(f"WARNING: {p}")

    if args.check:
        n = sum(len(e["bullets"]) for e in entries)
        print(f"Checked: {len(entries)} accepted ADR(s) with rules, {n} rule(s), "
              f"{len(problems)} problem(s)")
        sys.exit(1 if problems else 0)

    out_path = Path(args.output) if args.output else root / "03-architecture" / "architecture-rules.md"
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(render(entries, skipped, root), encoding="utf-8")
    n = sum(len(e["bullets"]) for e in entries)
    print(f"Architecture rules saved: {out_path} "
          f"({n} rule(s) from {len(entries)} accepted ADR(s))")
    if problems:
        print(f"NOTE: {len(problems)} lint problem(s) above — fix the ADR(s) and regenerate.")


if __name__ == "__main__":
    main()
