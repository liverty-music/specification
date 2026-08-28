## MODIFIED Requirements

### Requirement: Scheduled Concert Discovery Job

The system SHALL run a scheduled batch job that discovers new concerts for all followed artists by invoking the existing `SearchNewConcerts` use case for each artist, **except artists associated with an active organizer**. An artist associated with an active organizer SHALL be excluded from the discovery run — filtered out of the artist list **before** `SearchNewConcerts` is called (so the Gemini/search call is skipped entirely, not merely dropped downstream). Disassociating the artist (or deactivating the organizer) SHALL return it to the discovery run.

#### Scenario: Daily execution in production

- **WHEN** the CronJob triggers at 18:00 JST (09:00 UTC) daily
- **THEN** the job SHALL retrieve all distinct followed artists via `ListAllFollowed`
- **AND** call `SearchNewConcerts` for each artist not associated with an active organizer, sequentially

#### Scenario: Weekly execution in dev

- **WHEN** the CronJob is deployed in the dev environment
- **THEN** it SHALL run only on Fridays at 18:00 JST (09:00 UTC)

#### Scenario: Organizer-represented artist is skipped before search

- **WHEN** the discovery job builds its artist list and an artist is associated with an active organizer
- **THEN** the job SHALL NOT call `SearchNewConcerts` for that artist (the search/Gemini call is skipped)
- **AND** when that artist is later disassociated (or its organizer deactivated), the job SHALL call `SearchNewConcerts` for it again
