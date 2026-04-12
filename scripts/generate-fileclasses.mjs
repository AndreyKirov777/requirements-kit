#!/usr/bin/env node
/**
 * generate-fileclasses.mjs
 *
 * Reads schema/*.schema.json (single source of truth) and generates
 * Metadata Menu fileClass files for Obsidian.
 *
 * Usage:
 *   node scripts/generate-fileclasses.mjs
 *
 * Output:
 *   _metadata-menu/fileclasses/<name>.md  — one per artifact type
 *
 * The generated folder should be configured as the "FileClass files folder"
 * in Metadata Menu plugin settings.
 */

import { readFileSync, writeFileSync, readdirSync, mkdirSync, existsSync } from "fs";
import { join, basename } from "path";
import { createHash } from "crypto";

// ─── Config ──────────────────────────────────────────────────────────────────

const ROOT = new URL("..", import.meta.url).pathname.replace(/\/$/, "");
const SCHEMA_DIR = join(ROOT, "schema");
const OUT_DIR = join(ROOT, "_metadata-menu", "fileclasses");

/**
 * Map: schema file name (without .schema.json) → artifact config.
 *   name  — fileClass name (used as filename and display name)
 *   paths — vault-relative folder paths where these artifacts live
 *   icon  — Lucide icon name for Metadata Menu sidebar
 */
const ARTIFACT_MAP = {
  "fr":                     { name: "FR",              paths: ["02-requirements/fr"],                icon: "file-check" },
  "nfr":                    { name: "NFR",             paths: ["02-requirements/nfr"],               icon: "shield-check" },
  "user-story":             { name: "US",              paths: ["02-requirements/user-stories"],      icon: "user" },
  "epic":                   { name: "EPIC",            paths: ["02-requirements/epics"],             icon: "layers" },
  "brq":                    { name: "BRQ",             paths: ["01-product/business-requirements"],  icon: "briefcase" },
  "br":                     { name: "BR",              paths: ["01-product/business-rules"],         icon: "book-open" },
  "ctrl":                   { name: "CTRL",            paths: ["01-product/controls"],               icon: "lock" },
  "constraint":             { name: "CON",             paths: ["01-product/constraints"],            icon: "alert-triangle" },
  "vision":                 { name: "VISION",          paths: ["01-product/vision"],                 icon: "eye" },
  "persona":                { name: "PERSONA",         paths: ["01-product/personas"],               icon: "users" },
  "journey":                { name: "JOURNEY",         paths: ["01-product/journeys"],               icon: "map" },
  "assumption":             { name: "ASSUM",           paths: ["01-product/assumptions"],            icon: "help-circle" },
  "use-case":               { name: "UC",              paths: ["01-product/use-cases"],              icon: "git-branch" },
  "src":                    { name: "SRC",             paths: ["01-product/sources"],                icon: "file-text" },
  "adr":                    { name: "ADR",             paths: ["03-architecture/adr"],               icon: "git-commit" },
  "architecture-overview":  { name: "ARCH-OVERVIEW",   paths: ["03-architecture"],                   icon: "layout" },
  "domain-architecture":    { name: "ARCH-DOMAIN",     paths: ["03-architecture"],                   icon: "layout" },
  "data-model":             { name: "DM",              paths: ["03-architecture/data-model"],        icon: "database" },
  "contract":               { name: "CONTRACT",        paths: ["03-architecture/integrations"],      icon: "file-signature" },
  "change-request":         { name: "CR",              paths: ["04-delivery/change-requests"],       icon: "git-pull-request" },
  "release":                { name: "REL",             paths: ["04-delivery/releases"],              icon: "rocket" },
  "risk":                   { name: "RISK",            paths: ["04-delivery/risks"],                 icon: "alert-octagon" },
  "task":                   { name: "TASK",            paths: ["04-delivery/tasks"],                 icon: "check-square" },
  "test":                   { name: "TEST",            paths: ["05-quality/acceptance"],             icon: "test-tube" },
};

// ─── Helpers ─────────────────────────────────────────────────────────────────

/** Deterministic 6-char ID from field + artifact name (stable across runs). */
function fieldId(artifactName, fieldName) {
  const hash = createHash("sha256")
    .update(`${artifactName}:${fieldName}`)
    .digest("base64url");
  return hash.slice(0, 6);
}

/** Convert JSON Schema enum values to Metadata Menu ValuesList format. */
function toValuesList(enumValues) {
  const result = {};
  enumValues.forEach((val, i) => {
    result[String(i + 1)] = val;
  });
  return result;
}

/**
 * Extract all fields with `enum` from a JSON Schema's `properties`.
 * Returns array of { name, enumValues }.
 */
function extractEnumFields(schema) {
  const props = schema.properties || {};
  const fields = [];

  for (const [name, def] of Object.entries(props)) {
    if (def.enum && Array.isArray(def.enum)) {
      fields.push({ name, enumValues: def.enum });
    }
  }

  return fields;
}

/** Build YAML frontmatter string for a fileClass. */
function buildFileClass(artifactName, icon, paths, fields) {
  const yamlFields = fields.map((f) => {
    const id = fieldId(artifactName, f.name);
    return [
      `  - name: ${f.name}`,
      `    type: Select`,
      `    options:`,
      `      sourceType: ValuesList`,
      `      valuesList:`,
      ...Object.entries(toValuesList(f.enumValues)).map(
        ([k, v]) => `        "${k}": "${v}"`
      ),
      `    path: ""`,
      `    id: ${id}`,
    ].join("\n");
  });

  const filesPaths = paths.map((p) => `  - ${p}`).join("\n");
  const fieldsOrder = fields
    .map((f) => `  - ${fieldId(artifactName, f.name)}`)
    .join("\n");

  return [
    "---",
    `version: "2.14"`,
    `mapWithTag: false`,
    `icon: ${icon}`,
    `tagNames: `,
    `filesPaths:`,
    filesPaths,
    `bookmarksGroups: `,
    `excludes: `,
    `extends: `,
    `limit: 100`,
    `savedViews: []`,
    `favoriteView: `,
    `fieldsOrder:`,
    fieldsOrder,
    `fields:`,
    yamlFields.join("\n"),
    "---",
    "",
    `# ${artifactName}`,
    "",
    `> Auto-generated from \`schema/\` by \`scripts/generate-fileclasses.mjs\`.`,
    `> Do not edit manually — re-run the script after changing schemas.`,
    "",
  ].join("\n");
}

// ─── Main ────────────────────────────────────────────────────────────────────

function main() {
  // Ensure output directory
  if (!existsSync(OUT_DIR)) {
    mkdirSync(OUT_DIR, { recursive: true });
  }

  const schemaFiles = readdirSync(SCHEMA_DIR).filter(
    (f) => f.endsWith(".schema.json") && f !== "base.schema.json"
  );

  let generated = 0;
  let skipped = 0;

  for (const file of schemaFiles) {
    const key = file.replace(".schema.json", "");
    const config = ARTIFACT_MAP[key];

    if (!config) {
      console.warn(`⚠  No mapping for ${file} — skipping`);
      skipped++;
      continue;
    }

    const schema = JSON.parse(readFileSync(join(SCHEMA_DIR, file), "utf-8"));
    const enumFields = extractEnumFields(schema);

    if (enumFields.length === 0) {
      console.log(`   ${config.name}: no enum fields — skipping`);
      skipped++;
      continue;
    }

    const content = buildFileClass(config.name, config.icon, config.paths, enumFields);
    const outPath = join(OUT_DIR, `${config.name}.md`);
    writeFileSync(outPath, content, "utf-8");
    console.log(`✓  ${config.name} → ${enumFields.length} field(s): ${enumFields.map((f) => f.name).join(", ")}`);
    generated++;
  }

  console.log(`\nDone: ${generated} fileClasses generated, ${skipped} skipped.`);
  console.log(`Output: ${OUT_DIR}/`);
}

main();
