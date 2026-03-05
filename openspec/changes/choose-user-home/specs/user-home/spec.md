## ADDED Requirements

### Requirement: Unified Home Area Selector Component

The frontend SHALL provide a single reusable `user-home-selector` component for selecting the user's home area. This component SHALL be used in both the onboarding flow (Dashboard BottomSheet) and the Settings page. The component SHALL implement a consistent 2-step selection flow with an optional quick-select shortcut.

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

#### Scenario: Persistence for authenticated users

- **WHEN** an authenticated user selects a home area
- **THEN** the component SHALL call `UserService.updateHome()` with the structured Home object
- **AND** the component SHALL NOT write to localStorage

#### Scenario: Persistence for guest users

- **WHEN** a guest user selects a home area
- **THEN** the component SHALL store the ISO 3166-2 code in localStorage under `guest.home`
- **AND** the component SHALL NOT call any backend RPC

### Requirement: Home area i18n namespace

The frontend SHALL use a unified `userHome.*` i18n namespace for all home area selection UI text, replacing the previous `region.*` and `areaSelector.*` namespaces.

#### Scenario: i18n key structure

- **WHEN** the `user-home-selector` component renders translated text
- **THEN** it SHALL use keys under the `userHome` namespace:
  - `userHome.title` for the dialog title
  - `userHome.description` for the subtitle
  - `userHome.quickSelect` for the quick-select section heading
  - `userHome.selectByRegion` for the region section heading
  - `userHome.back` for the Step 2 back button
  - `userHome.regions.*` for region names
  - `userHome.prefectures.*` for prefecture names
  - `userHome.cities.*` for quick-select city names

## MODIFIED Requirements

### Requirement: Frontend home area persistence via RPC

The frontend SHALL store the user's home area server-side via RPC, replacing localStorage-based persistence for authenticated users.

#### Scenario: Onboarding home area selection persisted at account creation

- **WHEN** a guest user has selected their home area during onboarding
- **AND** the user subsequently creates an account
- **THEN** the frontend SHALL include the selected home in the `UserService.Create` request
- **AND** SHALL NOT make a separate `UpdateHome` call for the initial home

#### Scenario: Settings home area change triggers UpdateHome RPC

- **WHEN** an authenticated user changes their home area via the `user-home-selector`
- **THEN** the frontend SHALL call `UserService.UpdateHome` with the new structured home
- **AND** SHALL NOT write to localStorage for the home area

#### Scenario: Dashboard reads home from User entity

- **WHEN** the dashboard loads for an authenticated user
- **THEN** the lane assignment logic SHALL read the user's home area from the `User` entity obtained via `UserService.Get`
- **AND** SHALL NOT read from localStorage

#### Scenario: Guest fallback to localStorage

- **WHEN** a guest (unauthenticated) user selects their home area
- **THEN** the frontend SHALL store the selection in localStorage under `guest.home`
- **AND** the dashboard SHALL read from localStorage for lane assignment
