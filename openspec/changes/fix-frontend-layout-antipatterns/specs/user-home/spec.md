## MODIFIED Requirements

### Requirement: Unified Home Area Selector Component
The frontend SHALL provide a single reusable `user-home-selector` component for selecting the user's home area. This component SHALL be used in both the onboarding flow (Dashboard BottomSheet) and the Settings page. The component SHALL support a `required` mode that prevents dismissal without completing a selection.

#### Scenario: Step 1 displays quick-select cities and regions
- **WHEN** the `user-home-selector` component is opened
- **THEN** Step 1 SHALL display quick-select buttons for major cities (Tokyo, Osaka, Nagoya, Fukuoka, Sapporo, Sendai)
- **AND** Step 1 SHALL display region buttons (Hokkaido, Tohoku, Kanto, Chubu, Kinki, Chugoku, Shikoku, Kyushu)

#### Scenario: Quick-select city confirms immediately
- **WHEN** a user taps a quick-select city button
- **THEN** the component SHALL confirm the selection with the city's ISO 3166-2 prefecture code
- **AND** the component SHALL NOT transition to Step 2
- **AND** the component SHALL invoke the `onHomeSelected` callback with the code

#### Scenario: Region tap transitions to Step 2
- **WHEN** a user taps a region button
- **THEN** the component SHALL transition to Step 2 displaying the prefectures within that region
- **AND** Step 2 SHALL display a back button to return to Step 1

#### Scenario: Prefecture selection in Step 2 confirms
- **WHEN** a user taps a prefecture in Step 2
- **THEN** the component SHALL confirm the selection with the prefecture's ISO 3166-2 code
- **AND** the component SHALL invoke the `onHomeSelected` callback with the code

#### Scenario: Backdrop click closes selector in optional mode
- **WHEN** the `required` bindable is `false` (default)
- **AND** the user taps the backdrop area outside the selector
- **THEN** the component SHALL close the dialog

#### Scenario: Backdrop click blocked in required mode
- **WHEN** the `required` bindable is `true`
- **AND** the user taps the backdrop area outside the selector
- **THEN** the component SHALL NOT close the dialog
- **AND** the selector SHALL remain open

#### Scenario: ESC key closes selector in optional mode
- **WHEN** the `required` bindable is `false` (default)
- **AND** the user presses the Escape key
- **THEN** the component SHALL close the dialog

#### Scenario: ESC key blocked in required mode
- **WHEN** the `required` bindable is `true`
- **AND** the user presses the Escape key
- **THEN** the component SHALL prevent the default cancel event
- **AND** the component SHALL NOT close the dialog

#### Scenario: Persistence for authenticated users
- **WHEN** an authenticated user selects a home area
- **THEN** the component SHALL call `UserService.updateHome()` with the structured Home object
- **AND** the component SHALL NOT write to localStorage

#### Scenario: Persistence for guest users
- **WHEN** a guest user selects a home area
- **THEN** the component SHALL store the ISO 3166-2 code in localStorage under `guest.home`
- **AND** the component SHALL NOT call any backend RPC
