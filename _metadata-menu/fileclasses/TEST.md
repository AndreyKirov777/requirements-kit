---
version: "2.14"
mapWithTag: false
icon: test-tube
tagNames: 
filesPaths:
  - 05-quality/acceptance
bookmarksGroups: 
excludes: 
extends: 
limit: 100
savedViews: []
favoriteView: 
fieldsOrder:
  - 0YG1H_
  - vRX1JY
  - 5yxtXi
  - TOehWm
  - Zet3F1
fields:
  - name: status
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "draft"
        "2": "ready"
        "3": "passed"
        "4": "failed"
    path: ""
    id: 0YG1H_
  - name: type
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "unit"
        "2": "integration"
        "3": "e2e"
        "4": "manual"
        "5": "functional"
        "6": "non-functional"
        "7": "security"
        "8": "performance"
    path: ""
    id: vRX1JY
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
    id: 5yxtXi
  - name: domain
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "auth"
        "2": "payments"
        "3": "catalog"
    path: ""
    id: TOehWm
  - name: owner
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "@alice"
        "2": "@bob"
        "3": "team-platform"
    path: ""
    id: Zet3F1
---

# TEST

> Auto-generated from `schema/` by `scripts/generate-fileclasses.mjs`.
> Do not edit manually — re-run the script after changing schemas.
