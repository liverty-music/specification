# components/usecase/ticket-sale/set-window Specification

## Purpose
TicketSaleUseCase.SetWindow lets an Organizer move the start and end times of one of its TicketSales: a lottery sale until its window opens, a first-come sale at any time.

## Requirements

### Requirement: Only the Series' Organizer moves the window

SetWindow SHALL take the caller's Organizer, a sale, a start time, an end time and the current time. It SHALL read the sale with TicketSale.Get, failing with NotFound when it does not exist, read its Series with Series.GetAuthored, and fail with PermissionDenied when the calling Organizer does not own that Series.

#### Scenario: Another Organizer's sale
- **WHEN** an Organizer moves the window of a sale on a Series owned by a different Organizer
- **THEN** SetWindow fails with PermissionDenied and nothing changes

#### Scenario: Unknown sale
- **WHEN** the sale does not exist
- **THEN** SetWindow fails with NotFound

### Requirement: A lottery sale's window changes only before it opens

SetWindow SHALL fail with FailedPrecondition, changing nothing, when the sale's method is Lottery and the current time is at or after its current start time, so no fan's entry is made under a window that later moves. A FirstCome sale's window SHALL be changeable at any time.

#### Scenario: Lottery sale before it opens
- **WHEN** a Lottery sale opening on 1 November is moved on 25 October to open on 2 November
- **THEN** the window is changed

#### Scenario: Lottery sale already open
- **WHEN** a Lottery sale that opened on 1 November is moved on 3 November
- **THEN** SetWindow fails with FailedPrecondition and nothing changes

#### Scenario: First-come sale extended while on sale
- **WHEN** a FirstCome sale that opened on 1 November has its end moved later on 3 November, still no later than the event's start time
- **THEN** the window is changed

### Requirement: The new window keeps the sale rules

SetWindow SHALL fail with InvalidArgument when the window breaks the TicketSale rules. It SHALL read the start time of each event the sale names with Event.GetEventStartTime and fail with FailedPrecondition when, for a Lottery sale, the end time is not before the start time of every event, or, for a FirstCome sale, the end time is after the start time of any event. It SHALL read the other sales of each event with TicketSale.ListByEvent and fail with FailedPrecondition when the new window overlaps the window of any of them; the sale's own current window is not compared. Only then SHALL it store the window with TicketSale.SetWindow and return the updated sale with its events.

#### Scenario: Moved onto another sale
- **WHEN** an event's presale runs from 1 to 10 November and its general sale is moved to start on 8 November
- **THEN** SetWindow fails with FailedPrecondition and nothing changes

#### Scenario: Moved within its own window
- **WHEN** a sale running from 1 to 10 November, alone on its events, is moved to run from 2 to 9 November
- **THEN** the window is changed

#### Scenario: Ends after the show starts
- **WHEN** the event starts at 19:00 on 20 November and a FirstCome sale's end is moved to 19:30 the same day
- **THEN** SetWindow fails with FailedPrecondition and nothing changes
