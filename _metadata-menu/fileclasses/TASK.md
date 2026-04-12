---
version: "2.14"
mapWithTag: false
icon: check-square
tagNames: 
filesPaths:
  - 04-delivery/tasks
bookmarksGroups: 
excludes: 
extends: 
limit: 100
savedViews: []
favoriteView: 
fieldsOrder:
  - 51UkCC
  - OeP-pO
  - Fgv1Av
  - TPKO20
fields:
  - name: status
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "backlog"
        "2": "ready"
        "3": "in-progress"
        "4": "done"
        "5": "blocked"
    path: ""
    id: 51UkCC
  - name: estimated_complexity
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "simple"
        "2": "medium"
        "3": "complex"
    path: ""
    id: OeP-pO
  - name: domain
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "auth"
        "2": "payments"
        "3": "catalog"
    path: ""
    id: Fgv1Av
  - name: owner
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "@alice"
        "2": "@bob"
        "3": "team-platform"
    path: ""
    id: TPKO20
---

# TASK

> Auto-generated from `schema/` by `scripts/generate-fileclasses.mjs`.
> Do not edit manually — re-run the script after changing schemas.
