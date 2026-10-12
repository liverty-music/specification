# Lottery Sale Editor

## Purpose

The organizer console screen where an operator puts one published event on sale by lottery: the sale's name and window, and its TicketType's quantity, per-account limit and price.

## Requirements

### Requirement: The sale window defaults to 10 days

A new lottery sale form SHALL open with the window starting now and closing 10 days later. The screen SHALL accept a window of 1 to 14 days and SHALL show an error next to the window, without saving, for any other length.

#### Scenario: Blank form

- **WHEN** an operator opens the lottery sale editor for an event without a sale at 2026-10-01 12:00
- **THEN** the window opens at 2026-10-01 12:00 and closes at 2026-10-11 12:00

#### Scenario: Window too long

- **WHEN** the operator sets a window of 15 days and saves
- **THEN** an error is shown next to the window and nothing is saved

### Requirement: An event goes on sale only with its start time

When the event has no start time, the lottery sale editor SHALL say that the start time must be set in the concert editor before the event can go on sale, link to the concert editor, and SHALL not save the sale. An event without an open time SHALL go on sale as usual.

#### Scenario: Start time not set

- **WHEN** an operator opens the lottery sale editor for a published event with no start time
- **THEN** the screen says the start time must be set first, links to the concert editor, and saving is not offered

### Requirement: The editor creates a named lottery sale for one event

The editor SHALL create a Lottery TicketSale for the event it was opened from, with a name, the window, and one TicketType for that event with a quantity, a per-account limit and a price. The name SHALL be required, and the per-account limit SHALL default to 4 and accept 1 to 10. When a sale of the event already overlaps the entered window, the screen SHALL say so next to the window and SHALL not save.

#### Scenario: Presale for one event
- **WHEN** an operator names the sale ファンクラブ先行, keeps the 10-day window and enters 100 tickets at 8000 yen
- **THEN** a Lottery sale named ファンクラブ先行 is created with one TicketType of 100 tickets at 8000 yen and a per-account limit of 4

#### Scenario: Missing name
- **WHEN** the operator saves without a name
- **THEN** an error is shown next to the name and nothing is saved

#### Scenario: Overlapping window
- **WHEN** the event already has a sale from 1 to 10 November and the operator enters a window starting 8 November
- **THEN** the screen says the window overlaps that sale and nothing is saved
