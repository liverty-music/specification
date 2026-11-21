# Delta for home-area-selector

## MODIFIED Requirements

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
