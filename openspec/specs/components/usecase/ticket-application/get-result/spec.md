# LotteryUseCase.GetResult

## Purpose

LotteryUseCase.GetResult returns the calling fan's TicketApplication for a phase once the draw has run, its state telling whether it won or lost.

## Requirements

### Requirement: Result after the draw

GetResult SHALL read the calling fan's active application for the phase with TicketApplication.GetByPhaseAndApplicant, failing with NotFound when there is none, and SHALL fail with FailedPrecondition while that application is still Applied. Otherwise it SHALL return the application, which is Won or Lost.

#### Scenario: Fan won

- **WHEN** the draw has run and the fan's application is Won
- **THEN** the Won application is returned

#### Scenario: Fan lost

- **WHEN** the draw has run and the fan's application is Lost
- **THEN** the Lost application is returned

#### Scenario: Draw not run

- **WHEN** the fan's application is still Applied
- **THEN** GetResult fails with FailedPrecondition

#### Scenario: Withdrawn or never applied

- **WHEN** the fan has no active application for the phase
- **THEN** GetResult fails with NotFound
