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
  - t5O_Ns
  - tZlqdd
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
  - name: domain
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "auth"
        "2": "payments"
        "3": "catalog"
    path: ""
    id: t5O_Ns
  - name: owner
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "@alice"
        "2": "@bob"
        "3": "team-platform"
    path: ""
    id: tZlqdd
---

# RISK

> Auto-generated from `schema/` by `scripts/generate-fileclasses.mjs`.
> Do not edit manually — re-run the script after changing schemas.
