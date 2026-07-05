---
id: META-KIT-OVERVIEW
title: Requirements Kit — Live Overview
updated: 2026-07-04
---

# Requirements Kit — Live Overview

> **How it works:** Every section below is a live [Dataview](https://blacksmithgu.github.io/obsidian-dataview/) query that reads YAML frontmatter from the kit's markdown files. No manual updates needed — edit an artifact's frontmatter and this page refreshes automatically.
>
> **Prerequisites:** Install the Dataview community plugin and enable JavaScript queries in its settings (`Enable JavaScript Queries` → ON, `Enable Inline JavaScript Queries` → ON).

---

## 1 — Inventory by Artifact Type

How many artifacts of each kind exist in the kit (excludes `_examples/` and `_framework/`).

```dataviewjs
const folders = {
  "Vision":       '"01-product/vision"',
  "Persona":      '"01-product/personas"',
  "Journey":      '"01-product/journeys"',
  "Assumption":   '"01-product/assumptions"',
  "BRQ":          '"01-product/business-requirements"',
  "BR":           '"01-product/business-rules"',
  "CTRL":         '"01-product/controls"',
  "CON":          '"01-product/constraints"',
  "Source":       '"01-product/sources"',
  "Use Case":     '"01-product/use-cases"',
  "Epic":         '"02-requirements/epics"',
  "User Story":   '"02-requirements/user-stories"',
  "FR":           '"02-requirements/fr"',
  "NFR":          '"02-requirements/nfr"',
  "ADR":          '"03-architecture/adr"',
  "Data Model":   '"03-architecture/data-model"',
  "Contract":     '"03-architecture/contracts"',
  "Task":         '"04-delivery/tasks"',
  "CR":           '"04-delivery/change-requests"',
  "Risk":         '"04-delivery/risks"',
  "Release":      '"04-delivery/releases"',
  "Test":         '"05-quality/acceptance"',
};

let rows = [];
let total = 0;
for (const [label, folder] of Object.entries(folders)) {
  const pages = dv.pages(folder);
  const count = pages.length;
  if (count > 0) {
    rows.push([label, count]);
    total += count;
  }
}
rows.push(["**TOTAL**", `**${total}**`]);
dv.table(["Artifact Type", "Count"], rows);
```

---

## 2 — Status Summary

Artifact counts grouped by status across the entire kit.

```dataviewjs
const pages = dv.pages('"01-product" or "02-requirements" or "03-architecture" or "04-delivery" or "05-quality"')
  .where(p => p.status && p.id);

const statusMap = {};
for (const p of pages) {
  const s = String(p.status);
  statusMap[s] = (statusMap[s] || 0) + 1;
}

const rows = Object.entries(statusMap)
  .sort((a, b) => b[1] - a[1])
  .map(([status, count]) => [status, count]);

dv.table(["Status", "Count"], rows);
```

---

## 3 — All Artifacts Register

A single sortable table of every artifact in the kit. Click column headers to sort.

```dataviewjs
const pages = dv.pages('"01-product" or "02-requirements" or "03-architecture" or "04-delivery" or "05-quality"')
  .where(p => p.id)
  .sort(p => p.id, "asc");

dv.table(
  ["ID", "Title", "Status", "Priority", "Owner", "Domain", "Updated"],
  pages.map(p => [
    p.file.link,
    p.title || "",
    p.status || "—",
    p.priority || "—",
    p.owner || "—",
    p.domain || "—",
    p.updated || "—",
  ])
);
```

---

## 4 — Status × Type Matrix

See at a glance which artifact types are in which state.

```dataviewjs
const typeMap = {
  "01-product/vision":                "VISION",
  "01-product/personas":              "PERSONA",
  "01-product/journeys":              "JOURNEY",
  "01-product/assumptions":           "ASSUM",
  "01-product/business-requirements": "BRQ",
  "01-product/business-rules":        "BR",
  "01-product/controls":              "CTRL",
  "01-product/constraints":           "CON",
  "01-product/sources":               "SRC",
  "01-product/use-cases":             "UC",
  "02-requirements/epics":            "EPIC",
  "02-requirements/user-stories":     "US",
  "02-requirements/fr":               "FR",
  "02-requirements/nfr":              "NFR",
  "03-architecture/adr":              "ADR",
  "03-architecture/data-model":       "DM",
  "03-architecture/contracts":        "CONTRACT",
  "04-delivery/tasks":                "TASK",
  "04-delivery/change-requests":      "CR",
  "04-delivery/risks":                "RISK",
  "04-delivery/releases":             "REL",
  "05-quality/acceptance":            "TEST",
};

const pages = dv.pages('"01-product" or "02-requirements" or "03-architecture" or "04-delivery" or "05-quality"')
  .where(p => p.id && p.status);

// Collect all statuses and types
const statuses = new Set();
const matrix = {};

for (const p of pages) {
  const folder = p.file.folder;
  let artifactType = "OTHER";
  for (const [path, label] of Object.entries(typeMap)) {
    if (folder.includes(path)) { artifactType = label; break; }
  }
  const status = String(p.status);
  statuses.add(status);
  if (!matrix[artifactType]) matrix[artifactType] = {};
  matrix[artifactType][status] = (matrix[artifactType][status] || 0) + 1;
}

const sortedStatuses = [...statuses].sort();
const headers = ["Type", ...sortedStatuses];
const rows = Object.entries(matrix)
  .sort((a, b) => a[0].localeCompare(b[0]))
  .map(([type, counts]) => [
    type,
    ...sortedStatuses.map(s => counts[s] || "·"),
  ]);

dv.table(headers, rows);
```

---

## 5 — Domain Breakdown

Artifacts per domain, so you can see which areas have the most (or least) coverage.

```dataviewjs
const pages = dv.pages('"01-product" or "02-requirements" or "03-architecture" or "04-delivery" or "05-quality"')
  .where(p => p.id && p.domain);

const domainMap = {};
for (const p of pages) {
  const d = String(p.domain);
  domainMap[d] = (domainMap[d] || 0) + 1;
}

const rows = Object.entries(domainMap)
  .sort((a, b) => b[1] - a[1])
  .map(([domain, count]) => [domain, count]);

dv.table(["Domain", "Artifact Count"], rows);
```

---

## 6 — Recently Updated

The 20 most recently changed artifacts — useful for tracking current work.

```dataviewjs
const pages = dv.pages('"01-product" or "02-requirements" or "03-architecture" or "04-delivery" or "05-quality"')
  .where(p => p.id && p.updated)
  .sort(p => p.updated, "desc")
  .limit(20);

dv.table(
  ["ID", "Title", "Status", "Updated"],
  pages.map(p => [
    p.file.link,
    p.title || "",
    p.status || "—",
    p.updated,
  ])
);
```

---

## 7 — Traceability Gaps

> **Note:** The kit stores links **upward only** (child → parent). Reverse links (`verified_by`, `delivered_by`, `implemented_by`) are never written to frontmatter — the queries below compute them on the fly by scanning the child artifacts' up-links.

### 7a — FRs / NFRs missing verification

Requirements that no TEST references in its `verifies` field — meaning no test covers them yet.

```dataviewjs
// Collect requirement IDs verified by at least one TEST (computed reverse link)
const extractIds = (val) => {
  const arr = Array.isArray(val) ? val : (val ? [val] : []);
  return arr
    .map(v => String(v).match(/([A-Z]+-[A-Z0-9]+-[0-9]{3,})/))
    .filter(m => m)
    .map(m => m[1]);
};

const verified = new Set();
for (const t of dv.pages('"05-quality/acceptance"').where(t => t.id)) {
  for (const reqId of extractIds(t.verifies)) verified.add(reqId);
}

const pages = dv.pages('"02-requirements/fr" or "02-requirements/nfr"')
  .where(p => p.id && p.status !== "deprecated" && !verified.has(String(p.id)))
  .sort(p => p.id, "asc");

if (pages.length === 0) {
  dv.paragraph("✅ All FRs and NFRs are verified by at least one test.");
} else {
  dv.table(
    ["ID", "Title", "Status", "Priority"],
    pages.map(p => [
      p.file.link,
      p.title || "",
      p.status || "—",
      p.priority || "—",
    ])
  );
}
```

### 7b — FRs / NFRs with no upstream traceability

Requirements that have an empty `source_docs` and no `derives_from` — potential orphans with no business justification.

```dataviewjs
const pages = dv.pages('"02-requirements/fr" or "02-requirements/nfr"')
  .where(p => p.id
    && (!p.source_docs || p.source_docs.length === 0)
    && (!p.derives_from || p.derives_from.length === 0)
    && (!p.parent_epic || String(p.parent_epic).trim() === "")
  )
  .sort(p => p.id, "asc");

if (pages.length === 0) {
  dv.paragraph("✅ All FRs and NFRs trace to an upstream source.");
} else {
  dv.table(
    ["ID", "Title", "Status", "Domain"],
    pages.map(p => [
      p.file.link,
      p.title || "",
      p.status || "—",
      p.domain || "—",
    ])
  );
}
```

### 7c — Tasks not linked to a requirement

Tasks where `implements` is empty — work with no requirement justification.

```dataviewjs
const pages = dv.pages('"04-delivery/tasks"')
  .where(p => p.id && (!p.implements || String(p.implements).trim() === ""))
  .sort(p => p.id, "asc");

if (pages.length === 0) {
  dv.paragraph("✅ All tasks trace to a requirement.");
} else {
  dv.table(
    ["ID", "Title", "Status", "Assigned To"],
    pages.map(p => [
      p.file.link,
      p.title || "",
      p.status || "—",
      p.assigned_to || "—",
    ])
  );
}
```

### 7d — FRs without a delivering User Story

FRs that no User Story references in its `delivers` field — the requirement has no carrier of acceptance criteria.

```dataviewjs
const extractIds = (val) => {
  const arr = Array.isArray(val) ? val : (val ? [val] : []);
  return arr
    .map(v => String(v).match(/([A-Z]+-[A-Z0-9]+-[0-9]{3,})/))
    .filter(m => m)
    .map(m => m[1]);
};

const delivered = new Set();
for (const us of dv.pages('"02-requirements/user-stories"').where(u => u.id)) {
  for (const frId of extractIds(us.delivers)) delivered.add(frId);
}

const pages = dv.pages('"02-requirements/fr"')
  .where(p => p.id && p.status !== "deprecated" && !delivered.has(String(p.id)))
  .sort(p => p.id, "asc");

if (pages.length === 0) {
  dv.paragraph("✅ Every FR is delivered by at least one User Story.");
} else {
  dv.table(
    ["ID", "Title", "Status", "Priority"],
    pages.map(p => [
      p.file.link,
      p.title || "",
      p.status || "—",
      p.priority || "—",
    ])
  );
}
```

---

## 8 — Assumptions at Risk

Assumptions that are still `unvalidated` and have `risk_if_wrong: high` or `critical`.

```dataviewjs
const pages = dv.pages('"01-product/assumptions"')
  .where(p => p.id
    && p.status === "unvalidated"
    && (p.risk_if_wrong === "high" || p.risk_if_wrong === "critical")
  )
  .sort(p => p.id, "asc");

if (pages.length === 0) {
  dv.paragraph("✅ No high-risk unvalidated assumptions.");
} else {
  dv.table(
    ["ID", "Title", "Risk If Wrong", "Related Requirements"],
    pages.map(p => [
      p.file.link,
      p.title || "",
      p.risk_if_wrong || "—",
      p.related_requirements || "—",
    ])
  );
}
```

---

## 9 — Delivery Pipeline

### 9a — Task board

```dataviewjs
const pages = dv.pages('"04-delivery/tasks"')
  .where(p => p.id)
  .sort(p => p.id, "asc");

const statuses = ["backlog", "ready", "in-progress", "blocked", "done"];
for (const status of statuses) {
  const filtered = pages.where(p => String(p.status) === status);
  if (filtered.length > 0) {
    dv.header(4, `${status.toUpperCase()} (${filtered.length})`);
    dv.table(
      ["ID", "Title", "Implements", "Assigned To", "Complexity"],
      filtered.map(p => [
        p.file.link,
        p.title || "",
        p.implements || "—",
        p.assigned_to || "—",
        p.estimated_complexity || "—",
      ])
    );
  }
}
```

### 9b — Open change requests

```dataviewjs
const pages = dv.pages('"04-delivery/change-requests"')
  .where(p => p.id && p.status !== "applied" && p.status !== "rejected")
  .sort(p => p.priority === "critical" ? 0 : p.priority === "high" ? 1 : p.priority === "medium" ? 2 : 3, "asc");

if (pages.length === 0) {
  dv.paragraph("✅ No open change requests.");
} else {
  dv.table(
    ["ID", "Title", "Status", "Priority", "Affects"],
    pages.map(p => [
      p.file.link,
      p.title || "",
      p.status || "—",
      p.priority || "—",
      p.affects || "—",
    ])
  );
}
```

---

## 10 — Open Risks

```dataviewjs
const pages = dv.pages('"04-delivery/risks"')
  .where(p => p.id && p.status !== "closed")
  .sort(p => p.id, "asc");

if (pages.length === 0) {
  dv.paragraph("✅ No open risks.");
} else {
  dv.table(
    ["ID", "Title", "Status", "Owner"],
    pages.map(p => [
      p.file.link,
      p.title || "",
      p.status || "—",
      p.owner || "—",
    ])
  );
}
```

---

## 11 — Awaiting Human Approval

Artifacts stuck at a status that requires human sign-off to advance (e.g., `proposed`, `analyzed`, `defined`).

```dataviewjs
const humanGateStatuses = ["proposed", "analyzed", "defined"];

const pages = dv.pages('"01-product" or "02-requirements" or "03-architecture" or "04-delivery" or "05-quality"')
  .where(p => p.id && humanGateStatuses.includes(String(p.status)))
  .sort(p => p.id, "asc");

if (pages.length === 0) {
  dv.paragraph("✅ Nothing waiting for human approval.");
} else {
  dv.table(
    ["ID", "Title", "Status", "Owner", "Domain"],
    pages.map(p => [
      p.file.link,
      p.title || "",
      p.status || "—",
      p.owner || "—",
      p.domain || "—",
    ])
  );
}
```
