# User Home Selector

## Purpose

Provides the shared control that lets a user select and see their home area preference, used consistently in both onboarding and settings.

## Requirements

### Requirement: My Home Area Preference
The system SHALL allow users to change their home area preference (prefecture) which determines the Live Highway Dashboard's geographical context.

#### Scenario: Opening home area selector
- **WHEN** a user taps the "My Home Area" row in Settings
- **THEN** the system SHALL display the `user-home-selector` component as a native `<dialog>` element via `showModal()`
- **AND** the dialog SHALL be promoted to the browser's Top Layer, rendering above all page content including the bottom navigation bar
- **AND** the dialog SHALL NOT use z-index utilities for stacking
- **AND** Step 1 SHALL show quick-select major city buttons (Tokyo, Osaka, Nagoya, Fukuoka, Sapporo, Sendai) and region buttons (Hokkaido, Tohoku, Kanto, Chubu, Kinki, Chugoku, Shikoku, Kyushu)
- **AND** WHEN a user taps a region, Step 2 SHALL show prefectures within the selected region

#### Scenario: Dialog backdrop and dismiss
- **WHEN** the home area selector dialog is open from Settings, as the All Nearby area selector, or as the home sheet of a guest who has finished onboarding
- **THEN** the `::backdrop` pseudo-element SHALL display a dark translucent overlay with blur effect
- **AND** tapping the backdrop area SHALL close the dialog
- **AND** pressing the ESC key SHALL close the dialog

#### Scenario: Dialog open/close animation
- **WHEN** the home area selector dialog opens
- **THEN** the dialog panel SHALL slide up from the bottom of the viewport with a fade-in (300ms ease-out)
- **AND** WHEN the dialog closes
- **THEN** the panel SHALL slide down with a fade-out (300ms ease-out)
- **AND** users with `prefers-reduced-motion: reduce` SHALL see instant open/close without animation

#### Scenario: Changing home area
- **WHEN** a user selects a prefecture in Step 2 or a quick-select city in Step 1
- **THEN** the system SHALL update the user's home area preference
- **AND** the dialog SHALL close
- **AND** the Settings row SHALL reflect the new home area
- **AND** the Dashboard SHALL use the new home area for Live Highway lane calculations on next load

#### Scenario: My Home Area displays from backend User entity
- **WHEN** the Settings page loads for an authenticated user
- **THEN** the My Home Area row SHALL display the home area from `UserService.current.home`
- **AND** SHALL NOT read from localStorage for home area display
- **AND** if `UserService.current.home` is absent, the row SHALL display the localized "Not set" text

---

### Requirement: Home Area Selected-State Indicator
The home-area selector SHALL indicate the currently selected prefecture/city reactively, consistent with the language selector's selected-state treatment.

#### Scenario: Current home area is highlighted
- **WHEN** the home-area selector is open and the user has a current home area
- **THEN** the option matching the user's current home area SHALL carry a selected-state indicator (`aria-checked`/`data-selected`)
- **AND** the indicator SHALL update reactively if the current home area changes

### Requirement: Unified home area selector

The frontend SHALL provide a single reusable `user-home-selector` component for selecting the user's home area. This component SHALL be used as the home sheet of the Dashboard and My Artists ("A person without a home is asked on the Dashboard and My Artists"), on the Settings page, and as the All Nearby area selector. The component SHALL implement a consistent 2-step selection flow with an optional quick-select shortcut.

The component SHALL be a pure selection UI: it SHALL NOT call `UserService.setHome()`, write to localStorage, or resolve the user store / the auth service internally. All persistence decisions are delegated to the caller via the `onHomeSelected` callback.

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
- **AND** the back control SHALL NOT carry a separately bound `aria-label`; the visible text label supplies the accessible name directly, and a diverging `aria-label` would violate WCAG 2.5.3 (Label in Name). Use visible text as the sole accessible name to eliminate that risk.

#### Scenario: Prefecture selection in Step 2 confirms

- **WHEN** a user taps a prefecture in Step 2
- **THEN** the component SHALL confirm the selection with the prefecture's ISO 3166-2 code
- **AND** the component SHALL invoke the `onHomeSelected` callback with the code

#### Scenario: Caller owns persistence — authenticated home save

- **WHEN** the `user-home-selector` is used for a signed-in fan on the Settings page or as the home sheet of the Dashboard or My Artists
- **THEN** the caller (the Settings page, the Dashboard or My Artists) SHALL call `UserService.setHome()` in its `onHomeSelected` handler
- **AND** the component itself SHALL NOT call any backend RPC

#### Scenario: Caller owns persistence — guest home save

- **WHEN** the `user-home-selector` is used for a guest user on the Settings page or as the home sheet of the Dashboard or My Artists
- **THEN** the caller SHALL write the ISO 3166-2 code to localStorage under `guest.home`
- **AND** the component itself SHALL NOT write to localStorage

#### Scenario: Caller owns persistence — session-only override

- **WHEN** the `user-home-selector` is used as the All Nearby area selector
- **THEN** the caller SHALL update only the route's local state with the selected code
- **AND** neither `UserService.setHome()` nor localStorage SHALL be written

#### Scenario: Current selection highlight via bindable prop

- **WHEN** the `user-home-selector` component is opened
- **THEN** it SHALL accept a `@bindable currentCode: string | null` prop representing the currently active ISO 3166-2 code
- **AND** the component SHALL use `currentCode` to highlight the matching prefecture or city button
- **AND** `currentCode` SHALL replace the former store-derived `currentHomeCode` getter; the component SHALL NOT derive the current code from internal state
- **WHEN** the caller does not provide `currentCode`
- **THEN** no prefecture SHALL be highlighted

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

### Requirement: A person without a home is asked on the Dashboard and My Artists

When the Dashboard or My Artists opens and the person has no home area (a guest who has not chosen one, or a signed-in fan whose account has none), the screen SHALL open the `user-home-selector` as a sheet. For a signed-in fan, and for a guest in onboarding, the sheet SHALL NOT close by tapping the backdrop, pressing ESC or swiping down; it SHALL close only when an area is selected. A guest who has finished onboarding MAY close it, and it SHALL open again the next time either screen opens. The selected area SHALL become the person's home: on the device for a guest, through `UserService.SetHome` for a signed-in fan. No other screen SHALL open the sheet because the home is missing.

#### Scenario: New account without a home opens the Dashboard

- **WHEN** a fan whose account was created without a home opens the Dashboard
- **THEN** the home sheet opens, and tapping the backdrop or pressing ESC leaves it open
- **AND** selecting 東京都 closes it and saves home JP-13 to the account

#### Scenario: Signed-in fan without a home opens My Artists

- **WHEN** a signed-in fan whose account has no home opens My Artists
- **THEN** the home sheet opens and cannot be closed until an area is selected

#### Scenario: Sheet left without a choice

- **WHEN** a signed-in fan closes the app while the home sheet is open, and later opens the Dashboard
- **THEN** the home sheet opens again

#### Scenario: Guest after onboarding closes the sheet

- **WHEN** a guest who finished onboarding without a home opens My Artists and closes the sheet
- **THEN** My Artists stays open without a home, and the sheet opens again the next time the guest opens the Dashboard or My Artists

#### Scenario: Event page does not ask

- **WHEN** a signed-in fan without a home opens an Event page
- **THEN** no home sheet opens
