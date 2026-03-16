## MODIFIED Requirements

### Requirement: Guest Data Storage

The system SHALL store guest session data via Store dispatch during the onboarding tutorial. The Store's persistence middleware SHALL handle localStorage serialization.

#### Scenario: Followed artists stored via Store

- **WHEN** a guest user taps an artist bubble during Step 1 (Artist Discovery)
- **THEN** the system SHALL dispatch `{ type: 'guest/follow', artistId, name }` to the Store
- **AND** the persistence middleware SHALL write the updated follows to localStorage under `liverty:guest:followedArtists`

#### Scenario: Home area stored via Store

- **WHEN** a guest user selects a home area during Step 3 (Dashboard)
- **THEN** the system SHALL dispatch `{ type: 'guest/setUserHome', code }` to the Store
- **AND** the persistence middleware SHALL write the code to localStorage under `liverty:guest:home`

### Requirement: Data Merge on Authentication

The system SHALL sync all Store-managed guest data to the backend via existing RPCs immediately after successful Passkey authentication at Step 6.

#### Scenario: Successful data merge

- **WHEN** Passkey authentication completes successfully
- **THEN** the system SHALL read guest data from `store.getState().guestArtists`
- **AND** the system SHALL call `UserService.Create` with the user's email and `guestArtists.home` as the home field
- **AND** the system SHALL call `ArtistService.Follow` for each artist in `guestArtists.follows`
- **AND** upon successful completion, the system SHALL dispatch `{ type: 'guest/clearAll' }` to clear Store state and localStorage

#### Scenario: User already exists during merge

- **WHEN** `UserService.Create` returns `ALREADY_EXISTS`
- **THEN** the system SHALL treat this as success and continue with artist follow calls

#### Scenario: Follow call fails during merge

- **WHEN** any `ArtistService.Follow` call fails during the merge
- **THEN** the system SHALL log the error
- **AND** the system SHALL continue with remaining follow calls (best-effort)
- **AND** the system SHALL still dispatch `{ type: 'onboarding/complete' }`

#### Scenario: Merge progress indication

- **WHEN** the data merge is in progress
- **THEN** the system SHALL display a loading indicator on the SignUp modal
- **AND** the system SHALL NOT navigate away until the merge completes or all retries are exhausted

### Requirement: Guest Data Cleanup

The system SHALL remove all guest data from the Store and localStorage after a successful merge or when the user starts a fresh tutorial.

#### Scenario: Cleanup after successful merge

- **WHEN** the data merge completes (regardless of partial failures)
- **THEN** the system SHALL dispatch `{ type: 'guest/clearAll' }` to the Store
- **AND** the persistence middleware SHALL remove guest keys from localStorage

#### Scenario: Cleanup on fresh tutorial start

- **WHEN** a user taps [Get Started] on the LP to begin the tutorial
- **AND** stale guest data exists in the Store or localStorage
- **THEN** the system SHALL dispatch `{ type: 'guest/clearAll' }` before starting Step 1
- **AND** the system SHALL dispatch `{ type: 'onboarding/reset' }` to reset the onboarding state
