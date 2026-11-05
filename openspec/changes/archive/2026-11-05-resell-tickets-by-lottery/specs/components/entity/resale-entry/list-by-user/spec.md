# Spec Delta

## Purpose

Lists a fan's ResaleEntries with their Orders and TicketStocks, so the fan can follow their applications and results.

## ADDED Requirements

### Requirement: A fan's entries

ListByUser SHALL return every ResaleEntry whose Order's user is the given user, in any state, newest first, each with its Order, its TicketStock and the stock's SeatType, and SHALL return an empty list when the user has none.

#### Scenario: Entered and Lapsed
- **WHEN** a fan has an Entered entry made today and a Lapsed entry made last week
- **THEN** both are returned, the Entered one first

#### Scenario: No entries
- **WHEN** the fan never applied
- **THEN** the list is empty
