---
version: "2.14"
mapWithTag: false
icon: alert-octagon
tagNames: 
filesPaths:
  - 04-delivery/risks
bookmarksGroups: 
excludes: 
extends: 
limit: 100
savedViews: []
favoriteView: 
fieldsOrder:
  - w2tsYO
  - CwnwmJ
  - aVGvWJ
fields:
  - name: status
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "open"
        "2": "mitigating"
        "3": "mitigated"
        "4": "accepted"
        "5": "closed"
    path: ""
    id: w2tsYO
  - name: severity
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "high"
        "2": "medium"
        "3": "low"
    path: ""
    id: CwnwmJ
  - name: likelihood
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "high"
        "2": "medium"
        "3": "low"
    path: ""
    id: aVGvWJ
---

# RISK

> Auto-generated from `schema/` by `scripts/generate-fileclasses.py`.
> Do not edit manually — re-run the script after changing schemas.
