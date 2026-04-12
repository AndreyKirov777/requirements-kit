---
version: "2.14"
mapWithTag: false
icon: shield-check
tagNames: 
filesPaths:
  - 02-requirements/nfr
bookmarksGroups: 
excludes: 
extends: 
limit: 100
savedViews: []
favoriteView: 
fieldsOrder:
  - Sj_CFN
  - bIjQpF
  - VRvGEv
  - zTS--J
  - V3SDwI
fields:
  - name: status
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "draft"
        "2": "proposed"
        "3": "approved"
        "4": "in-implementation"
        "5": "implemented"
        "6": "verified"
        "7": "deprecated"
    path: ""
    id: Sj_CFN
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
    id: bIjQpF
  - name: quality_attribute
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "performance"
        "2": "security"
        "3": "scalability"
        "4": "reliability"
        "5": "availability"
        "6": "usability"
        "7": "maintainability"
        "8": "portability"
        "9": "compliance"
        "10": "observability"
    path: ""
    id: VRvGEv
  - name: domain
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "auth"
        "2": "payments"
        "3": "catalog"
    path: ""
    id: zTS--J
  - name: owner
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "@alice"
        "2": "@bob"
        "3": "team-platform"
    path: ""
    id: V3SDwI
---

# NFR

> Auto-generated from `schema/` by `scripts/generate-fileclasses.mjs`.
> Do not edit manually — re-run the script after changing schemas.
