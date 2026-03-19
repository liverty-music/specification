## MODIFIED Requirements

### Requirement: Linear Step Progression

The system SHALL enforce a strict linear progression through onboarding steps. Users SHALL NOT be able to skip steps or navigate freely during onboarding. Direct navigation via the bottom nav bar SHALL advance the step when the prerequisite conditions are met.

#### Scenario: Step 1 - Artist Discovery completion with concert data gate

- **WHEN** a user is at Step `'discovery'`
- **AND** the user has followed 3 or more artists via bubble taps
- **AND** the backend search status for all followed artists has reached `COMPLETED` or `FAILED` (verified via `ListSearchStatuses` polling), or the per-artist frontend polling deadline (15 seconds) has elapsed
- **AND** at least one followed artist has concerts in the database (verified via `ConcertService/List` per artist)
- **THEN** the system SHALL activate the continuous spotlight on the Dashboard icon in the bottom navigation bar (target: `[data-nav-dashboard]`)
- **AND** the coach mark SHALL display the message: "タイムテーブルを見てみよう！"
- **AND** when the user taps the Dashboard icon through the spotlight, the system SHALL advance `onboardingStep` to `'dashboard'`
- **AND** the system SHALL navigate to the Dashboard (`/dashboard`)

#### Scenario: Step 1 - Concert data verification after search completion

- **WHEN** all followed artists have reached a terminal search state (`COMPLETED`, `FAILED`, or timed out)
- **AND** the user has followed 3 or more artists
- **THEN** the system SHALL call `ConcertService/List` for each followed artist in parallel to verify that concert data exists in the database
- **AND** the system SHALL NOT require `guest.home` for this verification
- **AND** if at least 1 artist has concerts, the system SHALL activate the Dashboard coach mark
- **AND** if 0 artists have concerts, the system SHALL NOT activate the Dashboard coach mark and SHALL re-evaluate each time a new artist's search completes

#### Scenario: Step 1 - Concert searches complete with no results

- **WHEN** a user is at Step `'discovery'`
- **AND** the user has followed 3 or more artists
- **AND** all artists' search statuses have reached a terminal state
- **AND** no followed artist has concerts (all `ConcertService/List` responses are empty)
- **THEN** the system SHALL NOT activate the Dashboard coach mark
- **AND** the system SHALL re-evaluate the concert data gate each time a new artist is followed and their search reaches a terminal state

#### Scenario: Step 1 - Search status polling mechanism

- **WHEN** a user follows an artist during onboarding
- **THEN** the system SHALL fire the `SearchNewConcerts` RPC to initiate the backend search
- **AND** the system SHALL NOT treat the RPC return as search completion (the RPC is fire-and-forget; the actual search runs asynchronously on the backend)
- **AND** the system SHALL poll `ListSearchStatuses` every 2 seconds to detect when the backend search log transitions to `COMPLETED` or `FAILED`
- **AND** the system SHALL batch all pending artist IDs into a single `ListSearchStatuses` call per poll cycle
- **AND** the system SHALL enforce a 15-second per-artist polling deadline as a fallback timeout

#### Scenario: Step 1 - Direct Home nav tap when coach mark is active

- **WHEN** a user is at Step `'discovery'`
- **AND** the coach mark spotlight on the Dashboard icon is active
- **AND** the user taps the Home/Dashboard icon in the bottom nav bar (bypassing the coach mark overlay)
- **THEN** the system SHALL advance `onboardingStep` to `'dashboard'`
- **AND** the system SHALL navigate to `/dashboard`

#### Scenario: Step 1 - Spotlight deactivation before navigation

- **WHEN** a user is at Step `'discovery'`
- **AND** the user taps the Dashboard coach mark
- **THEN** the system SHALL deactivate the spotlight (`deactivateSpotlight()`) before navigating to `/dashboard`
