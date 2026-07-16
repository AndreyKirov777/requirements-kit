#!/usr/bin/env python3
"""
generate-fileclasses.py

Reads schema/*.schema.json (single source of truth) and generates
Metadata Menu fileClass files for Obsidian.

Project-specific values (domains, owners, etc.) come from
project-config.json in the vault root. Copy project-config.example.json
and fill in your values.

Usage:
    python scripts/generate-fileclasses.py

Output:
    _metadata-menu/fileclasses/<name>.md  — one per artifact type

The generated folder should be configured as the "FileClass files folder"
in Metadata Menu plugin settings.
"""

import base64
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kit_manifest import (
    load_manifest,
    resolve_project_config,
    active_profile,
    enabled_types,
    ProfileConfigError,
)

# ─── Config ──────────────────────────────────────────────────────────────────

ROOT = Path(__file__).resolve().parent.parent
SCHEMA_DIR = ROOT / "schema"
OUT_DIR = ROOT / "_metadata-menu" / "fileclasses"
PROJECT_CONFIG_PATH = ROOT / "project-config.json"
BASE_SCHEMA_PATH = SCHEMA_DIR / "base.schema.json"

# Map: schema file name (without .schema.json) → artifact config, derived from
# kit-manifest.json (single source of truth). The fileClass display name is
# taken from the manifest's ARCH-OVERVIEW/ARCH-DOMAIN naming where the prefix
# differs from the fileClass name.
_MANIFEST = load_manifest()

# Manifest prefix → fileClass display name (only where they differ).
_FILECLASS_NAME_OVERRIDE = {
    "ARCH-OVERVIEW": "ARCH-OVERVIEW",
    "ARCH": "ARCH-DOMAIN",
}


def _build_artifact_map() -> dict:
    out = {}
    for prefix, cfg in _MANIFEST["artifact_types"].items():
        schema_key = cfg["schema"][: -len(".schema.json")]
        out[schema_key] = {
            "name": _FILECLASS_NAME_OVERRIDE.get(prefix, prefix),
            "paths": [cfg["folder"]],
            "icon": cfg.get("icon", "file"),
            "prefix": prefix,
        }
    return out


ARTIFACT_MAP = _build_artifact_map()

# Fields from project-config.json that map to base.schema.json properties.
# key   = property name in project-config.json
# value = frontmatter field name in artifacts
PROJECT_CONFIG_FIELDS = {
    "domains": "domain",
    "owners": "owner",
}


# ─── Helpers ─────────────────────────────────────────────────────────────────

def field_id(artifact_name: str, field_name: str) -> str:
    """Deterministic 6-char ID from field + artifact name (stable across runs).

    Matches Node's `crypto.createHash("sha256").update(...).digest("base64url")`
    — URL-safe base64 without padding, sliced to 6 chars.
    """
    digest = hashlib.sha256(f"{artifact_name}:{field_name}".encode("utf-8")).digest()
    b64 = base64.urlsafe_b64encode(digest).rstrip(b"=").decode("ascii")
    return b64[:6]


def to_values_list(enum_values):
    """Convert a list of values to Metadata Menu ValuesList format."""
    return {str(i + 1): val for i, val in enumerate(enum_values)}


def extract_enum_fields(schema):
    """Extract all fields with `enum` from a JSON Schema's `properties`.

    Returns a list of {"name": str, "enumValues": list}.
    """
    props = schema.get("properties") or {}
    fields = []
    for name, definition in props.items():
        enum_values = definition.get("enum")
        if isinstance(enum_values, list):
            fields.append({"name": name, "enumValues": enum_values})
    return fields


def load_project_config_fields():
    """Load project-config.json and return project-specific Select fields."""
    if not PROJECT_CONFIG_PATH.exists():
        return []
    with PROJECT_CONFIG_PATH.open(encoding="utf-8") as f:
        config = json.load(f)
    fields = []
    for config_key, field_name in PROJECT_CONFIG_FIELDS.items():
        values = config.get(config_key)
        if isinstance(values, list) and len(values) > 0:
            fields.append({"name": field_name, "enumValues": values})
    return fields


def load_base_enum_fields():
    """Load base.schema.json and return any enum fields defined there.

    These apply to all artifact types.
    """
    if not BASE_SCHEMA_PATH.exists():
        return []
    with BASE_SCHEMA_PATH.open(encoding="utf-8") as f:
        base = json.load(f)
    return extract_enum_fields(base)


def build_fileclass(artifact_name, icon, paths, fields):
    """Build YAML frontmatter string for a fileClass."""
    yaml_fields = []
    for f in fields:
        fid = field_id(artifact_name, f["name"])
        lines = [
            f"  - name: {f['name']}",
            "    type: Select",
            "    options:",
            "      sourceType: ValuesList",
            "      valuesList:",
        ]
        for k, v in to_values_list(f["enumValues"]).items():
            lines.append(f'        "{k}": "{v}"')
        lines.append('    path: ""')
        lines.append(f"    id: {fid}")
        yaml_fields.append("\n".join(lines))

    files_paths = "\n".join(f"  - {p}" for p in paths)
    fields_order = "\n".join(
        f"  - {field_id(artifact_name, f['name'])}" for f in fields
    )

    return "\n".join([
        "---",
        'version: "2.14"',
        "mapWithTag: false",
        f"icon: {icon}",
        "tagNames: ",
        "filesPaths:",
        files_paths,
        "bookmarksGroups: ",
        "excludes: ",
        "extends: ",
        "limit: 100",
        "savedViews: []",
        "favoriteView: ",
        "fieldsOrder:",
        fields_order,
        "fields:",
        "\n".join(yaml_fields),
        "---",
        "",
        f"# {artifact_name}",
        "",
        "> Auto-generated from `schema/` by `scripts/generate-fileclasses.py`.",
        "> Do not edit manually — re-run the script after changing schemas.",
        "",
    ])


# ─── Main ────────────────────────────────────────────────────────────────────

def main():
    OUT_DIR.mkdir(parents=True, exist_ok=True)

    try:
        project_config = resolve_project_config(ROOT)
        profile = active_profile(project_config, _MANIFEST)
        enabled = enabled_types(project_config, _MANIFEST)
    except ProfileConfigError as e:
        print(f"ERROR: invalid project-config.json — {e}")
        sys.exit(1)

    if profile is not None:
        print(f"📐 Profile: {profile} — {len(enabled)} artifact type(s) enabled\n")

    # Load shared fields: base schema enums + project config
    base_enum_fields = load_base_enum_fields()
    project_fields = load_project_config_fields()

    if project_fields:
        summary = ", ".join(
            f"{f['name']} ({len(f['enumValues'])} values)" for f in project_fields
        )
        print(f"📋 project-config.json: {summary}")
    elif PROJECT_CONFIG_PATH.exists():
        print("📋 project-config.json: found but no usable fields")
    else:
        print("📋 project-config.json: not found — domain/owner will be free text")
        print("   Copy project-config.example.json → project-config.json to enable dropdowns.\n")

    # Combine base + project fields (project overrides base if same name)
    shared_fields = list(base_enum_fields)
    for pf in project_fields:
        existing = next(
            (i for i, f in enumerate(shared_fields) if f["name"] == pf["name"]),
            -1,
        )
        if existing >= 0:
            shared_fields[existing] = pf
        else:
            shared_fields.append(pf)

    schema_files = sorted(
        f.name
        for f in SCHEMA_DIR.iterdir()
        if f.name.endswith(".schema.json") and f.name != "base.schema.json"
    )

    generated = 0
    skipped = 0

    for file_name in schema_files:
        key = file_name[:-len(".schema.json")]
        config = ARTIFACT_MAP.get(key)

        if not config:
            print(f"⚠  No mapping for {file_name} — skipping")
            skipped += 1
            continue

        if enabled is not None and config["prefix"] not in enabled:
            print(f"⊘  {config['name']}: outside profile {profile} — skipping (schema still validates if authored)")
            skipped += 1
            continue

        with (SCHEMA_DIR / file_name).open(encoding="utf-8") as f:
            schema = json.load(f)

        schema_enum_fields = extract_enum_fields(schema)

        # Merge: schema-specific fields take priority, then shared fields
        # (only add a shared field if not already present from the schema).
        all_fields = list(schema_enum_fields)
        for sf in shared_fields:
            if not any(f["name"] == sf["name"] for f in all_fields):
                all_fields.append(sf)

        if not all_fields:
            print(f"   {config['name']}: no fields — skipping")
            skipped += 1
            continue

        content = build_fileclass(
            config["name"], config["icon"], config["paths"], all_fields
        )
        out_path = OUT_DIR / f"{config['name']}.md"
        out_path.write_text(content, encoding="utf-8")
        names = ", ".join(f["name"] for f in all_fields)
        print(f"✓  {config['name']} → {len(all_fields)} field(s): {names}")
        generated += 1

    print(f"\nDone: {generated} fileClasses generated, {skipped} skipped.")
    print(f"Output: {OUT_DIR}/")


if __name__ == "__main__":
    main()
