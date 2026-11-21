# Delta for home-area-selector

## MODIFIED Requirements

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
