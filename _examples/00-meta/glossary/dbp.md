---
id: GLOSS-DBP
title: Digital Battery Passport Glossary
domain: all
updated: 2026-03-28
---

# Digital Battery Passport Glossary

This glossary defines business and regulatory terms for the DBP Accelerator and maps them to code identifiers. AI agents must use `code_name` values when creating or modifying source code.

## Core Terms

### Battery Passport

| Field      | Value                                                               |
| ---------- | ------------------------------------------------------------------- |
| Definition | A digital record containing all regulated data for a single battery, covering its entire lifecycle |
| Code Name  | `batteryPassport`                                                   |
| Type       | `object`                                                            |
| Aliases    | DBP, digital battery passport, passport                             |

### Economic Operator

| Field      | Value                                                               |
| ---------- | ------------------------------------------------------------------- |
| Definition | A legal entity that places batteries on the EU market and bears regulatory obligations under EU 2023/1542 |
| Code Name  | `economicOperator`                                                  |
| Type       | `object`                                                            |
| Aliases    | EO, operator                                                        |

### Completeness Score

| Field      | Value                                                               |
| ---------- | ------------------------------------------------------------------- |
| Definition | Percentage (0–100) indicating how many regulated fields in a battery passport are populated and valid |
| Code Name  | `completenessScore`                                                 |
| Type       | `number`                                                            |
| Aliases    | passport completeness, readiness score                              |

### Data Cluster

| Field      | Value                                                               |
| ---------- | ------------------------------------------------------------------- |
| Definition | A logical grouping of related battery passport attributes (e.g., general info, materials, performance, carbon footprint) |
| Code Name  | `dataCluster`                                                       |
| Type       | `object`                                                            |
| Aliases    | attribute group, data category                                      |

### Static Data

| Field      | Value                                                               |
| ---------- | ------------------------------------------------------------------- |
| Definition | Battery attributes that do not change after manufacturing (e.g., chemistry, weight, manufacturer, rated capacity) |
| Code Name  | `staticData`                                                        |
| Type       | `object`                                                            |
| Aliases    | static attributes                                                   |

### Dynamic Data

| Field      | Value                                                               |
| ---------- | ------------------------------------------------------------------- |
| Definition | Battery attributes that change during the battery lifecycle (e.g., state of health, cycle count, usage events) |
| Code Name  | `dynamicData`                                                       |
| Type       | `object`                                                            |
| Aliases    | dynamic attributes, lifecycle data, telemetry                       |

### Bronze Layer

| Field      | Value                                                               |
| ---------- | ------------------------------------------------------------------- |
| Definition | First data tier — raw data ingestion; stores incoming data in original form, immutable, auditable |
| Code Name  | `bronzeLayer`                                                       |
| Type       | `module`                                                            |
| Aliases    | raw data layer, ingestion layer                                     |

### Silver Layer

| Field      | Value                                                               |
| ---------- | ------------------------------------------------------------------- |
| Definition | Second data tier — cleansed, normalized data mapped to the unified battery passport data model |
| Code Name  | `silverLayer`                                                       |
| Type       | `module`                                                            |
| Aliases    | standardization layer, integration layer                            |

### Gold Layer

| Field      | Value                                                               |
| ---------- | ------------------------------------------------------------------- |
| Definition | Third data tier — business-ready, role-based, exportable battery passport data products |
| Code Name  | `goldLayer`                                                         |
| Type       | `module`                                                            |
| Aliases    | passport layer, data products layer                                 |

### Legitimate User

| Field      | Value                                                               |
| ---------- | ------------------------------------------------------------------- |
| Definition | A legal or natural person with a legitimate interest in battery data (second-life operators, repairers, recyclers, etc.) |
| Code Name  | `legitimateUser`                                                    |
| Type       | `role`                                                              |
| Aliases    | legitimate interest user, authorized third party                    |

### Data Lineage

| Field      | Value                                                               |
| ---------- | ------------------------------------------------------------------- |
| Definition | A traceable, field-level record of when and how each battery passport attribute was created, updated, or derived |
| Code Name  | `dataLineage`                                                       |
| Type       | `object`                                                            |
| Aliases    | field-level lineage, audit trail                                    |

### Unique Battery Identifier

| Field      | Value                                                               |
| ---------- | ------------------------------------------------------------------- |
| Definition | A globally unique identifier assigned to each battery, encoded in the QR code and used across all passport operations |
| Code Name  | `batteryId`                                                         |
| Type       | `string`                                                            |
| Aliases    | battery ID, unique ID, passport ID                                  |

## Naming Rules

1. **Variables and function parameters**: use `code_name` in camelCase as listed above.
2. **Database columns**: use snake_case version of `code_name` (e.g., `battery_passport`, `completeness_score`).
3. **API fields**: use camelCase `code_name` in JSON payloads.
4. **Config keys**: use kebab-case (e.g., `completeness-score`, `bronze-layer`).
5. **Never invent synonyms.** If you need a new term, add it to this glossary first.
