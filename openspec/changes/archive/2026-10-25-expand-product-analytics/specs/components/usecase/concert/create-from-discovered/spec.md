## ADDED Requirements

### Requirement: Each batch reports what it did

At the end of a batch, whether it completed or failed, CreateFromDiscovered SHALL send one "concert ingest completed" signal for product analytics, under the trace of the discovery it handles, carrying the Artist, whether the batch completed or failed, and the numbers of events it published, staged for review, filled in on an existing Event, found suppressed and kept as conflicts. A failed batch reports what it had done before failing; each redelivery of a failed batch is a batch of its own. A failure to send it SHALL NOT change the batch.

#### Scenario: Mixed batch
- **WHEN** a batch publishes 3 events and stages 1 for review
- **THEN** one signal is sent with 3 published and 1 staged, in the same trace as the search that found them

#### Scenario: Batch fails part way
- **WHEN** a batch publishes 2 events and then fails on the next series
- **THEN** one signal is sent stating the batch failed, with 2 published, and the batch still fails
