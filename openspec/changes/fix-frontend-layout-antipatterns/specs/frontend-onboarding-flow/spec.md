## MODIFIED Requirements

### Requirement: Just-in-Time Region Configuration
The system SHALL collect the user's home area during the Dashboard reveal step of the tutorial (Step 3), presenting the home area selector as a BottomSheet overlay before displaying personalized content. The selector SHALL be non-dismissible during onboarding — the user MUST select a home area to proceed.

#### Scenario: Home area setup overlay on Dashboard reveal (Step 3)
- **WHEN** the user arrives at the Dashboard during the tutorial (Step 3)
- **AND** the user has not yet configured their home area
- **THEN** the system SHALL display the Dashboard with a blurred background
- **AND** the system SHALL present the `user-home-selector` BottomSheet overlay as a native `<dialog>` element via `showModal()`
- **AND** the system SHALL pass `required="true"` to the selector component

#### Scenario: Home selector cannot be dismissed during onboarding
- **WHEN** the home selector is displayed during onboarding (Step 3) with `required="true"`
- **AND** the user taps the backdrop area outside the selector
- **THEN** the system SHALL NOT close the selector
- **AND** the selector SHALL remain open until the user completes a selection

#### Scenario: Home selector cannot be dismissed via ESC during onboarding
- **WHEN** the home selector is displayed during onboarding (Step 3) with `required="true"`
- **AND** the user presses the Escape key
- **THEN** the system SHALL prevent the default cancel event
- **AND** the selector SHALL remain open until the user completes a selection

#### Scenario: Magic moment after home area selection
- **WHEN** the user selects their home area (via quick-select or region-to-prefecture)
- **THEN** the system SHALL store the selected code in localStorage under `guest.home`
- **AND** the system SHALL immediately close the BottomSheet
- **AND** the system SHALL unblur the Dashboard background with a smooth transition animation
- **AND** the system SHALL dynamically populate the Live Highway UI with home-area-relevant events
