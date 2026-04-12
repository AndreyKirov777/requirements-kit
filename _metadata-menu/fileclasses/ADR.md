---
version: "2.14"
mapWithTag: false
icon: git-commit
tagNames: 
filesPaths:
  - 03-architecture/adr
bookmarksGroups: 
excludes: 
extends: 
limit: 100
savedViews: []
favoriteView: 
fieldsOrder:
  - fWXNcd
  - 0HxwrD
  - e796a5
fields:
  - name: status
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "proposed"
        "2": "accepted"
        "3": "rejected"
        "4": "superseded"
        "5": "deprecated"
    path: ""
    id: fWXNcd
  - name: domain
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "auth"
        "2": "payments"
        "3": "catalog"
    path: ""
    id: 0HxwrD
  - name: owner
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "@alice"
        "2": "@bob"
        "3": "team-platform"
    path: ""
    id: e796a5
---

# ADR

> Auto-generated from `schema/` by `scripts/generate-fileclasses.mjs`.
> Do not edit manually — re-run the script after changing schemas.
