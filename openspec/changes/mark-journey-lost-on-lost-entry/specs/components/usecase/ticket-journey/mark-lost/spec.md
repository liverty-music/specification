# Spec Delta

## Purpose

TicketJourneyUseCase.MarkLost records Lost on a fan's ticket journey for an event once their lottery entry on the platform is lost, outside the draw's own transaction, so a failure here never fails or undoes the draw.

## ADDED Requirements

### Requirement: Lost after a lost lottery entry

MarkLost SHALL run for each lottery entry announced as lost (LotteryEntry.Lost), with its Order's user and the event of its TicketStock. It SHALL record nothing when the entry's lost reason is that the concert was cancelled. It SHALL record nothing when Order.GetHeldForEvent reports one or more tickets for the user and the event, because the fan holds tickets or has another application that may receive them. Otherwise it SHALL record Lost, set by the platform, for the user's journey for the event through TicketJourney.UpsertIfReplaceable. It SHALL NOT raise a hype level. Running it again for the same entry SHALL leave the journey as the first run left it. When a read or UpsertIfReplaceable fails, MarkLost SHALL fail with that error and is run again.

#### Scenario: Not drawn

- **WHEN** a fan whose journey for the event is Applied has their only entry announced lost as not drawn
- **THEN** the journey is Lost set by the platform

#### Scenario: Card could not be charged

- **WHEN** a fan whose journey is Applied has their only entry announced lost because the card could not be charged
- **THEN** the journey is Lost set by the platform

#### Scenario: Concert cancelled

- **WHEN** an entry is announced lost because the concert was cancelled
- **THEN** the fan's journey is unchanged

#### Scenario: Another application still open

- **WHEN** a fan's presale entry is announced lost while their entry in another sale of the event is Entered
- **THEN** the journey stays Applied

#### Scenario: Fan already has a ticket

- **WHEN** an entry is announced lost for a fan who holds an Issued Ticket for the event
- **THEN** the journey is unchanged

#### Scenario: No journey

- **WHEN** an entry is announced lost for a fan who removed their journey for the event and holds nothing for it
- **THEN** the fan's journey is Lost set by the platform

#### Scenario: Recording fails

- **WHEN** TicketJourney.UpsertIfReplaceable fails with Unavailable
- **THEN** MarkLost fails and the journey is Lost when it runs again
