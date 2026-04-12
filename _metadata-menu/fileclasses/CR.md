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
  - 4XJxJR
  - E0YP3V
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
  - name: domain
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "auth"
        "2": "payments"
        "3": "catalog"
    path: ""
    id: 4XJxJR
  - name: owner
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "@alice"
        "2": "@bob"
        "3": "team-platform"
    path: ""
    id: E0YP3V
---

# CR

> Auto-generated from `schema/` by `scripts/generate-fileclasses.mjs`.
> Do not edit manually — re-run the script after changing schemas.
