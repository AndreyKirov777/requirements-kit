#!/usr/bin/env python3
"""
install-agent-files.py — Install or update AI agent instruction files.

Reads the canonical source (docs/agent-instructions.md) from the kit,
replaces {{VAULT_PREFIX}} with the actual path, and injects the content
into each agent's instruction file in the project root.

Existing content outside the managed markers is preserved.

Usage:
    # Auto-detect: finds the project root (nearest .git above this script)
    python requirements/scripts/install-agent-files.py

    # Explicit prefix (relative to project root)
    python requirements/scripts/install-agent-files.py --prefix requirements

    # Dry run — show what would change without writing
    python requirements/scripts/install-agent-files.py --dry-run
"""

import argparse
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from kit_manifest import (
    load_manifest,
    resolve_project_config,
    active_profile,
    active_flags,
    ProfileConfigError,
)

# --- Markers ------------------------------------------------------------------

BEGIN_MARKER = "<!-- BEGIN REQUIREMENTS-KIT (managed by install-agent-files.py — do not edit manually) -->"
END_MARKER = "<!-- END REQUIREMENTS-KIT -->"

# Profile-conditional blocks inside docs/agent-instructions.md (v2.2.0+).
# <!-- IF-PROFILE S --> ... <!-- END-IF -->   kept only when the active profile is S
# <!-- IF-PROFILE M L --> ... <!-- END-IF --> kept when the active profile is M or L
# <!-- IF-FLAG compliance --> ... <!-- END-IF --> kept when the "compliance" flag is active
# Blocks are flat (no nesting). In full mode (no profile selected) every
# block is kept, matching pre-2.2.0 output exactly.
CONDITIONAL_BLOCK_RE = re.compile(
    r"<!-- IF-(PROFILE|FLAG) ([^>]+?) -->\n(.*?)<!-- END-IF -->\n?", re.DOTALL
)

# --- Agent targets ------------------------------------------------------------
# Each entry: (file path relative to project root, header for new files)

AGENT_TARGETS = [
    {
        "path": ".claude/CLAUDE.md",
        "header": "# Project Instructions\n\n<!-- Add your project-specific instructions above the REQUIREMENTS-KIT section -->\n",
        "comment": None,
    },
    {
        "path": ".codex/instructions.md",
        "header": "# Project Instructions\n\n<!-- Add your project-specific instructions above the REQUIREMENTS-KIT section -->\n",
        "comment": None,
    },
    {
        "path": ".cursor/rules/requirements-vault.mdc",
        "header": "",
        "comment": None,
    },
    {
        "path": ".kiro/steering.md",
        "header": "# Project Instructions\n\n<!-- Add your project-specific instructions above the REQUIREMENTS-KIT section -->\n",
        "comment": None,
    },
]

# --- Helpers ------------------------------------------------------------------


def find_project_root(start: Path) -> Path:
    """Walk up from `start` until we find a .git directory."""
    current = start.resolve()
    while current != current.parent:
        if (current / ".git").exists():
            return current
        current = current.parent
    # Fallback: if no .git found, assume two levels up from scripts/
    return start.resolve().parent.parent


def detect_prefix(project_root: Path, script_path: Path) -> str:
    """Detect the vault prefix from the script's own location.

    If the script lives at <root>/requirements/scripts/install-agent-files.py,
    then the prefix is "requirements".
    """
    try:
        rel = script_path.resolve().parent.parent.relative_to(project_root)
        return str(rel) if str(rel) != "." else ""
    except ValueError:
        return ""


def read_canonical_source(vault_path: Path) -> str:
    """Read docs/agent-instructions.md from the vault."""
    source = vault_path / "docs" / "agent-instructions.md"
    if not source.exists():
        print(f"ERROR: Canonical source not found: {source}", file=sys.stderr)
        sys.exit(1)
    return source.read_text(encoding="utf-8")


def filter_conditional_blocks(text: str, profile: str | None, flags: list[str]) -> str:
    """Strip IF-PROFILE / IF-FLAG blocks that don't apply to the active
    profile+flags.

    Full mode (profile is None) must reproduce the pre-2.2.0 document
    byte-for-byte, so it is NOT simply "keep every block": IF-FLAG blocks are
    purely additive (the compliance/sources content they gate was always
    present, unconditionally, before flags existed) and are always kept.
    IF-PROFILE blocks are kept in full mode UNLESS the block is gated
    exclusively to "S" — S-only phrasing exists to describe the ABSENCE of
    FR/NFR/EPIC/CON/CR, which is meaningless in full mode where every type is
    present; every other profile combination (e.g. "M L") represents content
    that existed unconditionally pre-2.2.0 and is kept.
    """

    def replace(match: re.Match) -> str:
        kind, names_str, content = match.group(1), match.group(2), match.group(3)
        names = names_str.split()
        if kind == "FLAG":
            if profile is None:
                return content
            return content if any(name in flags for name in names) else ""
        # PROFILE
        if profile is None:
            return content if any(name != "S" for name in names) else ""
        return content if profile in names else ""

    return CONDITIONAL_BLOCK_RE.sub(replace, text)


def replace_prefix(content: str, prefix: str) -> str:
    """Replace {{VAULT_PREFIX}} and strip leading ./ if prefix is empty."""
    if prefix:
        return content.replace("{{VAULT_PREFIX}}", prefix)
    else:
        # Kit is at repo root — remove prefix placeholder and trailing slash
        return content.replace("{{VAULT_PREFIX}}/", "").replace("{{VAULT_PREFIX}}", ".")


def build_managed_block(instructions: str) -> str:
    """Wrap instructions in BEGIN/END markers."""
    return f"{BEGIN_MARKER}\n{instructions}\n{END_MARKER}"


def inject_into_file(file_path: Path, managed_block: str, header: str, dry_run: bool) -> str:
    """Inject or replace the managed block in the target file.

    Returns a status string: 'created', 'updated', or 'unchanged'.
    """
    if file_path.exists():
        existing = file_path.read_text(encoding="utf-8")

        if BEGIN_MARKER in existing and END_MARKER in existing:
            # Replace existing managed block
            before = existing[: existing.index(BEGIN_MARKER)]
            after = existing[existing.index(END_MARKER) + len(END_MARKER) :]
            new_content = before + managed_block + after
        else:
            # Append managed block to existing file
            separator = "\n\n" if existing.strip() else ""
            new_content = existing.rstrip() + separator + managed_block + "\n"

        if new_content == existing:
            return "unchanged"

        if not dry_run:
            file_path.write_text(new_content, encoding="utf-8")
        return "updated"
    else:
        # Create new file with header + managed block
        new_content = header + managed_block + "\n"
        if not dry_run:
            file_path.parent.mkdir(parents=True, exist_ok=True)
            file_path.write_text(new_content, encoding="utf-8")
        return "created"


# --- Main ---------------------------------------------------------------------


def main():
    parser = argparse.ArgumentParser(
        description="Install or update AI agent instruction files from the requirements kit."
    )
    parser.add_argument(
        "--prefix",
        help="Vault prefix relative to project root (e.g., 'requirements'). Auto-detected if omitted.",
    )
    parser.add_argument(
        "--project-root",
        help="Project root directory. Auto-detected if omitted.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would change without writing files.",
    )
    parser.add_argument(
        "--profile",
        choices=["S", "M", "L"],
        help="Override the active scale profile for this run (ignores project-config.json). Mainly for testing.",
    )
    parser.add_argument(
        "--flags",
        nargs="*",
        default=None,
        help="Override the active flags for this run (space-separated, e.g. --flags compliance). Requires --profile.",
    )
    args = parser.parse_args()

    if args.flags is not None and args.profile is None:
        print("ERROR: --flags requires --profile.", file=sys.stderr)
        sys.exit(1)

    script_path = Path(__file__)

    # Determine project root
    if args.project_root:
        project_root = Path(args.project_root).resolve()
    else:
        project_root = find_project_root(script_path)

    # Determine prefix
    if args.prefix is not None:
        prefix = args.prefix
    else:
        prefix = detect_prefix(project_root, script_path)

    vault_path = project_root / prefix if prefix else project_root

    # Determine active profile/flags: CLI override takes precedence over
    # project-config.json (which resolve_project_config looks up at vault_path).
    if args.profile is not None:
        profile, flags = args.profile, list(args.flags or [])
    else:
        try:
            project_config = resolve_project_config(vault_path)
            manifest = load_manifest()
            profile = active_profile(project_config, manifest)
            flags = active_flags(project_config, manifest)
        except ProfileConfigError as e:
            print(f"ERROR: invalid project-config.json — {e}", file=sys.stderr)
            sys.exit(1)

    print(f"Project root : {project_root}")
    print(f"Vault prefix : {prefix or '(root)'}")
    print(f"Vault path   : {vault_path}")
    print(f"Profile      : {profile or '(full — every type enabled)'}")
    if flags:
        print(f"Flags        : {', '.join(flags)}")
    if args.dry_run:
        print("Mode         : DRY RUN (no files will be written)")
    print()

    # Read and process canonical source
    raw_instructions = read_canonical_source(vault_path)
    filtered_instructions = filter_conditional_blocks(raw_instructions, profile, flags)
    instructions = replace_prefix(filtered_instructions, prefix)

    # Build the managed block
    managed_block = build_managed_block(instructions)

    # Inject into each agent file
    results = []
    for target in AGENT_TARGETS:
        file_path = project_root / target["path"]
        status = inject_into_file(file_path, managed_block, target["header"], args.dry_run)
        results.append((target["path"], status))
        icon = {"created": "+", "updated": "~", "unchanged": "="}[status]
        print(f"  [{icon}] {target['path']} — {status}")

    print()
    created = sum(1 for _, s in results if s == "created")
    updated = sum(1 for _, s in results if s == "updated")
    unchanged = sum(1 for _, s in results if s == "unchanged")
    print(f"Done: {created} created, {updated} updated, {unchanged} unchanged.")

    if args.dry_run and (created + updated) > 0:
        print("\nRe-run without --dry-run to apply changes.")


if __name__ == "__main__":
    main()
