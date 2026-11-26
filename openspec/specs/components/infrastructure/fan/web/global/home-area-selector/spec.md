# Home Area Selector

## Purpose

Provides the shared control that lets a user select and see their home area preference, used consistently in both onboarding and settings.

## Requirements

### Requirement: My Home Area Preference
The system SHALL allow users to change their home area preference (prefecture) which determines the Timetable's geographical context.

#### Scenario: Opening home area selector
- **WHEN** a user taps the "My Home Area" row in Settings
- **THEN** the system SHALL display the `home-area-selector` component in a bottom sheet (the `bottom-sheet` component, a native `<dialog popover="manual">`)
- **AND** the sheet SHALL be promoted to the browser's Top Layer, rendering above all page content including the bottom navigation bar
- **AND** the sheet SHALL NOT use z-index utilities for stacking
- **AND** Step 1 SHALL show quick-select major city buttons (Tokyo, Osaka, Nagoya, Fukuoka, Sapporo, Sendai) and region buttons (Hokkaido, Tohoku, Kanto, Chubu, Kinki, Chugoku, Shikoku, Kyushu)
- **AND** WHEN a user taps a region, Step 2 SHALL show prefectures within the selected region

#### Scenario: Dialog backdrop and dismiss
- **WHEN** the home area selector sheet is open from Settings, as the Concerts view's area selector, or as the home sheet of a guest who has finished onboarding
- **THEN** the `::backdrop` pseudo-element SHALL display a dark translucent overlay with blur effect
- **AND** tapping the dimmed area SHALL close the sheet
- **AND** pressing the ESC key SHALL close the sheet

#### Scenario: Dialog open/close animation
- **WHEN** the home area selector sheet opens
- **THEN** the sheet SHALL slide up from the bottom of the viewport as every bottom sheet does (see the bottom-sheet requirement "The sheet rises from the bottom edge on entry")
- **AND** WHEN the sheet closes
- **THEN** it SHALL close by the dismiss scroll that every bottom sheet closes by
- **AND** users with `prefers-reduced-motion: reduce` SHALL see the sheet fade in over at most 100 ms without sliding, and the sheet close without sliding

#### Scenario: Changing home area
- **WHEN** a user selects a prefecture in Step 2 or a quick-select city in Step 1
- **THEN** the system SHALL update the user's home area preference
- **AND** the sheet SHALL close
- **AND** the Settings row SHALL reflect the new home area
- **AND** the Timetable SHALL use the new home area for Timetable Grid lane calculations on next load

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

### Requirement: Home area i18n namespace

The frontend SHALL use a unified `homeAreaSelector.*` i18n namespace for all home area selection UI text, replacing the previous `region.*` and `areaSelector.*` namespaces.

#### Scenario: i18n key structure

- **WHEN** the `home-area-selector` component renders translated text
- **THEN** it SHALL use keys under the `homeAreaSelector` namespace:
  - `homeAreaSelector.title` for the dialog title
  - `homeAreaSelector.description` for the subtitle
  - `homeAreaSelector.quickSelect` for the quick-select section heading
  - `homeAreaSelector.selectByRegion` for the region section heading
  - `homeAreaSelector.selectPrefecture` for the Step 2 instruction line
  - `homeAreaSelector.backToRegions` for the Step 2 back control's visible text label (this label is the sole source of the control's accessible name; no separate `homeAreaSelector.back` aria-label key SHALL be introduced)
  - `homeAreaSelector.regions.*` for region names
  - `homeAreaSelector.prefectures.*` for prefecture names
  - `homeAreaSelector.cities.*` for quick-select city names

#### Scenario: Description copy explains what the HOME lane displays and asks for residence

- **WHEN** the `home-area-selector` is opened
- **THEN** the title SHALL read `HOMEエリアを選択`
- **AND** the `homeAreaSelector.description` JA value SHALL ask which area the person lives in and say that its concerts go in the HOME lane, in the app's friend voice
- **AND** the canonical JA form SHALL be: `住んでるエリアを教えてね！近くのライブを HOME に並べるよ`

#### Scenario: One name for the home area

- **WHEN** any fan screen names the home area (the selector's title, Settings, help, the hype snack, a save failure)
- **THEN** it SHALL call it `HOMEエリア` in Japanese, and never `ホームエリア` or `居住エリア`

### Requirement: A person without a home is asked on the Timetable and My Artists

When the Timetable or My Artists opens and the person has no home area (a guest who has not chosen one, or a signed-in fan whose account has none), the screen SHALL open the `home-area-selector` as a sheet. For a signed-in fan, and for a guest in onboarding, the sheet SHALL NOT close by tapping the backdrop, pressing ESC or swiping down; it SHALL close only when an area is selected. A guest who has finished onboarding MAY close it, and it SHALL open again the next time either screen opens. The selected area SHALL become the person's home: on the device for a guest, through `UserService.SetHome` for a signed-in fan. No other screen SHALL open the sheet because the home is missing. Discovery's Concerts view, which only signed-in fans see, opens the selector as its area selector when the fan has no home area and the device keeps no override (Discovery's "Signed-in fan without a home area"); there the choice is kept as the view's area override, not as a home.

#### Scenario: New account without a home opens the Timetable

- **WHEN** a fan whose account was created without a home opens the Timetable
- **THEN** the home sheet opens, and tapping the backdrop or pressing ESC leaves it open
- **AND** selecting 東京都 closes it and saves home JP-13 to the account

#### Scenario: Signed-in fan without a home opens My Artists

- **WHEN** a signed-in fan whose account has no home opens My Artists
- **THEN** the home sheet opens and cannot be closed until an area is selected

#### Scenario: Sheet left without a choice

- **WHEN** a signed-in fan closes the app while the home sheet is open, and later opens the Timetable
- **THEN** the home sheet opens again

#### Scenario: Guest after onboarding closes the sheet

- **WHEN** a guest who finished onboarding without a home opens My Artists and closes the sheet
- **THEN** My Artists stays open without a home, and the sheet opens again the next time the guest opens the Timetable or My Artists

#### Scenario: Concert page does not ask

- **WHEN** a signed-in fan without a home opens a Concert page
- **THEN** no home sheet opens

### Requirement: One home area selector serves every caller

The frontend SHALL provide a single reusable `home-area-selector` component for selecting the user's home area. This component SHALL be used as the home sheet of the Timetable and My Artists ("A person without a home is asked on the Timetable and My Artists"), on the Settings page, and as the Concerts view's area selector. The component SHALL implement a consistent 2-step selection flow with an optional quick-select shortcut.

The component SHALL be a pure selection UI: it SHALL NOT call `UserService.setHome()`, write to localStorage, or resolve the user store / the auth service internally. All persistence decisions are delegated to the caller via the `onHomeSelected` callback.

#### Scenario: Step 1 displays quick-select cities and regions

- **WHEN** the `home-area-selector` component is opened
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

- **WHEN** the `home-area-selector` is used for a signed-in fan on the Settings page or as the home sheet of the Timetable or My Artists
- **THEN** the caller (the Settings page, the Timetable or My Artists) SHALL call `UserService.setHome()` in its `onHomeSelected` handler
- **AND** the component itself SHALL NOT call any backend RPC

#### Scenario: Caller owns persistence — guest home save

- **WHEN** the `home-area-selector` is used for a guest user on the Settings page or as the home sheet of the Timetable or My Artists
- **THEN** the caller SHALL write the ISO 3166-2 code to localStorage under `guest.home`
- **AND** the component itself SHALL NOT write to localStorage

#### Scenario: Caller owns persistence — Concerts view's area override

- **WHEN** the `home-area-selector` is used as the Concerts view's area selector
- **THEN** the caller SHALL keep the selected code on the device as the Concerts view's area override, as Discovery's "The Concerts view's area is chosen in the filter sheet and kept on the device" states
- **AND** `UserService.setHome()` SHALL NOT be called and the guest home SHALL NOT be written

#### Scenario: Current selection highlight via bindable prop

- **WHEN** the `home-area-selector` component is opened
- **THEN** it SHALL accept a `@bindable currentCode: string | null` prop representing the currently active ISO 3166-2 code
- **AND** the component SHALL use `currentCode` to highlight the matching prefecture or city button
- **AND** `currentCode` SHALL replace the former store-derived `currentHomeCode` getter; the component SHALL NOT derive the current code from internal state
- **WHEN** the caller does not provide `currentCode`
- **THEN** no prefecture SHALL be highlighted
