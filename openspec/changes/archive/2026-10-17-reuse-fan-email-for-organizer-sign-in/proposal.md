## Why

An admin cannot create an Organizer for a person who already has a fan account with the same email: `OrganizerUseCase.Create` fails with AlreadyExists (`entity/organizer/check-operator-email-available`). Sign-in user names are unique across the whole identity provider, and today each Organizer identity's user name is its email. The people Organizers are made of - self-publishing artists, label and agency staff, promoters - are often fans on Liverty Music too and expect one email for both.

Two more problems sit on the same path (liverty-music/specification#1149): an Organizer's Organization at the identity provider is named `org-<Organizer id>`, which identifies nothing, and an organizer who opens the console on a new device, without the invitation link or a remembered Organizer, gets a sign-in tied to no Organization - which, once one email has two accounts, signs them in to the fan account.

The fix keeps the structure the identity provider recommends for business customers - one Organization per Organizer, holding the identities of the people who run it - which is also what later lets an Organizer bring its own sign-in (SSO), its own sign-in policy and its own team. The fan account and the Organizer identity stay separate accounts that share an email; the person signs in to either by typing that email.

## What Changes

- **Email is the sign-in, not the user name.** An Organizer identity's user name becomes `<email> (<short name>)`, unique across the identity provider; its email is the person's email, which may also be a fan account's. People sign in by typing their email, the identity provider's documented "login with the email attribute" (verified in production on 2026-10-15). The product and admin organizations are not changed.
- **Organizer short name** (liverty-music/specification#1149). An admin gives every Organizer a short name at creation: 3 to 32 lowercase letters, digits and hyphens, starting with a letter, unique, never changed, `admin` and `liverty-music` reserved. It names the Organizer's Organization at the identity provider, completes the identity user names, and gives the console a readable sign-in address (`?org=<short name>`).
- **No identity-provider-wide email check.** `Organizer.CheckOperatorEmailAvailable` is removed; `Organizer.ProvisionTenant` no longer fails for an email used in another Organization.
- **Sign-in is always tied to one Organization.** The console never starts a sign-in that names no Organization. Without one it asks for the email and sends sign-in links (new `OrganizerService.SendSignInLinks`), one per active Organizer the address owns; the answer never reveals whether any exists. An Organizer's Organization reports an unknown email at sign-in instead of hiding it (`ignoreUnknownUsernames` off), because with it on the identity provider cannot complete a passkey sign-in typed by email (verified in production); the product organization keeps hiding it.
- **One email value object.** Every email in the API (a User's email, an Organizer's owner and contact emails, the address SendSignInLinks takes) becomes the generic `Email`, as `PhoneNumber` and `Url` already are; the field name says whose address it is. An email is at most 165 characters everywhere, so that any address can become an Organizer identity's user name `<email> (<short name>)` within the identity provider's 200. **BREAKING (generated code)**: `UserEmail` and `ContactEmail` are removed (wire-compatible).
- **Vocabulary (only where this change writes).** A new entity **Organization** names the identity provider's sign-in unit; the Organizer attribute **operator email** becomes **owner email**. **BREAKING (admin API)**: `CreateRequest.operator_email` → `owner_email`, and `short_name` is required. The tenant- and operator-named operations keep their names here; renaming a method is a change of its own (spec schema), done with the forbidden-word CI check.

## Capabilities

### New Capabilities

- `components/entity/organization`: the identity provider's sign-in unit; one per Organizer, named by its short name, plus the product and admin organizations; a person signs in with their email
- `components/entity/organizer/list-by-owner-email`: the active Organizers whose owner email is a given address
- `components/entity/organizer/send-sign-in-links`: the email that carries one console sign-in link per Organizer
- `components/usecase/organizer/send-sign-in-links`: a person asks for their Organizers' sign-in links by email, without learning whether any exist
- `components/infrastructure/organizer/web/route/find-organizer`: the console screen that asks for the email when it does not know the Organization

### Modified Capabilities

- `components/entity/organizer` (Purpose): `short name` added; `operator email` → `owner email`; `provider organizer ID` is the ID of the Organizer's Organization. contact email at most 165 characters. Requirements: "Name and operator email are well-formed" → "Name, short name and owner email are well-formed"; "Business details": the contact email is at most 165 characters
- `components/entity/user` (Purpose): the email is at most 165 characters
- `components/entity/organizer/create`: stores the short name; AlreadyExists for a short name already used
- `components/entity/organizer/ensure-tenant-org`, `find-tenant-org`: the Organization is named by the short name
- `components/entity/organizer/provision-tenant`: the owner identity's user name is `<email> (<short name>)`; any email is accepted, including a fan's; the Organization reports unknown emails at sign-in
- `components/entity/organizer/check-operator-email-available`: removed
- `components/usecase/organizer/create`: takes the short name; no email check; a fan's email succeeds
- `components/usecase/organizer/reconcile-provisioning`: the permanent-failure scenario uses a rejected email
- `components/usecase/payout-account/get`: the account is opened with the owner email
- `components/adapter/admin/api/rpc/organizer`: Create takes and validates the short name and the owner email; reads return the short name
- `components/adapter/organizer/api/rpc/organizer`: SendSignInLinks, the one call that needs no sign-in
- `components/infrastructure/organizer/web/global/hosted-login`: the Organization's policy reports unknown emails; identities sign in with their email; the console names the Organization by `?org=<short name>`, `?org_id` or the device
- `components/infrastructure/organizer/web/global/organizer-shell`: without a known Organization the console opens the find-organizer screen instead of a sign-in
- `components/infrastructure/fan/web/global/hosted-login`: a fan's user name stays their email
- `stories/sign-in-as-organizer`: same email as the fan account; a new device finds the Organizer by email or by short name

Entity operations this change relies on and does not change: `Organizer.SetProviderOrganizerID`, `Organizer.CompareAndSetStatus`, `Organizer.GetByProviderOrganizerID`, `Organizer.ListByStatus`, `PayoutAccount.*`.

In flight on the same specs: `organizer-antisocial-vetting` adds requirements to `usecase/organizer/deactivate` and `usecase/payout-account/get` (ADDED blocks; no overlap with this change's MODIFIED block on `payout-account/get`).

Follow-ups this change prepares and does not do: owner-invited team members with roles, per-Organizer SSO, the tenant/operator renames with the forbidden-word CI check, the console's post-sign-in crash (`AUR3500` when the callback lands on `/`), and the `SeriesService.SetCoverImage` ownership gap.

## Impact

- **specification**: proto `entity/v1/entity.proto` (`Email`, replacing `entity.v1.UserEmail` and `entity.v1.ContactEmail` in `User`, `Organizer`, `rpc/user/v1` and `rpc/admin/organizer/v1`), `entity/v1/organizer.proto` (`OrganizerShortName`, `short_name` on admin reads), `rpc/admin/organizer/v1` (`owner_email`, `short_name`), `rpc/organizer/v1` (`SendSignInLinks`). Closes liverty-music/specification#1149.
- **backend**: `organizers.operator_email` → `owner_email`, new `short_name` (unique); `users.email`, `organizers.owner_email` and `organizers.contact_email` at most 165 characters (entity and DB); the generated `Email` in the user and organizer mappers; provisioning names the Organization by the short name, creates the owner identity with user name `<email> (<short name>)` and sets `ignoreUnknownUsernames` off; `CheckOperatorEmailAvailable` removed; `OrganizerUseCase.SendSignInLinks` with Postmark mail and limits; the organizer server exposes `SendSignInLinks` without sign-in.
- **frontend**: organizer console - `?org=<short name>`, no sign-in without an Organization, the find-organizer screen; admin console - short name and owner email fields; every use of the generated `UserEmail` and `ContactEmail` becomes `Email`.
- **cloud-provisioning**: none (no identity-provider policy changes outside the Organizer Organizations, which the backend provisions).
- **production**: the one existing Organizer gets a short name; its Organization is renamed, its login policy updated and its identities' user names rewritten (design Migration Plan).
