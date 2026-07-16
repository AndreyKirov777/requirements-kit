# Scale Profiles Specification (S / M / L)

> **Status:** DRAFT for review — not yet implemented.
> **Target kit version:** 2.2.0
> **Date:** 2026-07-16
> **Depends on:** kit-manifest.json v2.1.0, tier model from v1.0.0

## 1. Motivation

The kit currently ships 24 artifact types across 6 top-level folders. Even the
core tier alone is 10 types. For a small project (~20–30 requirements, one or
two domains, a solo developer working with AI coding agents) this is too heavy
in three independent ways:

1. **Type count** — most types are never instantiated, but agents are told
   about all of them.
2. **Ceremony** — human gates, 5–7 statuses per type, CR required for any
   change to an approved artifact.
3. **Agent context size** — the generated agent instruction files
   (`CLAUDE.md`, `.codex/instructions.md`, …) describe every type and every
   rule. Irrelevant instruction text is not free: it dilutes the context of
   every coding-agent task and measurably hurts output quality.

The tier model introduced in v1.0.0 (`core` / `discovery` / `compliance` /
`source` / `architecture` / `delivery`) already classifies every type, but
nothing consumes it: scripts and generated instructions behave identically for
every project. This spec makes the tiers operational through **profiles**.

## 2. Design summary (decisions already made)

These decisions were made on 2026-07-16 and are fixed inputs to this spec:

- Profiles are **named presets** declared in `kit-manifest.json` and selected
  in `project-config.json`. No separate "lite kit" fork. No per-profile
  status-transition graphs.
- **S-profile composition: VISION, US, TASK, TEST, ADR** (5 types).
  - The atom of the S profile is the **User Story**, not FR — AC already live
    in the US body, so no schema redesign is needed.
  - TASK stays in S: the chain is `US → TASK → TEST`.
  - ADR stays in S: `architecture-rules.md` is generated from accepted ADRs
    and is binding on every coding-agent task; this mechanism must work at
    every scale.
- **Compliance is an orthogonal flag**, not a size step — a small project can
  be regulated too.
- **Validator behavior: artifact types outside the active profile produce a
  WARNING** (with a hint naming the tier/flag to enable), never an error —
  organic growth must not be punished.
- Ceremony simplification for S is done by **excluding CR** and softening the
  human-gate language in the generated agent instructions — not by altering
  state machines.

## 3. Concepts

### 3.1 Profile

A profile is a named set of enabled artifact types. Three profiles ship with
the kit:

| Profile | Intent | Enabled types | Count |
|---------|--------|---------------|-------|
| **S**   | Small projects, solo dev + AI agents | VISION, US, TASK, TEST, ADR | 5 |
| **M**   | Standard projects | = `core` tier: VISION, CON, EPIC, US, FR, NFR, ADR, TASK, CR, TEST | 10 |
| **L**   | Large / complex systems | `core` + `discovery` + `architecture` + `delivery` tiers | 20 |

Notes:

- S is a **subset of the core tier**, so profiles cannot be expressed purely
  as tier sets. In the manifest, S is declared as an explicit type list; M and
  L are declared as tier lists (see §5.1).
- The S chain is `VISION → US → TASK → TEST`, with ADR/architecture-rules
  alongside. There is no EPIC, FR, NFR, CON, or CR in S.
- M is exactly today's core tier — no behavior change for core types.
- L enables everything except the compliance stack and SRC.

### 3.2 Flags (orthogonal to profile)

| Flag | Adds types | Tier |
|------|-----------|------|
| `compliance` | BRQ, BR, CTRL | `compliance` |
| `sources`    | SRC           | `source` |

Flags combine with any profile. `S + compliance` is valid: a small regulated
project keeps the US → TASK → TEST chain and adds the obligation stack
(SRC/BRQ/BR/CTRL derive into… see §7.3 open question).

### 3.3 Default behavior (backward compatibility)

If `project-config.json` is absent, or has no `profile` field, **no filtering
happens**: all 24 types are enabled, all scripts behave exactly as in v2.1.0.
Existing projects upgrade to kit 2.2.0 with zero observable change.

## 4. `project-config.json` changes

```json
{
  "$comment": "profile: S | M | L. Omit for full (all types). flags: optional list.",
  "profile": "S",
  "flags": ["compliance"],
  "domains": ["auth", "catalog"],
  "owners": ["@alice"]
}
```

- `profile` (optional string, enum `S | M | L`) — selects the preset.
- `flags` (optional array, items enum `compliance | sources`) — enables
  orthogonal type groups.
- Unknown profile names or flags are a hard **error** in every script that
  reads the config (fail fast — this is project misconfiguration, not vault
  content).
- `project-config.example.json` gains the two fields with comments.

Note: `project-config.example.json` currently references
`./schema/project-config.schema.json`, which **does not exist**. Implementation
should either create that schema (recommended — it now has real structure to
validate) or drop the dangling `$schema` reference.

## 5. `kit-manifest.json` changes

### 5.1 New `profiles` section

```json
"profiles": {
  "$comment": "A profile enables a set of artifact types. 'types' lists explicit prefixes; 'tiers' pulls in every type of those tiers. A profile may use either or both. Flags are orthogonal additions selected in project-config.json.",
  "S": { "types": ["VISION", "US", "TASK", "TEST", "ADR"] },
  "M": { "tiers": ["core"] },
  "L": { "tiers": ["core", "discovery", "architecture", "delivery"] }
},
"flags": {
  "compliance": { "tiers": ["compliance"] },
  "sources":    { "tiers": ["source"] }
}
```

Resolution rule: `enabled_types = union(profile.types, types of profile.tiers,
types of each active flag)`. Special-ID types follow their tier as usual
(ARCH-OVERVIEW and ARCH are `architecture` tier → enabled in L, disabled in
S/M unless a future flag adds them).

### 5.2 `TEST.up_links.verifies` gains US as a target

```json
"verifies": { "targets": ["FR", "NFR", "US"], "cardinality": "many" }
```

This closes the S chain (`TEST → US`). It is an **additive** change: existing
vaults where every TEST points at FR/NFR remain valid. In M/L projects,
pointing a TEST directly at a US is now also legal — the recommended practice
(TEST verifies FR/NFR; `covers_criteria` maps to AC in the US) stays in the
agent instructions as guidance, not as a hard rule.

`test.schema.json` needs **no change**: `verifies` items are plain strings;
target-type checking is manifest-driven.

### 5.3 No other up-link changes

`TASK.part_of_story → US` already exists and carries the S chain.
`US.delivers → FR` remains declared even though FR is disabled in S — links to
disabled types are simply never instantiated. Scripts must tolerate declared
up-links whose target types are outside the active profile.

## 6. Schema changes

Two required-field constraints currently make the S profile impossible. Both
fixes are relaxations of the shared schema (schemas encode the **union** of
what any profile allows; profile-specific expectations are enforced as
warnings by profile-aware scripts, per §8).

### 6.1 `task.schema.json` — `implements` no longer unconditionally required

Today: `required: [..., "implements", ...]`. In S there is no FR/NFR to
implement.

Change: remove `implements` from `required`; add

```json
"anyOf": [
  { "required": ["implements"] },
  { "required": ["part_of_story"] }
]
```

A TASK must link upward to *something* — an FR/NFR or a US. Profile-aware
orphan checking (§8.2) adds the stricter per-profile expectation (in M/L a
TASK without `implements` is still flagged).

### 6.2 `user-story.schema.json` — `persona` no longer required

Today `persona` is in `required`, but PERSONA is a **discovery-tier** type —
this is a latent inconsistency in v2.1.0 that profiles surface: even an
M-profile (core-only) project cannot legally author a US today without a
persona link pointing at a type it doesn't use.

Change: remove `persona` from `required`. The field stays in `properties`; in
S (and core-only M) authors may either omit it or fill it with a plain-text
actor name ("Developer", "Operator") instead of a wiki link. Profile-aware
checking warns when the `discovery` tier is active but a US lacks a persona
link.

### 6.3 No other schema changes

FR/NFR/EPIC/CR and all other schemas are untouched. Status enums, transition
graphs, and `human_gate_statuses` in the manifest are untouched (per the "no
per-profile state machines" decision).

## 7. S-profile semantics

### 7.1 Trace chain

```
VISION
  └─ US  (carries Acceptance Criteria in body)
      └─ TASK  (part_of_story → US; acceptance_criteria_subset picks AC)
           └─ TEST (verifies → US; covers_criteria picks AC)

ADR (accepted) ──▶ architecture-rules.md  (binding on every TASK)
```

- US is the root requirement artifact. `parent_epic`, `persona`, `delivers`
  are all unused (and now optional).
- TASK links via `part_of_story` only. `implements` is unused.
- TEST links via `verifies → US` and maps AC via `covers_criteria`.
- ADR lifecycle and the `# Rules` → `architecture-rules.md` generator work
  unchanged. `related_requirements` on an ADR (targets FR/NFR) is simply left
  empty in S.

### 7.2 Ceremony in S

- **CR is excluded.** Changes to an `approved` US go through a normal PR with
  human review instead of a CR artifact. The generated agent instructions for
  S must say exactly that (agents still must not silently edit approved
  artifacts — they stop and ask, the human approves via PR).
- **Human gates are unchanged in the manifest** (US still passes through
  `proposed`). The S agent instructions keep one gate prominent — "do not
  transition US to `approved` without human review" — and drop the
  gate-related text for types that don't exist in S.
- Status machines are unchanged. `draft → proposed → approved` is two steps;
  that is already cheap.

### 7.3 S + compliance (open question — needs a decision at review)

With `S + compliance`, BRQ/BR/CTRL become enabled, but their downstream link
(`FR/NFR.derives_from`) has no home because FR/NFR are disabled. Options:

- **(a)** Add `derives_from` (targets BRQ, BR, CTRL) to the US schema +
  manifest, used only when compliance flag is on. US then carries the
  obligation link directly. One added optional field; keeps S small.
- **(b)** Rule: `compliance` flag requires profile M or L (error in config
  validation if combined with S). Simplest, but contradicts "small regulated
  projects exist".

Recommendation: **(a)** — one optional field on US is a small price for
keeping the compliance flag truly orthogonal. TEST already has
`verifies_control` for CTRL evidence, which works in S unchanged.

## 8. Script changes

### 8.1 `kit_manifest.py` (shared loader) — new profile API

New helpers (single implementation point for every other script):

```python
load_project_config(path=None) -> dict   # {} if file absent
active_profile(config, manifest) -> str | None    # None = no filtering
enabled_types(config=None, manifest=None) -> set[str]
    # all types when profile is None; resolved per §5.1 otherwise
```

Config discovery mirrors `find_manifest()` (walk up from the vault root).
Unknown profile/flag values raise with a clear message (§4).

### 8.2 `check-orphans.py` — profile-aware rules + manifest-driven cleanup

This script currently hardcodes FR/NFR/TASK/TEST logic. Two changes:

1. **Profile-aware expectations table:**

   | Check | Full / M / L | S |
   |-------|--------------|---|
   | Requirement without TEST | FR/NFR without incoming `verifies` | **US** without incoming `verifies` |
   | Requirement without TASK | FR/NFR `approved`/`in-implementation` without incoming `implements` | US `approved`/`in-implementation` without incoming `part_of_story` |
   | TASK orphan | no `implements` | no `part_of_story` |
   | TEST orphan | no `verifies` | no `verifies` (unchanged) |
   | US without `parent_epic` | (not checked today — keep) | not an issue |

2. **Out-of-profile artifact = WARNING.** When a file's type prefix is not in
   `enabled_types()`, report
   `PROFILE WARNING: FR-AUTH-001 is type FR, outside profile S — enable a profile/flag that includes FR (M, L)`
   and **do not** apply orphan rules to it. Warnings never affect the exit
   code; only errors do. (This is the agreed validator behavior and applies
   to §8.3 identically.)

### 8.3 `validate-frontmatter.py` — out-of-profile warning

Schema validation itself is profile-independent (an FR file must still be a
valid FR even if FR is outside the profile). Add the same out-of-profile
WARNING as §8.2, printed in a separate section, not counted as an error.
Exit code stays 0 when there are only warnings.

### 8.4 `install-agent-files.py` + `docs/agent-instructions.md` — profile-conditional generation

**This is the highest-value change.** The canonical source gains conditional
blocks:

```markdown
<!-- IF-PROFILE M L -->
2. **Read the requirement.** Follow the `implements` field to the parent FR…
<!-- END-IF -->
<!-- IF-PROFILE S -->
2. **Read the story.** Follow `part_of_story` to the US and read the
   **Acceptance Criteria** — in this project the US is the requirement.
<!-- END-IF -->
<!-- IF-FLAG compliance -->
7. **Trace the "why"** — follow `derives_from` to BR/CTRL/BRQ…
<!-- END-IF -->
```

Rules:

- `<!-- IF-PROFILE p1 p2 … -->` keeps the block when the active profile is in
  the list; `<!-- IF-FLAG f -->` keeps it when the flag is active. Blocks may
  not nest (keep the source flat; split into sibling blocks instead).
- Unmarked content is included in every profile.
- No active profile (full mode) must reproduce the pre-2.2.0 document
  byte-for-byte — this is **not** "keep every block" when two blocks are
  mutually-exclusive alternates for the same step (e.g. the FR-based vs
  US-based phrasing of "read the requirement"). The precise rule: `IF-FLAG`
  blocks are always kept in full mode (the compliance/sources content they
  gate existed unconditionally pre-2.2.0, before flags existed). `IF-PROFILE`
  blocks are kept in full mode unless the block is gated **exclusively** to
  `S` — S-only phrasing describes the *absence* of FR/NFR/EPIC/CON/CR, which
  is meaningless in full mode where every type exists; any other profile list
  (e.g. `M L`) represents content that existed unconditionally before
  profiles and is kept.
- `install-agent-files.py` reads `project-config.json` (via §8.1), filters the
  blocks, then does the existing `{{VAULT_PREFIX}}` replacement and marker
  injection. `--profile S` CLI override for testing.

Sections of `agent-instructions.md` that need profile conditioning (audit of
the current file):

- "Before Starting Any Task" steps 2 (FR vs US), 7 (compliance), 8
  (architecture tier), 9 (CON — absent in S)
- "During Implementation" bullets referencing FR, CON
- "After Implementation" step 2 (FR status) → S variant: US status
- "Requirement Hierarchy" — S variant collapses to the §7.1 chain
- "ID Format" type list — render only enabled types
- "What NOT to Do" — CR bullets get an S variant ("changes to approved US
  require human PR approval"), BRQ/CTRL bullets become flag-conditional,
  including the "Do not create FR/NFR/CON without linking to at least one
  BRQ" bullet (compliance-flag-only)
- "Workflow Summary" ASCII box and "Key Reminders" — S variants

### 8.5 `generate-fileclasses.py` — skip disabled types

Skip schema files whose manifest type is outside `enabled_types()` (report as
"skipped (outside profile S)"). Keeps the Obsidian Metadata Menu dropdowns
free of the 19 fileClasses a small project never uses.

### 8.6 `assemble-context.py` — chain assembly without FR

Audit required: the task-context assembler follows `implements` → FR → …
today. Change: when `implements` is absent, enter the chain via
`part_of_story` → US and collect AC + VISION + architecture-rules. Must work
in any profile (a TASK with only `part_of_story` is now schema-legal
everywhere).

### 8.7 Traceability generators (`generate-traceability.py`, `-matrix.py`, `-trace-chains.py`)

Audit required at implementation time. Expected changes:

- Coverage semantics: in S, "requirement coverage" = US coverage
  (`US ← verifies` and `US ← part_of_story`), not FR/NFR coverage.
- Chain rendering must accept `US → TASK → TEST` as a complete chain (no FR
  hop) and must not report the absent FR level as a gap when the profile is S.
- Out-of-profile artifacts appear in reports with the same WARNING marker.

### 8.8 No changes needed

- `check-status-transitions.py` — validates whatever types exist in the
  vault; out-of-profile files still get correct state-machine checking. (Its
  parent/child consistency checks operate on links that exist; nothing
  assumes FR presence.) Verify at implementation, but no design change.
- `check-duplicates.py`, `check-updated-dates.py` — type-agnostic.
- `generate-architecture-rules.py` — ADR is in every profile.
- `generate-status-transitions.py` — optionally annotate each type with its
  tiers/profiles in the generated doc (cosmetic, non-blocking).
- `migrate-artifacts.py`, `upgrade-kit.py`, `pull-kit-update.sh` — kit
  plumbing, profile-agnostic.

## 9. Folder layout

**No folders are added, removed, or renamed.** Folders for disabled types
simply stay empty (they are cheap, and keeping them makes profile upgrades a
pure config change). The README folder tree gains per-folder profile
annotations (`[S,M,L]` / `[M,L]` / `[L]` / `[flag:compliance]`).

## 10. Upgrade path

### S → M

1. Change `profile` to `M` in `project-config.json`.
2. Re-run generators: `install-agent-files.py`, `generate-fileclasses.py`.
3. Nothing existing breaks: US files are valid M artifacts (all S fields are
   a subset), TESTs pointing at US remain valid (§5.2 keeps US a legal
   `verifies` target in every profile).
4. Organic growth from here: new FRs appear, existing US gain `delivers`
   links, new TASKs use `implements`, new TESTs point at FR/NFR. The orphan
   checker's M rules immediately start expecting TASK `implements` — expect a
   transition period with warnings on legacy S-style TASKs; they are
   warnings-by-design, fix by backfilling `implements` as FRs are authored.

### M → L, adding flags

Pure additive: change config, re-run generators, start authoring the new
types. No existing artifact changes meaning.

### Downgrade (L → M → S)

Supported as config change; existing out-of-profile artifacts become
WARNINGs, never errors (§8.2). Files are never deleted — deprecate per the
usual rule.

## 11. Versioning & rollout

- Kit version **2.2.0** (minor: additive manifest section, relaxed schemas,
  new config fields; no breaking change for existing vaults per §3.3).
- CHANGELOG.md entry + README version bump on implementation (per project
  rule).
- README: new "Profiles" section (composition table from §3.1, config
  example from §4) + folder-tree annotations (§9).
- `docs/installation-guide.md`: add "choose a profile" as step 1 of setup.
- `_examples/`: unchanged (examples document all types). Optionally add an
  `_examples/profile-s/` mini-vault later — out of scope for 2.2.0.

## 12. Acceptance checklist (definition of done for the implementation)

1. Fresh vault + `profile: S`: authoring VISION/US/TASK/TEST/ADR only,
   `validate-frontmatter.py`, `check-orphans.py`,
   `check-status-transitions.py` all pass with zero warnings; a US → TASK →
   TEST chain with `covers_criteria` validates end-to-end.
2. Same vault + one FR file: both validators emit exactly one PROFILE
   WARNING each, exit code 0 (frontmatter valid) — the FR is otherwise
   schema-checked normally.
3. `install-agent-files.py` under S: generated CLAUDE.md contains no mention
   of FR, NFR, EPIC, CON, CR, BRQ, BR, CTRL, SRC, PERSONA, JOURNEY, ASSUM,
   UC, ARCH, CONTRACT, DM, RISK, REL (grep-verifiable), and contains the S
   variants of the workflow steps.
4. `install-agent-files.py` with no `project-config.json`: byte-identical
   output to v2.1.0 (backward compatibility proof).
5. `generate-fileclasses.py` under S: exactly 5 fileClasses generated.
6. `assemble-context.py TASK-…` on an S-style task (no `implements`)
   produces a bundle containing the US with its AC.
7. TASK with neither `implements` nor `part_of_story` fails schema
   validation in every profile.
8. S → M config flip: all checks still pass on the untouched S vault (only
   expected transition warnings per §10 appear).
9. Manifest sanity: `python scripts/kit_manifest.py` lists profiles and
   resolves S/M/L to 5/10/20 types.

## 13. Open questions for review

1. **§7.3** — S + compliance linkage: add optional `derives_from` to US
   (recommended) or forbid the combination?
2. **§8.4** — marker syntax `IF-PROFILE` / `IF-FLAG`: OK, or prefer
   tier-based conditions (`IF-TYPE FR`)? Type-based is more granular but
   makes the source noisier; profile-based reads better for prose.
3. **§11** — should `profile: S` become the recommended default in
   `project-config.example.json` (opinionated onboarding), or stay unset
   (full mode) as the example?
4. Naming: `S`/`M`/`L` vs `minimal`/`standard`/`full` in config values.
   Single letters are terse in config; words are self-documenting. Spec
   assumes `S`/`M`/`L`.
