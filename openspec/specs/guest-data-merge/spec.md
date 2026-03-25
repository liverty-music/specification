### Requirement: Guest Data Storage

The system SHALL store guest session data in LocalStorage under namespaced keys during the onboarding tutorial.

#### Scenario: Followed artists stored locally

- **WHEN** a guest user taps an artist bubble during Step 1 (Artist Discovery)
- **THEN** the system SHALL append the artist's ID and name to a JSON array in LocalStorage under `liverty:guest:followedArtists`

#### Scenario: Region selection stored locally

- **WHEN** a guest user selects a region during Step 3 (Dashboard)
- **THEN** the system SHALL store the selected region value in LocalStorage under `liverty:guest:region`

### Requirement: Guest Hype Data Storage

The system SHALL store guest hype level selections in localStorage and merge them to the backend on signup.

#### Scenario: Guest hype stored in localStorage

- **WHEN** a guest user changes a hype level for an artist
- **THEN** the system SHALL store the value in `GuestService` under `liverty:guest:hypes` as a JSON object mapping artistId → hype type string

#### Scenario: Guest hype included in data merge on signup

- **WHEN** Passkey authentication completes successfully
- **AND** `liverty:guest:hypes` contains one or more entries
- **THEN** the system SHALL call `FollowService.SetHype` for each artist in `liverty:guest:hypes` as part of the merge sequence
- **AND** hype merge SHALL occur after artist follow calls complete

#### Scenario: Hype merge failure is non-blocking

- **WHEN** a `FollowService.SetHype` call fails during merge
- **THEN** the system SHALL log the error
- **AND** the system SHALL continue with remaining hype calls (best-effort)
- **AND** the merge SHALL still be considered complete

#### Scenario: Guest hype cleared after merge

- **WHEN** the data merge completes
- **THEN** the system SHALL remove `liverty:guest:hypes` from localStorage as part of the standard guest data cleanup

### Requirement: Data Merge on Authentication

The system SHALL sync all locally stored guest data to the backend via existing RPCs immediately after successful Passkey authentication at Step 6.

#### Scenario: Successful data merge

- **WHEN** Passkey authentication completes successfully
- **THEN** the system SHALL call `UserService.Create` with the user's email
- **AND** the system SHALL call `ArtistService.Follow` for each artist in `liverty:guest:followedArtists`
- **AND** upon successful completion of all calls, the system SHALL clear all `liverty:guest:*` keys from LocalStorage

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
- **THEN** the system SHALL remove `liverty:guest:followedArtists` from LocalStorage
- **AND** the system SHALL remove `liverty:guest:region` from LocalStorage

#### Scenario: Cleanup on fresh tutorial start

- **WHEN** a user taps [Get Started] on the LP to begin the tutorial
- **AND** stale `liverty:guest:*` keys exist in LocalStorage
- **THEN** the system SHALL clear all `liverty:guest:*` keys before starting Step 1
