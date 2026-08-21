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

The system SHALL create the initial operator as a human user in the
Organizer's tenant org with no password (`request_passwordless_registration`),
and deliver the Zitadel passkey-registration init link. The operator SHALL
complete first sign-in by registering a passkey. The tenant org's login policy
is **passkey-primary** with a mandatory recovery path (admin re-invite via
re-issued init link) and permits workspace-IdP federation — NOT passkey-only,
and NOT email-domain discovery. Org resolution is **org-pinned**: the operator
is returned to their own tenant org via the org-scoped init link on first
sign-in, and thereafter via an org handle (remembered `org_id`, or an org
code / "email me a sign-in link") that the console turns into the Zitadel
`urn:zitadel:iam:org:id:<orgId>` scope. (The login-policy shape + the
`organizer-console` project/role are provided by `organizer-tenancy`; this
change applies the policy per org and seeds the operator.)

#### Scenario: Operator completes first sign-in via init link and passkey

- **WHEN** an initial operator opens their passkey-registration init link and
  starts first sign-in
- **THEN** they SHALL register a passkey and be returned authenticated to
  their Organizer tenant org

#### Scenario: Operator is routed to their org by org-pinned entry

- **WHEN** the operator returns to sign in
- **THEN** the org SHALL be resolved by an org-pinned entry (org-scoped init
  link, remembered `org_id`, or org code / "email me a link") and pinned via
  the Zitadel `org:id` scope — never by raw email domain
- **AND** a mismatched org entry SHALL simply fail auth (no cross-org access)

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

