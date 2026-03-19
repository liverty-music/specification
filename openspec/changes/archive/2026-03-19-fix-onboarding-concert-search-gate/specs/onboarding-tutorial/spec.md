## MODIFIED Requirements

### Requirement: Linear Step Progression

The system SHALL enforce a strict linear progression through onboarding steps. Users SHALL NOT be able to skip steps or navigate freely during onboarding. Direct navigation via the bottom nav bar SHALL advance the step when the prerequisite conditions are met.

#### Scenario: Step 0 - Landing Page entry

- **WHEN** a user is at Step `'lp'`
- **AND** the user taps the [Get Started] CTA
- **THEN** the system SHALL advance `onboardingStep` to `'discovery'`
- **AND** navigate to the Artist Discovery screen

#### Scenario: Step 1 - Artist Discovery completion with concert data gate

- **WHEN** a user is at Step `'discovery'`
- **AND** the user has followed 3 or more artists via bubble taps
- **AND** the backend search status for all followed artists has reached `COMPLETED` or `FAILED` (verified via `ListSearchStatuses` polling), or the per-artist frontend polling deadline (15 seconds) has elapsed
- **AND** `ListWithProximity` returns at least 1 proximity group for the followed artists
- **THEN** the system SHALL activate the continuous spotlight on the Dashboard icon in the bottom navigation bar (target: `[data-nav-dashboard]`)
- **AND** the coach mark SHALL display the message: "タイムテーブルを見てみよう！"
- **AND** when the user taps the Dashboard icon through the spotlight, the system SHALL advance `onboardingStep` to `'dashboard'`
- **AND** the system SHALL navigate to the Dashboard (`/dashboard`)

#### Scenario: Step 1 - Search status polling mechanism

- **WHEN** a user follows an artist during onboarding
- **THEN** the system SHALL fire the `SearchNewConcerts` RPC to initiate the backend search
- **AND** the system SHALL NOT treat the RPC return as search completion (the RPC is fire-and-forget; the actual search runs asynchronously on the backend)
- **AND** the system SHALL poll `ListSearchStatuses` every 2 seconds to detect when the backend search log transitions to `COMPLETED` or `FAILED`
- **AND** the system SHALL batch all pending artist IDs into a single `ListSearchStatuses` call per poll cycle
- **AND** the system SHALL enforce a 15-second per-artist polling deadline as a fallback timeout

#### Scenario: Step 1 - Concert data verification after search completion

- **WHEN** all followed artists have reached a terminal search state (`COMPLETED`, `FAILED`, or timed out)
- **AND** the user has followed 3 or more artists
- **THEN** the system SHALL call `ListWithProximity` to verify that concert data exists in the database
- **AND** if at least 1 proximity group is returned, the system SHALL activate the Dashboard coach mark
- **AND** if 0 proximity groups are returned, the system SHALL NOT activate the Dashboard coach mark and SHALL re-evaluate each time a new artist's search completes

#### Scenario: Step 1 - Concert searches complete with no results

- **WHEN** a user is at Step `'discovery'`
- **AND** the user has followed 3 or more artists
- **AND** all artists' search statuses have reached a terminal state
- **AND** `ListWithProximity` returns 0 proximity groups
- **THEN** the system SHALL NOT activate the Dashboard coach mark
- **AND** the system SHALL re-evaluate the concert data gate each time a new artist is followed and their search reaches a terminal state

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

#### Scenario: Step 3 - Dashboard reveal with celebration and lane introduction

- **WHEN** a user is at Step `'dashboard'`
- **THEN** the system SHALL display the celebration overlay only once per onboarding session, persisted via `localStorage` key `onboarding.celebrationShown`
- **AND** after celebration (or immediately if already shown), the system SHALL display the region selection BottomSheet overlay (if home area not yet set)
- **AND** after region selection, the system SHALL run the lane introduction sequence
- **AND** the spotlight SHALL slide to the first concert card
- **AND** the system SHALL display a coach mark tooltip: "タップして詳細を見てみよう！"

#### Scenario: Step 3 - Concert card tap

- **WHEN** a user is at Step `'dashboard'`
- **AND** the user taps the spotlighted concert card
- **THEN** the system SHALL advance `onboardingStep` to `'detail'`
- **AND** open the concert detail sheet (popover)
- **AND** the spotlight SHALL slide to the [My Artists] tab in the bottom navigation bar

#### Scenario: Step 4 - Detail sheet with My Artists tab guidance

- **WHEN** a user is at Step `'detail'` (Detail sheet open)
- **THEN** the spotlight SHALL be highlighting the [My Artists] tab
- **AND** the system SHALL display a coach mark tooltip: "アーティスト一覧も見てみよう！"

#### Scenario: Step 4 - My Artists tab tap

- **WHEN** a user is at Step `'detail'`
- **AND** the user taps the highlighted [My Artists] tab
- **THEN** the system SHALL advance `onboardingStep` to `'my-artists'`
- **AND** navigate to the My Artists screen

#### Scenario: Step 5 - Passion Level guidance

- **WHEN** a user is at Step `'my-artists'`
- **THEN** the spotlight SHALL highlight the Passion Level toggle

#### Scenario: Step 5 - Passion Level changed

- **WHEN** a user is at Step `'my-artists'`
- **AND** the user changes the Passion Level of any artist
- **THEN** the system SHALL apply the change as a visual demo only (no server persistence)
- **AND** the system SHALL deactivate the spotlight
- **AND** the system SHALL advance `onboardingStep` to `'completed'`
- **AND** the system SHALL navigate to the landing page

### Requirement: Coach Mark Overlay System

The system SHALL provide a reusable coach mark overlay component that highlights a target element. The `aria-label` on the tooltip SHALL be `"Onboarding tip"`.

#### Scenario: Spotlight renders for active step

- **WHEN** an onboarding step requires a coach mark
- **THEN** the system SHALL display the spotlight overlay with instructional text
- **AND** the tooltip `aria-label` SHALL be `"Onboarding tip"`

### Requirement: Route guard onboarding enforcement

The system SHALL use route data `onboardingStep` (string step value) to control access during onboarding. The auth hook SHALL compare step ordering using `stepIndex()` rather than numeric comparison.

#### Scenario: Route guard allows current or past steps

- **WHEN** a route has `data.onboardingStep` set to a step value
- **AND** the user is in the onboarding flow
- **THEN** the auth hook SHALL allow navigation if `stepIndex(currentStep) >= stepIndex(route.onboardingStep)`

#### Scenario: Route guard redirects future steps

- **WHEN** a route has `data.onboardingStep` set to a step value
- **AND** the user is in the onboarding flow
- **AND** `stepIndex(currentStep) < stepIndex(route.onboardingStep)`
- **THEN** the auth hook SHALL redirect to the route for the current step
