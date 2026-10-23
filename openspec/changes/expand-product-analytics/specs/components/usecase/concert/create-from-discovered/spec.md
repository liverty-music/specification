## ADDED Requirements

### Requirement: Each batch reports what it did

At the end of a batch, CreateFromDiscovered SHALL send one "concert ingest completed" signal for product analytics, under the trace of the discovery it handles, carrying the Artist and the numbers of events it published, staged for review, filled in on an existing Event, found suppressed and kept as conflicts. A failure to send it SHALL NOT change the batch.

#### Scenario: Mixed batch
- **WHEN** a batch publishes 3 events and stages 1 for review
- **THEN** one signal is sent with 3 published and 1 staged, in the same trace as the search that found them
