## MODIFIED Requirements

### Requirement: Linear Step Progression

The system SHALL enforce a strict linear progression through onboarding steps. Users SHALL NOT be able to skip steps or navigate freely during onboarding. Direct navigation via the bottom nav bar SHALL advance the step when the prerequisite conditions are met.

#### Scenario: Step 5 - Passion Level guidance

- **WHEN** a user is at Step `'my-artists'`
- **AND** followed artists have been loaded
- **THEN** the spotlight SHALL highlight the `[data-artist-rows]` element (the `<tbody>` containing artist rows with hype sliders)
- **AND** the coach mark SHALL display the message: "絶対に見逃したくないアーティストの熱量を上げておこう"

#### Scenario: Step 5 - User taps a hype dot

- **WHEN** a user is at Step `'my-artists'`
- **AND** the user taps any hype dot on the inline slider
- **THEN** the native `change` event SHALL bubble to `MyArtistsRoute`
- **AND** the parent SHALL detect `isOnboardingStepMyArtists` and revert the hype change
- **AND** the system SHALL deactivate the spotlight
- **AND** the system SHALL advance `onboardingStep` to `'completed'`
- **AND** if the user is not authenticated, the system SHALL open the hype-notification-dialog on the same tap (without requiring a second tap)

#### Scenario: Step 5 - Spotlight activation for unauthenticated users

- **WHEN** a user is at Step `'my-artists'`
- **AND** the user is not authenticated
- **THEN** `loading()` SHALL NOT call `ListFollowed` RPC (the RPC requires authentication)
- **AND** the system SHALL still activate the spotlight on `[data-artist-rows]` with the guidance message
- **AND** the artist list SHALL display artists from the guest store (populated during onboarding)
