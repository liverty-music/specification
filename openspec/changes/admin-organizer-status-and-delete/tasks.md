# Tasks

Every test task cites its scenarios with `@spec <capability-path> "<scenario>"` so `scripts/check-scenario-coverage.py` finds them at archive.

## 1. Proto (specification → BSR)

- [ ] 1.1 `entity/v1/organizer.proto`: `enum OrganizerStatus` (UNSPECIFIED 0, PROVISIONING 1, ACTIVE 2, DEACTIVATED 3) and `OrganizerStatus status = 11` (OUTPUT_ONLY, "set on admin reads; fan-facing reads never set it"); rewrite the message comment's backend-only sentence to name only the provider organizer ID and owner email; add status to the returned-fields sentence in `rpc/admin/organizer/v1/organizer_service.proto`; verify `buf lint`, `buf format -d --exit-code` pass and `buf breaking` reports nothing (additive)
- [ ] 1.2 Open the proto PR from a worktree cut from origin/main, merge it, cut a Release; verify `buf-release.yml` succeeds and record the BSR Go and npm versions here

## 2. Backend (components/adapter/admin/api/rpc/organizer)

- [ ] 2.1 Consume the release from 1.2 (`consume-proto-release` skill); verify `make check` passes
- [ ] 2.2 `mapper.OrganizerToProto` sets `Status` from the entity status (provisioning, active, deactivated; Unspecified → UNSPECIFIED); `PublicOrganizerToProto` unchanged; verify a mapper test asserts each status maps and a fan-facing mapping leaves it unset
- [ ] 2.3 Add a test for `@spec components/adapter/admin/api/rpc/organizer "Admin lists Organizers in every status"` (List returns a provisioning, an active and a deactivated Organizer each with its status) and extend the existing `"Admin reads any Organizer"` test to assert status deactivated; the other scenarios of the modified requirement already have marked tests on backend main; verify `make check` passes
- [ ] 2.4 Open the backend PR citing this change, merge, release and confirm the prod rollout; verify with a read-only prod check (admin `OrganizerService.List` response or backend logs) that Organizers carry a status

## 3. Frontend (components/infrastructure/admin/web/route/organizers)

- [ ] 3.1 Consume the release from 1.2; `OrganizerClient.delete(organizerId, signal?)` mirroring `deactivate`; verify a `test/admin/services/organizer-client.spec.ts` case sends `organizerId` and propagates errors
- [ ] 3.2 `OrganizerRow.status` and the status labels in the list and the detail; Deactivate offered only for provisioning or active (and UNSPECIFIED), Delete only for deactivated; verify route tests for `@spec components/infrastructure/admin/web/route/organizers "Organizers in every status"`, "Active Organizer", "Provisioning Organizer" and "Deactivated Organizer" pass
- [ ] 3.3 Deactivate sets the row's status to deactivated (list and detail together) and reloads the roster; on failure the status and action are unchanged; verify route tests for "Deactivate succeeds" and "Deactivate fails" pass
- [ ] 3.4 Delete confirmation `<dialog>` (name and short name, Cancel focused, Escape and Cancel dismiss, Delete control disabled in flight, one call per confirmation); verify route tests for "Confirm deletes", "Dismiss keeps the Organizer" and "Dialog names the Organizer" pass
- [ ] 3.5 Delete outcome: on success remove the row and clear the selection; FailedPrecondition shows `This organizer cannot be deleted: <server reason>.` (Delete-specific mapping in `organizer-error-message.ts`); other errors through `toUserMessage`; verify route tests for "Delete succeeds", "Delete blocked by an order" and "Delete fails otherwise" pass
- [ ] 3.6 Open the frontend PR citing this change after 2.4 is in prod; `make check` passes; merge and confirm the admin console deploy

## 4. Production check (stories/retire-an-organizer)

- [ ] 4.1 On the prod admin console's Organizers screen, confirm `fan-test` and `fan-test-2` are labelled Deactivated and offer Delete and not Deactivate (`@spec-manual stories/retire-an-organizer "Deactivated Organizer is shown deactivated"`); record the result here
- [ ] 4.2 Delete `fan-test` (01a142c8-2971-7993-a41f-620783586665) and `fan-test-2` (01a142c8-64c5-7b0d-b3e9-4b6c6768834b) from the screen; reload and confirm they are not listed, and confirm with a read-only query (cloud-provisioning `docs/runbooks/cloud-sql-access.md`) that no `organizers` row has either id (`@spec-manual stories/retire-an-organizer "Deleted Organizer is gone"`); record the result here; if Delete is refused, record the reason shown and resolve the blocker first
