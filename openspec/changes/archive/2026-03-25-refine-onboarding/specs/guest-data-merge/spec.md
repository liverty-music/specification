## ADDED Requirements

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
