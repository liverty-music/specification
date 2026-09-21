<!-- merge_group: SET-HYPE | target: components/usecase/follow/set-hype | members: 3 -->
<!-- renamed_scenarios: 0 -->

### Requirement: Hype Changes Require Authentication for Server-Side Persistence

The system SHALL prevent unauthenticated users from calling the `SetHype` RPC or persisting hype changes to any server-side store. Guest hype selections MAY be held in client-side storage (localStorage) pending signup; see the `my-artists` capability for the guest-hype lifecycle and the `guest-data-merge` capability for the signup-time merge semantics. For authenticated users, the system SHALL persist each user's hype level per followed artist in the backend database, enabling cross-device synchronization, via a `SetHype` RPC endpoint that accepts an artist ID and a hype level and updates the user's preference for that artist; the endpoint SHALL accept all four defined `HypeType` values (WATCH, HOME, NEARBY, AWAY).

#### Scenario: Unauthenticated user attempts hype change (server-side write blocked)

- **WHEN** an unauthenticated user attempts to change a hype level (via slider tap or any UI control)
- **THEN** the system SHALL NOT call the `SetHype` RPC
- **AND** the system SHALL persist the chosen value in client-side storage (localStorage) so the choice survives reloads and can be merged into the user's account on signup
- **AND** the signup-prompt-banner SHALL be visible (per the `signup-prompt-banner` capability) so the user is aware that server-side persistence requires signup

#### Scenario: Authenticated user changes hype

- **WHEN** an authenticated user changes a hype level
- **THEN** the system SHALL call `SetHype` RPC and persist the change on the backend
- **AND** the UI SHALL update optimistically

#### Scenario: Hype level survives session restart

- **GIVEN** a user sets an artist to Away (どこでも！)
- **WHEN** the user closes and reopens the app
- **THEN** the artist SHALL still display as Away (どこでも！)

#### Scenario: Successful update

- **GIVEN** an authenticated user who follows an artist
- **WHEN** the user calls SetHype with a valid artist ID and hype level
- **THEN** the system SHALL update the hype level and return success

#### Scenario: Unauthenticated request

- **GIVEN** an unauthenticated request
- **WHEN** the user calls SetHype
- **THEN** the system SHALL return an Unauthenticated error

#### Scenario: Invalid artist ID

- **GIVEN** an authenticated user
- **WHEN** the user calls SetHype without an artist ID
- **THEN** the system SHALL return an InvalidArgument error
