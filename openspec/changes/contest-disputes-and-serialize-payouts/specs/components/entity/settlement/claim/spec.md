# Spec Delta

## Purpose

Starts the release of a Held Settlement by making it Releasing under a release claim, so only the release that holds the claim pays it out and no claw-back records it Reversed while its payout is under way.

## ADDED Requirements

### Requirement: Claimed once, not while disputed

Claim SHALL take a Settlement and a new release claim, and make a Held Settlement Releasing with that release claim when its Order has no open and no unsettled Dispute. It SHALL fail with FailedPrecondition, changing nothing, when the Settlement is not Held, when its Order has an open or unsettled Dispute, or when no Settlement has the id.

#### Scenario: Held settlement claimed
- **WHEN** Claim is called for a Held Settlement whose Order was never disputed
- **THEN** the Settlement is Releasing with the given release claim

#### Scenario: Claimed twice
- **WHEN** Claim is called for a Releasing Settlement
- **THEN** it fails with FailedPrecondition and the Settlement keeps its first release claim

#### Scenario: Payment disputed
- **WHEN** Claim is called for a Held Settlement whose Order has a Contested Dispute
- **THEN** it fails with FailedPrecondition and the Settlement stays Held

#### Scenario: Lost dispute not yet settled
- **WHEN** Claim is called for a Held Settlement whose Order has a Lost Dispute with no settle time
- **THEN** it fails with FailedPrecondition and the Settlement stays Held

#### Scenario: Dispute already won
- **WHEN** Claim is called for a Held Settlement whose Order has only a Won Dispute
- **THEN** the Settlement is Releasing
