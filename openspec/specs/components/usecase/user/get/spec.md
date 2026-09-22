# Get

## Purpose

Define the user's home area capability end to end: the structured `Home` data model (proto, database, Go entity, centroid resolution), the RPCs that create and update it, and the unified `user-home-selector` frontend component and its `userHome.*` i18n namespace used in both onboarding and Settings.

## Requirements

### Requirement: Home included in User retrieval

The `User.home` field SHALL be populated in all RPCs that return a `User` entity. `UserService.Get` requests SHALL carry an explicit `user_id` that the backend verifies against the JWT-derived userID; mismatches SHALL be rejected with `PERMISSION_DENIED`.

#### Scenario: Get returns home

- **WHEN** `UserService.Get` is called for a user who has set their home area
- **AND** the supplied `user_id` equals the userID derived from the JWT
- **THEN** the returned `User.home` field SHALL contain the full structured home (country_code, level_1, and level_2 if set)

#### Scenario: Get returns nil home

- **WHEN** `UserService.Get` is called for a user who has not set their home area
- **AND** the supplied `user_id` equals the userID derived from the JWT
- **THEN** the returned `User.home` field SHALL be absent (not set)

#### Scenario: Get rejects mismatched user_id

- **WHEN** `UserService.Get` is called with a `user_id` that differs from the userID derived from the JWT
- **THEN** the system SHALL return `PERMISSION_DENIED`
- **AND** the response SHALL NOT carry any user data
