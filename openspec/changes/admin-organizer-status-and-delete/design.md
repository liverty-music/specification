## Context

See proposal.md - Why. Current state, verified on origin/main of each repository on 2026-10-17:

- `entity.v1.Organizer` (`proto/liverty_music/entity/v1/organizer.proto`) has no status; its doc comment says the provisioning lifecycle is backend-only. The backend entity already has `OrganizerStatus` (provisioning 1, active 2, deactivated 3; `internal/entity/organizer.go`) and loads it on every read.
- Backend `internal/adapter/rpc/mapper/organizer.go`: `OrganizerToProto` (used only by `admin_organizer_handler.go` for Create, List, Get, SetBusinessDetails and SetPlatformFeeRate) builds on `PublicOrganizerToProto` (used by the fan concert mapper) and adds the short name and fee rate.
- Delete's refusals are already distinguishable by message: the repository returns FailedPrecondition with `organizer is not deactivated`, `an event of the organizer has an order that is not refunded`, `an event of the organizer has a settlement that is not reversed` or `the organizer has a payout account` (`internal/infrastructure/database/rdb/organizer_repo.go:484-500`), and the usecase adds `organizer is not deactivated` (`internal/usecase/organizer_uc.go:562`). The go-apperr Connect interceptor returns a non-internal AppErr as `connect.NewError(code, appErr)` (`go-apperr@v1.1.0/apperr/connect/interceptor.go:156`), so the message reaches the client; the exact `Error()` text of an AppErr (whether a cause is appended) is inferred, not checked.
- Frontend `admin/organizers/organizers-route.ts` keeps `OrganizerRow {organizer, id, name, shortName}`; `deactivate()` only reloads the roster. `organizer-error-message.ts` maps every FailedPrecondition to "This organizer is deactivated and can no longer be changed.", which is wrong for Delete. `admin/services/organizer-client.ts` has no `delete`. The approved-concerts screen already has a modal confirmation for delete.
- No admin E2E suite exists: admin screens are verified by vitest route tests (`test/admin/organizers/organizers-route.spec.ts`), and the dev environment is stopped.

## Goals / Non-Goals

**Goals:**
- Expose the status the backend already has on admin Organizer reads, and use it on the Organizers screen to show the status and offer the one lifecycle action it allows.
- Delete a deactivated Organizer from the screen, with a confirmation and readable refusal reasons.

**Non-Goals:**
- Disabling the roster, association and business-details controls for a deactivated Organizer. They are still shown and their calls fail with FailedPrecondition, as today (see Open Questions).
- A confirmation dialog for Deactivate (today it has none; unchanged).
- Status filtering or sorting of the list.
- Renaming tenant- or operator-named Organizer operations (#1158).

## Decisions

### Status on `entity.v1.Organizer` as an OUTPUT_ONLY enum, set on admin reads only

Add `enum OrganizerStatus { ORGANIZER_STATUS_UNSPECIFIED = 0; PROVISIONING = 1; ACTIVE = 2; DEACTIVATED = 3; }` (values prefixed `ORGANIZER_STATUS_`, matching the backend's numbering) in `organizer.proto`, and `OrganizerStatus status = 11 [(google.api.field_behavior) = OUTPUT_ONLY]` on `Organizer`. Its comment states it is set on admin reads; fan-facing reads never set it (UNSPECIFIED). Rewrite the message comment's "the provisioning lifecycle ... intentionally not part of this consumer entity" sentence accordingly; the provider organizer ID and owner email stay backend-only.

- Why the field: the screen's every new behavior (label, which action is offered) reads it, and the adapter spec now names it among the returned attributes.
- Why an enum and not a `deactivated` bool: the entity defines three states, and the screen distinguishes provisioning (an Organizer whose tenant is not linked yet) from active. A bool would collapse two states the entity spec names and need replacing later.
- Why on the shared entity and not an admin-only wrapper message: `short_name` and `platform_fee_rate_bps` already follow the same "set on admin reads, never on fan reads" pattern on this message; a wrapper would add a second Organizer shape for one field.
- No `deactivate_time` or similar: no requirement reads it.
- Additive (new enum, new field number); not breaking, so no `buf skip breaking` label.

Backend: `OrganizerToProto` sets `Status` from `o.Status` (a small switch to the proto enum; Unspecified maps to UNSPECIFIED); `PublicOrganizerToProto` is unchanged, so fan reads stay without it.

### Deactivate success sets the row's status locally

After Deactivate returns OK, the route sets the selected row's status to deactivated and reloads the roster (as now). No extra Get: Deactivate succeeds only after the usecase sets the status to deactivated, or when it already was (idempotent), so OK implies deactivated. A Get would add a round-trip and a failure mode for no new information.

`OrganizerRow` gains `status` (the proto enum value); rows are rebuilt from `toOrganizerRow`, and the selected row and the list entry must be the same object (or both updated) so the list label and the detail change together.

### Delete through a confirmation dialog, reusing the approved-concerts pattern

`OrganizerClient.delete(organizerId, signal?)` mirrors `deactivate`. The route opens a native `<dialog>` with `showModal()` (as approved-concerts does), naming the Organizer by name and short name. Initial focus goes to Cancel, not to Delete: the action is permanent, and the WAI-ARIA APG dialog pattern recommends focusing the least destructive control in that case (approved-concerts focuses confirm because a concert can be re-imported; an Organizer's tenant and records cannot be restored). The dialog's Delete control is disabled while the call is in flight, so a double activation sends one request.

On OK: remove the row from `organizers`, set `selected = null`, close the dialog. On error: close the dialog and show the message in the detail (`deleteError`), keep the row.

### FailedPrecondition on Delete shows the server's reason

Add a Delete-specific mapping in `organizer-error-message.ts`: for FailedPrecondition return `This organizer cannot be deleted: <rawMessage>.` (falling back to a generic sentence when the message is empty). The server's messages are short English sentences already written for this (see Context) and name exactly which blocker applies. Other codes go through `toUserMessage` as today.

- Alternative: structured `ErrorInfo` details with a reason enum per blocker. Rejected for now: it adds a proto contract and backend plumbing for a screen used only by the owner, and the four messages are stable repository strings. If the console is ever localized, revisit.

### Status labels

`Provisioning`, `Active`, `Deactivated` (the console is English). The list shows the label next to the short name; the detail shows it under the title. UNSPECIFIED (an older backend before the backend change deploys) shows no label and offers Deactivate, which is today's behavior, so a frontend that deploys first degrades to the current screen.

### Verification of scenarios

Component scenarios are covered by unit tests: the backend mapper test for the adapter scenarios, and `test/admin/organizers/organizers-route.spec.ts` (view-model and template, with the clients mocked) for the route scenarios. The story scenarios need the real backend, tenant and database, and no admin E2E suite exists, so they are verified by hand in production:

@spec-manual stories/retire-an-organizer "Deactivated Organizer is shown deactivated" -- in production, open the admin console's Organizers screen and confirm `fan-test` and `fan-test-2` (deactivated 2026-10-17) are labelled Deactivated and their detail offers Delete and not Deactivate
@spec-manual stories/retire-an-organizer "Deleted Organizer is gone" -- in production, delete `fan-test` (01a142c8-2971-7993-a41f-620783586665) and `fan-test-2` (01a142c8-64c5-7b0d-b3e9-4b6c6768834b) from the screen, reload and confirm they are not listed, and confirm with a read-only query through the db-proxy runbook that no `organizers` row has either id

## Risks / Trade-offs

- [The refusal reason depends on backend message text] → The mapping only prefixes the message, so a reworded message still reads correctly; the route test asserts the prefix and that the message is included, not the exact backend wording.
- [Frontend deploys before the backend sets the status] → UNSPECIFIED renders as today's screen (Deactivate offered, no Delete); the order in tasks (backend first) avoids it.
- [Deleting the wrong Organizer] → Delete is offered only for a deactivated Organizer, the backend refuses otherwise, and the dialog names the Organizer with Cancel focused.
- [The test Organizers turn out to have a blocker] → The screen shows the reason and nothing is removed (the usecase checks blockers before removing files or the tenant); resolve the blocker and delete again.

## Migration Plan

1. specification: proto PR, merge, Release, wait for BSR gen.
2. backend: consume the release, set the status in the admin mapper, release and deploy.
3. frontend: consume the release, ship the screen changes.
4. Production check: the two `@spec-manual` lines above.

Rollback: revert the frontend deploy (the old screen ignores the field); the proto field is additive and can stay.

## Open Questions

- Should a deactivated Organizer's detail also hide the roster's Remove, the artist search and the business-details form, since their calls are refused? Deferrable: it changes only which controls render, not this change's API or Delete flow, and can be a follow-up issue.
