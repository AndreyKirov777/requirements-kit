#!/usr/bin/env python3
"""
Validate frontmatter in all markdown files against JSON schemas.

Usage:
    python scripts/validate-frontmatter.py [--path PATH]

Requires: pip install pyyaml jsonschema
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
    from jsonschema import validate, ValidationError, Draft7Validator
except ImportError:
    print("ERROR: Install dependencies first: pip install pyyaml jsonschema")
    sys.exit(1)

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)

# Map ID prefixes to schema files
PREFIX_SCHEMA_MAP = {
    "FR": "requirement.schema.json",
    "NFR": "requirement.schema.json",
    "CON": "requirement.schema.json",
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
}

# Special-case IDs that don't follow the TYPE-DOMAIN-NNN pattern
SPECIAL_ID_SCHEMA_MAP = {
    "ARCH-OVERVIEW": "architecture-overview.schema.json",
}


def load_schemas(schema_dir: Path) -> dict:
    raw = {}
    for path in schema_dir.glob("*.json"):
        with open(path) as f:
            raw[path.name] = json.load(f)

    # Resolve $ref: inline base schema properties into type-specific schemas
    base = raw.get("base.schema.json", {})
    schemas = {}
    for name, schema in raw.items():
        if name == "base.schema.json":
            schemas[name] = schema
            continue
        # Remove allOf with $ref and merge base properties directly
        if "allOf" in schema:
            schema = {k: v for k, v in schema.items() if k != "allOf"}
        merged_props = dict(base.get("properties", {}))
        merged_props.update(schema.get("properties", {}))
        schema["properties"] = merged_props
        # Merge required fields
        base_req = set(base.get("required", []))
        schema_req = set(schema.get("required", []))
        schema["required"] = list(base_req | schema_req)
        schema["additionalProperties"] = True
        schemas[name] = schema
    return schemas


def extract_frontmatter(filepath: Path) -> dict | None:
    text = filepath.read_text(encoding="utf-8")
    match = FRONTMATTER_RE.match(text)
    if not match:
        return None
    try:
        fm = yaml.safe_load(match.group(1))
        if fm is None:
            return None
        # YAML auto-parses dates as datetime.date — convert back to string for validation
        for key in ("updated", "date", "release_date"):
            if key in fm and not isinstance(fm[key], str):
                fm[key] = str(fm[key])
        return fm
    except yaml.YAMLError:
        return None


def get_schema_for_artifact(artifact_id: str, schemas: dict) -> dict | None:
    # Check special-case IDs first (e.g., ARCH-OVERVIEW)
    if artifact_id in SPECIAL_ID_SCHEMA_MAP:
        schema_name = SPECIAL_ID_SCHEMA_MAP[artifact_id]
        if schema_name in schemas:
            return schemas[schema_name]
    # Then check prefix-based mapping
    prefix = artifact_id.split("-")[0]
    schema_name = PREFIX_SCHEMA_MAP.get(prefix)
    if schema_name and schema_name in schemas:
        return schemas[schema_name]
    # Fall back to base schema
    return schemas.get("base.schema.json")


def validate_file(filepath: Path, schemas: dict) -> list[str]:
    errors = []
    fm = extract_frontmatter(filepath)

    if fm is None:
        errors.append(f"{filepath}: no valid frontmatter found")
        return errors

    artifact_id = fm.get("id", "")
    if not artifact_id:
        errors.append(f"{filepath}: missing 'id' field in frontmatter")
        return errors

    schema = get_schema_for_artifact(artifact_id, schemas)
    if schema is None:
        errors.append(f"{filepath}: no schema found for ID prefix '{artifact_id.split('-')[0]}'")
        return errors

    validator = Draft7Validator(schema)
    for error in validator.iter_errors(fm):
        path = " → ".join(str(p) for p in error.absolute_path) if error.absolute_path else "(root)"
        errors.append(f"{filepath}: [{path}] {error.message}")

    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate requirement frontmatter")
    parser.add_argument("--path", default=".", help="Root path of the requirements vault")
    parser.add_argument("--schema-dir", default=None, help="Path to schema directory (default: schema/ relative to --path, then parent directories)")
    args = parser.parse_args()

    root = Path(args.path)

    # Determine schema directory
    if args.schema_dir:
        schema_dir = Path(args.schema_dir)
    else:
        # First look in root/schema, then walk up parent directories
        schema_dir = root / "schema"
        if not schema_dir.exists():
            current = root.parent
            while current != current.parent:  # Stop at filesystem root
                candidate = current / "schema"
                if candidate.exists():
                    schema_dir = candidate
                    break
                current = current.parent

    if not schema_dir.exists():
        print(f"ERROR: Schema directory not found: {schema_dir}")
        sys.exit(1)

    schemas = load_schemas(schema_dir)
    all_errors = []

    # Folders to skip — contain reference docs, not tracked artifacts
    skip_folders = {"templates", "scripts", ".codex"}

    # Scan all markdown files except templates and reference docs
    for md_file in sorted(root.rglob("*.md")):
        if any(part in skip_folders for part in md_file.parts):
            continue
        if md_file.name.startswith("README") or md_file.name == "CLAUDE.md":
            continue

        fm = extract_frontmatter(md_file)
        if fm is None:
            continue  # Skip files without frontmatter (non-artifact files)

        # Skip meta/reference files that don't follow artifact ID patterns
        artifact_id = fm.get("id", "")
        if artifact_id.startswith("META-") or artifact_id.startswith("GLOSS-") or artifact_id.startswith("CODEMAP-"):
            continue

        errors = validate_file(md_file, schemas)
        all_errors.extend(errors)

    if all_errors:
        print(f"\n{'='*60}")
        print(f"VALIDATION FAILED — {len(all_errors)} error(s) found")
        print(f"{'='*60}\n")
        for err in all_errors:
            print(f"  ✗ {err}")
        print()
        sys.exit(1)
    else:
        print(f"\n✓ All frontmatter valid. Scanned {sum(1 for _ in root.rglob('*.md'))} files.")
        sys.exit(0)


if __name__ == "__main__":
    main()
