## ADDED Requirements

### Requirement: Guest Data Storage

The system SHALL store guest session data in LocalStorage under namespaced keys during the onboarding tutorial.

#### Scenario: Followed artists stored locally

- **WHEN** a guest user taps an artist bubble during Step 1 (Artist Discovery)
- **THEN** the system SHALL append the artist's ID and name to a JSON array in LocalStorage under `liverty:guest:followedArtists`

#### Scenario: Region selection stored locally

- **WHEN** a guest user selects a region during Step 3 (Dashboard)
- **THEN** the system SHALL store the selected region value in LocalStorage under `liverty:guest:region`

#### Scenario: Passion level stored locally

- **WHEN** a guest user changes a Passion Level during Step 5 (My Artists)
- **THEN** the system SHALL update the passion level for the corresponding artist in `liverty:guest:followedArtists`

### Requirement: Data Merge on Authentication

The system SHALL sync all locally stored guest data to the backend via existing RPCs immediately after successful Passkey authentication at Step 6.

#### Scenario: Successful data merge

- **WHEN** Passkey authentication completes successfully
- **THEN** the system SHALL call `UserService.Create` with the user's email
- **AND** the system SHALL call `ArtistService.Follow` for each artist in `liverty:guest:followedArtists`
- **AND** the system SHALL call `ArtistService.SetPassionLevel` for each artist with a non-default passion level
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
