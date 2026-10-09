## Why

Creating an Organizer whose operator email already belongs to a sign-in user in another tenant failed with Internal. It also left an Organizer stuck in provisioning forever and an orphaned tenant (liverty-music/backend#564, prod 2026-10-08). The fix shipped in liverty-music/backend#565; this change brings the specs in line with it.

## What Changes

- Create checks the operator email against every existing sign-in user before storing anything. It fails with AlreadyExists when another account uses the email.
- The tenant is recorded on the Organizer as soon as it exists, before the remaining provisioning steps, so a retry reuses it.
- A provisioning failure that retrying cannot fix (AlreadyExists, InvalidArgument, FailedPrecondition) is no longer left for the reconciler:
  - Create discards the Organizer and its tenant.
  - ReconcileProvisioning deactivates the Organizer so it stops being retried.
- ProvisionTenant reports a taken or rejected operator email with AlreadyExists or InvalidArgument instead of Internal.
- Deactivate finds the tenant of an Organizer whose tenant link was never recorded by the tenant's Organizer-derived name.

## Capabilities

### New Capabilities

- `components/entity/organizer/check-operator-email-available`: whether an email can become a new tenant's initial operator
- `components/entity/organizer/ensure-tenant-org`: create the Organizer's tenant, or return the one an earlier attempt created
- `components/entity/organizer/find-tenant-org`: find an Organizer's tenant by its Organizer-derived name

### Modified Capabilities

- `components/usecase/organizer/create`: email check first; tenant recorded early; a permanent failure discards the Organizer
- `components/usecase/organizer/reconcile-provisioning`: reuses a recorded tenant; a permanent failure deactivates the Organizer
- `components/usecase/organizer/deactivate`: an unlinked tenant is found by name
- `components/entity/organizer/provision-tenant`: completes a given tenant; reports a taken or rejected email as AlreadyExists or InvalidArgument

The other entity operations these usecases use (Create, SetZitadelOrgID, CompareAndSetStatus, ListByStatus, DeactivateOperators, FreeArtists, SetStatus) are unchanged.

`components/usecase/organizer/delete` is still a delta of the in-progress change `admin-delete-test-data`, and that change carries uncommitted edits. Its step 2 should read "remove its tenant through Organizer.DeleteTenant, when it has a tenant link or a tenant found by Organizer.FindTenantOrg". It also needs a scenario "Unlinked tenant". This is left to that change.

## Impact

- backend: already implemented in liverty-music/backend#565 (merged). Tests for the new and modified scenarios still need `@spec` annotations.
- No proto, frontend or infrastructure change. The admin console's error copy is fixed separately.
