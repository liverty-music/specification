## Why

The admin console's Organizers screen cannot finish an Organizer's lifecycle (#1164). The admin Organizer read carries no status, so after Deactivate succeeds the screen still shows the Deactivate button and nothing visibly changes; and although `OrganizerService.Delete` exists, the screen has no way to call it, so a deactivated test Organizer can only be removed by calling the API by hand. Two deactivated test Organizers (`fan-test`, `fan-test-2`, deactivated on 2026-10-17) are waiting to be deleted.

## What Changes

- The admin `OrganizerService` returns each Organizer with its status (provisioning, active or deactivated) on Create, List, Get, SetBusinessDetails and SetPlatformFeeRate. Fan-facing reads still never carry it. Additive proto change: a new `OrganizerStatus` enum and an output-only `status` field on `entity.v1.Organizer`.
- The Organizers screen shows each Organizer's status in the list and in the selected Organizer's detail.
- The screen offers Deactivate only for a provisioning or active Organizer and shows the new status as soon as Deactivate succeeds.
- A deactivated Organizer's detail hides the controls whose calls it refuses (the roster's Remove, the artist search and Associate, the business-details form); the platform fee rate stays.
- The screen offers Delete only for a deactivated Organizer, behind a confirmation dialog that names it; a successful Delete removes it from the list, and a refusal (FailedPrecondition) shows the reason the server gives (an order that is not refunded, a settlement that is not reversed, a payout account).
- A first spec for the Organizers screen, covering the parts this change touches: the list, the status, the controls a deactivated Organizer keeps, Deactivate and Delete.

## Capabilities

### New Capabilities

- `components/infrastructure/admin/web/route/organizers`: the admin Organizers screen - the Organizer list with status, the selected Organizer's status and the controls a deactivated Organizer keeps, Deactivate and Delete with confirmation and refusal reasons.
- `stories/retire-an-organizer`: an admin retires an Organizer from the console, from deactivation to permanent deletion.

### Modified Capabilities

- `components/adapter/admin/api/rpc/organizer`: an Organizer is returned with its status.

The Organizer entity (`components/entity/organizer`) is unchanged: its status attribute and state diagram already define provisioning, active and deactivated. OrganizerUseCase.List, Get, Deactivate and Delete (`components/usecase/organizer/{list,get,deactivate,delete}`) and the entity operations they call (`components/entity/organizer/{list,get,delete,delete-tenant,deactivate-operators,free-artists,set-status}`) are unchanged: they already return the status and already enforce the deactivated precondition; this change only exposes the status and calls Delete from the screen.

## Impact

- **specification**: `proto/liverty_music/entity/v1/organizer.proto` gains `enum OrganizerStatus` and `Organizer.status` (OUTPUT_ONLY, set on admin reads only); the admin `OrganizerService` doc comment lists status among the returned fields. Additive, not breaking. Needs a Release and BSR gen before backend and frontend can consume it.
- **backend**: the admin Organizer mapper sets the status; the fan-facing mapper does not.
- **frontend**: `admin/services/organizer-client.ts` gains `delete`; `admin/organizers/organizers-route` shows the status, hides Deactivate and the refused roster, association and business-details controls for a deactivated Organizer, and adds Delete with a confirmation dialog and refusal reasons.
- **Production check**: delete `fan-test` (`01a142c8-2971-7993-a41f-620783586665`) and `fan-test-2` (`01a142c8-64c5-7b0d-b3e9-4b6c6768834b`) from the new screen.
- **Overlap with #1158** (change `rename-organization-operations`, liverty-music/specification#1169, which moves the Organizer operations on the Organization at the identity provider into an `organization` entity): this change cites those operations only by their current spec paths in this proposal and changes none of them, and its specs use the vocabulary #1169 settles (Organizer is the business, a member uses the organizer console, an identity is an account at the identity provider, admin is Liverty Music staff), so the two changes do not conflict.
