# Spec Delta

## Purpose

Returns a Releasing Settlement whose payout could not start to Held, so a later release can claim it again.

## ADDED Requirements

### Requirement: Back to held when nothing was paid

Unclaim SHALL take a Settlement and its release claim and make it Held again, clearing the release claim. It SHALL fail with FailedPrecondition, changing nothing, when the Settlement is not Releasing under that release claim, when any of its splits has a provider payout ID, or when no Settlement has the id.

#### Scenario: Payout never started
- **WHEN** Unclaim is called for a Releasing Settlement with its release claim and no provider payout ID recorded
- **THEN** the Settlement is Held

#### Scenario: Not releasing
- **WHEN** Unclaim is called for a Released Settlement
- **THEN** it fails with FailedPrecondition and the Settlement stays Released
