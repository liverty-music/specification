# RejectedConcertLog.Append

## Purpose

Adds one entry to the RejectedConcertLog.

## Requirements

### Requirement: Append a new entry

Append SHALL store the entry with the current time as its rejected time and SHALL never change an existing entry.

#### Scenario: Two rejections of the same concert
- **WHEN** the same concert is appended twice
- **THEN** the log holds two entries
