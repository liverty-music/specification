# Spec Delta

## REMOVED Requirements

### Requirement: Release recorded once

**Reason**: A release now claims the Settlement first (Settlement.Claim, Held to Releasing), so the release is recorded from Releasing, not from Held.
**Migration**: Replaced by "Release recorded once, from Releasing" below. No Settlement is Releasing at rest before this change, so no data moves.

## ADDED Requirements

### Requirement: Release recorded once, from Releasing

MarkReleased SHALL take a Settlement and its release claim, and set the Settlement, Releasing under that release claim, to Released with the given provider charge ID and release time, and record each given split's provider payout ID, all together or not at all. When the Settlement is already Released under that release claim with the same provider payout IDs, as when the release was recorded but its caller did not learn it, MarkReleased SHALL change nothing and succeed. It SHALL fail with FailedPrecondition, changing nothing, when the Settlement is not Releasing under that release claim, otherwise, or no Settlement has the id.

#### Scenario: Releasing settlement released

- **WHEN** MarkReleased is called for a Releasing Settlement
- **THEN** it is Released with its provider charge ID, release time and provider payout IDs

#### Scenario: Recorded before a lost response

- **WHEN** MarkReleased is called again under the same release claim with the same provider payout IDs for a Settlement it already made Released
- **THEN** nothing changes and the call succeeds

#### Scenario: Not claimed

- **WHEN** the Settlement is Held, Released or Reversed
- **THEN** MarkReleased fails with FailedPrecondition and changes nothing

#### Scenario: Unknown id

- **WHEN** no Settlement has the id
- **THEN** MarkReleased fails with FailedPrecondition

#### Scenario: Failure changes nothing

- **WHEN** recording any split's provider payout ID fails
- **THEN** the Settlement stays Releasing, with no provider charge ID or release time recorded and no split's provider payout ID recorded
