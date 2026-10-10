# Lottery Phase Editor

## Purpose

The organizer console screen where an operator puts one published event on sale by lottery: the application window, the ticket capacity, the per-application limit and the price.

## Requirements

### Requirement: The application window defaults to 10 days

A new lottery phase form SHALL open with the window starting now and closing 10 days later. The screen SHALL accept a window of 1 to 14 days and SHALL show an error next to the window, without saving, for any other length.

#### Scenario: Blank form

- **WHEN** an operator opens the lottery phase editor for an event without a phase at 2026-10-01 12:00
- **THEN** the window opens at 2026-10-01 12:00 and closes at 2026-10-11 12:00

#### Scenario: Window too long

- **WHEN** the operator sets a window of 15 days and saves
- **THEN** an error is shown next to the window and nothing is saved

### Requirement: An event goes on sale only with its start time

When the event has no start time, the lottery phase editor SHALL say that the start time must be set in the concert editor before the event can go on sale, link to the concert editor, and SHALL not save the phase. An event without an open time SHALL go on sale as usual.

#### Scenario: Start time not set

- **WHEN** an operator opens the lottery phase editor for a published event with no start time
- **THEN** the screen says the start time must be set first, links to the concert editor, and saving is not offered
