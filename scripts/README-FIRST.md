# Read Me First

## First 30 Minutes

1. Copy this kit into your repository (monorepo recommended).
2. Open `README.md` for a full overview.
3. Read `00-meta/sdlc-pipeline.md` to understand the AI SDLC stages and approval gates.
4. Review `00-meta/status-transitions.md` for valid state machines.
5. Review templates in `00-meta/templates/`.
6. Duplicate `EPIC-INGEST-001.md` and `FR-INGEST-001.md` as your first real artifacts — replace example IDs, owners, and domains.
7. Update `00-meta/taxonomy/domains.md` with your domains and components.
8. Create a glossary file in `00-meta/glossary/` for your first domain.
9. Update `03-architecture/code-map/` to map your components to source paths.
10. Configure agent instruction files with your repo-specific paths (see AI Agent Setup below).

## First Useful Views in Obsidian

- Requirements by status
- Missing verification (`verified_by` is empty)
- Approved but not implemented
- NFRs by quality attribute
- Tasks by status (backlog, ready, in-progress, done)
- Orphan artifacts (no upstream link)

## Validation Scripts

Install dependencies and run:

```bash
pip install pyyaml jsonschema

# Validate frontmatter
python scripts/validate-frontmatter.py --path .

# Check orphans and broken links
python scripts/check-orphans.py --path .

# Check status consistency
python scripts/check-status-transitions.py --path .

# Regenerate traceability map
python scripts/generate-traceability.py --path .
```

## Recommended Git Workflow

- One requirement change per branch.
- Review all `approved` status transitions through pull requests.
- Require a human reviewer for ADR updates.
- Run validation scripts in CI (see `scripts/` README for GitHub Actions example).
- Use Change Requests (CR) for modifications to approved artifacts.

## AI Agent Setup

1. For **Claude Code**: ensure `CLAUDE.md` is in the repo root (or vault root). Claude Code reads it automatically.
2. For **Codex**: place instructions in `.codex/instructions.md`.
3. For **Cursor**: place rules in `.cursor/rules/requirements-vault.mdc`.
4. For **Kiro**: place steering files in `.kiro/`.
5. Use agent prompts from `scripts/agent-prompts.md` for specific roles (analyst, planner, QA, etc.).
6. For autonomous operation: agents pick up tasks from `04-delivery/tasks/` with `status: ready`.
