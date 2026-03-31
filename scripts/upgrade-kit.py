#!/usr/bin/env python3
"""
upgrade-kit.py — Apply structural migrations when upgrading the kit version.

Each kit version that introduced breaking structural changes (folder renames,
file moves, path updates in docs) has a corresponding migration step registered
in MIGRATIONS below. The script detects which steps have already been applied
by reading .kit-version, runs only the outstanding ones, and updates
.kit-version on success.

Usage:
    # Apply all pending migrations (auto-detects vault root)
    python requirements/scripts/upgrade-kit.py

    # Dry run — show what would happen without changing anything
    python requirements/scripts/upgrade-kit.py --dry-run

    # Target a specific vault path
    python requirements/scripts/upgrade-kit.py --path /path/to/vault

    # Show migration history and exit
    python requirements/scripts/upgrade-kit.py --status

After running this script, always re-run:
    python requirements/scripts/install-agent-files.py
    python requirements/scripts/migrate-artifacts.py
    python requirements/scripts/validate-frontmatter.py --path .

Requires: no external dependencies (stdlib only)
"""

import argparse
import re
import shutil
import sys
from datetime import date
from pathlib import Path

# ---------------------------------------------------------------------------
# Kit version file
# ---------------------------------------------------------------------------

KIT_VERSION_FILE = ".kit-version"
CURRENT_KIT_VERSION = "0.4.0"


# ---------------------------------------------------------------------------
# Migration registry
#
# Each migration is a dict:
#   version     str   — the kit version that introduced this change
#   description str   — human-readable summary
#   fn          func  — callable(vault: Path, dry_run: bool) -> list[str]
#                       Returns a list of human-readable change descriptions.
#                       Must be idempotent (safe to run twice).
# ---------------------------------------------------------------------------

def _migrate_0_4_0(vault: Path, dry_run: bool) -> list:
    """
    v0.4.0: Extract _framework/ from 00-meta/.

    Moves:
      00-meta/templates/         -> _framework/templates/
      00-meta/sdlc-pipeline.md   -> _framework/sdlc-pipeline.md
      00-meta/status-transitions.md -> _framework/status-transitions.md

    Updates path references in:
      README.md, docs/installation-guide.md, docs/agent-instructions.md,
      scripts/README-FIRST.md, scripts/agent-prompts.md, _examples/README.md
    """
    changes = []

    moves = [
        ("00-meta/templates",           "_framework/templates"),
        ("00-meta/sdlc-pipeline.md",    "_framework/sdlc-pipeline.md"),
        ("00-meta/status-transitions.md", "_framework/status-transitions.md"),
    ]

    # --- File / folder moves ---
    for src_rel, dst_rel in moves:
        src = vault / src_rel
        dst = vault / dst_rel

        if not src.exists():
            if dst.exists():
                changes.append(f"  SKIP (already done): {src_rel} → {dst_rel}")
            else:
                changes.append(f"  WARN: source not found and destination missing: {src_rel}")
            continue

        if dst.exists():
            changes.append(f"  SKIP (destination exists): {dst_rel}")
            continue

        changes.append(f"  MOVE: {src_rel} → {dst_rel}")
        if not dry_run:
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.move(str(src), str(dst))

    # --- Path replacements in text files ---
    replacements = [
        # (old_pattern, new_text)
        (r"00-meta/templates/",          "_framework/templates/"),
        (r"00-meta/sdlc-pipeline\.md",   "_framework/sdlc-pipeline.md"),
        (r"00-meta/status-transitions\.md", "_framework/status-transitions.md"),
    ]

    target_files = [
        "README.md",
        "docs/installation-guide.md",
        "docs/agent-instructions.md",
        "scripts/README-FIRST.md",
        "scripts/agent-prompts.md",
        "_examples/README.md",
    ]

    for rel in target_files:
        path = vault / rel
        if not path.exists():
            continue

        original = path.read_text(encoding="utf-8")
        updated = original

        for pattern, replacement in replacements:
            updated = re.sub(pattern, replacement, updated)

        if updated != original:
            changes.append(f"  UPDATE refs: {rel}")
            if not dry_run:
                path.write_text(updated, encoding="utf-8")
        else:
            changes.append(f"  SKIP refs (no matches): {rel}")

    return changes


MIGRATIONS = [
    {
        "version": "0.4.0",
        "description": "Extract _framework/ from 00-meta/ (templates, sdlc-pipeline, status-transitions)",
        "fn": _migrate_0_4_0,
    },
    # Add future migrations here, e.g.:
    # {
    #     "version": "0.5.0",
    #     "description": "...",
    #     "fn": _migrate_0_5_0,
    # },
]


# ---------------------------------------------------------------------------
# Version helpers
# ---------------------------------------------------------------------------

def _parse_version(v: str) -> tuple:
    """Parse 'X.Y.Z' into (int, int, int) for comparison."""
    try:
        parts = v.strip().split(".")
        return tuple(int(p) for p in parts)
    except (ValueError, AttributeError):
        return (0, 0, 0)


def _read_installed_version(vault: Path) -> str:
    """Read currently installed kit version from .kit-version, or '0.0.0'."""
    kv = vault / KIT_VERSION_FILE
    if not kv.exists():
        return "0.0.0"
    for line in kv.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if re.match(r"^\d+\.\d+\.\d+", line):
            return line.split()[0]
        m = re.match(r"^version\s*[:=]\s*(\S+)", line, re.IGNORECASE)
        if m:
            return m.group(1)
    return "0.0.0"


def _write_version(vault: Path, version: str, dry_run: bool) -> None:
    kv = vault / KIT_VERSION_FILE
    content = (
        f"{version}\n"
        f"upgraded: {date.today().isoformat()}\n"
        f"script: scripts/upgrade-kit.py\n"
    )
    if not dry_run:
        kv.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# Auto-detect vault root
# ---------------------------------------------------------------------------

def _find_vault(start: Path) -> Path:
    """
    Walk upward from start looking for a directory that looks like a kit vault
    (contains 00-meta/ or _framework/ or schema/ alongside scripts/).
    Falls back to start itself.
    """
    for candidate in [start, *start.parents]:
        if (candidate / "scripts").is_dir() and (
            (candidate / "00-meta").is_dir()
            or (candidate / "_framework").is_dir()
            or (candidate / "schema").is_dir()
        ):
            return candidate
    return start


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> int:
    parser = argparse.ArgumentParser(
        description="Apply structural kit migrations after a version upgrade.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    parser.add_argument(
        "--path",
        default=None,
        help="Path to the vault root (auto-detected from script location if omitted).",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would happen without making any changes.",
    )
    parser.add_argument(
        "--status",
        action="store_true",
        help="Show installed version, pending migrations, and exit.",
    )
    args = parser.parse_args()

    # Resolve vault root
    if args.path:
        vault = Path(args.path).resolve()
    else:
        vault = _find_vault(Path(__file__).resolve().parent)

    if not vault.is_dir():
        print(f"ERROR: vault path does not exist: {vault}")
        return 1

    installed = _read_installed_version(vault)
    installed_tuple = _parse_version(installed)

    # Filter pending migrations
    pending = [
        m for m in MIGRATIONS
        if _parse_version(m["version"]) > installed_tuple
    ]

    # --status
    if args.status:
        print(f"Vault:             {vault}")
        print(f"Installed version: {installed}")
        print(f"Current kit:       {CURRENT_KIT_VERSION}")
        print()
        if not pending:
            print("No pending migrations. Kit is up to date.")
        else:
            print(f"Pending migrations ({len(pending)}):")
            for m in pending:
                print(f"  [{m['version']}] {m['description']}")
        return 0

    # Nothing to do
    if not pending:
        print(f"Kit is already up to date (installed: {installed}, current: {CURRENT_KIT_VERSION}).")
        return 0

    # Run migrations
    mode = "[DRY RUN] " if args.dry_run else ""
    print(f"{mode}Vault: {vault}")
    print(f"{mode}Installed: {installed}  →  Target: {CURRENT_KIT_VERSION}")
    print()

    errors = []
    for m in pending:
        print(f"{'[DRY RUN] ' if args.dry_run else ''}Applying [{m['version']}]: {m['description']}")
        try:
            changes = m["fn"](vault, args.dry_run)
            for line in changes:
                print(f"  {line}" if not line.startswith("  ") else line)
        except Exception as exc:
            msg = f"  ERROR in migration {m['version']}: {exc}"
            print(msg)
            errors.append(msg)
        print()

    if errors:
        print("Migration completed with errors:")
        for e in errors:
            print(e)
        return 1

    # Update .kit-version
    _write_version(vault, CURRENT_KIT_VERSION, args.dry_run)
    if args.dry_run:
        print(f"[DRY RUN] Would write {KIT_VERSION_FILE}: {CURRENT_KIT_VERSION}")
    else:
        print(f"Updated {KIT_VERSION_FILE} → {CURRENT_KIT_VERSION}")

    print()
    print("Next steps:")
    print("  python scripts/install-agent-files.py")
    print("  python scripts/migrate-artifacts.py --dry-run")
    print("  python scripts/validate-frontmatter.py --path .")

    return 0


if __name__ == "__main__":
    sys.exit(main())
