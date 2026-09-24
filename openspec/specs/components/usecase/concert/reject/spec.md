# Reject

## Purpose

Reject lets an admin drop a StagedConcert with a reason and record it in the analysis-only RejectedConcertLog. The rejection is not permanent: a later discovery of the same concert is handled like any new discovery.

## Requirements

### Requirement: Reject logs and drops

Reject SHALL record the StagedConcert in the RejectedConcertLog (RejectedConcertLog.Append) with its details as discovered, its resolved preview, the Artist's current name, the reason and the reviewing admin's identity when known, and then remove it (StagedConcert.Delete). When the Artist cannot be read, Reject SHALL fail and change nothing.

#### Scenario: Reject with a reason
- **WHEN** an admin rejects a StagedConcert with reason "wrong artist"
- **THEN** a RejectedConcertLog entry with that reason exists and the StagedConcert is gone

### Requirement: Reject is idempotent

When the StagedConcert does not exist, Reject SHALL succeed and write no log entry.

#### Scenario: Already rejected
- **WHEN** an admin rejects a StagedConcert that is already gone
- **THEN** Reject succeeds and the log is unchanged

### Requirement: Empty series is removed

After removing the StagedConcert, Reject SHALL remove its Series when that Series has no Event and no other StagedConcert (Series.DeleteOrphaned); a failure here SHALL NOT fail Reject.

#### Scenario: Last staged event of a series
- **WHEN** every event of a discovered series was staged and the last one is rejected
- **THEN** the Series is removed
