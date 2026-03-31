#!/usr/bin/env bash
# ──────────────────────────────────────────────────────────────
# pull-kit-update.sh — Pull upstream kit updates via git subtree
#                      and run all post-update scripts.
#
# Usage:
#   ./requirements/scripts/pull-kit-update.sh              # from main branch
#   ./requirements/scripts/pull-kit-update.sh v0.5.0       # pin to a tag
#   ./requirements/scripts/pull-kit-update.sh --dry-run     # preview only
#
# Expects:
#   - Git remote "requirements-kit" already configured
#   - Subtree prefix = "requirements" (override with KIT_PREFIX env var)
#   - Python 3.8+ with pyyaml installed
# ──────────────────────────────────────────────────────────────
set -euo pipefail

# ── Configuration ─────────────────────────────────────────────

REMOTE="${KIT_REMOTE:-requirements-kit}"
PREFIX="${KIT_PREFIX:-requirements}"
BRANCH="main"
DRY_RUN=false

# ── Parse arguments ───────────────────────────────────────────

for arg in "$@"; do
  case "$arg" in
    --dry-run)  DRY_RUN=true ;;
    --help|-h)
      sed -n '2,/^# ──/{ /^# ──/d; s/^# \?//p; }' "$0"
      exit 0
      ;;
    *)          BRANCH="$arg" ;;
  esac
done

# ── Detect Python ─────────────────────────────────────────────
# macOS ships with python3 only; python is not aliased by default.

if command -v python3 &>/dev/null; then
  PYTHON=python3
elif command -v python &>/dev/null; then
  PYTHON=python
else
  echo "ERROR: Neither python3 nor python found in PATH." >&2
  exit 1
fi

# ── Helpers ───────────────────────────────────────────────────

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
BOLD='\033[1m'
NC='\033[0m'

step()  { echo -e "\n${CYAN}${BOLD}[$1/$TOTAL]${NC} ${BOLD}$2${NC}"; }
info()  { echo -e "  ${GREEN}✓${NC} $1"; }
warn()  { echo -e "  ${YELLOW}⚠${NC} $1"; }
fail()  { echo -e "  ${RED}✗${NC} $1"; exit 1; }
dry()   { if $DRY_RUN; then echo -e "  ${YELLOW}[DRY RUN]${NC} would run: $*"; else "$@"; fi; }

TOTAL=7

# ── Preflight checks ─────────────────────────────────────────

step 0 "Preflight checks"

# Must be in a git repo
git rev-parse --git-dir > /dev/null 2>&1 || fail "Not inside a git repository."

# Find project root
PROJECT_ROOT="$(git rev-parse --show-toplevel)"
cd "$PROJECT_ROOT"

# Remote must exist
git remote get-url "$REMOTE" > /dev/null 2>&1 || fail "Remote '$REMOTE' not found. Run: git remote add $REMOTE <URL>"

# Subtree prefix must exist
[ -d "$PREFIX" ] || fail "Subtree prefix '$PREFIX/' not found in project root."

# Working tree must be clean
if [ -n "$(git status --porcelain)" ]; then
  fail "Working tree is dirty. Commit or stash changes before upgrading."
fi

# Read current version
if [ -f "$PREFIX/.kit-version" ]; then
  CURRENT_VERSION=$(head -1 "$PREFIX/.kit-version" | tr -d '[:space:]')
else
  CURRENT_VERSION="unknown"
fi

info "Project root:    $PROJECT_ROOT"
info "Kit prefix:      $PREFIX/"
info "Remote:          $REMOTE"
info "Target branch:   $BRANCH"
info "Current version: $CURRENT_VERSION"

if $DRY_RUN; then
  warn "DRY RUN mode — no changes will be written"
fi

# ── Step 1: Fetch ─────────────────────────────────────────────

step 1 "Fetching from $REMOTE"
dry git fetch "$REMOTE"

if ! $DRY_RUN; then
  UPSTREAM_LOG=$(git log "HEAD..${REMOTE}/${BRANCH}" --oneline 2>/dev/null || true)
  if [ -z "$UPSTREAM_LOG" ]; then
    info "No new commits upstream. Kit is up to date."
    exit 0
  fi
  echo "$UPSTREAM_LOG" | head -15
  COMMIT_COUNT=$(echo "$UPSTREAM_LOG" | wc -l | tr -d ' ')
  info "$COMMIT_COUNT new commit(s) from upstream"
fi

# ── Step 2: Subtree pull ─────────────────────────────────────

step 2 "Pulling subtree updates (--squash)"
dry git subtree pull --prefix="$PREFIX" --squash "$REMOTE" "$BRANCH"

# If subtree pull left conflicts, stop early
if ! $DRY_RUN && [ -n "$(git diff --name-only --diff-filter=U 2>/dev/null)" ]; then
  warn "Merge conflicts detected. Resolve them, then re-run this script."
  echo ""
  echo "  Conflicting files:"
  git diff --name-only --diff-filter=U | sed 's/^/    /'
  echo ""
  echo "  After resolving:"
  echo "    git add $PREFIX/"
  echo "    git commit"
  echo "    $0 $*"
  exit 1
fi

# ── Step 3: Structural migrations ────────────────────────────

step 3 "Running structural migrations (upgrade-kit.py)"
if $DRY_RUN; then
  dry $PYTHON "$PREFIX/scripts/upgrade-kit.py" --dry-run
else
  $PYTHON "$PREFIX/scripts/upgrade-kit.py"
fi

# ── Step 4: Agent instruction files ──────────────────────────

step 4 "Regenerating agent instruction files"
if $DRY_RUN; then
  dry $PYTHON "$PREFIX/scripts/install-agent-files.py" --dry-run
else
  $PYTHON "$PREFIX/scripts/install-agent-files.py"
fi

# ── Step 5: Artifact migration ────────────────────────────────

step 5 "Migrating artifacts"
if $DRY_RUN; then
  $PYTHON "$PREFIX/scripts/migrate-artifacts.py" --path "$PREFIX" --dry-run
else
  # Always preview first
  echo -e "  ${CYAN}Preview:${NC}"
  $PYTHON "$PREFIX/scripts/migrate-artifacts.py" --path "$PREFIX" --dry-run 2>&1 | sed 's/^/    /'

  # Check if there are actual changes to apply.
  # migrate-artifacts.py uses markers: [!] (required field), [+] (optional field),
  # [§] (section), and summary line "Modified: N files".
  PREVIEW_OUTPUT=$($PYTHON "$PREFIX/scripts/migrate-artifacts.py" --path "$PREFIX" --dry-run 2>&1)
  if echo "$PREVIEW_OUTPUT" | grep -qE '\[!\]|\[\+\]|\[§\]|Modified: [1-9]'; then
    echo ""
    read -rp "  Apply artifact migrations? [y/N] " CONFIRM
    if [[ "$CONFIRM" =~ ^[Yy]$ ]]; then
      $PYTHON "$PREFIX/scripts/migrate-artifacts.py" --path "$PREFIX"
      info "Artifact migrations applied"
    else
      warn "Artifact migrations skipped (run manually: $PYTHON $PREFIX/scripts/migrate-artifacts.py --path $PREFIX)"
    fi
  else
    info "No artifact migrations needed"
  fi
fi

# ── Step 6: Validation ────────────────────────────────────────

step 6 "Validating frontmatter"
if $DRY_RUN; then
  dry $PYTHON "$PREFIX/scripts/validate-frontmatter.py" --path "$PREFIX"
else
  if $PYTHON "$PREFIX/scripts/validate-frontmatter.py" --path "$PREFIX"; then
    info "All artifacts pass validation"
  else
    warn "Validation errors found — review output above"
  fi
fi

# ── Step 7: Commit ────────────────────────────────────────────

step 7 "Committing changes"

if $DRY_RUN; then
  dry echo "git add + git commit"
else
  # Read new version
  if [ -f "$PREFIX/.kit-version" ]; then
    NEW_VERSION=$(head -1 "$PREFIX/.kit-version" | tr -d '[:space:]')
  else
    NEW_VERSION="$BRANCH"
  fi

  # Check if there's anything to commit
  if [ -z "$(git status --porcelain)" ]; then
    info "Nothing to commit — all changes were part of the subtree merge"
  else
    git add "$PREFIX/" .claude/ .codex/ .cursor/ .kiro/ 2>/dev/null || true
    git commit -m "chore: upgrade requirements kit to v${NEW_VERSION}"
    info "Committed: chore: upgrade requirements kit to v${NEW_VERSION}"
  fi
fi

# ── Done ──────────────────────────────────────────────────────

echo ""
echo -e "${GREEN}${BOLD}Kit upgrade complete.${NC}"
if [ "${CURRENT_VERSION:-}" != "unknown" ] && [ -f "$PREFIX/.kit-version" ] && ! $DRY_RUN; then
  NEW_VERSION=$(head -1 "$PREFIX/.kit-version" | tr -d '[:space:]')
  echo -e "  ${CURRENT_VERSION} → ${NEW_VERSION}"
fi
