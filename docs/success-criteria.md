# Success Criteria: Requirements as Code Kit

> Version: 0.1 | Date: 2026-03-29
> Goal: evaluate the effectiveness of the Requirements as Code approach when working with AI Coding Agents

---

## 1. Agent Comprehension

**What we check:** whether the AI agent is able to find, read, and correctly interpret requirements from the vault.

| # | Criterion | How to measure | Target value |
|---|----------|-------------|-----------------|
| 1.1 | Agent finds the relevant TASK and linked FR without a manually specified path | Give the agent only the task ID — check whether it found the FR, US, ADR | 100% of cases |
| 1.2 | Agent correctly extracts Acceptance Criteria from the markdown body | Compare the list of AC extracted by the agent against the reference | ≥95% of AC extracted correctly |
| 1.3 | Agent respects the "Out of Scope" section and does not implement extra functionality | Check whether the code contains functionality explicitly excluded in the FR | 0 out-of-scope violations |
| 1.4 | Agent reads and applies ADR constraints | Give a task with a linked ADR — check that the architectural decision is respected | 100% of ADR constraints respected |
| 1.5 | Agent uses the glossary for naming in the code | Check function/class names against `code_name` from the glossary | ≥90% matches |

---

## 2. Output Quality

**What we check:** whether the structured requirements lead to higher-quality code compared to ad-hoc prompts.

| # | Criterion | How to measure | Target value |
|---|----------|-------------|-----------------|
| 2.1 | Acceptance Criteria coverage in the code | % of AC from the US that have a corresponding implementation | ≥95% |
| 2.2 | AC coverage by automated tests | % of AC for which the agent wrote tests | ≥90% |
| 2.3 | Reduction in the number of rework iterations | How many "review → fix" cycles until PR acceptance (compared to the baseline without the kit) | ≤2 iterations (vs 4-5 without the kit) |
| 2.4 | Compliance with architectural constraints | % of generated code that conforms to the ADR and architecture-overview | ≥95% |
| 2.5 | No "hallucinations" in the implementation | Number of functions/endpoints that are not in the requirements | 0 unrequested additions |

---

## 3. Traceability

**What we check:** whether the chain of links BRQ → [CTRL →] Epic → FR ↔ US → Task → Code → Test is preserved (FR and US are peer-level, linked via `delivers`/`delivered_by`).

| # | Criterion | How to measure | Target value |
|---|----------|-------------|-----------------|
| 3.1 | No orphaned artifacts | `check-orphans.py` after a full implementation cycle | 0 orphans |
| 3.2 | Agent updates `implemented_by` in the FR after implementation | Check whether the agent added file references to the FR frontmatter | 100% of implemented FR updated |
| 3.3 | Agent updates statuses (TASK → done, FR → implemented) | `check-status-transitions.py` after implementation | 0 state machine violations |
| 3.4 | Traceability map generates without errors | `generate-traceability.py` runs successfully | 0 broken links |
| 3.5 | Each test is linked to specific AC-N | Check that TEST files reference specific AC | 100% of tests have an AC link |

---

## 4. Cross-Agent Portability

**What we check:** whether different agents work equally well with the same vault.

| # | Criterion | How to measure | Target value |
|---|----------|-------------|-----------------|
| 4.1 | All 4 agents successfully find and read the requirements | The same TASK — give it to each agent | 4/4 agents successful |
| 4.2 | Implementation results are comparable | Compare AC coverage across agents on the same task | Spread ≤10% |
| 4.3 | Instruction files are sufficient without additional prompts | Agent works solely on the basis of CLAUDE.md / instructions.md / etc. | No manual prompt required |
| 4.4 | Validation scripts work with the output of each agent | Run validate + check-orphans after each agent | 0 validation errors |

---

## 5. Process Efficiency

**What we check:** whether the kit saves time and effort compared to working without it.

| # | Criterion | How to measure | Target value |
|---|----------|-------------|-----------------|
| 5.1 | Time from task to a working PR | Measure wall-clock time for tasks with the kit vs without | Reduction ≥30% |
| 5.2 | Amount of manual intervention (human-in-the-loop) | Number of manual prompt/code corrections per task | ≤3 interventions per task |
| 5.3 | Onboarding time for a new project | How many minutes from cloning the kit to the first valid FR | ≤30 minutes |
| 5.4 | Reusability of prompts from agent-prompts.md | % of prompts that work without modification | ≥80% |
| 5.5 | Token cost per task | Total input+output tokens to implement one TASK | Reduction ≥20% vs ad-hoc |

---

## 6. Scalability

**What we check:** whether the approach works as the number of requirements grows.

| # | Criterion | How to measure | Target value |
|---|----------|-------------|-----------------|
| 6.1 | Validation scripts work with 100-500 FR | Execution time of `validate-frontmatter.py` on a full vault | ≤30 seconds |
| 6.2 | Agent does not lose context with a large vault | Agent navigation accuracy with 200+ artifacts | Degradation ≤5% vs a small vault |
| 6.3 | Traceability map remains readable | `generate-traceability.py` on 500 artifacts — a human can navigate it | Subjective rating: ≥7/10 |
| 6.4 | Time for the agent to find the relevant FR in a large vault | Measure from query to finding the correct FR | ≤10 seconds |

---

## 7. Requirements Quality

**What we check:** whether the kit's structure helps write higher-quality requirements.

| # | Criterion | How to measure | Target value |
|---|----------|-------------|-----------------|
| 7.1 | Frontmatter completeness | % of required fields filled in correctly | 100% required fields |
| 7.2 | Each FR is delivered by at least one US with ≥1 AC | Check that each FR has `delivered_by` → US, and each US contains AC in the markdown body | 100% of FR have a linked US with AC |
| 7.3 | AC are testable (Given/When/Then) | Review the AC format — whether all contain specific conditions | ≥90% of AC testable |
| 7.4 | No duplication of requirements | Semantic analysis of FR for overlaps | 0 duplicates |
| 7.5 | Schema validation passes | `validate-frontmatter.py` on the entire vault | 0 schema violations |

---

## 8. Adoption & Developer Experience

**What we check:** how easy and pleasant the kit is to use in practice.

| # | Criterion | How to measure | Target value |
|---|----------|-------------|-----------------|
| 8.1 | README is sufficient for a self-guided start | An unprepared user creates their first FR from the template | Success on the first attempt |
| 8.2 | Templates are clear and require no explanation | Survey: "Is it clear what to fill in?" | ≥8/10 |
| 8.3 | Obsidian compatibility | Vault opens in Obsidian, links work, the graph renders | 100% of links working |
| 8.4 | Git-friendliness | Diffs are readable, merge conflicts are minimal | Subjective rating: ≥8/10 |
| 8.5 | Documentation covers edge cases | There are answers to "what if..." (no ADR, no test, dependency not ready) | ≥80% of common questions covered |

---

## Evaluation Methodology

### Baseline experiment

An objective evaluation of the criteria in groups 2 and 5 requires an **A/B experiment**:

- **Group A (control):** the AI agent receives the task as a text description in the prompt (ad-hoc approach).
- **Group B (treatment):** the AI agent works on the same task, but through a vault with a full chain of requirements.
- **Tasks:** 5-10 typical TASKs of varying complexity (CRUD, integration, business logic).
- **Metrics:** AC coverage, number of iterations, time, token cost.

### Scoring

For each criterion:

- **Pass** — the target value is achieved
- **Partial** — the result is within 70-99% of the target
- **Fail** — the result is below 70% of the target

**Overall kit rating:** % of criteria with a Pass status. The target threshold for production-ready: ≥75% Pass, 0 Fail in groups 1 and 3 (comprehension and traceability are critical).

---

## Prioritization

If resources are limited, check first:

1. **Group 1** (Agent Comprehension) — if the agent does not understand the requirements, nothing else matters
2. **Group 3** (Traceability) — the key advantage of the approach; without it, the kit is just templates
3. **Group 2** (Output Quality) — the ultimate goal that everything is aimed at
4. **Group 4** (Cross-Agent) — confirmation of universality
5. The remaining groups — as the kit matures
