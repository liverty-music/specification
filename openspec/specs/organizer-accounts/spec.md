# organizer-accounts Specification

## Purpose
The Organizer domain: the vetted seller an admin creates, its link to the
artists it represents, the runtime provisioning that gives each Organizer an
isolated Zitadel tenant its operator can sign into, and the admin surface to
manage them. The organizer-facing API and console are separate capabilities.
## Requirements
### Requirement: Admin creates an organizer with an initial operator

The system SHALL let an operator holding the platform `admin` role create an
Organizer with a name and an initial operator email. Creation is the vetting
— there is no separate `verified` flag and no self-serve registration. An
Organizer is distinct from an Artist and has its own OrganizerId. On success
the Organizer is provisioned an isolated Zitadel tenant (see idempotent
provisioning) with the initial operator seeded as its `owner`.

#### Scenario: Admin creates an organizer

- **WHEN** an operator with the `admin` role creates an Organizer with a name
  and an initial operator email
- **THEN** the Organizer SHALL exist with an isolated tenant and a `owner`
  operator, and SHALL become an active organizer

#### Scenario: Non-admin cannot create an organizer

- **WHEN** a create request is made without the `admin` role
- **THEN** the system SHALL reject it with a permission-denied error

#### Scenario: Organizer identity is separate from artist identity

- **WHEN** an artist self-publishes and an Organizer account is created for
  them
- **THEN** the Organizer SHALL have its own OrganizerId distinct from the
  Artist's ArtistId

### Requirement: Initial operator bootstraps credentials on first sign-in

The system SHALL create the initial operator as a human user in the Organizer's
tenant org with a **verified email and no password**, and onboard them using
Zitadel's **standard invitation flow**: the system creates an invite code for
the operator and has Zitadel send **one** branded invitation email whose
"accept" link opens the identity provider's own credential-setup page with the
code already carried in the link. The operator SHALL complete first sign-in by
**clicking that link** (never by transcribing a code) and registering a passkey.
On completion the operator SHALL be returned to the organizer console
authenticated (the tenant login policy's post-setup redirect targets the
console — see `organizer-tenancy`), landing on the owner-gated placeholder.

The invitation email SHALL be the **only** message the operator must act on for
first sign-in (no separate "transport" email, and no second code email under the
normal single-entry flow). The credential (invite/verification code) SHALL
remain on the identity-provider surface and SHALL NOT be exposed in a
console/application URL.

Recovery SHALL be an **admin-initiated re-invite** (the system re-issues the
operator's invitation), consistent with the tenant org's passkey-primary policy
and its recovery path in `organizer-tenancy`. Org resolution is bound to the
operator's account by the invitation itself — the operator cannot be routed to a
different org by supplying a different email (no cross-org access).

#### Scenario: Operator completes first sign-in via init link and passkey

- **WHEN** an initial operator opens their invitation ("accept invite") link and
  starts first sign-in
- **THEN** they SHALL register a passkey without transcribing any code, and be
  returned to the organizer console authenticated to their own Organizer tenant
  org

#### Scenario: Operator is routed to their org by org-pinned entry

- **WHEN** an operator signs in (first-time via the invitation, or thereafter
  with their passkey)
- **THEN** the org SHALL be resolved from the operator's own account/token — the
  invitation binds the operator to exactly one tenant org — never by raw email
  domain
- **AND** supplying a different email SHALL NOT route them into a different org
  (no cross-org access)

#### Scenario: The invitation credential is never placed in a console URL

- **WHEN** the invitation email and its link are generated
- **THEN** the invite/verification code SHALL appear only on the identity
  provider surface and SHALL NOT appear in any console/application URL

#### Scenario: Recovery is an admin re-invite

- **WHEN** an operator cannot sign in (e.g. lost all authenticators)
- **THEN** recovery SHALL be an admin-initiated re-invite that re-issues the
  operator's invitation, not a weaker password/self-registration lane

### Requirement: An artist is represented by at most one organizer

The system SHALL associate an Organizer with zero or more Artists, and each
Artist SHALL be represented by **at most one** Organizer. Associating an
Artist that does not exist SHALL be rejected (no create-on-demand);
associating an Artist already represented SHALL be rejected. An admin SHALL
be able to disassociate an Artist; reassignment is disassociate followed by
associate.

#### Scenario: A label organizer represents multiple artists

- **WHEN** an Organizer is associated with several existing Artists
- **THEN** all associated Artists SHALL be retrievable for that Organizer

#### Scenario: Associating a non-existent artist is rejected

- **WHEN** an admin associates an ArtistId that does not exist
- **THEN** the system SHALL reject it with a not-found error and SHALL NOT
  create the artist

#### Scenario: An artist cannot be claimed by a second organizer

- **WHEN** an Artist already represented by one Organizer is associated with
  a different Organizer
- **THEN** the system SHALL reject it with an already-exists error

#### Scenario: Disassociate frees the artist

- **WHEN** an admin disassociates an Artist from its Organizer
- **THEN** the association SHALL be removed and the Artist SHALL be
  associable to another Organizer

### Requirement: Admin can list and inspect organizers

The system SHALL provide admin-gated `List` and `Get` returning Organizers, and
`ListArtists` returning the artists an Organizer represents, so the admin
console can render the organizer-management screen.

#### Scenario: Admin lists organizers and inspects an organizer's artists

- **WHEN** an operator with the `admin` role lists organizers and then requests
  a given Organizer's artists
- **THEN** the system SHALL return the Organizers, and SHALL return the artists
  that Organizer represents

#### Scenario: Non-admin cannot list organizers

- **WHEN** a list/get request is made without the `admin` role
- **THEN** the system SHALL reject it with a permission-denied error

### Requirement: Organizer provisioning is idempotent and compensating

Creating an Organizer SHALL be idempotent and compensating across the
tenant-provisioning steps (tenant org, login policy, project grant, operator
+ owner grant, and the persisted `zitadel_org_id`). A retry after a partial
failure SHALL complete provisioning without creating a duplicate Organizer or
duplicate tenant org, and SHALL never leave the Organizer without a `owner`
operator.

#### Scenario: Retry after mid-provisioning failure does not duplicate

- **WHEN** a `Create` is retried after failing partway through provisioning
- **THEN** the system SHALL complete the remaining steps without creating a
  second Organizer or a second tenant org

#### Scenario: Operator is never left without an owner grant

- **WHEN** provisioning completes for an Organizer
- **THEN** the Organizer SHALL have at least one operator holding the
  `owner` role

### Requirement: An organizer can be deactivated

The system SHALL support deactivating an Organizer. For a deactivated
Organizer, the backend SHALL reject all organizer operations, its operators
SHALL be deactivated in Zitadel, and its artist associations SHALL be freed
so the artists can be re-associated. Full teardown of the tenant org and
grants is out of scope for this change.

#### Scenario: Deactivated organizer's operations are rejected

- **WHEN** an Organizer is deactivated and a request targets it
- **THEN** the system SHALL reject the request and the Organizer's operators
  SHALL no longer be able to act

#### Scenario: Deactivation frees the organizer's artists

- **WHEN** an Organizer with associated artists is deactivated
- **THEN** those artists SHALL become associable to another Organizer

### Requirement: Organizer lifecycle emits analytics events

The system SHALL emit backend analytics events `organizer.created` and
`organizer.artist.associated`, keyed on `organizer_id` (admin-actor / group
events, not fan-user events), forwarded to the analytics pipeline.

#### Scenario: Creating an organizer emits an event

- **WHEN** an Organizer is created
- **THEN** the system SHALL emit an `organizer.created` analytics event with
  the `organizer_id`

#### Scenario: Associating an artist emits an event

- **WHEN** an Artist is associated with an Organizer
- **THEN** the system SHALL emit an `organizer.artist.associated` event with
  the `organizer_id` and `artist_id`

