---
version: "2.14"
mapWithTag: false
icon: file-signature
tagNames: 
filesPaths:
  - 03-architecture/integrations
bookmarksGroups: 
excludes: 
extends: 
limit: 100
savedViews: []
favoriteView: 
fieldsOrder:
  - p9tr-V
  - INewPs
  - RvZReg
  - AczLf4
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
    id: p9tr-V
  - name: protocol
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "REST"
        "2": "gRPC"
        "3": "Event"
        "4": "GraphQL"
        "5": "WebSocket"
        "6": "Other"
    path: ""
    id: INewPs
  - name: domain
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "auth"
        "2": "payments"
        "3": "catalog"
    path: ""
    id: RvZReg
  - name: owner
    type: Select
    options:
      sourceType: ValuesList
      valuesList:
        "1": "@alice"
        "2": "@bob"
        "3": "team-platform"
    path: ""
    id: AczLf4
---

# CONTRACT

> Auto-generated from `schema/` by `scripts/generate-fileclasses.mjs`.
> Do not edit manually — re-run the script after changing schemas.
