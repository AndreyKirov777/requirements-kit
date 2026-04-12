---
version: "2.14"
mapWithTag: false
icon: git-branch
tagNames: 
filesPaths:
  - 01-product/use-cases
bookmarksGroups: 
excludes: 
extends: 
limit: 100
savedViews: []
favoriteView: 
fieldsOrder:
  - oqsOjY
  - xJXDMr
  - ICG9Tx
  - rNKjWo
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
    id: oqsOjY
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
    id: xJXDMr
  - name: domain
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "auth"
        "2": "payments"
        "3": "catalog"
    path: ""
    id: ICG9Tx
  - name: owner
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "@alice"
        "2": "@bob"
        "3": "team-platform"
    path: ""
    id: rNKjWo
---

# UC

> Auto-generated from `schema/` by `scripts/generate-fileclasses.mjs`.
> Do not edit manually — re-run the script after changing schemas.
