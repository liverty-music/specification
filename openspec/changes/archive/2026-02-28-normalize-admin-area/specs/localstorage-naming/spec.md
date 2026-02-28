## MODIFIED Requirements

### Requirement: Domain term alignment

Keys storing geographic preference data MUST use the term `home` (matching Proto `User.home`), not `adminArea` or `region`.

#### Scenario: Guest home storage

- **WHEN** the anonymous user's geographic preference is stored
- **THEN** the key MUST be `guest.home`

## REMOVED Requirements

### Requirement: Domain term alignment (original adminArea keys)

**Reason**: The `user.adminArea` key is replaced by server-side persistence via `User.home` field and `UserService.UpdateHome` RPC. The `guest.adminArea` key is renamed to `guest.home` to align with the new domain term.

**Migration**: Authenticated user's area is now read from `User.home` via `UserService.Get`. Guest area is stored under `guest.home`. On first load after migration, the legacy `guest.adminArea` and `user.adminArea` keys SHALL be removed. The old `guest.adminArea` value SHALL NOT be copied to `guest.home` because the old values were free-text Japanese strings (e.g. "東京") which are incompatible with the new ISO 3166-2 code format. Users must re-select their home area.
