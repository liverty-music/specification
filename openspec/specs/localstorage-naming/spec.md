## Requirements

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
Keys storing geographic preference data MUST use the term `home` (matching Proto `User.home`), not `adminArea` or `region`. The authenticated user's home is persisted server-side via `User.home` and `UserService.UpdateHome` RPC; no localStorage key is used for authenticated users.

#### Scenario: Guest home storage
- **WHEN** the anonymous user's geographic preference is stored
- **THEN** the key MUST be `guest.home`

#### Scenario: Legacy key migration
- **WHEN** the application initializes after the domain term change
- **THEN** the legacy `guest.adminArea` and `user.adminArea` keys SHALL be removed
- **AND** the old `guest.adminArea` value SHALL NOT be copied to `guest.home` because legacy values were free-text Japanese strings (e.g. "東京") incompatible with the new ISO 3166-2 code format
- **AND** users must re-select their home area
