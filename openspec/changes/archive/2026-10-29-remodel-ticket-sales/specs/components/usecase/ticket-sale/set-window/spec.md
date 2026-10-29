# Spec Delta

## MODIFIED Requirements

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
