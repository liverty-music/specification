# LotteryUseCase.GetLotteryPhaseStatus

## Purpose

LotteryUseCase.GetLotteryPhaseStatus shows an Organizer a LotterySalesPhase together with the tallies of its applications and whether its draw has completed.

## Requirements

### Requirement: Phase with its tallies

GetLotteryPhaseStatus SHALL read the phase with LotterySalesPhase.Get, failing with NotFound when it does not exist, and return it with the tallies from TicketApplication.GetPhaseStats.

#### Scenario: Drawn phase

- **WHEN** an Organizer asks for a drawn phase's status
- **THEN** the phase is returned with its application, ticket, winner and waitlist counts and the draw completed

#### Scenario: Unknown phase

- **WHEN** the phase does not exist
- **THEN** GetLotteryPhaseStatus fails with NotFound

### Requirement: Only the event's Organizer sees the status

GetLotteryPhaseStatus SHALL fail with PermissionDenied when the calling Organizer does not own the phase's event.

Known defect: liverty-music/backend#467

#### Scenario: Another Organizer's phase

- **WHEN** an Organizer asks for the status of a phase on an event owned by a different Organizer
- **THEN** GetLotteryPhaseStatus fails with PermissionDenied
