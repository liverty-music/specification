## MODIFIED Requirements

### Requirement: Guest Data Storage
The system SHALL store guest session data in LocalStorage under namespaced keys during the onboarding tutorial. Guest follows SHALL be stored as `FollowedArtist[]` including hype level, under a single key.

#### Scenario: Followed artists stored locally with hype
- **WHEN** a guest user taps an artist bubble during Artist Discovery
- **THEN** the system SHALL append `{ artist, hype: DEFAULT_HYPE }` to a JSON array in LocalStorage under `guest.followedArtists`

#### Scenario: Hype update stored inline in follow entry
- **WHEN** a guest user changes a hype level for a followed artist
- **THEN** the system SHALL update the `hype` field of the matching entry in `guest.followedArtists`
- **AND** the system SHALL NOT write to the `liverty:guest:hypes` key

#### Scenario: Legacy data read with hype fallback
- **WHEN** `guest.followedArtists` contains entries in the old `GuestFollow` format (missing `hype` field)
- **THEN** the system SHALL accept those entries and assign `DEFAULT_HYPE` as the hype value
- **AND** the system SHALL NOT throw or discard those entries

### Requirement: Guest hype included in data merge on signup
The system SHALL merge guest hype values to the backend on signup by reading hype from the unified `guest.followedArtists` entries.

#### Scenario: Guest hype merged from follow entries
- **WHEN** Passkey authentication completes successfully
- **AND** `guest.followedArtists` contains entries with `hype !== DEFAULT_HYPE`
- **THEN** the system SHALL call `FollowService.SetHype` for each such artist as part of the merge sequence
- **AND** hype merge SHALL occur after artist follow calls complete

#### Scenario: Hype merge failure is non-blocking
- **WHEN** a `FollowService.SetHype` call fails during merge
- **THEN** the system SHALL log the error
- **AND** the system SHALL continue with remaining hype calls (best-effort)
- **AND** the merge SHALL still be considered complete

#### Scenario: Guest data cleared after merge
- **WHEN** the data merge completes
- **THEN** the system SHALL remove `guest.followedArtists` from localStorage as part of the standard guest data cleanup
- **AND** the system SHALL NOT need to remove `liverty:guest:hypes` (key is no longer written)

## REMOVED Requirements

### Requirement: Guest Hype Data Storage (REMOVED)
**Reason**: Hype is now stored inline in each `FollowedArtist` entry under `guest.followedArtists`. The separate `liverty:guest:hypes` key is redundant and eliminated.
**Migration**: Remove `saveHypes`, `loadHypes`, `clearHypes` from `guest-storage.ts`. Remove `hypes: Record<string, string>` sidecar field from `GuestService`. Replace `setHype(id, hype)` + `getHypes()` methods with inline mutation of the matching entry in `follows`. Remove `clearHypes()` call from `GuestService.clearAll()`.

### Requirement: Guest hype cleared after merge (superseded)
**Reason**: Replaced by the updated "Guest data cleared after merge" scenario above, which covers hype cleanup via the unified follow entry.
**Migration**: No separate `clearHypes()` call in the merge path; hype data is cleared as part of `guest.followedArtists` cleanup.
