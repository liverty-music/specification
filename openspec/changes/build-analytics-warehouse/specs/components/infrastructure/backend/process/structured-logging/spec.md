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
