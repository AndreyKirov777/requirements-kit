---
id: META-STATUS-TRANSITIONS
title: Status Transition Rules
updated: 2026-03-28
---

# Status Transition Rules

Each artifact type has a defined state machine. Agents and humans must follow these transitions. Any transition not listed below is **invalid**.

## Product Vision (VISION)

```
draft → proposed → approved → superseded
                            → deprecated
```

| From     | To          | Trigger                                      | Who            |
| -------- | ----------- | -------------------------------------------- | -------------- |
| draft    | proposed    | Author submits vision for review             | Agent or Human |
| proposed | approved    | Product owner accepts the vision             | **Human only** |
| proposed | draft       | Reviewer requests changes                    | Human          |
| approved | superseded  | A new VISION artifact replaces this one      | Human          |
| approved | deprecated  | Product discontinued or vision no longer relevant | Human     |

> **Pipeline note:** The vision must reach `approved` before any downstream
> product-discovery or requirements-elaboration work begins (see `sdlc-pipeline.md`, Stage 1).

## Functional Requirement / NFR / Constraint (FR, NFR, CON)

```
draft → proposed → approved → in-implementation → implemented → verified
                                                                    ↓
                                                               deprecated

approved → deprecated  (via Change Request only)
verified → approved    (via Change Request — reopens for rework)
```

| From               | To                 | Trigger                       | Who            |
| ------------------ | ------------------ | ----------------------------- | -------------- |
| draft              | proposed           | Author submits for review     | Agent or Human |
| proposed           | approved           | Reviewer accepts              | **Human only** |
| proposed           | draft              | Reviewer requests changes     | Human          |
| approved           | in-implementation  | First task moves to in-progress | Agent        |
| in-implementation  | implemented        | All tasks for this requirement are done | Agent |
| implemented        | verified           | All acceptance criteria pass  | QA Agent       |
| verified           | deprecated         | Superseded or removed         | Human          |
| approved           | deprecated         | Cancelled before implementation | Human        |
| verified           | approved           | Change Request reopens it     | Human          |

## User Story (US)

```
draft → proposed → approved → in-implementation → implemented → verified
                                                                    ↓
                                                               deprecated
```

| From               | To                 | Trigger                       | Who            |
| ------------------ | ------------------ | ----------------------------- | -------------- |
| draft              | proposed           | Author submits for review     | Agent or Human |
| proposed           | approved           | Reviewer accepts              | **Human only** |
| proposed           | draft              | Reviewer requests changes     | Human          |
| approved           | in-implementation  | First related FR enters implementation | Agent |
| in-implementation  | implemented        | All related FRs implemented   | Agent          |
| implemented        | verified           | All related FRs verified      | QA Agent       |
| verified           | deprecated         | Superseded or removed         | Human          |

## Epic (EPIC)

```
draft → proposed → approved → in-progress → completed → deprecated
```

| From        | To          | Trigger                                   | Who            |
| ----------- | ----------- | ----------------------------------------- | -------------- |
| draft       | proposed    | Author submits                            | Agent or Human |
| proposed    | approved    | Reviewer accepts                          | **Human only** |
| proposed    | draft       | Reviewer requests changes                 | Human          |
| approved    | in-progress | First child requirement enters implementation | Agent     |
| in-progress | completed   | All child requirements are verified       | Agent          |
| completed   | deprecated  | Superseded                                | Human          |

## Architecture Overview (ARCH-OVERVIEW)

```
draft → proposed → approved → deprecated
```

| From     | To         | Trigger                              | Who            |
| -------- | ---------- | ------------------------------------ | -------------- |
| draft    | proposed   | Author submits for review            | Agent or Human |
| proposed | approved   | Reviewer accepts                     | **Human only** |
| proposed | draft      | Reviewer requests changes            | Human          |
| approved | deprecated | Architecture fundamentally replaced  | Human          |

> **Pipeline note:** The architecture overview must reach `approved` before domain-specific architecture documents are considered stable. Domain architectures may be drafted in parallel but should not be approved before the overview.

## Domain Architecture (ARCH-{DOMAIN}-{NNN})

```
draft → proposed → approved → deprecated
```

| From     | To         | Trigger                              | Who            |
| -------- | ---------- | ------------------------------------ | -------------- |
| draft    | proposed   | Author submits for review            | Agent or Human |
| proposed | approved   | Reviewer accepts                     | **Human only** |
| proposed | draft      | Reviewer requests changes            | Human          |
| approved | deprecated | Domain architecture replaced or removed | Human       |

> **Pipeline note:** Domain architectures link to their parent `architecture-overview.md` via the `parent_overview` frontmatter field. Changes to the overview may require review of domain architectures.

## Architecture Decision Record (ADR)

```
proposed → accepted → superseded
                   → deprecated
```

| From       | To          | Trigger                          | Who            |
| ---------- | ----------- | -------------------------------- | -------------- |
| proposed   | accepted    | Reviewer approves                | **Human only** |
| proposed   | rejected    | Reviewer rejects                 | Human          |
| accepted   | superseded  | New ADR replaces this one        | Human          |
| accepted   | deprecated  | No longer relevant               | Human          |

## Task (TASK)

```
backlog → ready → in-progress → done
                → blocked → ready
```

| From        | To          | Trigger                              | Who   |
| ----------- | ----------- | ------------------------------------ | ----- |
| backlog     | ready       | Dependencies met, requirement approved | Agent |
| ready       | in-progress | Agent picks up task                  | Agent |
| in-progress | done        | Implementation complete, tests pass  | Agent |
| in-progress | blocked     | Dependency or issue discovered       | Agent |
| blocked     | ready       | Blocker resolved                     | Agent |

## Test (TEST)

```
draft → ready → passed → failed → ready
                                → draft
```

| From   | To     | Trigger                        | Who      |
| ------ | ------ | ------------------------------ | -------- |
| draft  | ready  | Test fully specified           | QA Agent |
| ready  | passed | Test execution succeeds        | QA Agent |
| ready  | failed | Test execution fails           | QA Agent |
| failed | ready  | Defect fixed, re-run scheduled | Agent    |
| failed | draft  | Test needs redesign            | QA Agent |

## Change Request (CR)

```
proposed → approved → applied → rejected
```

| From     | To       | Trigger                    | Who            |
| -------- | -------- | -------------------------- | -------------- |
| proposed | approved | Reviewer accepts impact    | **Human only** |
| proposed | rejected | Reviewer declines          | Human          |
| approved | applied  | All affected artifacts updated | Agent      |

## Persona (PERSONA)

```
draft → proposed → approved → deprecated
```

| From     | To         | Trigger                              | Who            |
| -------- | ---------- | ------------------------------------ | -------------- |
| draft    | proposed   | Author submits for review            | Agent or Human |
| proposed | approved   | Reviewer accepts                     | **Human only** |
| proposed | draft      | Reviewer requests changes            | Human          |
| approved | deprecated | Persona no longer relevant           | Human          |

## Assumption (ASSUM)

```
unvalidated → validating → validated → invalidated
                                    → deprecated
```

| From        | To          | Trigger                        | Who            |
| ----------- | ----------- | ------------------------------ | -------------- |
| unvalidated | validating  | Validation work begins         | Agent or Human |
| validating  | validated   | Assumption confirmed           | **Human only** |
| validating  | invalidated | Assumption disproven           | Human          |
| validated   | deprecated  | No longer relevant             | Human          |
| invalidated | unvalidated | Re-evaluation needed           | Human          |

## Journey (JOURNEY)

```
draft → proposed → approved → deprecated
```

| From     | To         | Trigger                              | Who            |
| -------- | ---------- | ------------------------------------ | -------------- |
| draft    | proposed   | Author submits for review            | Agent or Human |
| proposed | approved   | Reviewer accepts                     | **Human only** |
| proposed | draft      | Reviewer requests changes            | Human          |
| approved | deprecated | Journey no longer relevant           | Human          |

## Risk (RISK)

```
open → mitigating → mitigated → closed
                  → accepted → closed
```

| From       | To         | Trigger                        | Who            |
| ---------- | ---------- | ------------------------------ | -------------- |
| open       | mitigating | Mitigation plan created        | Agent or Human |
| mitigating | mitigated  | Mitigation complete            | **Human only** |
| mitigating | accepted   | Risk accepted as-is            | Human          |
| mitigated  | closed     | Risk fully resolved            | Human          |
| accepted   | closed     | Risk acceptance confirmed      | Human          |
| closed     | open       | Risk re-emerges                | Human          |

## Release (REL)

```
planned → ready → released → rolled-back
```

| From     | To         | Trigger                              | Who            |
| -------- | ---------- | ------------------------------------ | -------------- |
| planned  | ready      | All requirements verified            | Agent          |
| ready    | released   | Release authorized                   | **Human only** |
| released | rolled-back | Defects discovered post-release      | Human          |

## Use Case (UC)

```
draft → proposed → approved → deprecated
```

| From     | To         | Trigger                              | Who            |
| -------- | ---------- | ------------------------------------ | -------------- |
| draft    | proposed   | Author submits for review            | Agent or Human |
| proposed | approved   | Reviewer accepts                     | **Human only** |
| proposed | draft      | Reviewer requests changes            | Human          |
| approved | deprecated | Use case no longer relevant          | Human          |

## Contract (CONTRACT)

```
draft → proposed → approved → deprecated
```

| From     | To         | Trigger                              | Who            |
| -------- | ---------- | ------------------------------------ | -------------- |
| draft    | proposed   | Author submits for review            | Agent or Human |
| proposed | approved   | Reviewer accepts                     | **Human only** |
| proposed | draft      | Reviewer requests changes            | Human          |
| approved | deprecated | Contract no longer applicable        | Human          |

## Data Model (DM)

```
draft → proposed → approved → deprecated
```

| From     | To         | Trigger                              | Who            |
| -------- | ---------- | ------------------------------------ | -------------- |
| draft    | proposed   | Author submits for review            | Agent or Human |
| proposed | approved   | Reviewer accepts                     | **Human only** |
| proposed | draft      | Reviewer requests changes            | Human          |
| approved | deprecated | Data model superseded or obsolete    | Human          |

## Validation Rules for Agents

1. Before changing any status, verify the transition is listed in this document.
2. Transitions marked **Human only** must not be performed by agents — agents may propose but must wait for human approval.
3. When a transition is blocked, create or update a task with `status: blocked` and describe the reason.
