# Reject

## Purpose

Concerts discovered by the search pipeline are staged for human review before
they become fan-visible. Discovery resolves the venue and writes a `pending`
staged concert instead of publishing directly; a developer approves (publishing
the concert and notifying followers) or rejects (dropping it and appending to an
analysis-only log). This gates AI-sourced data quality while keeping rejection
non-permanent and re-discovery idempotent.

## Requirements

### Requirement: Rejection drops the concert and is non-permanent

The system SHALL provide a reject operation that removes a `pending` staged concert and records
the rejection in an append-only log. Rejection SHALL NOT permanently suppress the concert: a
later discovery run that produces the same natural key SHALL re-stage it as `pending` for
re-review.

#### Scenario: Reject drops and logs

- **WHEN** a developer rejects a `pending` staged concert with a reason
- **THEN** the system SHALL delete the staged row
- **AND** SHALL append a `rejected_concerts_log` entry capturing the raw scraped payload, the
  resolved-venue preview, the reason, the reviewer identity, and the timestamp

#### Scenario: Rejected concert can re-enter the queue

- **WHEN** a concert was previously rejected
- **AND** a later discovery run produces the same natural key
- **AND** that natural key is not present in `events` or as a `pending` staged row
- **THEN** the system SHALL re-stage it as `pending`

#### Scenario: Reject is idempotent

- **WHEN** a reject operation targets a staged concert that no longer exists
- **THEN** the operation SHALL succeed without error
