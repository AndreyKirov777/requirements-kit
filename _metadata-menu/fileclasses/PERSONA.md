---
version: "2.14"
mapWithTag: false
icon: users
tagNames: 
filesPaths:
  - 01-product/personas
bookmarksGroups: 
excludes: 
extends: 
limit: 100
savedViews: []
favoriteView: 
fieldsOrder:
  - -cHpqI
  - t-2xhp
  - MCJQDu
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
    id: -cHpqI
  - name: domain
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "auth"
        "2": "payments"
        "3": "catalog"
    path: ""
    id: t-2xhp
  - name: owner
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "@alice"
        "2": "@bob"
        "3": "team-platform"
    path: ""
    id: MCJQDu
---

# PERSONA

> Auto-generated from `schema/` by `scripts/generate-fileclasses.mjs`.
> Do not edit manually — re-run the script after changing schemas.
