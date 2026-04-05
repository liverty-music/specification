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

#### Scenario: Region selection stored locally

- **WHEN** a guest user selects a region during Step 3 (Dashboard)
- **THEN** the system SHALL store the selected region value in LocalStorage under `liverty:guest:region`

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

### Requirement: Data Merge on Authentication

The system SHALL sync all locally stored guest data to the backend via existing RPCs immediately after successful Passkey authentication at Step 6.

#### Scenario: Successful data merge

- **WHEN** Passkey authentication completes successfully
- **THEN** the system SHALL call `UserService.Create` with the user's email
- **AND** the system SHALL call `ArtistService.Follow` for each artist in `guest.followedArtists`
- **AND** upon successful completion of all calls, the system SHALL clear `guest.followedArtists` and `liverty:guest:region` from LocalStorage

#### Scenario: User already exists during merge

- **WHEN** `UserService.Create` returns `ALREADY_EXISTS`
- **THEN** the system SHALL treat this as success and continue with artist follow and passion level calls

#### Scenario: Follow call fails during merge

- **WHEN** any `ArtistService.Follow` call fails during the merge
- **THEN** the system SHALL log the error
- **AND** the system SHALL continue with remaining follow calls (best-effort)
- **AND** the system SHALL still set `onboardingStep` to COMPLETED

#### Scenario: Merge progress indication

- **WHEN** the data merge is in progress
- **THEN** the system SHALL display a loading indicator on the SignUp modal
- **AND** the system SHALL NOT navigate away until the merge completes or all retries are exhausted

### Requirement: Guest Data Cleanup

The system SHALL remove all guest data from LocalStorage after a successful merge or when the user starts a fresh tutorial.

#### Scenario: Cleanup after successful merge

- **WHEN** the data merge completes (regardless of partial failures)
- **THEN** the system SHALL remove `guest.followedArtists` from LocalStorage
- **AND** the system SHALL remove `liverty:guest:region` from LocalStorage

#### Scenario: Cleanup on fresh tutorial start

- **WHEN** a user taps [Get Started] on the LP to begin the tutorial
- **AND** stale guest keys (`guest.followedArtists`, `liverty:guest:region`) exist in LocalStorage
- **THEN** the system SHALL clear those keys before starting Step 1
