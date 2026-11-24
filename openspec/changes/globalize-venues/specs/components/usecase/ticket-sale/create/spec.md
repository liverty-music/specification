## MODIFIED Requirements

### Requirement: Only the owner, on published and timed events of one Series

Create SHALL take the caller's Organizer, a Series, a name, the method Lottery or FirstCome, a start time and an end time, each a local date-time, the time zone in which both are read, an optional verification requirement and one or more events. It SHALL:
- fail with InvalidArgument when no event or no end time is given, or when the values break the TicketSale rules;
- read the Series with Series.GetAuthored and fail with PermissionDenied, without revealing whether it exists, when it does not exist or is owned by another Organizer;
- fail with InvalidArgument when an event is not one of the Series' Events;
- fail with FailedPrecondition when Event.IsEventPublished reports false for an event;
- fail with FailedPrecondition when Event.GetEventStartTime returns no start time for an event;
- fail with InvalidArgument when the given time zone is not the time zone of the Venue of at least one of the events, as Event.GetEventStartTime returns it with the start time;
- fail with FailedPrecondition when TicketStock.ListByEvent returns no TicketStock for an event, so every sale has tickets to sell;
- for a Lottery sale, fail with FailedPrecondition when the end time is not before the start time of every event it covers, so a lottery is drawn and its tickets issued before the doors open;
- for a FirstCome sale, fail with FailedPrecondition when the end time is after the start time of any event it covers, so the sale closes no later than the doors open.

#### Scenario: Another Organizer's series
- **WHEN** a member creates a sale for a Series owned by another Organizer
- **THEN** Create fails with PermissionDenied and nothing is stored

#### Scenario: Event of another series
- **WHEN** one of the given events belongs to a different Series
- **THEN** Create fails with InvalidArgument and nothing is stored

#### Scenario: Event not published
- **WHEN** the Series is still draft
- **THEN** Create fails with FailedPrecondition and nothing is stored

#### Scenario: Start time not yet announced
- **WHEN** an event has a date but no start time
- **THEN** Create fails with FailedPrecondition and nothing is stored

#### Scenario: Event without a ticket stock
- **WHEN** one of the given events has no TicketStock
- **THEN** Create fails with FailedPrecondition and nothing is stored

#### Scenario: Sale ends after the event starts
- **WHEN** an event starts at 19:00 on 20 November and the sale's end time is 20:00 on 20 November
- **THEN** Create fails with FailedPrecondition and nothing is stored

#### Scenario: First-come sale ends after the show starts
- **WHEN** the event starts at 19:00 and a FirstCome sale's end time is 19:30 the same day
- **THEN** Create fails with FailedPrecondition and nothing is stored

#### Scenario: Lottery for a show abroad closes before it starts
- **WHEN** an event at a Venue in Asia/Seoul starts at 18:30 on 20 November and a Lottery sale in Asia/Seoul ends at 18:00 on 20 November
- **THEN** the sale is created in the time zone Asia/Seoul

#### Scenario: Tour across two time zones
- **WHEN** a sale covers an event at a Venue in Asia/Tokyo and an event at a Venue in Asia/Seoul, and its time zone is Asia/Tokyo
- **THEN** the sale is created in the time zone Asia/Tokyo

#### Scenario: Time zone of no event's Venue
- **WHEN** every event the sale covers is at a Venue in Asia/Tokyo and its time zone is Asia/Taipei
- **THEN** Create fails with InvalidArgument and nothing is stored

#### Scenario: Doors-open time not announced
- **WHEN** an event starts at 19:00 and has no doors-open time
- **THEN** the sale is created

#### Scenario: Invalid configuration
- **WHEN** the window of a Lottery sale lasts 15 days, or the name is empty
- **THEN** Create fails with InvalidArgument and nothing is stored

#### Scenario: No end time
- **WHEN** the owner creates a FirstCome sale without an end time
- **THEN** Create fails with InvalidArgument and nothing is stored
