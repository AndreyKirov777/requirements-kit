---
version: "2.14"
mapWithTag: false
icon: alert-triangle
tagNames: 
filesPaths:
  - 01-product/constraints
bookmarksGroups: 
excludes: 
extends: 
limit: 100
savedViews: []
favoriteView: 
fieldsOrder:
  - oAWXtG
  - 0MgPTu
  - jUMycg
  - 2U81AS
  - ZfMx53
fields:
  - name: status
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "draft"
        "2": "proposed"
        "3": "approved"
        "4": "deprecated"
    path: ""
    id: oAWXtG
  - name: constraint_type
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "business"
        "2": "regulatory"
        "3": "technical"
    path: ""
    id: 0MgPTu
  - name: priority
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "critical"
        "2": "high"
        "3": "medium"
        "4": "low"
    path: ""
    id: jUMycg
  - name: domain
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "auth"
        "2": "payments"
        "3": "catalog"
    path: ""
    id: 2U81AS
  - name: owner
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "@alice"
        "2": "@bob"
        "3": "team-platform"
    path: ""
    id: ZfMx53
---

# CON

> Auto-generated from `schema/` by `scripts/generate-fileclasses.mjs`.
> Do not edit manually — re-run the script after changing schemas.
