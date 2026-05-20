## MODIFIED Requirements

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
- **AND** Step 2 SHALL display a back control to return to Step 1
- **AND** the back control SHALL render BOTH a chevron-back icon AND a visible text label so the affordance is recognizable as a back action without relying on the icon alone
- **AND** the visible text label SHALL be sourced from a localized i18n key
- **AND** the back control SHALL NOT carry a separately bound `aria-label`; per WCAG 2.5.3 (Label in Name) the visible text label IS the accessible name, and supplying a separate `aria-label` risks divergence between the visible and the spoken label

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
  - `userHome.selectPrefecture` for the Step 2 instruction line
  - `userHome.backToRegions` for the Step 2 back control's visible text label (this label is the sole source of the control's accessible name; no separate `userHome.back` aria-label key SHALL be introduced)
  - `userHome.regions.*` for region names
  - `userHome.prefectures.*` for prefecture names
  - `userHome.cities.*` for quick-select city names

#### Scenario: Description copy explains what HOME STAGE displays and asks for residence

- **WHEN** the `user-home-selector` is opened
- **THEN** the `userHome.description` JA value SHALL explain what the selected area controls (the HOME STAGE lane contents) AND ask which area the user resides in, presented as a single string composed of two clearly-separated clauses
- **AND** the copy SHALL NOT use `あなたの地元` (which inaccurately implies a known home rather than a chosen area)
- **AND** the canonical JA form SHALL be: `HOME STAGEには選択したエリアのライブが並びます。あなたの居住エリアはどこですか？`
