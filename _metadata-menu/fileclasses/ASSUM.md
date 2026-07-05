---
version: "2.14"
mapWithTag: false
icon: help-circle
tagNames: 
filesPaths:
  - 01-product/assumptions
bookmarksGroups: 
excludes: 
extends: 
limit: 100
savedViews: []
favoriteView: 
fieldsOrder:
  - xou33j
  - 9FX3F9
fields:
  - name: status
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "unvalidated"
        "2": "validating"
        "3": "validated"
        "4": "invalidated"
        "5": "deprecated"
    path: ""
    id: xou33j
  - name: risk_if_wrong
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "high"
        "2": "medium"
        "3": "low"
    path: ""
    id: 9FX3F9
---

# ASSUM

> Auto-generated from `schema/` by `scripts/generate-fileclasses.py`.
> Do not edit manually — re-run the script after changing schemas.
