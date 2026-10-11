# Spec Delta

## Purpose

Records the hold opened for a Draft LotteryEntry; it changes no other attribute.

## ADDED Requirements

### Requirement: Record the hold on a draft

SetAuthorization SHALL set the entry's authorization to the given hold reference. It SHALL fail with FailedPrecondition when the entry is not a Draft, and with NotFound when no entry has the id.

#### Scenario: Hold recorded
- **WHEN** SetAuthorization records a hold on a Draft
- **THEN** the Draft carries the hold's reference and its other attributes are unchanged

#### Scenario: Not a draft
- **WHEN** the entry is Entered
- **THEN** SetAuthorization fails with FailedPrecondition and nothing changes

#### Scenario: Unknown id
- **WHEN** no entry has the id
- **THEN** SetAuthorization fails with NotFound
