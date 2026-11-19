# Spec Delta

## RENAMED Requirements

- FROM: `### Requirement: The discovered time is set once`
- TO: `### Requirement: The find time is set once`

## MODIFIED Requirements

### Requirement: The find time is set once

A discovered sale's find time SHALL be set when the sale is first stored and SHALL never change afterwards, however often the sale is discovered again.

#### Scenario: Re-discovery keeps the find time
- **WHEN** a sale first stored on 1 June is discovered again on 5 June with new details
- **THEN** its find time stays 1 June

### Requirement: An Organizer's sale names events, a discovered sale none

A TicketSale of a Series that has an Organizer SHALL be that Organizer's sale. It SHALL name at least one event, each an event of its Series, SHALL sell every TicketStock of the events it names, and SHALL have no find time. A TicketSale of a Series without an Organizer SHALL be a discovered sale. It SHALL name no event, SHALL have a find time and SHALL have the verification requirement None.

#### Scenario: Organizer's presale
- **WHEN** a sale belongs to a Series owned by an Organizer and names two of its events
- **THEN** it is the Organizer's sale and sells every TicketStock of those two events

#### Scenario: Sale found by discovery
- **WHEN** a sale belongs to a Series that has no Organizer
- **THEN** it is a discovered sale and names no event

#### Scenario: Discovered sale naming an event
- **WHEN** a sale of a Series without an Organizer names an event
- **THEN** the sale is invalid

#### Scenario: Organizer's sale without an event
- **WHEN** a sale of a Series with an Organizer names no event
- **THEN** the sale is invalid

#### Scenario: Event of another Series
- **WHEN** an Organizer's sale names an event of another Series
- **THEN** the sale is invalid
