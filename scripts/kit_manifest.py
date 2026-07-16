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


# --- Scale profiles (v2.2.0) ---------------------------------------------------
#
# A profile is a named preset (S/M/L) that enables a subset of artifact types,
# selected via project-config.json's "profile" field, with "flags" as an
# orthogonal addition (e.g. "compliance"). See kit-manifest.json's "profiles"
# and "flags" sections (single source of truth) and docs/profiles-spec.md.
#
# No project-config.json, or no "profile" field in it, means "full mode":
# every artifact type is enabled — this is the pre-2.2.0 behavior and the
# default for every script in this kit.


class ProfileConfigError(ValueError):
    """Raised when project-config.json declares an unknown profile/flag, or a
    profile+flag combination that kit-manifest.json marks as forbidden."""


def _named_defs(manifest: dict, key: str) -> dict:
    """manifest["profiles"] / manifest["flags"] as {name: cfg}, excluding the
    "$comment" documentation key that isn't a real profile/flag name."""
    return {k: v for k, v in manifest.get(key, {}).items() if not k.startswith("$")}


def find_project_config(start: Path | None = None) -> Path | None:
    """Locate project-config.json next to kit-manifest.json. None if absent."""
    manifest_path = find_manifest(start)
    candidate = manifest_path.parent / "project-config.json"
    return candidate if candidate.is_file() else None


def resolve_project_config(root: Path) -> dict:
    """Load project-config.json for a `--path root` validation run: checks
    `root/project-config.json` first (so a self-contained test/example vault
    is respected even if it lives outside the real kit tree), then falls back
    to load_project_config()'s own discovery (walk up from this script's
    location). Returns {} — full mode, no filtering — if neither is found."""
    local = Path(root) / "project-config.json"
    if local.is_file():
        with open(local, encoding="utf-8") as f:
            return json.load(f)
    return load_project_config()


@lru_cache(maxsize=8)
def load_project_config(path: str | None = None) -> dict:
    """Load project-config.json. Returns {} if the file does not exist —
    callers should treat an empty dict identically to "no profile selected"."""
    config_path = find_project_config(Path(path) if path else None)
    if config_path is None:
        return {}
    with open(config_path, encoding="utf-8") as f:
        return json.load(f)


def active_profile(config: dict | None = None, manifest: dict | None = None) -> str | None:
    """Return the active profile name, or None if no profile is selected
    (full mode — every type enabled). Raises ProfileConfigError on an
    unrecognized profile name."""
    config = config if config is not None else load_project_config()
    manifest = manifest or load_manifest()
    profile = config.get("profile")
    if profile is None:
        return None
    known = _named_defs(manifest, "profiles")
    if profile not in known:
        raise ProfileConfigError(
            f"project-config.json declares profile '{profile}', which is not defined in "
            f"kit-manifest.json's 'profiles' section (known: {', '.join(sorted(known)) or '(none)'})."
        )
    return profile


def active_flags(config: dict | None = None, manifest: dict | None = None) -> list[str]:
    """Return the active flags list. Raises ProfileConfigError on an unknown
    flag name, or a profile+flag combination kit-manifest.json forbids
    (e.g. profile S + flag compliance)."""
    config = config if config is not None else load_project_config()
    manifest = manifest or load_manifest()
    flags = list(config.get("flags") or [])
    known_flags = _named_defs(manifest, "flags")
    for flag in flags:
        if flag not in known_flags:
            raise ProfileConfigError(
                f"project-config.json declares flag '{flag}', which is not defined in "
                f"kit-manifest.json's 'flags' section (known: {', '.join(sorted(known_flags)) or '(none)'})."
            )
    profile = active_profile(config, manifest)
    for flag in flags:
        forbidden_with = known_flags[flag].get("forbidden_with_profiles", [])
        if profile in forbidden_with:
            reason = known_flags[flag].get("forbidden_reason", "this combination is not supported.")
            raise ProfileConfigError(
                f"project-config.json combines profile '{profile}' with flag '{flag}', which is "
                f"forbidden: {reason}"
            )
    return flags


def _types_for_tiers(tiers: list[str], manifest: dict) -> set[str]:
    return {
        prefix for prefix, cfg in artifact_types(manifest).items()
        if cfg.get("tier") in tiers
    }


def enabled_types(config: dict | None = None, manifest: dict | None = None) -> set[str] | None:
    """Return the set of enabled artifact-type prefixes for the active
    profile+flags, or None if no profile is selected (full mode — every type
    is enabled; callers should treat None as "no filtering", not as "nothing
    enabled"). Raises ProfileConfigError — see active_profile/active_flags."""
    config = config if config is not None else load_project_config()
    manifest = manifest or load_manifest()
    profile = active_profile(config, manifest)
    if profile is None:
        return None
    flags = active_flags(config, manifest)

    profiles = _named_defs(manifest, "profiles")
    known_flags = _named_defs(manifest, "flags")

    types = set(profiles[profile].get("types", []))
    types |= _types_for_tiers(profiles[profile].get("tiers", []), manifest)
    for flag in flags:
        types |= _types_for_tiers(known_flags[flag].get("tiers", []), manifest)
    return types


def is_type_enabled(prefix: str, config: dict | None = None, manifest: dict | None = None) -> bool:
    """True if `prefix` is enabled under the active profile (or if no profile
    is active — full mode enables everything)."""
    types = enabled_types(config, manifest)
    return types is None or prefix in types


def profile_membership(manifest: dict | None = None) -> dict:
    """{prefix: {"profiles": [names], "flags": [names]}} — which profiles and
    flags would include a given artifact type. Used by validators to build
    "enable profile/flag X" hints for out-of-profile warnings."""
    manifest = manifest or load_manifest()
    result = {p: {"profiles": [], "flags": []} for p in artifact_types(manifest)}
    for name, pcfg in _named_defs(manifest, "profiles").items():
        types = set(pcfg.get("types", [])) | _types_for_tiers(pcfg.get("tiers", []), manifest)
        for t in types:
            result.setdefault(t, {"profiles": [], "flags": []})["profiles"].append(name)
    for name, fcfg in _named_defs(manifest, "flags").items():
        types = _types_for_tiers(fcfg.get("tiers", []), manifest)
        for t in types:
            result.setdefault(t, {"profiles": [], "flags": []})["flags"].append(name)
    return result


def out_of_profile_hint(prefix: str, manifest: dict | None = None) -> str:
    """Human-readable "enable ..." hint for a type outside the active profile."""
    membership = profile_membership(manifest).get(prefix, {"profiles": [], "flags": []})
    parts = []
    if membership["profiles"]:
        parts.append(f"profile {'/'.join(sorted(membership['profiles']))}")
    if membership["flags"]:
        parts.append(f"flag {'/'.join(sorted(membership['flags']))}")
    if not parts:
        return "no profile or flag currently includes this type"
    return "enable " + " or ".join(parts)


if __name__ == "__main__":
    m = load_manifest()
    print(f"kit-manifest.json v{m['kit_version']} — {len(m['artifact_types'])} artifact types")
    for prefix, cfg in m["artifact_types"].items():
        life = "lifecycle" if cfg.get("has_lifecycle", True) else "no-lifecycle"
        print(f"  {prefix:14s} {cfg['tier']:13s} {life:12s} {cfg['folder']}")

    print()
    for name, pcfg in _named_defs(m, "profiles").items():
        resolved = set(pcfg.get("types", [])) | _types_for_tiers(pcfg.get("tiers", []), m)
        print(f"  profile {name}: {len(resolved)} types — {', '.join(sorted(resolved))}")
    for name, fcfg in _named_defs(m, "flags").items():
        resolved = _types_for_tiers(fcfg.get("tiers", []), m)
        print(f"  flag {name}: adds {len(resolved)} types — {', '.join(sorted(resolved))}")
