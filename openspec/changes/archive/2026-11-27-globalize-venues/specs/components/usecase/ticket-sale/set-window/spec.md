## MODIFIED Requirements

### Requirement: Only the Series' Organizer moves the window

SetWindow SHALL take the caller's Organizer, a sale, a start time and an end time, each a local date-time, the time zone in which both are read, and the current time. It SHALL read the sale with TicketSale.Get, failing with NotFound when it does not exist, read its Series with Series.GetAuthored, and fail with PermissionDenied when the calling Organizer does not own that Series.

#### Scenario: Another Organizer's sale
- **WHEN** an Organizer moves the window of a sale on a Series owned by a different Organizer
- **THEN** SetWindow fails with PermissionDenied and nothing changes

#### Scenario: Unknown sale
- **WHEN** the sale does not exist
- **THEN** SetWindow fails with NotFound

### Requirement: The new window keeps the sale rules

SetWindow SHALL fail with InvalidArgument when the window or the time zone breaks the TicketSale rules. It SHALL read the start time of each event the sale names, with the time zone of the event's Venue, with Event.GetEventStartTime, and SHALL fail with InvalidArgument when the given time zone is not the time zone of the Venue of at least one of those events. It SHALL fail with FailedPrecondition when, for a Lottery sale, the end time is not before the start time of every event, or, for a FirstCome sale, the end time is after the start time of any event. It SHALL read the other sales of each event with TicketSale.ListByEvent and fail with FailedPrecondition when the new window overlaps the window of any of them; the sale's own current window is not compared. Only then SHALL it store the window and its time zone with TicketSale.SetWindow and return the updated sale with its events.

#### Scenario: Moved onto another sale
- **WHEN** an event's presale runs from 1 to 10 November and its general sale is moved to start on 8 November
- **THEN** SetWindow fails with FailedPrecondition and nothing changes

#### Scenario: Moved within its own window
- **WHEN** a sale running from 1 to 10 November, alone on its events, is moved to run from 2 to 9 November
- **THEN** the window is changed

#### Scenario: Ends after the show starts
- **WHEN** the event starts at 19:00 on 20 November and a FirstCome sale's end is moved to 19:30 the same day
- **THEN** SetWindow fails with FailedPrecondition and nothing changes

#### Scenario: Time zone of another event's Venue
- **WHEN** a sale names an event at a Venue in Asia/Tokyo and an event at a Venue in Asia/Seoul, and its window is moved in the time zone Asia/Seoul
- **THEN** the window and the time zone Asia/Seoul are stored

#### Scenario: Time zone of no event's Venue
- **WHEN** a sale names only events at Venues in Asia/Tokyo and its window is moved in the time zone Europe/London
- **THEN** SetWindow fails with InvalidArgument and nothing changes
