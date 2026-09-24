# LotteryUseCase.GetMyApplication

## Purpose

LotteryUseCase.GetMyApplication returns the calling fan's active TicketApplication for a phase, in whatever state it is.

## Requirements

### Requirement: Caller's active application

GetMyApplication SHALL return the calling fan's active application for the phase with TicketApplication.GetByPhaseAndApplicant, and SHALL fail with NotFound when the fan has none; a fan whose applications are all Withdrawn has none.

#### Scenario: Applied application

- **WHEN** the fan has an Applied application for the phase
- **THEN** it is returned

#### Scenario: Only withdrawn

- **WHEN** the fan's only application for the phase is Withdrawn
- **THEN** GetMyApplication fails with NotFound
