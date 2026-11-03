## ADDED Requirements

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

## MODIFIED Requirements

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

- **WHEN** the `user-home-selector` is used on the Settings page or as the home sheet of the Dashboard or My Artists
- **THEN** the caller (Settings page / onboarding handler) SHALL call `UserService.setHome()` in its `onHomeSelected` handler
- **AND** the component itself SHALL NOT call any backend RPC

#### Scenario: Caller owns persistence — guest home save

- **WHEN** the `user-home-selector` is used on the Settings page or onboarding flow for a guest user
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
