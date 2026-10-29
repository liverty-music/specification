## ADDED Requirements

### Requirement: Analytics log lines carry the analytics mark

A log line that a backend process writes for analysis beyond operations SHALL carry the analytics mark and exactly one topic from this list: job_result, notification_delivery, catalog_review, catalog_sync, payment. The mark and the topic SHALL be recorded as labels of the log entry, not inside the message, so that one routing rule on the mark selects every such line, whatever its message or topic. A log line that carries a fan's email, name, phone number or address SHALL NOT carry the mark.

#### Scenario: Job summary
- **WHEN** the concert discovery job writes its summary line at the end of a run
- **THEN** the entry is labelled with the analytics mark and the topic job_result

#### Scenario: New topic
- **WHEN** a line with a topic added later to the list is written
- **THEN** it is routed with the other marked lines without a change to the routing rule

#### Scenario: Line with personal data
- **WHEN** a line includes a fan's email address
- **THEN** it does not carry the analytics mark

### Requirement: Job summary lines report how far the run got

The summary line that a scheduled job writes at the end of a run SHALL report the number of items the run processed, the number of those that failed, the number that succeeded, and whether the run stopped early after consecutive failures. The succeeded count SHALL equal processed minus failed: an item the run did not reach, because it stopped early or was interrupted, SHALL NOT count as succeeded.

#### Scenario: Run stops after consecutive failures
- **WHEN** concert discovery has 140 followed artists, and after reaching 20 of them stops because 3 searches in a row failed, 5 failed in total
- **THEN** the summary line reports 20 processed, 5 failed, 15 succeeded, and that the run stopped early

#### Scenario: Run reaches every item
- **WHEN** concert discovery reaches all 140 followed artists and 2 searches fail
- **THEN** the summary line reports 140 processed, 2 failed, 138 succeeded, and that the run did not stop early
