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
import sys
from pathlib import Path

# --- Markers ------------------------------------------------------------------

BEGIN_MARKER = "<!-- BEGIN REQUIREMENTS-KIT (managed by install-agent-files.py — do not edit manually) -->"
END_MARKER = "<!-- END REQUIREMENTS-KIT -->"

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
    args = parser.parse_args()

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

    print(f"Project root : {project_root}")
    print(f"Vault prefix : {prefix or '(root)'}")
    print(f"Vault path   : {vault_path}")
    if args.dry_run:
        print("Mode         : DRY RUN (no files will be written)")
    print()

    # Read and process canonical source
    raw_instructions = read_canonical_source(vault_path)
    instructions = replace_prefix(raw_instructions, prefix)

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
