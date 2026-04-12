---
version: "2.14"
mapWithTag: false
icon: file-check
tagNames: 
filesPaths:
  - 02-requirements/fr
bookmarksGroups: 
excludes: 
extends: 
limit: 100
savedViews: []
favoriteView: 
fieldsOrder:
  - cJP_8n
  - _MBM-4
fields:
  - name: status
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "draft"
        "2": "proposed"
        "3": "approved"
        "4": "in-implementation"
        "5": "implemented"
        "6": "verified"
        "7": "deprecated"
    path: ""
    id: cJP_8n
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
    id: _MBM-4
---

# FR

> Auto-generated from `schema/` by `scripts/generate-fileclasses.mjs`.
> Do not edit manually — re-run the script after changing schemas.
