### Requirement: User Home Area Data Model

The system SHALL support a structured `home` field on the User entity representing the user's home area — the geographic area where the user regularly attends live events without considering it a "trip" (遠征). The value is a structured geographic location expressed through a hierarchy of internationally standardized codes, with centroid coordinates for proximity calculations.

#### Scenario: Home message in Proto definition

- **WHEN** the `Home` proto message is defined
- **THEN** it SHALL contain a `string country_code` field validated as ISO 3166-1 alpha-2 (exactly two uppercase Latin letters, e.g., `JP`, `US`)
- **AND** a `string level_1` field validated as ISO 3166-2 format (4–6 characters, e.g., `JP-13`, `US-NY`)
- **AND** an `optional string level_2` field for finer-grained subdivision (1–20 characters when present)
- **AND** an `optional double centroid_latitude` field for the centroid latitude
- **AND** an `optional double centroid_longitude` field for the centroid longitude

#### Scenario: Home field on User message

- **WHEN** the `User` proto message is defined
- **THEN** it SHALL include a `Home home` field as an optional structured message
- **AND** the field SHALL be absent until the user explicitly selects their area

#### Scenario: Home field in database

- **WHEN** the `homes` table is defined
- **THEN** it SHALL include a primary key `id TEXT`
- **AND** a required `country_code TEXT` column storing an ISO 3166-1 alpha-2 code
- **AND** a required `level_1 TEXT` column storing an ISO 3166-2 subdivision code
- **AND** a nullable `level_2 TEXT` column storing a country-specific finer area code
- **AND** a nullable `centroid_latitude DOUBLE PRECISION` column for the centroid latitude
- **AND** a nullable `centroid_longitude DOUBLE PRECISION` column for the centroid longitude

#### Scenario: Home field in Go entity

- **WHEN** the Go `entity.Home` struct is defined
- **THEN** it SHALL include `ID string`, `CountryCode string`, `Level1 string`, `Level2 *string`, `Latitude float64`, and `Longitude float64` fields
- **AND** the `entity.User` struct SHALL include a `Home *Home` field
- **AND** a nil `Home` SHALL mean the user has not set their home area

#### Scenario: Centroid populated at write time

- **WHEN** `UserRepository.Create` or `UserRepository.UpdateHome` is called with a `Home` value
- **THEN** the repository implementation SHALL resolve the `Level1` ISO 3166-2 code to centroid coordinates
- **AND** store the resolved `centroid_latitude` and `centroid_longitude` alongside the other home fields
- **AND** the centroid resolution logic SHALL be an infrastructure implementation detail (not visible to usecase/entity layers)

#### Scenario: Code system contract for level_2

- **WHEN** `level_2` is populated
- **THEN** its code system SHALL be determined by `country_code`:
  - `JP` → future use (not yet defined; Phase 1 always omits level_2)
  - `US` → FIPS county code (e.g., `06037` for Los Angeles County)
  - `DE` → AGS code (e.g., `09162` for Munich)
- **AND** additional country mappings SHALL be documented in the `Home` proto message comment as they are introduced

### Requirement: Create User with Home

The system SHALL accept an optional home area during user creation, allowing the home selected during onboarding to be persisted atomically with the user record.

#### Scenario: Create user with home provided

- **WHEN** an authenticated user calls `UserService.Create` with a valid `home` field
- **THEN** the system SHALL create the user record and the associated home record in a single transaction
- **AND** the response SHALL include the created `User` entity with the `home` field populated

#### Scenario: Create user without home

- **WHEN** an authenticated user calls `UserService.Create` without a `home` field
- **THEN** the system SHALL create the user record with `home_id = NULL`
- **AND** the response SHALL include the created `User` entity with `home` absent

### Requirement: Update Home RPC

The system SHALL provide a dedicated RPC for users to set or change their home area.

#### Scenario: Set home area

- **WHEN** an authenticated user calls `UserService.UpdateHome` with a valid structured `Home`
- **THEN** the system SHALL create or update the home record in the `homes` table
- **AND** associate it with the user's `home_id`
- **AND** the response SHALL include the updated `User` entity

#### Scenario: Invalid code values

- **WHEN** `UpdateHome` is called with a `country_code` that is not a valid ISO 3166-1 alpha-2 code
- **OR** a `level_1` that does not match a known ISO 3166-2 subdivision code
- **THEN** the system SHALL return `INVALID_ARGUMENT`

#### Scenario: Unauthenticated request

- **WHEN** `UpdateHome` is called without valid authentication
- **THEN** the system SHALL return `UNAUTHENTICATED`

### Requirement: Home included in User retrieval

The `User.home` field SHALL be populated in all RPCs that return a `User` entity.

#### Scenario: Get returns home

- **WHEN** `UserService.Get` is called for a user who has set their home area
- **THEN** the returned `User.home` field SHALL contain the full structured home (country_code, level_1, and level_2 if set)

#### Scenario: Get returns nil home

- **WHEN** `UserService.Get` is called for a user who has not set their home area
- **THEN** the returned `User.home` field SHALL be absent (not set)

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
