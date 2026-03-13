## MODIFIED Requirements

### Requirement: Just-in-Time Region Configuration

The system SHALL collect the user's home area during the Dashboard reveal step of the tutorial (Step 3), presenting the home area selector as a BottomSheet overlay before displaying personalized content. The selector SHALL use the same 2-step region-to-prefecture flow used throughout the application.

#### Scenario: Home area setup overlay on Dashboard reveal (Step 3)

- **WHEN** the user arrives at the Dashboard during the tutorial (Step 3)
- **AND** the user has not yet configured their home area
- **THEN** the system SHALL display the Dashboard with a blurred background
- **AND** the system SHALL present the `user-home-selector` BottomSheet overlay as a native `<dialog>` element via `showModal()`, promoted to the browser's Top Layer (no z-index stacking)
- **AND** the selector SHALL display Step 1 with quick-select major city buttons (Tokyo, Osaka, Nagoya, Fukuoka, Sapporo, Sendai) and region buttons (Hokkaido, Tohoku, Kanto, Chubu, Kinki, Chugoku, Shikoku, Kyushu)
- **AND** the BottomSheet SHALL use the design system's dark surface palette and sheet radius token

#### Scenario: Quick-select city in onboarding

- **WHEN** the user taps a quick-select city button in Step 1
- **THEN** the system SHALL immediately confirm the selection with the city's prefecture code (e.g., Tokyo -> JP-13)
- **AND** the system SHALL NOT display Step 2

#### Scenario: Region-to-prefecture selection in onboarding

- **WHEN** the user taps a region button in Step 1
- **THEN** the system SHALL transition to Step 2 showing prefectures within the selected region
- **AND** Step 2 SHALL include a back button to return to Step 1
- **WHEN** the user taps a prefecture in Step 2
- **THEN** the system SHALL confirm the selection with the prefecture's ISO 3166-2 code

#### Scenario: Magic moment after home area selection

- **WHEN** the user selects their home area (via quick-select or region-to-prefecture)
- **THEN** the system SHALL store the selected code in localStorage under `guest.home`
- **AND** the system SHALL immediately close the BottomSheet
- **AND** the system SHALL unblur the Dashboard background with a smooth transition animation
- **AND** the system SHALL reload concert data from the backend so lane classification reflects the selected home area
- **AND** the system SHALL dynamically populate the Live Highway UI with the reloaded, home-area-classified events
