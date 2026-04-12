---
version: "2.14"
mapWithTag: false
icon: briefcase
tagNames: 
filesPaths:
  - 01-product/business-requirements
bookmarksGroups: 
excludes: 
extends: 
limit: 100
savedViews: []
favoriteView: 
fieldsOrder:
  - OEY_91
  - jq0UPG
  - O1djwF
fields:
  - name: status
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "identified"
        "2": "analyzed"
        "3": "approved"
        "4": "allocated"
        "5": "covered"
        "6": "deprecated"
    path: ""
    id: OEY_91
  - name: source_type
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "regulation"
        "2": "standard"
        "3": "contract"
        "4": "policy"
        "5": "business-goal"
        "6": "stakeholder-need"
    path: ""
    id: jq0UPG
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
    id: O1djwF
---

# BRQ

> Auto-generated from `schema/` by `scripts/generate-fileclasses.mjs`.
> Do not edit manually — re-run the script after changing schemas.
