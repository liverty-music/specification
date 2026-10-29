# Spec Delta

## Purpose

Sends the email telling a fan that their ResaleEntry lapsed or lost, at most once per entry.

## ADDED Requirements

### Requirement: One email per ended entry

SendEndedEmail SHALL take a Lapsed or Lost ResaleEntry and a message, send the message to the fan's email address and set the entry's ended email send time, unless that time is already set, in which case it SHALL send nothing. It SHALL fail with FailedPrecondition for an Entered or Won entry and with NotFound for an unknown entry.

#### Scenario: First send
- **WHEN** a Lapsed entry has no ended email send time
- **THEN** the email is sent and the time is set

#### Scenario: Sent already
- **WHEN** the entry's ended email send time is set
- **THEN** no email is sent

#### Scenario: Entry still in the draw
- **WHEN** the entry is Entered
- **THEN** SendEndedEmail fails with FailedPrecondition
