---
version: "2.14"
mapWithTag: false
icon: git-pull-request
tagNames: 
filesPaths:
  - 04-delivery/change-requests
bookmarksGroups: 
excludes: 
extends: 
limit: 100
savedViews: []
favoriteView: 
fieldsOrder:
  - KG9XSg
  - K12jkE
fields:
  - name: status
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "proposed"
        "2": "approved"
        "3": "applied"
        "4": "rejected"
    path: ""
    id: KG9XSg
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
    id: K12jkE
---

# CR

> Auto-generated from `schema/` by `scripts/generate-fileclasses.py`.
> Do not edit manually — re-run the script after changing schemas.
