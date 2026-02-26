## ADDED Requirements

### Requirement: Unified key naming convention
All localStorage keys MUST follow the `[<scope>.]<camelCase>` pattern where scope is one of: `user`, `guest`, `pwa`, `ui`, or omitted for app-level keys. No namespace prefix is used since localStorage is scoped to the origin.

#### Scenario: Key format validation
- **WHEN** a localStorage key is defined in the codebase
- **THEN** it MUST match the pattern `[<scope>.]<camelCase>` with dot separators

### Requirement: Centralized key registry
All localStorage key constants MUST be defined in a single `src/constants/storage-keys.ts` module and exported as a `StorageKeys` object.

#### Scenario: New key addition
- **WHEN** a developer needs a new localStorage key
- **THEN** it MUST be added to `StorageKeys` in `storage-keys.ts` and imported from there

#### Scenario: No inline key strings in source
- **WHEN** a service or component accesses localStorage
- **THEN** it MUST use a constant from `StorageKeys`, not a hardcoded string literal

### Requirement: Domain term alignment
Keys storing geographic administrative area data MUST use the term `adminArea` (matching Proto `admin_area` / `Venue.admin_area`), not `region`.

#### Scenario: User admin area storage
- **WHEN** the authenticated user's geographic preference is stored
- **THEN** the key MUST be `user.adminArea`

#### Scenario: Guest admin area storage
- **WHEN** the anonymous user's geographic preference is stored
- **THEN** the key MUST be `guest.adminArea`
