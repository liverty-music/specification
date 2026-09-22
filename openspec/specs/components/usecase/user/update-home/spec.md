# Update Home

## Purpose

Lets a user update their home area, resolving the selected area to a geographic centroid and persisting it so it can be used for proximity-based concert classification.

## Requirements

### Requirement: Resolve and store the home area's centroid on write

The system SHALL resolve geographic centroid coordinates for the user's home area at write time (when `UpdateHome` or `Create` is called) and store them on the `homes` table. The centroid lookup is an infrastructure implementation detail — the entity and usecase layers access centroids via `Home.Latitude` and `Home.Longitude` fields.

#### Scenario: Centroid resolved at home write time

- **WHEN** a user sets or updates their home area via `UpdateHome` or `Create`
- **THEN** the repository layer SHALL resolve the `level_1` ISO 3166-2 code to centroid coordinates
- **AND** store the centroid as `centroid_latitude` and `centroid_longitude` on the `homes` table row

#### Scenario: Japanese prefecture centroid resolution

- **WHEN** a home area is set with a Japanese ISO 3166-2 code (e.g., `JP-13`)
- **THEN** the repository SHALL resolve it to the prefecture's approximate geographic centroid

#### Scenario: Unsupported country code centroid

- **WHEN** a home area is set with an unsupported country's ISO 3166-2 code
- **THEN** the centroid columns SHALL be set to NULL
- **AND** `Concert.ProximityTo()` SHALL treat missing centroids as AWAY (no NEARBY classification possible)

#### Scenario: Existing rows backfilled

- **WHEN** the centroid columns migration is applied
- **THEN** all existing `homes` rows with Japanese ISO 3166-2 codes SHALL be backfilled with centroid coordinates

### Requirement: Update Home RPC

The system SHALL provide a dedicated RPC for users to set or change their home area. The request SHALL carry an explicit `user_id` that the backend verifies against the JWT-derived userID; mismatches SHALL be rejected with `PERMISSION_DENIED`.

#### Scenario: Set home area

- **WHEN** an authenticated user calls `UserService.UpdateHome` with a valid structured `Home`
- **AND** the supplied `user_id` equals the userID derived from the JWT
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

#### Scenario: user_id does not match authenticated user

- **WHEN** `UpdateHome` is called with a `user_id` that differs from the userID derived from the JWT
- **THEN** the system SHALL return `PERMISSION_DENIED`
- **AND** the `homes` table SHALL NOT be modified

#### Scenario: Missing user_id

- **WHEN** `UpdateHome` is called without a `user_id` field
- **THEN** the system SHALL return `INVALID_ARGUMENT` via `protovalidate` enforcement
