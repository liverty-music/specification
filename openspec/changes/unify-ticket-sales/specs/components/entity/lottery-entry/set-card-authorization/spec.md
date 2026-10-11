# Spec Delta

## Purpose

Records the card authorization opened for a Draft LotteryEntry; it changes no other attribute.

## ADDED Requirements

### Requirement: Record the card authorization on a draft

SetCardAuthorization SHALL set the entry's card authorization to the given CardAuthorization. When the entry already has the same card authorization, it SHALL change nothing and succeed. It SHALL fail with FailedPrecondition when the entry is not a Draft or already has another card authorization, and with NotFound when no entry has the id.

#### Scenario: Card authorization recorded
- **WHEN** SetCardAuthorization records a card authorization on a Draft
- **THEN** the Draft carries the card authorization and its other attributes are unchanged

#### Scenario: Same card authorization on retry
- **WHEN** the same card authorization is set again on the Draft
- **THEN** SetCardAuthorization succeeds and nothing changes

#### Scenario: Not a draft
- **WHEN** the entry is Entered
- **THEN** SetCardAuthorization fails with FailedPrecondition and nothing changes

#### Scenario: Unknown id
- **WHEN** no entry has the id
- **THEN** SetCardAuthorization fails with NotFound
