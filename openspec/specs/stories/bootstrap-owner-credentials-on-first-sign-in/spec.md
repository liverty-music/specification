# Bootstrap owner credentials on first sign in

## Purpose

The owner of a newly created Organizer sets up a passkey from a single
invitation email and lands in the organizer console signed in to their own
Organizer, without ever typing a code; an admin re-invites them when they lose
access.

```mermaid
usecase-beta
direction LR
actor Member("member")
actor Admin("admin")
systemBoundary "Liverty Music"
  Goal("Bootstrap owner credentials on first sign in")
  OrganizerUseCaseCreate("OrganizerUseCase.Create")
end
Member --> Goal
Goal ..> : include OrganizerUseCaseCreate
Admin --> OrganizerUseCaseCreate
```

## Requirements

### Requirement: Owner bootstraps credentials on first sign-in

When an admin creates an Organizer (OrganizerUseCase.Create), the provisioning
of its Organization (Organization.Provision) SHALL create the owner identity in
the Organizer's Organization with a **verified email and no password**, and
onboard the owner using the identity provider's **standard invitation flow**:
the system creates an invite code for the owner identity and has the identity
provider send **one** branded invitation email whose
"accept" link opens the identity provider's own credential-setup page with the
code already carried in the link. The owner SHALL complete first sign-in by
**clicking that link** (never by transcribing a code) and registering a passkey.
On completion the owner SHALL be returned to the organizer console
authenticated (the Organization's post-setup redirect targets the console, as
Organization.Provision sets it up), landing on the owner-gated placeholder.

The invitation email SHALL be the **only** message the owner must act on for
first sign-in (no separate "transport" email, and no second code email under the
normal single-entry flow). The credential (invite/verification code) SHALL
remain on the identity-provider surface and SHALL NOT be exposed in a
console/application URL.

Recovery SHALL be an **admin-initiated re-invite** (the system re-issues the
owner's invitation), consistent with the Organization's passkey-primary policy
that Organization.Provision sets up. Organization resolution is bound to the
owner identity by the invitation itself — the owner cannot be routed to a
different Organization by supplying a different email (no cross-Organization
access).

#### Scenario: Owner completes first sign-in via init link and passkey

- **WHEN** the owner opens their invitation ("accept invite") link and starts
  first sign-in
- **THEN** they SHALL register a passkey without transcribing any code, and be
  returned to the organizer console authenticated to their own Organizer's
  Organization

#### Scenario: Owner is routed to their Organization by org-pinned entry

- **WHEN** the owner signs in (first-time via the invitation, or thereafter
  with their passkey)
- **THEN** the Organization SHALL be resolved from the owner's own identity and
  token — the invitation binds the owner identity to exactly one Organization —
  never by raw email domain
- **AND** supplying a different email SHALL NOT route them into a different
  Organization (no cross-Organization access)

#### Scenario: The invitation credential is never placed in a console URL

- **WHEN** the invitation email and its link are generated
- **THEN** the invite/verification code SHALL appear only on the identity
  provider surface and SHALL NOT appear in any console/application URL

#### Scenario: Recovery is an admin re-invite

- **WHEN** the owner cannot sign in (e.g. lost all authenticators)
- **THEN** recovery SHALL be an admin-initiated re-invite that re-issues the
  owner's invitation, not a weaker password/self-registration lane
