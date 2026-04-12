---
version: "2.14"
mapWithTag: false
icon: eye
tagNames: 
filesPaths:
  - 01-product/vision
bookmarksGroups: 
excludes: 
extends: 
limit: 100
savedViews: []
favoriteView: 
fieldsOrder:
  - XuUj-y
  - Z5PL4J
  - D494ds
fields:
  - name: status
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "draft"
        "2": "proposed"
        "3": "approved"
        "4": "superseded"
        "5": "deprecated"
    path: ""
    id: XuUj-y
  - name: domain
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "auth"
        "2": "payments"
        "3": "catalog"
    path: ""
    id: Z5PL4J
  - name: owner
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "@alice"
        "2": "@bob"
        "3": "team-platform"
    path: ""
    id: D494ds
---

# VISION

> Auto-generated from `schema/` by `scripts/generate-fileclasses.mjs`.
> Do not edit manually — re-run the script after changing schemas.
