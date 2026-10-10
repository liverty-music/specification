# Spec Delta

## Purpose

Stores a new TicketSale together with its TicketTypes and returns it as stored, not yet drawn.

## ADDED Requirements

### Requirement: Store a sale with its ticket types

Create SHALL store the sale without a drawn time and every one of its TicketTypes together, or nothing, and return the sale with its TicketTypes. It SHALL fail with FailedPrecondition when the Series or an event of a TicketType does not exist, and with InvalidArgument when two of its TicketTypes are for the same event.

#### Scenario: Sale stored
- **WHEN** Create is called for an existing Series with TicketTypes for two of its events
- **THEN** the sale and both TicketTypes are stored and returned, and the sale is not drawn

#### Scenario: Unknown event
- **WHEN** one TicketType names an event that does not exist
- **THEN** Create fails with FailedPrecondition and stores neither the sale nor any TicketType

#### Scenario: Same event twice
- **WHEN** two TicketTypes of the sale are for the same event
- **THEN** Create fails with InvalidArgument and stores nothing
