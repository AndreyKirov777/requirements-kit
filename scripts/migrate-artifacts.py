#!/usr/bin/env python3
"""
migrate-artifacts.py — Upgrade existing artifacts after a kit version update.

Schema-driven approach:
  1. Reads JSON schemas and templates to build a "reference model" per artifact type
  2. Scans existing project artifacts
  3. Adds missing frontmatter fields with default values from the template
  4. Adds missing markdown sections from the template (before # Links or at the end)
  5. Never overwrites user-filled content

Modes:
  --dry-run    Show what would change, write nothing
  --report     Write a migration-report.md with full change details
  (default)    Apply safe changes (add-only, no deletions)

Usage:
    python requirements/scripts/migrate-artifacts.py
    python requirements/scripts/migrate-artifacts.py --dry-run
    python requirements/scripts/migrate-artifacts.py --report
    python requirements/scripts/migrate-artifacts.py --path /path/to/vault

Requires: pip install pyyaml
"""

import argparse
import json
import re
import sys
from datetime import date
from pathlib import Path
from collections import OrderedDict

try:
    import yaml
except ImportError:
    print("ERROR: Install dependency first: pip install pyyaml")
    sys.exit(1)

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)
SECTION_HEADER_RE = re.compile(r"^(#{1,3})\s+(.+)$", re.MULTILINE)

# Patterns that indicate a template placeholder (not a real value)
# Matches: XXX-000, YYYY-MM-DD, [[TYPE-XXX-000]], etc.
PLACEHOLDER_RE = re.compile(
    r"(XXX|YYY|000|YYYY-MM-DD|NNN)"
)

# Same mapping as validate-frontmatter.py — single source of truth for prefix→schema
PREFIX_SCHEMA_MAP = {
    "FR": "requirement.schema.json",
    "NFR": "requirement.schema.json",
    "CON": "constraint.schema.json",
    "US": "user-story.schema.json",
    "EPIC": "epic.schema.json",
    "ADR": "adr.schema.json",
    "TEST": "test.schema.json",
    "TASK": "task.schema.json",
    "CR": "change-request.schema.json",
    "PERSONA": "persona.schema.json",
    "ASSUM": "assumption.schema.json",
    "RISK": "risk.schema.json",
    "REL": "release.schema.json",
    "JOURNEY": "journey.schema.json",
    "UC": "use-case.schema.json",
    "CONTRACT": "contract.schema.json",
    "DM": "data-model.schema.json",
    "VISION": "vision.schema.json",
    "ARCH": "domain-architecture.schema.json",
    "BRQ": "brq.schema.json",
    "CTRL": "ctrl.schema.json",
    "BR": "br.schema.json",
}

SPECIAL_ID_SCHEMA_MAP = {
    "ARCH-OVERVIEW": "architecture-overview.schema.json",
}

# Map ID prefix → template filename
PREFIX_TEMPLATE_MAP = {
    "FR": "fr-template.md",
    "NFR": "nfr-template.md",
    "CON": "constraint-template.md",
    "US": "user-story-template.md",
    "EPIC": "epic-template.md",
    "ADR": "adr-template.md",
    "TEST": "test-template.md",
    "TASK": "task-template.md",
    "CR": "change-request-template.md",
    "PERSONA": "persona-template.md",
    "ASSUM": "assumption-template.md",
    "RISK": "risk-template.md",
    "REL": "release-template.md",
    "JOURNEY": "journey-template.md",
    "UC": "use-case-template.md",
    "CONTRACT": "contract-template.md",
    "DM": "data-model-template.md",
    "VISION": "vision-template.md",
    "BRQ": "brq-template.md",
    "CTRL": "ctrl-template.md",
    "BR": "br-template.md",
}

SPECIAL_TEMPLATE_MAP = {
    "ARCH-OVERVIEW": "architecture-overview-template.md",
}

# For ARCH-XXX-NNN (not ARCH-OVERVIEW)
# The prefix "ARCH" maps to domain-architecture, but ARCH-OVERVIEW is special
# We handle this in get_template_for_artifact()

# Folders to skip — not tracked artifacts
SKIP_FOLDERS = {"templates", "scripts", ".codex", ".cursor", ".kiro", ".claude",
                ".git", "_examples", ".snapshots", "docs", "schema", "node_modules"}

# ---------------------------------------------------------------------------
# YAML helpers — preserve order and formatting
# ---------------------------------------------------------------------------


class OrderedDumper(yaml.SafeDumper):
    """Dump YAML preserving key order."""
    pass


def _dict_representer(dumper, data):
    return dumper.represent_mapping("tag:yaml.org,2002:map", data.items())


OrderedDumper.add_representer(OrderedDict, _dict_representer)
OrderedDumper.add_representer(dict, _dict_representer)


def dump_yaml(data: dict) -> str:
    """Dump dict to YAML string with consistent formatting."""
    return yaml.dump(
        data,
        Dumper=OrderedDumper,
        default_flow_style=False,
        allow_unicode=True,
        sort_keys=False,
        width=200,
    )


# ---------------------------------------------------------------------------
# File parsing
# ---------------------------------------------------------------------------


def parse_artifact(filepath: Path) -> tuple[dict | None, str, str]:
    """Parse an artifact file into (frontmatter_dict, raw_yaml_text, body_text).

    Returns (None, "", full_text) if no frontmatter found.
    """
    text = filepath.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None, "", text

    raw_yaml = match.group(1)
    try:
        fm = yaml.safe_load(raw_yaml)
        if fm is None:
            return None, raw_yaml, text
    except yaml.YAMLError:
        return None, raw_yaml, text

    # Normalize date fields to strings
    for key in ("updated", "date", "release_date", "compliance_deadline"):
        if key in fm and not isinstance(fm[key], str):
            fm[key] = str(fm[key])

    body = text[match.end():]
    return fm, raw_yaml, body


def extract_sections(body: str) -> list[tuple[str, str, str]]:
    """Extract markdown sections from body text.

    Returns list of (level_hashes, title, full_text_including_header).
    """
    sections = []
    matches = list(SECTION_HEADER_RE.finditer(body))
    for i, m in enumerate(matches):
        level = m.group(1)
        title = m.group(2).strip()
        start = m.start()
        end = matches[i + 1].start() if i + 1 < len(matches) else len(body)
        sections.append((level, title, body[start:end]))
    return sections


def extract_section_titles(body: str) -> set[str]:
    """Extract set of normalized section titles (lowercase, stripped)."""
    return {title.lower().strip() for _, title, _ in extract_sections(body)}


# ---------------------------------------------------------------------------
# Schema & template loading
# ---------------------------------------------------------------------------


def load_schemas(schema_dir: Path) -> dict:
    """Load and merge JSON schemas (same logic as validate-frontmatter.py)."""
    raw = {}
    for path in schema_dir.glob("*.json"):
        with open(path) as f:
            raw[path.name] = json.load(f)

    base = raw.get("base.schema.json", {})
    schemas = {}
    for name, schema in raw.items():
        if name == "base.schema.json":
            schemas[name] = schema
            continue
        if "allOf" in schema:
            schema = {k: v for k, v in schema.items() if k != "allOf"}
        merged_props = dict(base.get("properties", {}))
        merged_props.update(schema.get("properties", {}))
        schema["properties"] = merged_props
        base_req = set(base.get("required", []))
        schema_req = set(schema.get("required", []))
        schema["required"] = list(base_req | schema_req)
        schema["additionalProperties"] = True
        schemas[name] = schema
    return schemas


def load_template_frontmatter(template_dir: Path) -> dict[str, dict]:
    """Load frontmatter defaults from all templates.

    Returns dict: template_filename -> {field: default_value}
    """
    templates = {}
    for tpl in template_dir.glob("*-template.md"):
        fm, _, _ = parse_artifact(tpl)
        if fm:
            templates[tpl.name] = fm
    return templates


def load_template_sections(template_dir: Path) -> dict[str, list[tuple[str, str, str]]]:
    """Load markdown sections from all templates.

    Returns dict: template_filename -> [(level, title, full_text)]
    """
    sections = {}
    for tpl in template_dir.glob("*-template.md"):
        _, _, body = parse_artifact(tpl)
        sections[tpl.name] = extract_sections(body)
    return sections


# ---------------------------------------------------------------------------
# Artifact → schema/template resolution
# ---------------------------------------------------------------------------


def get_schema_for_artifact(artifact_id: str, schemas: dict) -> dict | None:
    """Resolve the JSON schema for a given artifact ID."""
    if artifact_id in SPECIAL_ID_SCHEMA_MAP:
        return schemas.get(SPECIAL_ID_SCHEMA_MAP[artifact_id])
    prefix = artifact_id.split("-")[0]
    schema_name = PREFIX_SCHEMA_MAP.get(prefix)
    if schema_name and schema_name in schemas:
        return schemas[schema_name]
    return schemas.get("base.schema.json")


def get_template_for_artifact(artifact_id: str, template_fm: dict, template_sections: dict):
    """Resolve template frontmatter and sections for a given artifact ID.

    Returns (fm_defaults: dict, sections: list) or (None, None).
    """
    if artifact_id in SPECIAL_TEMPLATE_MAP:
        tpl_name = SPECIAL_TEMPLATE_MAP[artifact_id]
        return template_fm.get(tpl_name), template_sections.get(tpl_name, [])

    prefix = artifact_id.split("-")[0]

    # Special case: ARCH prefix but not ARCH-OVERVIEW
    if prefix == "ARCH" and artifact_id != "ARCH-OVERVIEW":
        tpl_name = "domain-architecture-template.md"
        return template_fm.get(tpl_name), template_sections.get(tpl_name, [])

    tpl_name = PREFIX_TEMPLATE_MAP.get(prefix)
    if tpl_name:
        return template_fm.get(tpl_name), template_sections.get(tpl_name, [])
    return None, None


# ---------------------------------------------------------------------------
# Migration logic
# ---------------------------------------------------------------------------


def _is_placeholder(value) -> bool:
    """Check if a template value is a placeholder that shouldn't be used as a real default."""
    if isinstance(value, str):
        return bool(PLACEHOLDER_RE.search(value))
    return False


def _sanitize_template_default(value, prop_schema: dict):
    """Replace template placeholder values with neutral defaults.

    Template values like '[[EPIC-XXX-000]]' or 'YYYY-MM-DD' are not useful
    as migration defaults — they pollute traceability and orphan-check reports.
    """
    if _is_placeholder(value):
        prop_type = prop_schema.get("type", "string")
        if prop_type == "array":
            return []
        return ""
    if isinstance(value, list):
        # Filter out placeholder items from list defaults
        cleaned = [v for v in value if not _is_placeholder(v)]
        return cleaned
    return value


def compute_frontmatter_changes(
    current_fm: dict,
    schema: dict,
    template_defaults: dict | None,
) -> list[tuple[str, str, object]]:
    """Compute what frontmatter fields need to be added.

    Returns list of (field_name, reason, default_value).
    Reasons: 'required-missing', 'optional-missing'.
    """
    changes = []
    if not schema:
        return changes

    schema_props = schema.get("properties", {})
    required = set(schema.get("required", []))

    for field_name in schema_props:
        if field_name in current_fm:
            continue  # Already present — never overwrite

        # Determine default value
        default = None
        prop = schema_props[field_name]
        if template_defaults and field_name in template_defaults:
            default = _sanitize_template_default(template_defaults[field_name], prop)
        else:
            # Infer from schema type
            prop_type = prop.get("type", "string")
            if prop_type == "array":
                default = []
            elif prop_type == "string":
                # If schema has an enum, use the first value as default
                if "enum" in prop:
                    default = prop["enum"][0]
                elif "const" in prop:
                    default = prop["const"]
                else:
                    default = ""
            elif prop_type == "object":
                default = {}
            else:
                default = ""

        reason = "required-missing" if field_name in required else "optional-missing"
        changes.append((field_name, reason, default))

    return changes


def compute_section_changes(
    current_body: str,
    template_sections: list[tuple[str, str, str]] | None,
) -> list[tuple[str, str, str]]:
    """Compute what markdown sections need to be added.

    Returns list of (level, title, placeholder_text) for missing sections.
    Only checks top-level (#) sections — sub-sections are part of the section body.
    """
    if not template_sections:
        return []

    existing = extract_section_titles(current_body)
    missing = []

    for level, title, full_text in template_sections:
        if level != "#":
            continue  # Only check top-level sections
        if title.lower().strip() in existing:
            continue  # Already exists
        missing.append((level, title, full_text))

    return missing


def _yaml_serialize_value(value) -> str:
    """Serialize a single YAML value for string insertion.

    Uses yaml.dump for correct formatting but strips the trailing newline
    and document markers.
    """
    dumped = yaml.dump(
        value,
        Dumper=OrderedDumper,
        default_flow_style=None,       # inline for simple lists/dicts
        allow_unicode=True,
        width=200,
    ).rstrip("\n")
    # yaml.dump adds "...\n" for scalars — strip it
    if dumped.endswith("\n..."):
        dumped = dumped[:-4].rstrip("\n")
    return dumped


def apply_frontmatter_changes(
    filepath: Path,
    current_fm: dict,
    raw_yaml_str: str,
    body: str,
    changes: list[tuple[str, str, object]],
) -> str:
    """Apply frontmatter field additions to file content.

    Appends new fields as YAML text at the end of the existing raw frontmatter.
    Preserves the original YAML verbatim (comments, quoting, order) — only
    adds new lines.
    """
    # Build YAML snippet for the new fields only
    new_lines = []
    for field_name, _, default in changes:
        serialized = _yaml_serialize_value(default)
        # Multi-line values (block-style lists/dicts) need the key on its own line
        if "\n" in serialized:
            new_lines.append(f"{field_name}:\n{serialized}")
        else:
            new_lines.append(f"{field_name}: {serialized}")

    patch = "\n".join(new_lines)
    patched_yaml = raw_yaml_str.rstrip() + "\n" + patch
    return f"---\n{patched_yaml}\n---{body}"


def apply_section_changes(
    body: str,
    missing_sections: list[tuple[str, str, str]],
) -> str:
    """Add missing markdown sections to the body.

    Inserts before '# Links' section if it exists, otherwise appends at the end.
    """
    if not missing_sections:
        return body

    # Build text to insert
    insert_text = ""
    for level, title, template_text in missing_sections:
        # Use the template text but strip the placeholder content — just add headers
        # with a minimal "..." placeholder
        insert_text += f"\n{level} {title}\n\n- ...\n"

    # Find the # Links section to insert before it
    links_match = re.search(r"^# Links\b", body, re.MULTILINE)
    if links_match:
        pos = links_match.start()
        return body[:pos] + insert_text + "\n" + body[pos:]
    else:
        return body.rstrip() + "\n" + insert_text


# ---------------------------------------------------------------------------
# File scanning
# ---------------------------------------------------------------------------


def scan_artifacts(root: Path) -> list[Path]:
    """Find all artifact markdown files in the vault."""
    artifacts = []
    for md_file in sorted(root.rglob("*.md")):
        # Skip non-artifact folders
        rel_parts = md_file.relative_to(root).parts
        if any(part in SKIP_FOLDERS for part in rel_parts):
            continue
        if md_file.name.startswith("README") or md_file.name == "CLAUDE.md":
            continue
        if md_file.name.endswith("-template.md"):
            continue

        # Only process files with frontmatter containing an artifact ID
        fm, _, _ = parse_artifact(md_file)
        if fm and fm.get("id"):
            artifact_id = fm["id"]
            # Skip meta/reference IDs
            if any(artifact_id.startswith(p) for p in ("META-", "GLOSS-", "CODEMAP-")):
                continue
            artifacts.append(md_file)

    return artifacts


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------


def format_change(field: str, reason: str, default) -> str:
    """Format a single frontmatter change for display."""
    icon = "!" if "required" in reason else "+"
    default_str = json.dumps(default, ensure_ascii=False) if not isinstance(default, str) else f'"{default}"'
    return f"  [{icon}] {field}: {default_str}  ({reason})"


def generate_report(
    all_changes: list[dict],
    report_path: Path,
    dry_run: bool,
):
    """Generate migration-report.md."""
    lines = [
        f"# Migration Report",
        f"",
        f"Generated: {date.today().isoformat()}",
        f"Mode: {'DRY RUN' if dry_run else 'APPLIED'}",
        f"",
        f"## Summary",
        f"",
    ]

    files_changed = sum(1 for c in all_changes if c["fm_changes"] or c["section_changes"])
    fm_total = sum(len(c["fm_changes"]) for c in all_changes)
    sec_total = sum(len(c["section_changes"]) for c in all_changes)

    lines.append(f"- Files scanned: {len(all_changes)}")
    lines.append(f"- Files with changes: {files_changed}")
    lines.append(f"- Frontmatter fields added: {fm_total}")
    lines.append(f"- Markdown sections added: {sec_total}")
    lines.append("")

    if files_changed == 0:
        lines.append("All artifacts are up to date. No changes needed.")
    else:
        lines.append("## Changes by File")
        lines.append("")
        for entry in all_changes:
            if not entry["fm_changes"] and not entry["section_changes"]:
                continue
            lines.append(f"### `{entry['file']}`")
            lines.append(f"- Type: `{entry['artifact_id']}`")
            if entry["fm_changes"]:
                lines.append(f"- **Frontmatter fields added:**")
                for field, reason, default in entry["fm_changes"]:
                    default_str = json.dumps(default, ensure_ascii=False) if not isinstance(default, str) else default
                    req = " (REQUIRED)" if "required" in reason else ""
                    lines.append(f"  - `{field}`: `{default_str}`{req}")
            if entry["section_changes"]:
                lines.append(f"- **Markdown sections added:**")
                for level, title, _ in entry["section_changes"]:
                    lines.append(f"  - `{level} {title}`")
            lines.append("")

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Migrate existing artifacts to match updated kit schemas and templates."
    )
    parser.add_argument(
        "--path", default=".",
        help="Root path of the requirements vault (default: current directory)",
    )
    parser.add_argument(
        "--dry-run", action="store_true",
        help="Show what would change without writing files.",
    )
    parser.add_argument(
        "--report", action="store_true",
        help="Generate migration-report.md with full change details.",
    )
    parser.add_argument(
        "--required-only", action="store_true",
        help="Only add missing required fields (skip optional fields).",
    )
    args = parser.parse_args()

    root = Path(args.path).resolve()

    # Locate directories
    schema_dir = root / "schema"

    # v0.4.0 moved templates from 00-meta/templates to _framework/templates
    template_dir = root / "_framework" / "templates"
    if not template_dir.exists():
        template_dir = root / "00-meta" / "templates"  # fallback for pre-0.4.0

    if not schema_dir.exists():
        print(f"ERROR: Schema directory not found: {schema_dir}")
        sys.exit(1)
    if not template_dir.exists():
        print(f"ERROR: Template directory not found. Checked _framework/templates/ and 00-meta/templates/")
        sys.exit(1)

    # Load reference data
    print(f"Vault root   : {root}")
    print(f"Schema dir   : {schema_dir}")
    print(f"Template dir : {template_dir}")
    if args.dry_run:
        print(f"Mode         : DRY RUN (no files will be written)")
    elif args.required_only:
        print(f"Mode         : REQUIRED ONLY (optional fields and sections skipped)")
    else:
        print(f"Mode         : APPLY (add-only, no deletions)")
    print()

    # Safety check: warn if working tree is dirty (best effort)
    if not args.dry_run:
        import subprocess
        try:
            result = subprocess.run(
                ["git", "status", "--porcelain"],
                capture_output=True, text=True, cwd=root, timeout=5,
            )
            if result.returncode == 0 and result.stdout.strip():
                print("WARNING: Git working tree has uncommitted changes.")
                print("         Consider committing or stashing before migration.")
                print()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            pass  # git not available or not a repo — skip silently

    schemas = load_schemas(schema_dir)
    tpl_fm = load_template_frontmatter(template_dir)
    tpl_sections = load_template_sections(template_dir)

    print(f"Loaded {len(schemas)} schemas, {len(tpl_fm)} templates")
    print()

    # Scan artifacts
    artifacts = scan_artifacts(root)
    print(f"Found {len(artifacts)} artifact files to check")
    print()

    # Process each artifact
    all_changes = []
    files_modified = 0

    for filepath in artifacts:
        fm, raw_yaml, body = parse_artifact(filepath)
        if not fm:
            continue

        artifact_id = fm.get("id", "")
        schema = get_schema_for_artifact(artifact_id, schemas)
        defaults, template_secs = get_template_for_artifact(artifact_id, tpl_fm, tpl_sections)

        # Compute changes
        fm_changes = compute_frontmatter_changes(fm, schema, defaults)
        if args.required_only:
            fm_changes = [(f, r, d) for f, r, d in fm_changes if "required" in r]

        section_changes = compute_section_changes(body, template_secs)
        if args.required_only:
            section_changes = []  # --required-only skips section additions

        rel_path = filepath.relative_to(root)
        entry = {
            "file": str(rel_path),
            "artifact_id": artifact_id,
            "fm_changes": fm_changes,
            "section_changes": section_changes,
        }
        all_changes.append(entry)

        if not fm_changes and not section_changes:
            continue

        files_modified += 1

        # Display
        print(f"  {rel_path}  ({artifact_id})")
        for field, reason, default in fm_changes:
            print(format_change(field, reason, default))
        for level, title, _ in section_changes:
            print(f"  [§] {level} {title}")

        # Apply changes (unless dry-run)
        if not args.dry_run:
            new_content = filepath.read_text(encoding="utf-8")

            if fm_changes:
                new_content = apply_frontmatter_changes(filepath, fm, raw_yaml, body, fm_changes)
                # Re-parse to get updated body for section changes
                match = FRONTMATTER_RE.match(new_content)
                if match:
                    body = new_content[match.end():]

            if section_changes:
                body = apply_section_changes(body, section_changes)
                # Reconstruct with frontmatter
                match = FRONTMATTER_RE.match(new_content)
                if match:
                    new_content = new_content[:match.end()] + body

            filepath.write_text(new_content, encoding="utf-8")

    # Summary
    print()
    fm_total = sum(len(c["fm_changes"]) for c in all_changes)
    sec_total = sum(len(c["section_changes"]) for c in all_changes)
    print(f"{'='*60}")
    print(f"Scanned: {len(artifacts)} files")
    print(f"Modified: {files_modified} files")
    print(f"  Frontmatter fields added: {fm_total}")
    print(f"  Markdown sections added: {sec_total}")
    print(f"{'='*60}")

    if args.dry_run and files_modified > 0:
        print("\nRe-run without --dry-run to apply changes.")

    # Generate report if requested
    if args.report:
        report_path = root / "migration-report.md"
        generate_report(all_changes, report_path, args.dry_run)
        print(f"\nReport written to: {report_path}")

    # Update .kit-version if it exists and changes were applied
    kit_version_file = root / ".kit-version"
    if kit_version_file.exists() and not args.dry_run and files_modified > 0:
        version_data = kit_version_file.read_text(encoding="utf-8")
        today = date.today().isoformat()
        # Replace existing last-migration line, or append if missing
        if re.search(r"^last-migration:.*$", version_data, re.MULTILINE):
            version_data = re.sub(
                r"^last-migration:.*$",
                f"last-migration: {today}",
                version_data,
                flags=re.MULTILINE,
            )
        else:
            version_data = version_data.rstrip() + f"\nlast-migration: {today}\n"
        kit_version_file.write_text(version_data, encoding="utf-8")


if __name__ == "__main__":
    main()
