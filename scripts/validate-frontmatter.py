#!/usr/bin/env python3
"""
Validate frontmatter in all markdown files against JSON schemas.

The artifact-type → schema mapping comes from kit-manifest.json (single source
of truth) via kit_manifest.py. Schemas enforce a closed field set
(additionalProperties: false); project-specific fields must be prefixed with
`x_`. Unknown fields that look like a typo of a known field get a
"did you mean" hint.

Usage:
    python scripts/validate-frontmatter.py [--path PATH]

Requires: pip install pyyaml jsonschema
"""

import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kit_manifest import load_manifest, prefix_schema_map, special_id_schema_map

try:
    import yaml
    from jsonschema import Draft7Validator
except ImportError:
    print("ERROR: Install dependencies first: pip install pyyaml jsonschema")
    sys.exit(1)

FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---", re.DOTALL)

# Registry mappings — loaded from kit-manifest.json (no hardcoded drift).
_MANIFEST = load_manifest()
PREFIX_SCHEMA_MAP = prefix_schema_map(_MANIFEST)
SPECIAL_ID_SCHEMA_MAP = special_id_schema_map(_MANIFEST)

# Extension escape hatch: project-specific fields must start with this prefix.
EXTENSION_PREFIX = "x_"


def levenshtein(a: str, b: str) -> int:
    if a == b:
        return 0
    if not a:
        return len(b)
    if not b:
        return len(a)
    prev = list(range(len(b) + 1))
    for i, ca in enumerate(a, 1):
        cur = [i]
        for j, cb in enumerate(b, 1):
            cur.append(min(prev[j] + 1, cur[j - 1] + 1, prev[j - 1] + (ca != cb)))
        prev = cur
    return prev[-1]


def load_schemas(schema_dir: Path) -> dict:
    raw = {}
    for path in schema_dir.glob("*.json"):
        with open(path) as f:
            raw[path.name] = json.load(f)

    # Resolve $ref: inline base schema properties into type-specific schemas.
    # Schemas that use allOf with $ref to base inherit base properties/required.
    # Standalone schemas (no allOf) are used as-is — e.g., SRC which intentionally
    # does not inherit lifecycle fields like owner/status from base.
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
            # Inherit base's additionalProperties unless the type schema overrides it.
            if "additionalProperties" not in schema:
                schema["additionalProperties"] = base.get("additionalProperties", False)
        # Allow project extension fields (x_*) regardless of additionalProperties.
        pattern_props = dict(schema.get("patternProperties", {}))
        pattern_props.setdefault(f"^{re.escape(EXTENSION_PREFIX)}", {})
        schema["patternProperties"] = pattern_props
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
        for key in ("updated", "date", "release_date", "publication_date", "effective_date", "compliance_deadline"):
            if key in fm and not isinstance(fm[key], str):
                fm[key] = str(fm[key])
        return fm
    except yaml.YAMLError:
        return None


def get_schema_for_artifact(artifact_id: str, schemas: dict) -> dict | None:
    if artifact_id in SPECIAL_ID_SCHEMA_MAP:
        schema_name = SPECIAL_ID_SCHEMA_MAP[artifact_id]
        if schema_name in schemas:
            return schemas[schema_name]
    prefix = artifact_id.split("-")[0]
    schema_name = PREFIX_SCHEMA_MAP.get(prefix)
    if schema_name and schema_name in schemas:
        return schemas[schema_name]
    return schemas.get("base.schema.json")


def unknown_field_hints(fm: dict, schema: dict) -> list[str]:
    """Report unknown (non-x_) fields with a did-you-mean suggestion."""
    allowed = set(schema.get("properties", {}).keys())
    hints = []
    for key in fm:
        if key in allowed or key.startswith(EXTENSION_PREFIX):
            continue
        # Closest known field by edit distance
        best, best_d = None, 99
        for cand in allowed:
            d = levenshtein(key, cand)
            if d < best_d:
                best, best_d = cand, d
        if best is not None and best_d <= 2:
            hints.append(f"unknown field '{key}' — did you mean '{best}'? "
                         f"(or prefix a real custom field with '{EXTENSION_PREFIX}')")
        else:
            hints.append(f"unknown field '{key}' — not in schema "
                         f"(prefix project-specific fields with '{EXTENSION_PREFIX}')")
    return hints


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

    # Nicer, per-field messages for unknown fields (replaces the generic
    # jsonschema additionalProperties error, which we suppress below).
    for hint in unknown_field_hints(fm, schema):
        errors.append(f"{filepath}: {hint}")

    validator = Draft7Validator(schema)
    for error in validator.iter_errors(fm):
        if error.validator == "additionalProperties":
            continue  # covered by unknown_field_hints with a better message
        path = " → ".join(str(p) for p in error.absolute_path) if error.absolute_path else "(root)"
        errors.append(f"{filepath}: [{path}] {error.message}")

    return errors


def main():
    parser = argparse.ArgumentParser(description="Validate requirement frontmatter")
    parser.add_argument("--path", default=".", help="Root path of the requirements vault")
    parser.add_argument("--schema-dir", default=None, help="Path to schema directory (default: schema/ relative to --path, then parent directories)")
    args = parser.parse_args()

    root = Path(args.path)

    if args.schema_dir:
        schema_dir = Path(args.schema_dir)
    else:
        schema_dir = root / "schema"
        if not schema_dir.exists():
            current = root.resolve().parent
            while current != current.parent:
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

    skip_folders = {"templates", "scripts", ".codex", "_metadata-menu", ".git", ".snapshots"}

    for md_file in sorted(root.rglob("*.md")):
        if any(part in skip_folders for part in md_file.parts):
            continue
        if md_file.name.startswith("README") or md_file.name == "CLAUDE.md":
            continue

        fm = extract_frontmatter(md_file)
        if fm is None:
            continue

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
