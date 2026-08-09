## MODIFIED Requirements

### Requirement: Brand Expression Registry
The system SHALL maintain a single registry table in this spec listing every Layer B brand expression with its canonical JA and EN forms.

#### Scenario: Initial registry contents
- **WHEN** this spec is interpreted at the current revision
- **THEN** the registry SHALL include the following Layer B expressions, each with identical JA and EN surface forms unless otherwise noted:
  - `Product name — full form` — JA: `Liverty Music` / EN: `Liverty Music` (used in the HTML `<title>`, the web app manifest `name` member, and prose)
  - `Product name — home-screen short form` — JA: `LivertyMusic` / EN: `LivertyMusic` (the web app manifest `short_name` member, chosen without a space to minimize home-screen label truncation)
  - `Navigation tab — Timetable` — JA: `Timetable` / EN: `Timetable`
  - `Navigation tab — Discovery` — JA: `Discovery` / EN: `Discovery`
  - `Navigation tab — My Artists` — JA: `My Artists` / EN: `My Artists`
  - `Navigation tab — Tickets` — JA: `Tickets` / EN: `Tickets`
  - `Navigation tab — Settings` — JA: `Settings` / EN: `Settings`
  - `Personal timetable promise` — JA: `あなただけのタイムテーブル` / EN: `your personal timetable`
  - `HOME STAGE lane` — JA: `HOME STAGE` / EN: `HOME STAGE`
  - `NEAR STAGE lane` — JA: `NEAR STAGE` / EN: `NEAR STAGE`
  - `AWAY STAGE lane` — JA: `AWAY STAGE` / EN: `AWAY STAGE`
  - `Hype concept label` — JA: `Hype` / EN: `Hype`
  - `Hype tier — Watch` — JA: `Watch` / EN: `Watch`
  - `Hype tier — Home` — JA: `Home` / EN: `Home`
  - `Hype tier — Nearby` — JA: `Nearby` / EN: `Nearby`
  - `Hype tier — Away` — JA: `Away` / EN: `Away`

#### Scenario: Navigation tab labels are invariant across locales
- **WHEN** a navigation tab label is rendered in any UI surface (bottom navigation bar or a route's page header)
- **THEN** the label SHALL be the invariant English form from the registry, identical in JA and EN locales
- **AND** a route's page header SHALL bind the shared `nav.*` label rather than a separate localized title key

#### Scenario: Adding a new brand expression
- **WHEN** a new coined phrase is introduced into user-facing copy
- **AND** the phrase has no corresponding protobuf entity
- **THEN** a row SHALL be added to this spec's registry table before or alongside the change that introduces the phrase

#### Scenario: Removing a graduated expression
- **WHEN** a Layer B expression becomes entity-modeled and is migrated to Layer A
- **THEN** its row SHALL be removed from this spec's registry table in the same change that performs the migration

#### Scenario: Japanese gloss is prose, not label
- **WHEN** a Japanese-locale help or descriptive sentence introduces a Layer B brand expression that may be unfamiliar to first-time JA readers (e.g. `Hype`)
- **THEN** the sentence MAY include a parenthetical gloss (e.g. `Hype（熱量）`) inline within the prose
- **AND** the gloss SHALL NOT be promoted to the canonical surface label or stored as a separate i18n key

#### Scenario: Registry SHALL NOT include deprecated colloquial terms

- **WHEN** a colloquial JA term (such as `推し`) is identified as deprecated per the Deprecated Colloquial Terms requirement
- **THEN** the term SHALL NOT be listed in the Layer B brand expression registry
- **AND** the term SHALL instead be tracked in the deprecated-terms registry with its canonical entity-grounded replacement
