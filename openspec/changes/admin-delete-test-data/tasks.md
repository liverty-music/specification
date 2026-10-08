## 1. Spike (backend, cloud-provisioning)

- [ ] 1.1 Verify the Zitadel rights the deletions need (design D4, Open Questions). Verify that the `organizer-provisioner` machine user (`IAM_ORG_MANAGER`) can `RemoveOrg` a tenant org. Then determine which machine user can remove a product-org human user (`organizer-provisioner` or `backend-app`), and whether that key is mounted in `admin-console-api`. Check each against the Zitadel docs and the current memberships in `cloud-provisioning/src/zitadel`. Record the answer in design.md D4, and if a right or mount is missing, add a task to group 7
- [ ] 1.2 Check that `admin-console-api`'s ConfigMap has `ORGANIZER_MEDIA_BUCKET` and `ORGANIZER_MEDIA_INTERNAL_BUCKET`, and that its service account may delete objects in both buckets. Record the result in design.md D5, and if anything is missing, add a task to group 7

## 2. Proto (specification → BSR)

- [ ] 2.1 Add `rpc Delete(DeleteRequest) returns (DeleteResponse)` to `rpc/admin/organizer/v1/OrganizerService` (`organizer_id` required, UUID), and a new `rpc/admin/user/v1/user_service.proto` with `UserService.Delete(DeleteRequest{user_id})` (required, UUID). Doc comments list Unauthenticated, PermissionDenied, InvalidArgument, NotFound and FailedPrecondition. Verify that `buf lint`, `buf format -d` and `buf breaking` pass
- [ ] 2.2 Open the specification PR, merge it, cut the Release, and verify that `buf-release.yml` succeeds and the BSR packages carry both RPCs

## 3. Entity operations (backend)

- [ ] 3.1 `components/entity/organizer/delete`: add `Delete(ctx, id, dryRun)` to `OrganizerRepository`, as one transaction per design D2/D3. Verify integration tests pass for:
  - Organizer with a published Series
  - Refunded purchase
  - Active Organizer
  - Paid order
  - Settlement
  - Payout account
  - Unknown id
  - a dry run that removes nothing
- [ ] 3.2 `components/entity/media/list-by-organizer`: add `ListByOrganizer` to `MediaRepository`. Verify integration tests pass for Cover and replaced upload, and No media
- [ ] 3.3 `components/entity/order/list-by-buyer`: add `ListByBuyer` to the order repository. Verify integration tests pass for Paid and refunded orders, and No orders
- [ ] 3.4 `components/entity/media/delete-original` and `delete-variants`: annotate the existing `ImageStorer.DeleteOriginal` and `DeleteVariants` tests with the spec scenarios (Uploaded original, Served cover, Already removed). Add the missing not-found cases, and verify they pass
- [ ] 3.5 `components/entity/organizer/delete-tenant`: add `DeleteTenant` to `OrganizerProvisioner` (Management API `RemoveOrg`, NotFound counts as success). Verify unit tests with a fake client pass for Tenant with operators and Already removed
- [ ] 3.6 `components/entity/user/delete-identity`: declare `IdentityRemover` in `internal/entity` and implement it in `internal/infrastructure/zitadel` with the client chosen in 1.1. Verify unit tests with a fake client pass for Existing identity and Already removed

## 4. Usecases (backend)

- [ ] 4.1 `components/usecase/organizer/delete`: add `OrganizerUseCase.Delete` in the order of design D1 (dry-run check, files, tenant, records). Verify unit tests pass with the operations mocked for:
  - Deactivated test Organizer
  - Active Organizer
  - Organizer without a tenant
  - Unknown Organizer
  - Paid order
  - Refunded order
  - Tenant removal fails
- [ ] 4.2 `components/usecase/user/delete`: extend `UserUseCase.Delete` with User.Get, the Ticket.ListByHolder / Order.ListByBuyer check and User.DeleteIdentity before User.Delete. Verify unit tests pass for:
  - Existing user
  - Unknown user
  - User holding a ticket
  - User with only refunded purchases
  - Retry after the record failed
- [ ] 4.3 Update the Purpose of `openspec/specs/components/usecase/user/delete/spec.md` at archive: it is now exposed through the admin UserService. Note this in the archive PR

## 5. Admin boundary (backend)

- [ ] 5.1 `components/adapter/admin/api/rpc/organizer`: add the `Delete` handler. Verify handler tests pass for Admin deletes a deactivated Organizer, Delete refused and Missing OrganizerId (via the validation interceptor), and that the existing tests still pass
- [ ] 5.2 `components/adapter/admin/api/rpc/user`: add the admin `UserHandler.Delete` and register it in the admin handler list in `internal/di/provider.go`. Verify tests pass for:
  - Not signed in
  - Non-admin (through the admin server's role interceptor, like `admin_authorization_test.go`)
  - Admin removes a test user
  - Missing UserId
  - User holds a ticket
- [ ] 5.3 Open the backend PR (after 2.2), get `make check` and CI green, merge, cut a release, and verify that `admin-console-api` runs the new version in prod

## 6. Cleanup run (prod operations, design D7)

- [ ] 6.1 Deactivate each test Organizer that is still active, through the admin `OrganizerService.Deactivate`
- [ ] 6.2 Delete the 15 test Organizers one at a time through `OrganizerService.Delete`, running the login probe from `docs/runbooks/zitadel-hang.md` after each. Verify the organizers, their series, events and media rows are gone, the GCS prefixes are empty and the Zitadel tenant orgs are gone
- [ ] 6.3 Delete the test fan Users `pannpers+dev1`, `+3`, `+6` and `+10` through `UserService.Delete`, and remove the Zitadel-only users `pannpers+2`, `+4`, `+5` and `+8` in the Zitadel console. Verify the kept accounts remain: `pepperoni9@gmail.com`, `crusher_theory_dsa@yahoo.co.jp` and `e2e-test-password@liverty-music.app`

## 7. Infrastructure follow-ups (cloud-provisioning)

- [ ] 7.1 Apply whatever 1.1 and 1.2 found missing (a Zitadel membership, a key mount, the bucket env vars or IAM). Verify with `kubectl kustomize` / the Pulumi preview, then merge and apply before 6.1. If nothing was missing, mark this done with a note in design.md
