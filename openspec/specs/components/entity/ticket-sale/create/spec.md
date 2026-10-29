# components/entity/ticket-sale/create Specification

## Purpose
Stores a new TicketSale together with its TicketTypes.

## Requirements

### Requirement: Store a sale with its events

Create SHALL store the sale together with the events it names, or nothing, and return the sale with its events. It SHALL fail with InvalidArgument when the sale breaks the TicketSale rules or names the same event twice, and with FailedPrecondition when the Series or a named event does not exist.

#### Scenario: Sale stored
- **WHEN** Create is called for an existing Series with two of its events
- **THEN** the sale is stored and returned with both events, and the sale is not drawn

#### Scenario: Unknown event
- **WHEN** the sale names an event that does not exist
- **THEN** Create fails with FailedPrecondition and stores nothing

#### Scenario: Same event twice
- **WHEN** the sale names the same event twice
- **THEN** Create fails with InvalidArgument and stores nothing

#### Scenario: Event of another Series
- **WHEN** an Organizer's sale names an event of another Series
- **THEN** Create fails with InvalidArgument and stores nothing
