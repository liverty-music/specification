<!-- spec: state-management | target: components/usecase/follow/follow | flags: CLASSNAME | new_name: Follow an artist -->

### Requirement: Follow an artist

Followed-artist state SHALL be owned by a single observable store, serving as the single source of truth for followed artists across all pages. The store SHALL expose derived views for the set of followed artist IDs and the count of followed artists. For guest users, changes SHALL be persisted to local storage. For authenticated users, changes SHALL be persisted via the backend Follow RPC.

#### Scenario: Hydrate from guest state

- **WHEN** the store is asked to hydrate during onboarding
- **THEN** it SHALL set the followed artists from the guest's locally stored follows
- **AND** any UI bound to the followed-artist count SHALL update automatically

#### Scenario: Follow an artist (guest)

- **WHEN** an artist is followed and the user is not authenticated
- **THEN** the system SHALL optimistically append the artist to the followed artists
- **AND** the system SHALL persist the follow to local storage
- **AND** the derived followed-artist set and count SHALL reflect the new state immediately

#### Scenario: Follow an artist (authenticated)

- **WHEN** an artist is followed and the user is authenticated
- **THEN** the system SHALL optimistically append the artist to the followed artists
- **AND** the system SHALL call the backend Follow RPC
- **AND** on RPC failure, the system SHALL roll back the followed artists to their previous state

#### Scenario: Duplicate follow is no-op

- **WHEN** an artist is followed whose ID is already among the followed artists
- **THEN** the followed artists SHALL remain unchanged

#### Scenario: Followed artist IDs derivation

- **WHEN** the set of followed artist IDs is accessed
- **THEN** it SHALL return the set of IDs derived from the current followed artists
