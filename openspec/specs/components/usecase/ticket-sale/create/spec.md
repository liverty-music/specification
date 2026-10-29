# components/usecase/ticket-sale/create Specification

## Purpose
TicketSaleUseCase.Create lets an Organizer open a sale (受付), by lottery or first come, first served - its name, window and verification requirement, and one or more events it covers - on published events of one of its Series.

## Requirements

### Requirement: Only the owner, on published and timed events of one Series

Create SHALL take the caller's Organizer, a Series, a name, the method Lottery or FirstCome, a start time, an end time, an optional verification requirement and one or more events. It SHALL:
- fail with InvalidArgument when no event or no end time is given, or when the values break the TicketSale rules;
- read the Series with Series.GetAuthored and fail with PermissionDenied, without revealing whether it exists, when it does not exist or is owned by another Organizer;
- fail with InvalidArgument when an event is not one of the Series' Events;
- fail with FailedPrecondition when Event.IsEventPublished reports false for an event;
- fail with FailedPrecondition when Event.GetEventStartTime returns no start time for an event;
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

#### Scenario: Doors-open time not announced
- **WHEN** an event starts at 19:00 and has no doors-open time
- **THEN** the sale is created

#### Scenario: Invalid configuration
- **WHEN** the window of a Lottery sale lasts 15 days, or the name is empty
- **THEN** Create fails with InvalidArgument and nothing is stored

#### Scenario: No end time
- **WHEN** the owner creates a FirstCome sale without an end time
- **THEN** Create fails with InvalidArgument and nothing is stored

### Requirement: A sale needs the Organizer's business details

For a sale of either method, Create SHALL read the Organizer with Organizer.Get and fail with FailedPrecondition, storing nothing, when the Organizer does not have complete business details (legal name, representative name, business address, business phone number and contact email), because a fan pays at checkout or when a lottery entry wins, and the 特商法 (Specified Commercial Transactions Act) disclosure must show them.

#### Scenario: Business details missing
- **WHEN** the Organizer has no business address and the owner creates a FirstCome sale
- **THEN** Create fails with FailedPrecondition and nothing is stored

#### Scenario: Lottery without business details
- **WHEN** the Organizer has no business address and the owner creates a Lottery sale
- **THEN** Create fails with FailedPrecondition and nothing is stored

### Requirement: Sales of one event never overlap

Create SHALL read the existing sales of every event it covers with TicketSale.ListByEvent and fail with FailedPrecondition, storing nothing, when the new sale's window overlaps the window of any of them.

#### Scenario: General sale after the presale
- **WHEN** an event's presale ends on 10 November and a general sale for the same event starts on 20 November
- **THEN** the general sale is created

#### Scenario: Overlapping sale
- **WHEN** an event's presale runs from 1 to 10 November and a new sale for the same event starts on 8 November
- **THEN** Create fails with FailedPrecondition and nothing is stored

#### Scenario: Other events are not affected
- **WHEN** the overlapping existing sale covers only other events of the Series
- **THEN** the sale is created

### Requirement: Store the sale with its events

Create SHALL store the sale naming its events with TicketSale.Create, with the verification requirement None when none is given, and return the stored sale with its events, not drawn.

#### Scenario: Tour presale
- **WHEN** the owner creates a 10-day Lottery sale named ファンクラブ先行 for two published, timed events that each have TicketStocks of S席 and A席
- **THEN** the sale is stored, not drawn, with the requirement None, and returned naming its two events
