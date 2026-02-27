## MODIFIED Requirements

### Requirement: Enrichment Job Execution

The venue enrichment pipeline SHALL be triggered by `venue.created.v1` events in addition to the existing batch processing. The CronJob post-step is removed; enrichment is driven by events.

#### Scenario: Enrichment triggered by venue.created.v1 event

- **WHEN** a `venue.created.v1` event is received by the enrich-venue consumer
- **THEN** the consumer SHALL call the enrichment logic for that specific venue
- **AND** follow the existing enrichment pipeline (MusicBrainz → Google Maps fallback)

#### Scenario: Batch enrichment as safety net

- **WHEN** a `venue.created.v1` event fails to be published or consumed
- **THEN** the venue SHALL remain in `pending` status
- **AND** a periodic batch process or manual trigger MAY process it later

#### Scenario: CronJob no longer runs enrichment post-step

- **WHEN** the concert-discovery CronJob completes
- **THEN** it SHALL NOT call `EnrichPendingVenues` directly
