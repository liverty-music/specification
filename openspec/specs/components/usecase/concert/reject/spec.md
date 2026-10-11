# Reject

## Purpose

Reject lets an admin drop a ConcertCandidate with a reason and record it in the analysis-only RejectedConcert. The rejection is not permanent: a later discovery of the same concert is handled like any new discovery.

## Requirements

### Requirement: Reject logs and drops

Reject SHALL record the ConcertCandidate in the RejectedConcert (RejectedConcert.Append) with its details as discovered, its resolved preview, the Artist's current name, the reason and the reviewing admin's identity when known, and then remove it (ConcertCandidate.Delete). When the Artist cannot be read, Reject SHALL fail and change nothing.

#### Scenario: Reject with a reason
- **WHEN** an admin rejects a ConcertCandidate with reason "wrong artist"
- **THEN** a RejectedConcert entry with that reason exists and the ConcertCandidate is gone

### Requirement: Reject is idempotent

When the ConcertCandidate does not exist, Reject SHALL succeed and write no log entry.

#### Scenario: Already rejected
- **WHEN** an admin rejects a ConcertCandidate that is already gone
- **THEN** Reject succeeds and the log is unchanged

### Requirement: Empty series is removed

After removing the ConcertCandidate, Reject SHALL remove its Series when that Series has no Event and no other ConcertCandidate (Series.DeleteOrphaned); a failure here SHALL NOT fail Reject.

#### Scenario: Last staged event of a series
- **WHEN** every event of a discovered series was staged and the last one is rejected
- **THEN** the Series is removed
