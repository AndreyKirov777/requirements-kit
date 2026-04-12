---
version: "2.14"
mapWithTag: false
icon: file-text
tagNames: 
filesPaths:
  - 01-product/sources
bookmarksGroups: 
excludes: 
extends: 
limit: 100
savedViews: []
favoriteView: 
fieldsOrder:
  - qlVf2H
  - OpoJKw
  - FtFk7e
  - g7bLIq
fields:
  - name: category
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "regulation"
        "2": "strategy"
        "3": "policy"
        "4": "standard"
        "5": "contract"
    path: ""
    id: qlVf2H
  - name: status
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "in_force"
        "2": "adopted"
        "3": "draft"
        "4": "proposed"
    path: ""
    id: OpoJKw
  - name: domain
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "auth"
        "2": "payments"
        "3": "catalog"
    path: ""
    id: FtFk7e
  - name: owner
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "@alice"
        "2": "@bob"
        "3": "team-platform"
    path: ""
    id: g7bLIq
---

# SRC

> Auto-generated from `schema/` by `scripts/generate-fileclasses.mjs`.
> Do not edit manually — re-run the script after changing schemas.
