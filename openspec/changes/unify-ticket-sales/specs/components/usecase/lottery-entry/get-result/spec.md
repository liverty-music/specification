# Spec Delta

## Purpose

LotteryUseCase.GetResult returns the calling fan's LotteryEntry for a TicketType once the draw has run, its state telling whether it won or lost.

## ADDED Requirements

### Requirement: Result after the draw

GetResult SHALL read the calling fan's active entry for the TicketType with LotteryEntry.GetByTicketTypeAndUser, failing with NotFound when there is none, and SHALL fail with FailedPrecondition while that entry is still Entered. Otherwise it SHALL return the entry, which is Won or Lost.

#### Scenario: Fan won
- **WHEN** the draw has run and the fan's entry is Won
- **THEN** the Won entry is returned

#### Scenario: Fan lost
- **WHEN** the draw has run and the fan's entry is Lost
- **THEN** the Lost entry is returned

#### Scenario: Draw not run
- **WHEN** the fan's entry is still Entered
- **THEN** GetResult fails with FailedPrecondition

#### Scenario: Withdrawn or never entered
- **WHEN** the fan has no active entry for the TicketType
- **THEN** GetResult fails with NotFound
