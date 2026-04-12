---
version: "2.14"
mapWithTag: false
icon: lock
tagNames: 
filesPaths:
  - 01-product/controls
bookmarksGroups: 
excludes: 
extends: 
limit: 100
savedViews: []
favoriteView: 
fieldsOrder:
  - SwikeO
  - 1uGdXb
  - Ct6iM-
  - zSaTor
  - FzOmni
fields:
  - name: status
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "identified"
        "2": "defined"
        "3": "allocated"
        "4": "implemented"
        "5": "verified"
        "6": "audited"
        "7": "deprecated"
    path: ""
    id: SwikeO
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
    id: 1uGdXb
  - name: verification_method
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "inspection"
        "2": "test"
        "3": "demonstration"
        "4": "analysis"
    path: ""
    id: Ct6iM-
  - name: domain
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "auth"
        "2": "payments"
        "3": "catalog"
    path: ""
    id: zSaTor
  - name: owner
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "@alice"
        "2": "@bob"
        "3": "team-platform"
    path: ""
    id: FzOmni
---

# CTRL

> Auto-generated from `schema/` by `scripts/generate-fileclasses.mjs`.
> Do not edit manually — re-run the script after changing schemas.
