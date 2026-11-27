## Purpose

Merges a discovered Event into another Event at the same Venue and date when the two turn out to be one concert, keeping what fans and performers had on the merged Event.

## ADDED Requirements

### Requirement: Merge one event into another

Merge SHALL take a source Event and a target Event and, all together or not at all:

- add every performer of the source to the target;
- move every fan's TicketJourney from the source to the target, except that a fan who already has a TicketJourney for the target keeps that one;
- move the source's links to TicketSales to the target;
- add the source's listed venue name and other listed venue names to the target's other listed venue names, where the target is not already listed under them;
- remove the source, and the source's Series when it is left with no Event, ConcertCandidate or TicketSale.

It SHALL announce nothing (no Concert.Created). It SHALL fail with InvalidArgument when the two Events are the same Event or are at different Venues or dates, with NotFound when either is not an Event that is not DRAFT, and with FailedPrecondition when the source has a publish state.

#### Scenario: Unknown-start event joins a shared bill

- **WHEN** Artist A's Event without a start time is merged into Artist B's Event at 18:00 at the same Venue and date
- **THEN** the 18:00 Event lists A and B as performers, the Event without a start time is gone, and nothing is announced

#### Scenario: Source series left empty

- **WHEN** the source was the only Event of its discovered Series and that Series has no ConcertCandidate or TicketSale
- **THEN** that Series is removed with the source

#### Scenario: Fan tracking the merged event

- **WHEN** a fan has a TicketJourney Tracking the source and none for the target
- **THEN** after the merge the fan has a TicketJourney Tracking the target

#### Scenario: Fan tracking both events

- **WHEN** a fan has a TicketJourney Applied for the target and Tracking for the source
- **THEN** after the merge the fan's TicketJourney for the target is still Applied

#### Scenario: Different date

- **WHEN** the source is on 2026-12-19 and the target on 2026-12-20
- **THEN** Merge fails with InvalidArgument and nothing changes

#### Scenario: First-party source

- **WHEN** the source is a PUBLISHED Event of a first-party Series
- **THEN** Merge fails with FailedPrecondition and nothing changes
