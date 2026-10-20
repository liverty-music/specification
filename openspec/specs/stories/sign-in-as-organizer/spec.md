# Sign in as a member of an Organizer

## Purpose

A member signs in to the organizer console, a separate app from the fan
app and the admin console, and always lands in their own Organizer's
Organization, never another one, whether signing in for the first time from an
invitation or returning with a passkey.

```mermaid
usecase-beta
direction LR
actor Member("member")
actor Admin("admin")
systemBoundary "Liverty Music"
  Goal("Sign in as organizer")
  OrganizerUseCaseCreate("OrganizerUseCase.Create")
  OrganizerUseCaseSendSignInLinks("OrganizerUseCase.SendSignInLinks")
end
Member --> Goal
Goal ..> : include OrganizerUseCaseCreate
Goal ..> : include OrganizerUseCaseSendSignInLinks
Admin --> OrganizerUseCaseCreate
```

## Requirements

### Requirement: Sign in as a member via org-pinned entry

The organizer console SHALL authenticate members through the identity provider's
sign-in (PKCE, no client secret) using the shared `organizer-console` client. The member's
Organization is **bound to their identity** — NOT granted by a URL parameter and NOT by
email domain. An entry link MAY carry the Organization's id as a hint (the `org_id`
query parameter of the invitation's return address) so that sign-in uses that
Organization's login policy, and the console MAY remember the hint on the device for later
sign-ins. The hint never grants access: the authenticated token's Organization decides, and
a hint that differs from it leads to re-authentication or denial, never into the
hinted Organization:

- **First sign-in** happens through the identity provider's standard invitation
  flow (the invite links to the IdP, not the console). After the member sets
  up a passkey, the Organization's login policy's default redirect returns them to the
  console (as Organization.Provision sets it up); the console then
  completes OIDC using the member's freshly established session.
- **Returning sign-in** is initiated from the console and authenticated with the
  member's existing passkey.

The console SHALL **enforce that the authenticated token's Organization is the intended
Organization** (the remembered hint, when there is one). A session belonging to a different Organization (e.g. an unrelated identity-provider
SSO session already present in the browser) SHALL NOT be silently accepted for a
different member or Organization: the console SHALL detect the mismatch and force
re-authentication (or sign the stale session out) rather than admitting the
wrong member. There is no fixed Organization id at build time and no Organization picker.

#### Scenario: Member signs in and is routed to their Organization by org-pinned entry

- **WHEN** a member completes sign-in
- **THEN** the console SHALL return them to their own Organizer's Organization,
  resolved from their authenticated identity and token (the Organization is bound to the
  member) — never by raw email domain
- **AND** a session or entry that does not resolve to the member's own Organization
  SHALL fail auth (no cross-Organization access)

#### Scenario: One OIDC client serves all Organizations

- **WHEN** members of different Organizers' Organizations sign in
- **THEN** the same `organizer-console` OIDC client SHALL serve them all (no
  per-Organizer client, no build-time Organization id)

#### Scenario: Invited owner lands on the console after accepting the invite

- **WHEN** an invited owner completes credential setup via the identity
  provider's invitation flow
- **THEN** they SHALL be returned to the organizer console and, after the console
  completes OIDC, land authenticated on their own Organizer's Organization

#### Scenario: A reused or mismatched session does not silently onboard the wrong member

- **WHEN** the console is entered while an identity-provider session for a different Organization
  already exists in the browser
- **THEN** the console SHALL NOT admit that session as the intended member; it
  SHALL force re-authentication (or sign the stale session out) so the member
  is authenticated in the correct Organization — never routed into another one

#### Scenario: A hint for another org grants nothing

- **WHEN** a member of one Organizer opens the console through a link whose `org_id` names another Organizer's Organization
- **THEN** the console SHALL NOT admit them into that Organization: after one re-authentication the token's Organization still differs, and the access denied page is shown

### Requirement: One email serves the fan account and the Organizer

A person SHALL be able to run an Organizer with the email of their fan account. The admin creates the Organizer with that email and a short name (OrganizerUseCase.Create), the person accepts the invitation and registers a passkey for their identity in the Organizer's Organization, and afterwards the fan app signs them in to the fan account and the organizer console to the Organizer, each after they type the same email and each with its own passkey. No user name is ever typed. Neither account can be reached through the other.

#### Scenario: Fan becomes an Organizer's owner

- **WHEN** an admin creates the Organizer `xx-records` with the email of an existing fan account, and the person accepts the invitation
- **THEN** the Organizer is active, the person signs in to the console by typing that email and using the new passkey, the sign-in shows `<email> (xx-records)`, and the fan app still signs them in to the fan account with the old passkey

### Requirement: A new device finds the Organizer by short name or by email

A member who opens the console on a device that remembers no Organization SHALL reach their Organizer's sign-in either through `https://organizer.liverty-music.app/?org=<short name>` or, from the find-organizer screen, through an emailed sign-in link for each Organizer they own (OrganizerUseCase.SendSignInLinks), and SHALL sign in to the right Organizer's Organization, never to their fan account.

#### Scenario: Owner on a new phone with the short name

- **WHEN** the owner of `xx-records`, who also has a fan account with the same email, opens `https://organizer.liverty-music.app/?org=xx-records` on a new phone and types the email
- **THEN** they sign in to xx-records' Organization and land on its Home

#### Scenario: Owner on a new phone without the short name

- **WHEN** the same owner opens the console without `?org`, enters the email on the find-organizer screen and opens the link from the email
- **THEN** they sign in to xx-records' Organization and land on its Home
