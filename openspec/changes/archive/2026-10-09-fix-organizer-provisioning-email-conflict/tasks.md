## 1. Backend

- [x] 1.1 Implement the email check, early tenant recording, permanent-failure handling and lookup by name (liverty-music/backend#565)
- [x] 1.2 Annotate the tests for every added or modified scenario with `@spec`

## 2. Release and verification

- [x] 2.1 After the prod release (backend v1.66.2), remove the stuck Organizer `01a11dec-968d-762a-a64d-17f4ce185b92` and its tenant `394277002850336802` with admin Deactivate and Delete. Verified 2026-10-09: Delete found the unlinked tenant by name and removed it with the row. The reconciler path was not exercised in prod, because an admin had deactivated the Organizer before the release; it is covered by unit tests
- [x] 2.2 Sync the delta specs to the main specs and archive the change
