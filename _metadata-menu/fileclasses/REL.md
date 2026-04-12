---
version: "2.14"
mapWithTag: false
icon: rocket
tagNames: 
filesPaths:
  - 04-delivery/releases
bookmarksGroups: 
excludes: 
extends: 
limit: 100
savedViews: []
favoriteView: 
fieldsOrder:
  - 89qZsI
  - aACISO
  - OvgAPB
fields:
  - name: status
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "planned"
        "2": "ready"
        "3": "released"
        "4": "rolled-back"
    path: ""
    id: 89qZsI
  - name: domain
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "auth"
        "2": "payments"
        "3": "catalog"
    path: ""
    id: aACISO
  - name: owner
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "@alice"
        "2": "@bob"
        "3": "team-platform"
    path: ""
    id: OvgAPB
---

# REL

> Auto-generated from `schema/` by `scripts/generate-fileclasses.mjs`.
> Do not edit manually — re-run the script after changing schemas.
