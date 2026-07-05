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
---

# SRC

> Auto-generated from `schema/` by `scripts/generate-fileclasses.py`.
> Do not edit manually — re-run the script after changing schemas.
