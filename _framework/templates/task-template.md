---
id: TASK-XXX-000
title: ""
status: backlog
owner: ""
assigned_to: ""
implements: "[[FR-XXX-000]]"
part_of_story: "[[US-XXX-000]]"
acceptance_criteria_subset: []
target_files: []
estimated_complexity: medium
updated: YYYY-MM-DD
---

# Objective

What this task accomplishes in one or two sentences.

# Implementation Notes

Guidance for the implementing agent: approach, constraints, patterns to follow.

# Target Files

- `src/path/to/file.ts` — what changes here
- `tests/path/to/file.test.ts` — test coverage

# Acceptance Criteria Covered

The AC IDs this task covers are listed in `acceptance_criteria_subset` in the
frontmatter (e.g., `[AC-1, AC-2]`). Read the full criterion text from the parent
User Story [[US-XXX-000]] — do not copy AC text here, it drifts when the US is
edited. (`scripts/assemble-context.py TASK-XXX-000` inlines the AC text for you.)

# Done Checklist

- [ ] Code implements all listed acceptance criteria
- [ ] Unit tests written and passing
- [ ] No existing tests broken
- [ ] Frontmatter updated (status)
- [ ] Validation scripts pass (`python scripts/validate-frontmatter.py`)
