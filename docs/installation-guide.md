# Installing & Updating the Requirements Kit via Git Subtree

> This guide explains how to add the kit to a real project and keep it in sync with the upstream repository.

## Prerequisites

- Git 1.7.11+ (subtree is built-in)
- Python 3.8+
- An existing project repository
- The kit repository URL (e.g., `git@github.com:yourorg/obsidian-requirements-kit.git`)

## Concepts

**Git subtree** merges an external repository into a subdirectory of your project. All files become regular commits in your project history. You can freely edit them, and later pull upstream updates — Git will do a three-way merge, preserving your local customizations.

### What gets updated vs. what you customize

| Layer | Location | Updated by |
|-------|----------|------------|
| Kit infrastructure | `requirements/schema/`, `requirements/scripts/`, `requirements/00-meta/templates/`, `requirements/_examples/`, `requirements/docs/` | `git subtree pull` from upstream |
| Agent instructions | `.claude/CLAUDE.md`, `.codex/instructions.md`, `.cursor/rules/*.mdc`, `.kiro/steering.md` (project root) | `install-agent-files.py` — regenerates from canonical source |
| Canonical source | `requirements/docs/agent-instructions.md` | `git subtree pull` from upstream (then re-run install script) |
| Project artifacts | `requirements/01-product/` through `requirements/05-quality/`, `requirements/00-meta/glossary/`, `requirements/00-meta/taxonomy/` | You — fully project-specific |
| Artifact structure | Frontmatter fields and markdown sections in existing artifacts | `migrate-artifacts.py` — adds missing fields/sections after kit upgrade |

### How agent instruction files work

The kit uses a **single canonical source** (`docs/agent-instructions.md`) with a `{{VAULT_PREFIX}}` placeholder for all paths. The script `install-agent-files.py` reads this file, replaces `{{VAULT_PREFIX}}` with the actual subtree path (e.g., `requirements`), and injects the result into all four agent files in the project root.

Each agent file in the project root can contain your own project-specific instructions. The script manages only the section between the markers:

```
<!-- BEGIN REQUIREMENTS-KIT (managed by install-agent-files.py — do not edit manually) -->
... generated content ...
<!-- END REQUIREMENTS-KIT -->
```

Everything outside these markers is preserved on every run.

---

## Step 1 — Initial Installation

From the root of your project repository:

```bash
# 1. Add the kit repo as a named remote
git remote add requirements-kit git@github.com:yourorg/obsidian-requirements-kit.git

# 2. Fetch the kit's history (without merging anything)
git fetch requirements-kit

# 3. Add the kit as a subtree in a chosen subdirectory
#    --prefix  = target folder inside your project
#    --squash  = collapse the kit's history into one commit (recommended)
git subtree add --prefix=requirements --squash requirements-kit main
```

This creates a `requirements/` folder in your project with the full kit contents.

### Generate agent instruction files

```bash
# Generate .claude/CLAUDE.md, .codex/instructions.md, .cursor/rules/*.mdc, .kiro/steering.md
# in the project root with correct paths
python requirements/scripts/install-agent-files.py
```

If your project already has a `.claude/CLAUDE.md`, the script appends the requirements section without touching your existing content.

### Customize for your project

```bash
# Edit the canonical source — replace {{PROJECT_NAME}}, {{DOMAIN_LIST}}, etc.
$EDITOR requirements/docs/agent-instructions.md

# Re-generate agent files with your customizations
python requirements/scripts/install-agent-files.py

# Set up your domain
$EDITOR requirements/00-meta/taxonomy/domains.md
$EDITOR requirements/00-meta/glossary/glossary.md

# Commit everything
git add requirements/ .claude/ .codex/ .cursor/ .kiro/
git commit -m "chore: install and customize requirements kit"
```

---

## Step 2 — Updating the Kit

When the upstream kit has new schemas, scripts, templates, or fixes:

```bash
# 1. Fetch the latest changes from the kit remote
git fetch requirements-kit

# 2. Pull updates into the subtree folder
git subtree pull --prefix=requirements --squash requirements-kit main

# 3. Re-generate agent files (the canonical source may have changed)
python requirements/scripts/install-agent-files.py

# 4. Migrate existing artifacts to match new schemas/templates
python requirements/scripts/migrate-artifacts.py --path requirements --dry-run   # preview
python requirements/scripts/migrate-artifacts.py --path requirements              # apply

# 5. Validate — ensure all artifacts pass the updated schemas
python requirements/scripts/validate-frontmatter.py --path requirements

# 6. Review and commit
git add requirements/ .claude/ .codex/ .cursor/ .kiro/
git commit -m "chore: upgrade requirements kit to vX.Y.Z"
```

### What happens during the update

- **Kit infrastructure** (schemas, scripts, examples) — updated cleanly by `git subtree pull`.
- **Canonical source** (`docs/agent-instructions.md`) — merged by Git. If you customized placeholders and upstream changed the same lines, you resolve a standard merge conflict in one file.
- **Agent files in project root** — regenerated by the script. Your project-specific content (above the markers) is preserved. The managed section is replaced with the latest version.
- **Project artifacts** (your requirements, user stories, etc.) — structure is upgraded by `migrate-artifacts.py`. The script adds missing frontmatter fields (with defaults from templates) and missing markdown sections. It never overwrites or removes anything you've already written.

### Resolving conflicts

If `git subtree pull` produces conflicts:

```bash
# See which files conflict
git status

# Resolve — typically only docs/agent-instructions.md if both sides changed it
$EDITOR requirements/docs/agent-instructions.md

# Complete the merge
git add requirements/
git commit

# Then regenerate agent files
python requirements/scripts/install-agent-files.py
git add .claude/ .codex/ .cursor/ .kiro/
git commit -m "chore: regenerate agent files after merge"
```

---

## Step 3 — Checking What Changed Upstream

Before pulling, you can preview what the update will bring:

```bash
# Fetch without merging
git fetch requirements-kit

# See the commit log of what changed in the kit
git log HEAD..requirements-kit/main --oneline

# See the actual diff
git diff HEAD...requirements-kit/main
```

You can also dry-run the agent file update:

```bash
python requirements/scripts/install-agent-files.py --dry-run
```

---

## Step 4 — Pinning to a Specific Version

If the kit uses tags for releases (e.g., `v0.3.0`):

```bash
# Install a specific version
git subtree add --prefix=requirements --squash requirements-kit v0.3.0

# Update to a specific version
git subtree pull --prefix=requirements --squash requirements-kit v0.3.0

# Always regenerate agent files after version change
python requirements/scripts/install-agent-files.py
```

---

## Quick Reference

| Action | Command |
|--------|---------|
| Add remote (once) | `git remote add requirements-kit <URL>` |
| Install kit | `git subtree add --prefix=requirements --squash requirements-kit main` |
| Generate agent files | `python requirements/scripts/install-agent-files.py` |
| Fetch updates | `git fetch requirements-kit` |
| Preview changes | `git log HEAD..requirements-kit/main --oneline` |
| Pull updates | `git subtree pull --prefix=requirements --squash requirements-kit main` |
| Regenerate after update | `python requirements/scripts/install-agent-files.py` |
| Migrate artifacts (preview) | `python requirements/scripts/migrate-artifacts.py --path requirements --dry-run` |
| Migrate artifacts (apply) | `python requirements/scripts/migrate-artifacts.py --path requirements` |
| Migration report | `python requirements/scripts/migrate-artifacts.py --path requirements --report` |
| Migrate required fields only | `python requirements/scripts/migrate-artifacts.py --path requirements --required-only` |
| Validate after migration | `python requirements/scripts/validate-frontmatter.py --path requirements` |
| Dry run (agent files) | `python requirements/scripts/install-agent-files.py --dry-run` |
| Pin to version | `git subtree pull --prefix=requirements --squash requirements-kit v0.3.0` |

---

## Tips

1. **Always use `--squash`** — keeps your project history clean by collapsing the kit's commits into a single merge commit.

2. **Commit before pulling** — ensures Git has a clean base for the three-way merge.

3. **Tag your kit releases** — in the kit repository, tag versions (`v0.2.1`, `v0.3.0`). This lets downstream projects pin to specific versions.

4. **Don't rename the subtree prefix** — Git subtree tracks the prefix internally. If you need a different folder name, remove and re-add.

5. **Edit `docs/agent-instructions.md`, not the root files** — the canonical source inside the vault is the single source of truth. Root agent files are generated.

6. **Run `install-agent-files.py` after every `git subtree pull`** — this ensures the agent files in the project root reflect the latest canonical source.

7. **Project-specific instructions go above the markers** — add your code-specific rules, build commands, etc. to the top of `.claude/CLAUDE.md` (or any agent file). The script only touches the content between `<!-- BEGIN REQUIREMENTS-KIT -->` and `<!-- END REQUIREMENTS-KIT -->`.

8. **Run `migrate-artifacts.py` after every `git subtree pull`** — this ensures your existing artifacts gain any new fields or sections introduced in the updated kit. The script is additive-only: it never overwrites existing values or removes sections.

9. **Use `--dry-run` and `--report` before applying** — always preview migration changes first. The `--report` flag generates a `migration-report.md` with a full list of every change per file.

10. **Track kit version with `.kit-version`** — the file `requirements/.kit-version` records which kit version is installed and when the last migration ran. Update it when upgrading.

## Removing the Kit

If you ever need to fully decouple from the upstream:

```bash
# Remove the remote — kit files stay as regular files in your repo
git remote remove requirements-kit

# Agent files in the project root also stay — you can edit them freely now
```

No data is lost. You just stop being able to pull updates.
