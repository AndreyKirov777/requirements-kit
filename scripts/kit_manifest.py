#!/usr/bin/env python3
"""
kit_manifest.py — shared loader for kit-manifest.json.

kit-manifest.json is the SINGLE SOURCE OF TRUTH for the artifact-type registry:
prefixes, folders, schemas, tiers, valid statuses, transition graphs, and up-links.
Every script that needs the registry imports this module instead of hardcoding it.

Usage:
    from kit_manifest import load_manifest, prefix_schema_map, valid_statuses, transitions

Requires: standard library only.
"""

import json
import re
from functools import lru_cache
from pathlib import Path


def find_manifest(start: Path | None = None) -> Path:
    """Locate kit-manifest.json: check the given path, then walk up from this file."""
    candidates = []
    if start is not None:
        candidates.append(Path(start))
    here = Path(__file__).resolve().parent
    candidates.append(here.parent / "kit-manifest.json")
    # Walk up from the current working tree too
    current = here
    while current != current.parent:
        candidates.append(current / "kit-manifest.json")
        current = current.parent
    for c in candidates:
        if c and c.is_file():
            return c
    raise FileNotFoundError(
        "kit-manifest.json not found. Expected it at the vault root."
    )


@lru_cache(maxsize=8)
def load_manifest(path: str | None = None) -> dict:
    manifest_path = find_manifest(Path(path) if path else None)
    with open(manifest_path, encoding="utf-8") as f:
        return json.load(f)


def artifact_types(manifest: dict | None = None) -> dict:
    manifest = manifest or load_manifest()
    return manifest["artifact_types"]


def prefix_schema_map(manifest: dict | None = None) -> dict:
    """{prefix: schema_filename} for prefix-based lookups (excludes special IDs)."""
    out = {}
    for prefix, cfg in artifact_types(manifest).items():
        if cfg.get("special_id"):
            continue
        out[prefix] = cfg["schema"]
    return out


def special_id_schema_map(manifest: dict | None = None) -> dict:
    """{special_id: schema_filename} for IDs that don't follow TYPE-DOMAIN-NNN."""
    out = {}
    for cfg in artifact_types(manifest).values():
        if cfg.get("special_id"):
            out[cfg["special_id"]] = cfg["schema"]
    return out


def valid_statuses(manifest: dict | None = None) -> dict:
    """{prefix: set(statuses)} — only for types that have a lifecycle."""
    out = {}
    for prefix, cfg in artifact_types(manifest).items():
        if cfg.get("has_lifecycle", True):
            out[prefix] = set(cfg.get("statuses", []))
    return out


def transitions(manifest: dict | None = None) -> dict:
    """{prefix: {from_status: [allowed_next, ...]}}."""
    out = {}
    for prefix, cfg in artifact_types(manifest).items():
        if cfg.get("has_lifecycle", True):
            out[prefix] = cfg.get("transitions", {})
    return out


def folder_for_prefix(prefix: str, manifest: dict | None = None) -> str | None:
    cfg = artifact_types(manifest).get(prefix)
    return cfg["folder"] if cfg else None


def prefix_for_id(artifact_id: str, manifest: dict | None = None) -> str | None:
    """Resolve an artifact ID to its type prefix, honoring special IDs."""
    specials = special_id_schema_map(manifest)
    if artifact_id in {cfg.get("special_id") for cfg in artifact_types(manifest).values()}:
        return artifact_id
    prefix = artifact_id.split("-")[0]
    if prefix in artifact_types(manifest):
        return prefix
    return None


def id_regex(manifest: dict | None = None) -> re.Pattern:
    """Regex matching any valid artifact ID across all known prefixes."""
    prefixes = [p for p in artifact_types(manifest) if not artifact_types(manifest)[p].get("special_id")]
    alt = "|".join(sorted((re.escape(p) for p in prefixes), key=len, reverse=True))
    return re.compile(rf"^(?:{alt})-[A-Z0-9]+-[0-9]{{3,}}$")


if __name__ == "__main__":
    m = load_manifest()
    print(f"kit-manifest.json v{m['kit_version']} — {len(m['artifact_types'])} artifact types")
    for prefix, cfg in m["artifact_types"].items():
        life = "lifecycle" if cfg.get("has_lifecycle", True) else "no-lifecycle"
        print(f"  {prefix:14s} {cfg['tier']:13s} {life:12s} {cfg['folder']}")
