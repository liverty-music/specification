<!-- spec: guest-data-merge | target: stories/merge-guest-data-on-signup | flags: CLASSNAME | new_name: Guest Data Storage -->

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

#### Scenario: Home area selection stored locally

- **WHEN** a guest user selects a home area during Step 3 (Dashboard)
- **THEN** the system SHALL store the selected value in LocalStorage under `guest.home`, so the existing per-store cleanup covers it
