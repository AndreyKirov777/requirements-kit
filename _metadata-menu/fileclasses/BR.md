---
version: "2.14"
mapWithTag: false
icon: book-open
tagNames: 
filesPaths:
  - 01-product/business-rules
bookmarksGroups: 
excludes: 
extends: 
limit: 100
savedViews: []
favoriteView: 
fieldsOrder:
  - PRiMGE
  - qG3_L6
  - GTMV_g
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
    id: PRiMGE
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
    id: qG3_L6
  - name: classification
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "regulatory"
        "2": "contractual"
        "3": "policy"
        "4": "domain-logic"
    path: ""
    id: GTMV_g
---

# BR

> Auto-generated from `schema/` by `scripts/generate-fileclasses.mjs`.
> Do not edit manually — re-run the script after changing schemas.
