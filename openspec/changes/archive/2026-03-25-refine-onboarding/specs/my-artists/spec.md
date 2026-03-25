## MODIFIED Requirements

### Requirement: Hype Change Persisted for Guest Users

The system SHALL persist hype changes made by guest users to localStorage without reverting them, regardless of onboarding step.

#### Scenario: Guest user changes hype during MY_ARTISTS onboarding step

- **WHEN** a user at Step `'my-artists'` changes a hype level
- **AND** the user is not authenticated
- **THEN** the system SHALL persist the hype value in `GuestService` under `liverty:guest:hypes`
- **AND** the system SHALL NOT revert the hype change in the UI
- **AND** the system SHALL advance `onboardingStep` to `'completed'`

#### Scenario: Guest user changes hype after onboarding completion

- **WHEN** a guest user (onboarding completed) changes a hype level on the My Artists page
- **THEN** the system SHALL persist the hype value in `GuestService`
- **AND** the system SHALL NOT show a modal dialog
- **AND** the system SHALL display the guest signup banner (non-modal)

## REMOVED Requirements

### Requirement: Hype change reverted during MY_ARTISTS step

**Reason**: Reverting the user's explicitly chosen hype value immediately after they set it is confusing and contradicts the "raise your hype" coaching message. Persisting the value and merging on signup is the correct behavior.

**Migration**: Remove `artist.hype = prev` revert line in `my-artists-route.ts` `onHypeInput()`. Remove the `isOnboardingStepMyArtists` branch that triggers revert.

### Requirement: HypeNotificationDialog auto-display on unauthenticated hype change

**Reason**: The dialog conflated hype explanation with account signup prompts, appearing after the user's action was silently discarded. Hype explanation is now provided upfront via PageHelp auto-open on first visit. Account promotion is handled by the non-modal signup banner.

**Migration**: Remove `showNotificationDialog = true` trigger from `onHypeInput()`. Remove `HypeNotificationDialog` component from `my-artists-route.html`. The `HypeNotificationDialog` component may be deleted.
