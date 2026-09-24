# TicketApplication.GetPhaseStats

## Purpose

Tallies the applications of one phase for the Organizer's view of it.

## Requirements

### Requirement: Phase tallies

GetPhaseStats SHALL return, over the phase's active applications: the number of applications, the sum of their requested ticket counts, the number of Won applications, the sum of the Won applications' ticket counts, the number of Lost applications, and whether the draw has completed, which is true once any application has a draw position. A phase with no applications SHALL yield all counts zero and the draw not completed.

#### Scenario: After the draw

- **WHEN** a drawn phase has 3 active applications for 2, 2 and 4 tickets, of which the two 2-ticket applications won
- **THEN** there are 3 applications for 8 tickets, 2 winning applications for 4 tickets, 1 waitlisted application, and the draw is completed

#### Scenario: Withdrawn applications excluded

- **WHEN** a phase has one Applied and one Withdrawn application
- **THEN** the application count is 1

#### Scenario: No applications

- **WHEN** the phase has no application
- **THEN** every count is zero and the draw is not completed
